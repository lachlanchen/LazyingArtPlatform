# Adapted from the owner's LazyingArtCoin account consumer at b3e7ebf.
# Profile-only Platform preparation; no Coin ledger or provider authority.
"""Protocol tests use synthetic credentials and make no network requests."""

import asyncio
import json
from types import SimpleNamespace
from urllib.parse import parse_qs, urlencode, urlsplit

import pytest
from tornado.httpclient import HTTPRequest

from server.account_client import (
    AccountClient, AccountError, ClientConfiguration, Credentials, Discovery,
    RefreshCoordinator, pkce_challenge,
)


ISSUER = 'https://accounts.example.test'
CALLBACK = 'https://platform.example.test/auth/callback'
SECRET = 'synthetic-server-client-secret'
SUBJECT = 'la_' + 'a' * 32


def discovery(**changes):
    result = {
        'issuer': ISSUER, 'contract_version': 1,
        'registration_requires_invitation': False,
        'providers': dict(password=True, google=False, apple=False, github=True),
        'response_types_supported': ['code'],
        'grant_types_supported': ['authorization_code', 'refresh_token'],
        'code_challenge_methods_supported': ['S256'], 'scopes_supported': ['profile'],
    }
    for key, path in [('authorization_endpoint', '/account/authorize'),
                      ('token_endpoint', '/account/token'), ('profile_endpoint', '/account/profile'),
                      ('revocation_endpoint', '/account/revoke'), ('account_endpoint', '/account')]:
        result[key] = ISSUER + path
    return result | changes


def token_response(**changes):
    return dict(access_token='a' * 48, refresh_token='r' * 48,
                token_type='Bearer', scope='profile', expires_in=600) | changes


class Transport:
    def __init__(self, *replies):
        self.replies, self.requests = list(replies), []

    async def fetch(self, url, *, raise_error, **kwargs):
        # Exercise Tornado's actual request options, not just an accepting mock.
        request = HTTPRequest(url, **kwargs)
        assert raise_error is False
        assert request.follow_redirects is False and request.validate_cert is True
        assert request.connect_timeout == 5 and request.request_timeout == 15
        self.requests.append(request)
        reply = self.replies.pop(0)
        if isinstance(reply, BaseException):
            raise reply
        if callable(reply):
            reply = await reply()
        if isinstance(reply, dict):
            reply = SimpleNamespace(code=200, body=json.dumps(reply).encode())
        return reply


def client(*responses):
    transport = Transport(*responses)
    config = ClientConfiguration(ISSUER, 'platform-web', 'platform-api', CALLBACK, SECRET)
    return AccountClient(config, http=transport, clock=lambda: 1000), transport


def callback(attempt, **changes):
    return CALLBACK + '?' + urlencode(dict(state=attempt.state, iss=ISSUER, code='c' * 48) | changes)


def run(coroutine):
    return asyncio.run(coroutine)


def test_rfc7636_vector():
    assert pkce_challenge('dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk') == 'E9Melhoa2OwvFrEMTJguCHaoeK1t8URWbuGJSstw-cM'


@pytest.mark.parametrize('field,value', [
    ('issuer', 'http://accounts.example.test'), ('issuer', ISSUER + '/'),
    ('issuer', 'https://user:pass@accounts.example.test'), ('issuer', ISSUER + '#'),
    ('redirect_uri', 'coin://callback'), ('redirect_uri', CALLBACK + '?'),
    ('redirect_uri', CALLBACK + '/*'), ('redirect_uri', CALLBACK + '\\extra'),
    ('client_id', '../bad?'), ('audience', ''),
])
def test_configuration_rejects_unsafe_endpoints(field, value):
    args = dict(issuer=ISSUER, client_id='platform-web', audience='platform-api', redirect_uri=CALLBACK)
    with pytest.raises(AccountError, match='invalid_configuration'):
        ClientConfiguration(**(args | {field: value}))


