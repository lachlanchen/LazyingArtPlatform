# LazyingArtPlatform

The customer-facing product hub at platform.lazying.art. Keep the existing
lazying.art GitHub Pages site, Figurine storefront, Stripe configuration and
Coin service independently owned and stable.

The product pages are buildless static HTML/CSS served by existing server
ingress. No payment credentials, wallet keys, analytics tracker or public admin
belongs in this release. The owner's September 27 follow-up authorizes the
isolated account consumer in server/, with private encrypted session state.
Registration, Platform callback/session and separately consented unmapped Coin
reads passed real-browser acceptance on September 27. Preserve that acceptance
gate for future auth changes; mapped balances and account linking are not qualified.
EchoMind owns identity/providers; Coin
owns a separately consented scoped read API. Do not create a competing issuer.
Native purchases go to the platform stores. Handmade orders go through the
existing Figurine product-selection and Stripe checkout path. Community grants
are not purchase rewards, revenue, or an advertised investment.

- Source assets: public/. Tests: tests/. Public evidence: docs/.
- Run `node --test` and `git diff --check` before commits.
- Only serve public/ as static files; install the exact reviewed server package
  privately as its isolated service. Never publish the repository root or .private/.
- Preserve foreign working-tree changes and commit only owned files.
- Machine paths, server topology, credential pointers and deployment receipts
  stay in ignored .private/ (0700, files 0600). Never commit secrets.
- Read the LazyEdge operations skill and private handoff before server changes.
  Existing shared Caddy owns TLS. Never change NAT, stop another service or
  start a second ingress to deploy this site.
- Keep app prices, release claims and external links tied to current evidence.
  Staging/review is not a production release. Do not expose an inactive airdrop
  as a claim button, use Coin legacy credentials, or create new checkout prices.
