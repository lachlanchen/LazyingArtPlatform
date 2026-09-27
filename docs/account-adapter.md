# Shared account consumer — preparation, not live login

The public hub remains available without signing in. EchoMind owns the shared
account and its Google, Apple, GitHub and email flows. This repository owns only
an app-local consumer; it must not become a second identity provider.

`server/account_client.py` and `server/account_sessions.py` adapt the owner's
LazyingArtCoin account-consumer patterns from commit `b3e7ebf`. Coin table/link
dependencies are removed. Reuse does not imply a new MIT license, shared SDK,
Coin authority, or access to any sibling database. Third-party dependencies
retain their own licenses. The new app-local SQLite file contains hashed
browser credentials and encrypted upstream credentials, not provider passwords.

The unmounted `server/http.py` adapter supports configuration discovery,
central sign-in/registration redirection, one-use PKCE callback, minimal profile
and CSRF-protected logout. It exposes no wallet signing, payment, Coin write,
legacy-ID linking or admin routes. Coin values remain null/not_connected in
the HTTP adapter. A separately scoped, subject-bound Coin resource contract
now exists in source, but central delegation and live qualification are pending.

## Before activation

1. Obtain the central owner's actual issuer and client registration, not an
   inferred URL. Agree the exact Platform callback and profile audience.
2. Obtain deployed schema/provider readiness, recovery and revocation evidence.
   The central source and mocked callbacks alone are insufficient.
3. Install a private app-owned state directory, distinct app secret/encryption
   key, explicit schema, and the pinned minimal dependencies in isolation.
4. Add a protected runtime loader and isolated loopback service with size/rate/
   resource limits, deployment and rollback tests; none is deployed today.
5. Qualify the real provider callbacks, cancellation, logout, revocation and
   outages through the exact HTTPS origin. Only then expose Sign in on the hub.
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

## Personal Coin summary preparation

`server/coin_client.py` implements the resource side of
[Coin summary v1](https://github.com/lachlanchen/LazyingArtCoin/blob/40c78b3108bfebbd256646891d50ce42135f06b1/docs/integrations/COIN-SUMMARY-V1.md).
It is not mounted by the HTTP application. The central owner must still accept
and implement the delegated authorization exchange; this consumer does not
invent that endpoint or mint a token.

- Fixed HTTPS GET resource, dedicated delegated-token header, no redirects,
  cookies, arbitrary subject selector, legacy bearer, retry or write operation.
- Issuer/subject/audience/actor/scope/expiry checks before and after the read;
  Coin independently introspects the actual opaque token.
- Strict versioned response validation and exact decimal-string formatting.
- Separate wallet balance, gas, pending grant buckets and historical receipts.
  Unlinked, deleted and unavailable states never become a numeric zero.
- Escaped server-rendered summary; no personal identifiers are logged.

The `ReadCredential` type is a defensive envelope, not proof that authorization
exists. Only a qualified central adapter may populate it. Before mounting this
view, bind acquisition and response to the app-local session, revalidate after
the read, discard responses after logout/account switching, and qualify actual
consent/revocation and resource-header forwarding. Do not cache personal reads.

123 Python tests pass, including 47 synthetic Coin-consumer cases. They prove
source behavior, not a live provider login, issued delegation or customer
balance. No sample quantities appear in the public product hub.