@pytest.mark.parametrize('changes', [
    dict(issuer='https://attacker.example'), dict(contract_version=True),
    dict(token_endpoint='https://attacker.example/token'),
    dict(profile_endpoint=ISSUER + '/legacy/profile'), dict(registration_requires_invitation=True),
    dict(code_challenge_methods_supported=['plain']), dict(grant_types_supported=['authorization_code']),
    dict(providers=dict(password=True, google='true', apple=False, github=False)),
])
def test_discovery_rejects_wrong_issuer_poisoned_endpoints_and_incompatible_contract(changes):
    api, transport = client(discovery(**changes))
    with pytest.raises(AccountError):
        run(api.discover())
    assert len(transport.requests) == 1
    assert 'Authorization' not in transport.requests[0].headers


def test_code_exchange_profile_and_revocation_are_client_bound():
    async def scenario():
        api, transport = client(discovery(), token_response(), dict(
            subject=SUBJECT, client_id='platform-web', display_name='Member', account_status='active'),
            dict(success=True))
        found = await api.discover()
        assert found.providers == ('password', 'github')
        attempt, url = api.begin(found)
        query = parse_qs(urlsplit(url).query)
        assert query['code_challenge'] == [pkce_challenge(attempt.verifier)]
        assert query['audience'] == ['platform-api'] and query['scope'] == ['profile']
        assert SECRET not in url and attempt.verifier not in url
        tokens = await api.complete(attempt, callback(attempt))
        identity = await api.profile(tokens)
        assert identity.subject == SUBJECT and identity.issuer == ISSUER
        exchange = json.loads(transport.requests[1].body)
        assert exchange == dict(client_id='platform-web', audience='platform-api', client_secret=SECRET,
                                grant_type='authorization_code', code='c' * 48,
                                redirect_uri=CALLBACK, code_verifier=attempt.verifier)
        assert transport.requests[2].headers['Authorization'] == 'Bearer ' + tokens.access_token
        await api.revoke(tokens)
        assert json.loads(transport.requests[3].body)['token'] == tokens.refresh_token
        assert SECRET not in repr(api.config)
        assert tokens.access_token not in repr(tokens) and tokens.refresh_token not in repr(tokens)
        assert attempt.verifier not in repr(attempt) and attempt.state not in repr(attempt)
        with pytest.raises(AccountError, match='expired'):
            await api.complete(attempt, callback(attempt))
        assert len(transport.requests) == 4
    run(scenario())


@pytest.mark.parametrize('modify', [
    lambda a: callback(a, state='wrong'), lambda a: callback(a, state='错误'),
    lambda a: callback(a, iss='https://attacker.example'),
    lambda a: callback(a) + '&code=' + 'd' * 48,
    lambda a: callback(a) + '&extra=yes', lambda a: callback(a) + '#',
    lambda a: callback(a).replace('/auth/callback?', '/other?'),
    lambda a: callback(a).replace('platform.example.test', 'attacker.example'),
])
def test_invalid_callback_does_not_exchange_or_consume_legitimate_attempt(modify):
    async def scenario():
        api, transport = client(token_response())
        attempt, _ = api.begin(Discovery(ISSUER, ('password',)))
        with pytest.raises(AccountError):
            await api.complete(attempt, modify(attempt))
        assert not attempt.consumed and not transport.requests
        await api.complete(attempt, callback(attempt))
        assert len(transport.requests) == 1
    run(scenario())


def test_cancellation_expiry_and_client_mixup_never_exchange():
    async def scenario():
        api, transport = client()
        attempt, _ = api.begin(Discovery(ISSUER, ()))
        denied = CALLBACK + '?' + urlencode(dict(state=attempt.state, iss=ISSUER, error='access_denied'))
        with pytest.raises(AccountError, match='cancelled'):
            await api.complete(attempt, denied)
        assert attempt.consumed
        attempt, _ = api.begin(Discovery(ISSUER, ()))
        attempt.expires_at = 1000
        with pytest.raises(AccountError, match='expired'):
            await api.complete(attempt, callback(attempt))
        attempt, _ = api.begin(Discovery(ISSUER, ()))
        attempt.audience = 'other-app'
        with pytest.raises(AccountError, match='mismatch'):
            await api.complete(attempt, callback(attempt))
        assert not transport.requests
    run(scenario())


