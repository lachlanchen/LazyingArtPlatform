[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*Ein kleiner Zugang zu nützlichen Werkzeugen.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform bündelt L & N, Bunko, handgefertigte Produkte und eine eigenständige Coin-Community. Die Seite verlinkt bestehende App-Stores und den Stripe-Checkout des Shops, statt ein zweites Zahlungssystem aufzubauen.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## Funktion

App-Links führen zu veröffentlichten Produkten; physische Produkte behalten ihre Auswahlseiten. Coin ist freiwillig, die Verteilung ist inaktiv und Käufe bringen keine Prämien.

## Inhalt

| Path | Description |
| --- | --- |
| `public/` | Öffentliches HTML, CSS und eigene Medien |
| `docs/` | Integrationsgrenzen und Medienherkunft |
| `tests/` | Prüfungen von Inhalten und Linkzielen |

## Lokal starten

Python 3 für die Vorschau und Node.js 18+ für Tests. Keine Paketinstallation und kein Build nötig.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## Stand und Umfang

Erste statische Version; geplante Adresse: https://platform.lazying.art/. Nur public/ bereitstellen. Keine Kontendatenbank, Zahlungsschlüssel, Tracker oder öffentliche Administration. Der bestehende Stripe-Ablauf bleibt maßgeblich. Hosting und Kaufziele haben eigene Bedingungen; Einnahmen werden nicht garantiert.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## Kontenintegration

EchoMind verlinkt seinen bestehenden Chat und seine nativen Apps. `server/` enthält einen lokal getesteten Adapter, keine bereitgestellte einheitliche Anmeldung. Anbieter und private Coin-Abfragen benötigen noch die reale Freigabe ihrer Dienste.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Zitieren

Zitationsmetadaten des Repositorys: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
