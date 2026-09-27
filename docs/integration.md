# Integration boundaries

The hub connects existing purchase paths instead of creating another payment
system. Optional shared sign-in is a separate service; its qualified release
status is in [account-adapter.md](account-adapter.md). It does not synchronize
orders, app workspaces or purchase entitlements.

| Journey | Authoritative destination |
| --- | --- |
| L & N native app | Apple App Store; Google Play |
| Bunko native reader | Apple App Store including Mac; no unpublished Play link |
| EchoMind | Its existing chat.lazying.art account flow, public Apple listing and Google Play listing |
| Notebook / panda / pendant | Figurine's product and option pages at buy.lazying.art, followed by its existing Stripe Payment Link |
| Payment changes, fulfillment and refunds | Existing Stripe/operator workflow, not a new public administrator endpoint |
| Coin community | coin.lazying.art; independent of purchases |

No Stripe key, unrestricted app token, wallet signer or customer data is needed
to serve the public product pages. The optional account consumer has its own
scoped credential and private encrypted session state. Do not copy sibling .env files. Existing app prices,
purchase models and checkout terms remain with their owners. In particular,
Google L & N's free download is not a free paid-feature entitlement.

Coin owns wallet proof, awards and receipts. The inspected public campaign
list is empty; the drafted community pool is not a claimable offer. No purchase,
install, review, star, referral or public post earns tokens through this hub.
Coin quantities and grants are not sales or dollar revenue.

Account, order and Coin reads need separate, audience-scoped contracts
and live acceptance. Profile login does not grant Coin consent. Do not forward Coin's legacy session to this platform.
Admin requires proper server authorization; robots.txt is not access control.

Deployment stays on the owner's selected server. Static assets need no new
application process, database, paid builder, analytics service or tunnel to the
workstation. The optional account service is isolated on the server and needs
no workstation runtime. TLS uses the existing ingress; server-specific
configuration and rollback records remain private. Serve only public/ as static
files, never the repository or private account configuration.