@pytest.mark.parametrize('response', [
    OSError('synthetic transport secret'),
    SimpleNamespace(code=302, body=b'synthetic transport secret'),
    SimpleNamespace(code=200, body=b'not-json synthetic transport secret'),
])
def test_uncertain_exchange_is_never_retried_and_error_bodies_are_private(response):
    async def scenario():
        api, transport = client(response)
        attempt, _ = api.begin(Discovery(ISSUER, ()))
        with pytest.raises(AccountError) as error:
            await api.complete(attempt, callback(attempt))
        assert 'synthetic transport secret' not in str(error.value)
        with pytest.raises(AccountError, match='expired'):
            await api.complete(attempt, callback(attempt))
        assert len(transport.requests) == 1
    run(scenario())


@pytest.mark.parametrize('changes', [dict(client_id='another-app'), dict(account_status='suspended'),
    dict(subject='echomind:123'), dict(legacy_user_id=123), dict(display_name=None)])
def test_profile_rejects_cross_app_inactive_or_privileged_identity(changes):
    api, _ = client(dict(subject=SUBJECT, client_id='platform-web', display_name='Member', account_status='active') | changes)
    with pytest.raises(AccountError, match='invalid_account_identity'):
        run(api.profile(Credentials('a' * 48, 'r' * 48, 1600)))


@pytest.mark.parametrize('changes', [dict(expires_in=True), dict(expires_in=601),
    dict(expires_in=0), dict(access_token='short'), dict(scope='admin'), dict(refresh_token=None)])
def test_invalid_credentials_fail_closed(changes):
    async def scenario():
        api, _ = client(token_response(**changes))
        attempt, _ = api.begin(Discovery(ISSUER, ()))
        with pytest.raises(AccountError, match='invalid_credential_response'):
            await api.complete(attempt, callback(attempt))
    run(scenario())


def test_concurrent_refresh_rotates_only_once():
    async def scenario():
        async def delayed():
            await asyncio.sleep(0)
            return token_response(refresh_token='n' * 48)
        api, transport = client(delayed)
        session = RefreshCoordinator(api, Credentials('a' * 48, 'r' * 48, 1001))
        results = await asyncio.gather(*(session.current() for _ in range(12)))
        assert len(transport.requests) == 1
        assert all(r.refresh_token == 'n' * 48 for r in results)
        assert json.loads(transport.requests[0].body)['audience'] == 'platform-api'
    run(scenario())


def test_lost_refresh_response_abandons_old_token():
    async def scenario():
        api, transport = client(OSError('lost response'))
        session = RefreshCoordinator(api, Credentials('a' * 48, 'r' * 48, 1001))
        with pytest.raises(AccountError, match='unavailable'):
            await session.current()
        with pytest.raises(AccountError, match='reconnect_required'):
            await session.current()
        assert len(transport.requests) == 1
    run(scenario())


def introspection(**changes):
    return dict(active=True, iss=ISSUER, sub=SUBJECT, client_id='platform-web', aud='platform-api', scope='profile',
        token_type='Bearer', iat=990, exp=1500, auth_time=900, verified_legacy_identities=[],
        account=dict(subject=SUBJECT, display_name='Member', account_status='active', email_verified=True)) | changes


@pytest.mark.parametrize('changes', [dict(iss='https://other.example'), dict(aud='other-api'),
    dict(client_id='other-app'), dict(exp=999), dict(exp=9999), dict(auth_time=True), dict(auth_time=1001),
    dict(iat=1100), dict(scope='admin'), dict(sub='echomind:123'),
    dict(verified_legacy_identities=[dict(user_id=123)]), dict(active=False)])
def test_introspection_requires_current_bound_minimal_claims(changes):
    api, _ = client(introspection(**changes))
    with pytest.raises(AccountError, match='invalid_account_identity'):
        run(api.introspect(Credentials('a' * 48, 'r' * 48, 1600)))


def test_introspection_distinguishes_revocation_from_client_auth_outage():
    api, _ = client({'active': False}, SimpleNamespace(code=401, body=b'client secret rejected'), introspection())
    tokens = Credentials('a' * 48, 'r' * 48, 1600)
    with pytest.raises(AccountError, match='authorization_required'):
        run(api.introspect(tokens))
    with pytest.raises(AccountError, match='service_unavailable'):
        run(api.introspect(tokens))
    result = run(api.introspect(tokens))
    assert result.identity.subject == SUBJECT and result.email_verified is True and result.auth_time == 900
