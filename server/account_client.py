# Adapted from the owner's LazyingArtCoin account consumer at b3e7ebf.
# Profile-only Platform preparation; no Coin ledger or provider authority.
"""Backend client for LazyingArt account contract v1 (OAuth, not OIDC).

Not imported by the production companion. Configuration and browser/native
callback registration must be supplied by the central account owner. No
provider password, ID token, wallet authority or credit grant is handled here.
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import re
import secrets
import time
from dataclasses import dataclass, field
from urllib.parse import parse_qs, urlencode, urlsplit

import tornado.httpclient


class AccountError(ValueError):
    """A safe error code; never includes provider bodies or credentials."""


def https_url(value: str, *, origin_only: bool = False) -> str:
    if not isinstance(value, str) or not value or re.search(r"[\s\\\x00-\x1f]", value):
        raise AccountError("invalid_configuration")
    try:
        parsed = urlsplit(value)
        port = parsed.port
    except ValueError:
        raise AccountError("invalid_configuration") from None
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username is not None
            or parsed.password is not None or parsed.query or parsed.fragment or "*" in value
            or "?" in value or "#" in value or (port is not None and port <= 0)
            or (origin_only and parsed.path)):
        raise AccountError("invalid_configuration")
    return value


@dataclass(frozen=True)
class ClientConfiguration:
    issuer: str
    client_id: str
    audience: str
    redirect_uri: str
    client_secret: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        https_url(self.issuer, origin_only=True)
        https_url(self.redirect_uri)
        for value in (self.client_id, self.audience):
            if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9:._/-]{1,200}", value):
                raise AccountError("invalid_configuration")
        if not isinstance(self.client_secret, str) or len(self.client_secret) > 4096:
            raise AccountError("invalid_configuration")

    def credentials(self) -> dict:
        result = {"client_id": self.client_id, "audience": self.audience}
        if self.client_secret:
            result["client_secret"] = self.client_secret
        return result


@dataclass(frozen=True)
class Discovery:
    issuer: str
    providers: tuple[str, ...]


@dataclass
class AuthorizationAttempt:
    issuer: str
    client_id: str
    audience: str
    redirect_uri: str
    state: str = field(repr=False)
    verifier: str = field(repr=False)
    expires_at: float
    consumed: bool = False


@dataclass(frozen=True)
class Credentials:
    access_token: str = field(repr=False)
    refresh_token: str = field(repr=False)
    expires_at: float


@dataclass(frozen=True)
class Identity:
    issuer: str
    subject: str
    display_name: str
    client_id: str


@dataclass(frozen=True)
class IdentityEvidence:
    identity: Identity
    email_verified: bool
    auth_time: int


def pkce_challenge(verifier: str) -> str:
    if not isinstance(verifier, str) or not re.fullmatch(r"[A-Za-z0-9._~-]{43,128}", verifier):
        raise AccountError("invalid_pkce")
    return base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).decode().rstrip("=")


def credential(value: object) -> str:
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{32,4096}", value):
        raise AccountError("invalid_credential_response")
    return value


class AccountClient:
    """Use one server-pinned configuration per registered app/platform client.

    Callers own protected persistence, browser binding, durable one-use state,
    local session issuance and CSRF. This protocol core is not an HTTP login
    endpoint or a production session store.
    """

    def __init__(self, config: ClientConfiguration, *, http=None, clock=time.time):
        self.config, self.clock = config, clock
        self._owns_http = http is None
        self.http = http or tornado.httpclient.AsyncHTTPClient(force_instance=True, max_body_size=65536)

    def close(self) -> None:
        if self._owns_http:
            self.http.close()

    async def _request(self, path: str, body=None, token=None) -> dict:
        headers = {"Accept": "application/json"}
        if body is not None:
            headers["Content-Type"] = "application/json"
        if token is not None:
            headers["Authorization"] = "Bearer " + credential(token)
        try:
            response = await self.http.fetch(
                self.config.issuer + path, method="GET" if body is None else "POST",
                body=None if body is None else json.dumps(body), headers=headers,
                follow_redirects=False, validate_cert=True, request_timeout=15,
                connect_timeout=5, raise_error=False,
            )
        except (tornado.httpclient.HTTPClientError, OSError, asyncio.TimeoutError):
            raise AccountError("account_service_unavailable") from None
        if response.code in (401, 403):
            raise AccountError("account_authorization_required")
        if response.code != 200:
            raise AccountError("account_service_unavailable")
        try:
            result = json.loads(response.body)
        except (ValueError, UnicodeError):
            raise AccountError("invalid_account_response") from None
        if not isinstance(result, dict):
            raise AccountError("invalid_account_response")
        return result

    async def discover(self, *, require_introspection=False) -> Discovery:
        data = await self._request("/.well-known/lazyingart-account")
        if (type(data.get("contract_version")) is not int or data["contract_version"] != 1
                or data.get("issuer") != self.config.issuer
                or data.get("registration_requires_invitation") is not False):
            raise AccountError("unsupported_account_contract")
        for key, path in {
            "authorization_endpoint": "/account/authorize", "token_endpoint": "/account/token",
            "profile_endpoint": "/account/profile", "revocation_endpoint": "/account/revoke",
            "account_endpoint": "/account",
        }.items():
            if data.get(key) != self.config.issuer + path:
                raise AccountError("untrusted_account_endpoint")
        for key, expected in {
            "response_types_supported": "code", "grant_types_supported": "authorization_code",
            "code_challenge_methods_supported": "S256", "scopes_supported": "profile",
        }.items():
            if not isinstance(data.get(key), list) or expected not in data[key]:
                raise AccountError("unsupported_account_contract")
        if "refresh_token" not in data["grant_types_supported"]:
            raise AccountError("unsupported_account_contract")
        if require_introspection and (not self.config.client_secret or data.get('introspection_endpoint') != self.config.issuer + '/account/introspect'):
            raise AccountError('unsupported_account_contract')
        flags = data.get("providers")
        if not isinstance(flags, dict) or any(type(flags.get(p)) is not bool for p in ("password", "google", "apple", "github")):
            raise AccountError("invalid_provider_discovery")
        return Discovery(self.config.issuer, tuple(p for p in ("password", "google", "apple", "github") if flags[p]))

    def begin(self, discovery: Discovery) -> tuple[AuthorizationAttempt, str]:
        if discovery.issuer != self.config.issuer:
            raise AccountError("issuer_mismatch")
        attempt = AuthorizationAttempt(
            self.config.issuer, self.config.client_id, self.config.audience,
            self.config.redirect_uri, secrets.token_urlsafe(32), secrets.token_urlsafe(48),
            self.clock() + 600,
        )
        query = {"response_type": "code", "client_id": self.config.client_id,
                 "audience": self.config.audience, "redirect_uri": self.config.redirect_uri,
                 "scope": "profile", "state": attempt.state,
                 "code_challenge": pkce_challenge(attempt.verifier), "code_challenge_method": "S256"}
        return attempt, self.config.issuer + "/account/authorize?" + urlencode(query)

    async def complete(self, attempt: AuthorizationAttempt, callback_url: str) -> Credentials:
        # No await before the local consumed flag is set. The HTTP integration
        # must additionally consume its durable browser-bound attempt atomically.
        if attempt.consumed or self.clock() >= attempt.expires_at:
            raise AccountError("authorization_attempt_expired")
        if (attempt.issuer, attempt.client_id, attempt.audience, attempt.redirect_uri) != (
                self.config.issuer, self.config.client_id, self.config.audience, self.config.redirect_uri):
            raise AccountError("authorization_attempt_mismatch")
        if (not isinstance(callback_url, str) or len(callback_url) > 8192
                or re.search(r"[\s\\\x00-\x1f]", callback_url)):
            raise AccountError("invalid_callback")
        expected = urlsplit(self.config.redirect_uri)
        try:
            url = urlsplit(callback_url)
            values = parse_qs(url.query, keep_blank_values=True, strict_parsing=True, max_num_fields=8)
        except ValueError:
            raise AccountError("invalid_callback") from None
        if (url.scheme, url.netloc, url.path) != (expected.scheme, expected.netloc, expected.path) or "#" in callback_url:
            raise AccountError("invalid_callback")
        if any(len(v) != 1 for v in values.values()) or set(values) not in ({"state", "iss", "code"}, {"state", "iss", "error"}):
            raise AccountError("invalid_callback")
        if not secrets.compare_digest(values["state"][0].encode(), attempt.state.encode()) or values["iss"][0] != self.config.issuer:
            raise AccountError("callback_binding_mismatch")
        if "error" in values:
            attempt.consumed = True
            raise AccountError("authorization_cancelled")
        code = credential(values["code"][0])
        attempt.consumed = True
        return self._tokens(await self._request("/account/token", {
            **self.config.credentials(), "grant_type": "authorization_code", "code": code,
            "redirect_uri": self.config.redirect_uri, "code_verifier": attempt.verifier,
        }))

    def _tokens(self, result: dict) -> Credentials:
        ttl = result.get("expires_in")
        if result.get("token_type") != "Bearer" or result.get("scope") != "profile" or type(ttl) is not int or not 0 < ttl <= 600:
            raise AccountError("invalid_credential_response")
        return Credentials(credential(result.get("access_token")), credential(result.get("refresh_token")), self.clock() + ttl)

    async def profile(self, tokens: Credentials) -> Identity:
        if self.clock() >= tokens.expires_at:
            raise AccountError("account_authorization_required")
        data = await self._request("/account/profile", self.config.credentials(), tokens.access_token)
        if (set(data) != {"subject", "display_name", "client_id", "account_status"}
                or data.get("client_id") != self.config.client_id or data.get("account_status") != "active"
                or not isinstance(data.get("subject"), str) or not re.fullmatch(r"la_[A-Za-z0-9_-]{16,160}", data["subject"])
                or not isinstance(data.get("display_name"), str) or len(data["display_name"]) > 200):
            raise AccountError("invalid_account_identity")
        return Identity(self.config.issuer, data["subject"], data["display_name"], self.config.client_id)

    async def refresh(self, tokens: Credentials) -> Credentials:
        # Deliberately no transport retry: the issuer revokes a family on reuse.
        return self._tokens(await self._request("/account/token", {
            **self.config.credentials(), "grant_type": "refresh_token", "refresh_token": credential(tokens.refresh_token),
        }))

    async def revoke(self, tokens: Credentials) -> None:
        result = await self._request("/account/revoke", {**self.config.credentials(), "token": credential(tokens.refresh_token)})
        if result.get("success") is not True:
            raise AccountError("invalid_account_response")

    async def introspect(self, tokens: Credentials) -> IdentityEvidence:
        if not self.config.client_secret:
            raise AccountError('confidential_client_required')
        try:
            data = await self._request('/account/introspect', {
                **self.config.credentials(), 'token': credential(tokens.access_token), 'token_type_hint': 'access_token'})
        except AccountError as exc:
            # Introspection reports revoked user tokens as HTTP 200 active:false.
            # HTTP 401 here is confidential-client authentication failure.
            if str(exc) == 'account_authorization_required':
                raise AccountError('account_service_unavailable') from None
            raise
        if data == {'active': False}:
            raise AccountError('account_authorization_required')
        account = data.get('account')
        now = self.clock()
        if (data.get('active') is not True or data.get('iss') != self.config.issuer
                or data.get('client_id') != self.config.client_id or data.get('aud') != self.config.audience
                or data.get('scope') != 'profile' or data.get('token_type') != 'Bearer'
                or any(type(data.get(k)) is not int for k in ('iat', 'exp', 'auth_time'))
                or not 0 < data['auth_time'] <= data['iat'] <= now + 30
                or not now < data['exp'] <= data['iat'] + 600
                or not isinstance(account, dict) or set(account) != {'subject', 'display_name', 'account_status', 'email_verified'}
                or account.get('subject') != data.get('sub') or account.get('account_status') != 'active'
                or not isinstance(data.get('sub'), str) or not re.fullmatch(r'la_[A-Za-z0-9_-]{16,160}', data['sub'])
                or not isinstance(account.get('display_name'), str) or len(account['display_name']) > 200
                or type(account.get('email_verified')) is not bool
                or data.get('verified_legacy_identities') != []):
            raise AccountError('invalid_account_identity')
        return IdentityEvidence(Identity(self.config.issuer, data['sub'], account['display_name'], self.config.client_id),
                                account['email_verified'], data['auth_time'])


class RefreshCoordinator:
    """Single-flight primitive for one app session, not durable persistence.

    Callers must persist a refresh-in-flight barrier before I/O. After a crash
    with that barrier or a lost response, reconnect through code/PKCE instead
    of loading and reusing the old refresh credential.
    """

    def __init__(self, client: AccountClient, tokens: Credentials):
        self.client, self._tokens = client, tokens
        self._lock = asyncio.Lock()

    async def current(self) -> Credentials:
        async with self._lock:
            if self._tokens is None:
                raise AccountError("account_reconnect_required")
            if self._tokens.expires_at - self.client.clock() > 30:
                return self._tokens
            previous, self._tokens = self._tokens, None
            # On cancellation, invalid grant or uncertain network outcome, the
            # old credential remains unusable. Existing app drafts are external.
            self._tokens = await self.client.refresh(previous)
            return self._tokens
