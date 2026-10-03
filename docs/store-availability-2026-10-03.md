# Public app availability · October 3, 2026

This is a dated public-listing check for the product hub, not a release action.
Apple's US lookup and the public Apple/Google product pages were read without
sign-in. Google listings returned the exact app identity and an in-stock USD
offer in their SoftwareApplication structured data. No purchase was made.
The public Apple developer catalogues for LazyingArt LLC and LightMind Tech
Limited, and both Google developer pages, were also checked for missed releases.

| App | Verified Apple route | Verified Google route | US download price (Apple / Google) |
| --- | --- | --- | --- |
| L & N | [iPhone/iPad/Watch](https://apps.apple.com/us/app/l-n-speech-practice/id6808872450) · 1.0.9 | [Android](https://play.google.com/store/apps/details?id=art.lazying.landn), [separate Pro edition](https://play.google.com/store/apps/details?id=art.lazying.landn.pro) | $0.99 / free; Pro $0.99 |
| Bunko | [iPhone/iPad/Watch](https://apps.apple.com/us/app/bunko-classics-with-ruby/id6815137919) · 1.0.9; [Mac](https://apps.apple.com/us/app/bunko-classics-with-ruby/id6815137919?platform=mac) | [Android](https://play.google.com/store/apps/details?id=art.lazying.bunko) | $0.99 / $0.99 |
| EchoMind | [iPhone/iPad](https://apps.apple.com/us/app/echomind-language-research/id6793615455) · 1.1 | [Android](https://play.google.com/store/apps/details?id=art.lazying.echomind) | $0.99 / free |
| OnlyIdeas | [Mac](https://apps.apple.com/us/app/onlyideas/id6816392935?platform=mac) · 1.0.4 | [Android](https://play.google.com/store/apps/details?id=art.onlyideas.app) | $0.99 / free |
| AiMemo | [iPhone/iPad/Watch companion](https://apps.apple.com/us/app/aimemo-ai-notes-voice/id6757573920) · 1.0 | [Android](https://play.google.com/store/apps/details?id=art.lazying.aimemo) | $0.99 / free |
| SHI | [iPhone/iPad](https://apps.apple.com/us/app/shi-the-shape-of-power/id6816377548) · 1.0.0 | [Android](https://play.google.com/store/apps/details?id=art.lazying.shi) | $0.99 / $0.99 |
| LazyOracle | Not verified public | [Android](https://play.google.com/store/apps/details?id=art.lazying.lazyoracle) | — / $0.99 |
| LightMind Agent | [iPhone/iPad](https://apps.apple.com/us/app/lightmind-agent/id6794785684) · 1.0 | [Android](https://play.google.com/store/apps/details?id=art.lightmind.mobile) | $0.99 / free |

Prices and availability can vary by storefront. These are download prices,
not proof of active subscriptions or other in-app entitlements. LightMind
Agent belongs to LightMind Tech Limited, a separate companion brand, not
LazyingArt LLC. Hardware-specific functions require compatible devices.

## Boundaries retained

- OnlyIdeas' Apple lookup is `mac-software`; its shared app ID does not establish
  iPhone approval. The latest owner record still has iOS in review.
- AiMemo's Mac submission is in review. No Mac download button is added.
- L & N's `platform=mac` page falls back to iOS. It is not Mac release evidence.
- LazyOracle and Auspice are separate products. LazyOracle gets its public
  Android route; no Apple or Auspice launch is inferred.
- Musia is not returned by Apple's public lookup, and its Google listing is
  404. Pronunciation-family internal builds are not public launches.
- EchoMind's invitation/access boundary, separately qualified Platform account
  flow, checkout authority and Coin read permission remain unchanged.
- Some owner release files still say Google review is pending. The public
  listing evidence above supersedes those snapshots for website download links
  only; app owners retain responsibility for production build records.

Both websites use the same 17 verified store destinations, including the
separate Android Pro edition and the two Mac-specific links. This refresh is
discovery infrastructure, not evidence of a sale or of installation testing.

The main website's `tools/check-public-store-links.py` rechecks all catalogue
store destinations without login and rejects wrong-platform Apple fallbacks,
missing product schemas and Google offers not marked available. Run it before
the next refresh rather than assuming this dated snapshot is still current.
