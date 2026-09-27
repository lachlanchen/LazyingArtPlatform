[English](README.md) · [العربية](i18n/README.ar.md) · [Español](i18n/README.es.md) · [Français](i18n/README.fr.md) · [日本語](i18n/README.ja.md) · [한국어](i18n/README.ko.md) · [Tiếng Việt](i18n/README.vi.md) · [中文 (简体)](i18n/README.zh-Hans.md) · [中文（繁體）](i18n/README.zh-Hant.md) · [Deutsch](i18n/README.de.md) · [Русский](i18n/README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*A small front door to useful tools.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform is a lightweight product hub for L & N, Bunko, handmade goods and a separate Coin community. It links to existing app stores and the shop’s Stripe checkout instead of creating a second payment system.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](public/assets/landn.png)

## What it does

App links use released products; physical products keep their option-selection pages. Coin participation is optional, distribution is inactive, and purchases do not earn awards.

## Contents

| Path | Description |
| --- | --- |
| `public/` | Public HTML, CSS and owned assets |
| `docs/` | Integration boundaries and asset provenance |
| `tests/` | Content and destination checks |

## Run locally

Requires Python 3 for preview and Node.js 18+ for tests. No package installation or build step.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## Status and scope

Initial static release; the target address is https://platform.lazying.art/. Deploy only public/. No account database, payment keys, tracking scripts or public admin. The existing Stripe workflow remains authoritative. Hosting and purchase destinations have their own terms; this is not an income guarantee.

[docs/integration.md](docs/integration.md) · [docs/assets.md](docs/assets.md)

## Account integration

EchoMind links to its existing chat and native apps. `server/` contains a locally tested account adapter, not deployed unified login. Provider readiness and private Coin reads await the owning services’ live acceptance.

[docs/account-adapter.md](docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Citation

Repository citation metadata: [CITATION.cff](CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
