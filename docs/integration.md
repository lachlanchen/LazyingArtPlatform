# Integration boundaries

The first release connects existing purchase paths instead of creating another
payment system. It is a customer hub, not a claim that shared account access or
order synchronization already works.

| Journey | Authoritative destination |
| --- | --- |
| L & N native app | Apple App Store; Google Play |
| Bunko native reader | Apple App Store including Mac; no unpublished Play link |
| Notebook / panda / pendant | Figurine's product and option pages at buy.lazying.art, followed by its existing Stripe Payment Link |
| Payment changes, fulfillment and refunds | Existing Stripe/operator workflow, not a new public administrator endpoint |
| Coin community | coin.lazying.art; independent of purchases |

No Stripe key, unrestricted app token, wallet signer or customer data is needed
to serve this release. Do not copy sibling .env files. Existing app prices,
purchase models and checkout terms remain with their owners. In particular,
Google L & N's free download is not a free paid-feature entitlement.

Coin owns wallet proof, awards and receipts. The inspected public campaign
list is empty; the drafted community pool is not a claimable offer. No purchase,
install, review, star, referral or public post earns tokens through this hub.
Coin quantities and grants are not sales or dollar revenue.

Future account, order and Coin reads need separate, audience-scoped contracts
and live acceptance. Do not forward Coin's legacy session to this platform.
Admin requires proper server authorization; robots.txt is not access control.

Deployment stays on the owner's selected server. Static assets need no new
application process, database, paid builder, analytics service or tunnel to the
workstation. TLS uses the existing ingress; server-specific configuration and
rollback records remain private. Deploy only public/, never the repository.
