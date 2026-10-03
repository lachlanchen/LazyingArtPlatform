# Public app availability · October 4, 2026

Checked against official public listings on October 4 (Hong Kong time).
This is a website discovery refresh, not a store release, install test or sale.
Apple US lookup identifies the public version; a Mac download additionally
requires the Mac-specific page to identify macOS. Google links were checked
for the exact package and an available US offer. No sign-in or purchase.

| App | Public Apple route / version | Public Google route | US download price (Apple / Google) |
| --- | --- | --- | --- |
| L & N | [iPhone/iPad/Watch](https://apps.apple.com/us/app/l-n-speech-practice/id6808872450) · 1.0.9; [Mac](https://apps.apple.com/us/app/l-n-speech-practice/id6808872450?platform=mac) | [Android](https://play.google.com/store/apps/details?id=art.lazying.landn), [separate Pro edition](https://play.google.com/store/apps/details?id=art.lazying.landn.pro) | $0.99 (phone and Mac) / free; Pro $0.99 |
| Bunko | [iPhone/iPad/Watch](https://apps.apple.com/us/app/bunko-classics-with-ruby/id6815137919) · **1.0.10**; [Mac](https://apps.apple.com/us/app/bunko-classics-with-ruby/id6815137919?platform=mac) · 1.0.8 | [Android](https://play.google.com/store/apps/details?id=art.lazying.bunko) | $0.99 / $0.99 |
| EchoMind | [iPhone/iPad](https://apps.apple.com/us/app/echomind-language-research/id6793615455) · **1.2** | [Android](https://play.google.com/store/apps/details?id=art.lazying.echomind) | $0.99 / free |
| OnlyIdeas | [Mac](https://apps.apple.com/us/app/onlyideas/id6816392935?platform=mac) · 1.0.4 | [Android](https://play.google.com/store/apps/details?id=art.onlyideas.app) | $0.99 / free |
| AiMemo | [iPhone/iPad/Watch companion](https://apps.apple.com/us/app/aimemo-ai-notes-voice/id6757573920) · 1.0 | [Android](https://play.google.com/store/apps/details?id=art.lazying.aimemo) | $0.99 / free |
| SHI | [iPhone/iPad](https://apps.apple.com/us/app/shi-the-shape-of-power/id6816377548) · 1.0.0 | [Android](https://play.google.com/store/apps/details?id=art.lazying.shi) | $0.99 / $0.99 |
| LazyOracle: Atlas & Notebook | Not verified public | [Android](https://play.google.com/store/apps/details?id=art.lazying.lazyoracle) | — / $0.99 |
| LightMind Agent | [iPhone/iPad](https://apps.apple.com/us/app/lightmind-agent/id6794785684) · 1.0 | [Android](https://play.google.com/store/apps/details?id=art.lightmind.mobile) | $0.99 / free |

Bunko's released iPhone/Watch update supports excerpt reading with pinyin,
furigana, sentence-level language alignment and separate text/ruby sizes.
The website describes this as an excerpt sent from a paired iPhone, not a
whole library on the Watch. Bunko Mac 1.0.10 remains in review; its current
public Mac route stays available without assigning it the mobile version.

## L & N Mac: public availability qualified

The release owner recorded Mac build 2 released at 2026-10-03T21:10:05Z
([release record](https://github.com/lachlanchen/L-and-N/commit/6d4778559ba0a0e7f38d4819b977445220e0a9a1)).
An initial website check still saw the iPhone fallback. At
**2026-10-03T21:28:46Z** (October 4, 05:28 HKT), the actual Mac page identified
**macOS 12.0 or later**, Mac availability and a **USD 0.99** offer. The HK page
independently identified macOS 12.0 and **HKD 8**. The download button is now
added to both homepages and the product directory.

The generic Apple lookup still selects the iOS 1.0.9 record; that does not
override the now-qualified Mac-specific page or imply that the Mac version
is also 1.0.9. No release, re-submission or owner release-file edit was made
by this website task.

## Other platform boundaries

- OnlyIdeas is verified on Mac and Android. Its shared Apple ID does not
  establish an iPhone release.
- AiMemo Mac and LazyOracle Apple remain unqualified public routes.
- EchoMind 1.2 is public; preparation of 1.3 is not a launch. Central account
  signup and full EchoMind access remain distinct. Current public issuer
  metadata still requires an invitation for full EchoMind access.
- LightMind Agent belongs to LightMind Tech Limited, a separate companion
  brand. Hardware functions require compatible devices.
- No new subscription, checkout, Coin reward or account entitlement is implied.
  Store prices and regional availability can change.

Both sites now use the same **18 verified store destinations**, including
Android Pro and the qualified L & N, Bunko and OnlyIdeas Mac routes.

Recheck with `python3 tools/check-public-store-links.py` in the main website
repository before changing download routes. It rejects iPhone fallback pages
masquerading as Mac releases. This dated record supersedes the October 3 check
for these public website claims only; release owners retain build authority.
