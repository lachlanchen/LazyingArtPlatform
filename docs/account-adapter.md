# Shared account and personal dashboard — not live yet

The public hub remains available without signing in. EchoMind owns the shared
account and its Google, Apple, GitHub and email flows. This repository owns only
an app-local consumer; it must not become a second identity provider.

`server/account_client.py` and `server/account_sessions.py` adapt the owner's
LazyingArtCoin account-consumer patterns from commit `b3e7ebf`. Coin table/link
dependencies are removed. Reuse does not imply a new MIT license, shared SDK,
Coin authority, or access to any sibling database. Third-party dependencies
retain their own licenses. The new app-local SQLite file contains hashed
browser credentials and encrypted upstream credentials, not provider passwords.

The unmounted `server/http.py` adapter now implements the account page,
central sign-in/registration redirection, one-use PKCE callback, minimal profile,
separate Coin consent and CSRF-protected logout. The signed-in dashboard shows
the account name, optional LAC summary and app shortcuts. It exposes no wallet
signing, payment, Coin write, legacy-ID linking or admin routes. Actual central
deployment, registration and live callback qualification remain pending.

Routes: `/account`, `/api/account/config`, `/api/account/start`,
`/api/account/callback`, `/api/account/me`, `/api/account/coin`,
`/api/account/coin/connect`, `/api/account/logout`. The internal `/healthz`
is independent of account traffic limits. App shortcuts are links, not a claim
of synchronized workspaces, purchases, EchoMind access or credits.

## Before activation

1. Obtain the central owner's actual issuer and client registration, not an
   inferred URL. Agree the exact Platform callback and profile audience.
2. Obtain deployed schema/provider readiness, recovery and revocation evidence.
   The central source and mocked callbacks alone are insufficient.
3. Install a private app-owned state directory, distinct app secret/encryption
   key, explicit schema, and the pinned minimal dependencies in isolation.
4. Deploy and qualify the protected runtime loader and isolated loopback
   service, size/rate/resource limits, exact ingress routes and rollback.
   The loader is implemented; none is deployed today.
5. Qualify the real provider callbacks, cancellation, logout, revocation and
   outages through the exact HTTPS origin. Only then expose Sign in on the hub
   and update its currently static-only privacy text.
6. Separately qualify Coin delegation before showing balances or grants. Never
   send a Platform-audience token to Coin or trust a caller-supplied subject.

The central contract is custom OAuth code/profile, not OIDC. No JWT/JWKS or
provider-hint shortcut is assumed. Central shows the available provider buttons;
Platform uses one honest Sign in / Create account entry. Host-only app cookies
do not authenticate chat or Coin directly. Each app retains its access policy.

## Local regression tests

```bash
python -m pytest server/tests -q
node --test
```

Fixtures test PKCE, issuer/audience rejection, replay, encrypted durable state,
refresh concurrency and crash barriers. They do not contact real providers or
establish a production sign-in. Dependencies are pinned for future isolated
qualification; do not modify another project's environment to install them.

## Personal Coin summary

`server/coin_client.py` implements the resource side of
[Coin summary v1](https://github.com/lachlanchen/LazyingArtCoin/blob/65739f4fd2cf26fafa0811428ad75def0a6418f8/docs/integrations/COIN-SUMMARY-V1.md).
It is wired into the HTTP application only when explicitly enabled by the
private runtime. Central has accepted the `platform-coin-read-v1` contract;
production implementation and activation evidence remain pending. The consumer
does not invent an issuer endpoint or mint a token.

Ordinary login asks only for `profile`. A separate explicit consent request asks
for `profile coin.summary.read`. The accepted form-encoded exchange uses the
[RFC 8693 token-exchange grant](https://www.rfc-editor.org/rfc/rfc8693.html)
to obtain a short-lived Coin-audience credential. Exact discovery metadata and
scope checks prevent treating a profile-only login as Coin permission.

- Fixed HTTPS GET resource, dedicated delegated-token header, no redirects,
  cookies, arbitrary subject selector, legacy bearer, retry or write operation.
- Issuer/subject/audience/actor/scope/expiry checks before and after the read;
  Coin independently introspects the actual opaque token.
- Strict versioned response validation and exact decimal-string formatting.
- Separate wallet balance, gas, pending grant buckets and historical receipts.
  Unlinked, deleted and unavailable states never become a numeric zero.
- Escaped server-rendered summary; no personal identifiers are logged.

The `ReadCredential` type is a defensive envelope, not proof that authorization
exists. Only the central adapter may populate it from the accepted exchange.
Acquisition and response are bound to the app-local session. Authoritative
checks before and after I/O discard responses after logout, account changes or
consent revocation. Real consent/revocation and public resource-header forwarding
still require production qualification. Personal reads are not cached.

## Private runtime

`server/runtime.py` accepts explicit owner-private regular configuration and
secret files, rejects shared/symlinked credentials, and requires an independent
encryption key and cookie secret. Private SQLite schema installation is explicit;
disabled mode needs no credentials or database. No issuer is guessed.

The runtime binds only to loopback, trusts no forwarded visitor IP and limits
headers and bodies to 16 KiB. The per-process request budget allows 16 active
account requests and a 60-request burst, refilling at two per second. Production
edge/service resource limits are qualified separately. Central and Coin requests
have bounded timeouts and no automatic token-exchange retries.

```bash
python -m server.runtime --config /private/runtime.json --state-dir /private/state --install-schema
python -m server.runtime --config /private/runtime.json --state-dir /private/state --check
python -m server.runtime --config /private/runtime.json --state-dir /private/state
```

These paths are placeholders. Actual credential locations and service topology
stay in private handoffs. Caddy keeps ownership of TLS and the explicit public
route allowlist. Never serve the repository root or private runtime configuration.

Pages and APIs use no-store/noindex, host-only Secure/HttpOnly cookies, strict
Host/Origin and CSRF checks, a script-free CSP and escaped display text. Request
access logs are disabled to avoid storing callback codes or personal identifiers.
The form policy allows only this app and the pinned issuer, including the
post-submit redirect. Browsers can enforce `form-action` on that redirect too;
see [MDN's form-action reference](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Content-Security-Policy/form-action).
Account pages use a same-origin referrer policy so browser form POSTs preserve
their Origin header; callback/API responses retain no-referrer. The isolated
browser test clicks the actual sign-in form through real Platform handlers and
reaches a synthetic external issuer without weakening the Origin/CSRF checks.

The complete local flow test exercises real Platform handlers and encrypted
state with a synthetic issuer/resource: sign-in, separate consent, LAC summary,
callback replay, cancellation and logout. Browser layout review covers sign-in,
disabled, permission and populated states at 320, 390 and 1280 pixels. These
prove source/layout behavior, not a production provider login or customer funds.
No sample quantities appear in the public product hub.
