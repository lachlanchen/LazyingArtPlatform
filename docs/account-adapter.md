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
legacy-ID linking or admin routes. Coin values remain null/not_connected until
a separately scoped, subject-bound read contract is accepted and implemented.

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
