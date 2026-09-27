[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*Une petite porte d’entrée vers des outils utiles.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform rassemble L & N, Bunko, des objets faits main et une communauté Coin distincte. Il renvoie aux boutiques d’applications et au paiement Stripe de la boutique existante, sans créer un second système de paiement.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## Fonctionnement

Les liens concernent les applications publiées ; les objets conservent leurs pages de choix d’options. Coin reste facultatif, sa distribution est inactive et les achats ne donnent aucune récompense.

## Contenu

| Path | Description |
| --- | --- |
| `public/` | HTML, CSS et ressources publiques du projet |
| `docs/` | Limites d’intégration et provenance des ressources |
| `tests/` | Vérifications du contenu et des destinations |

## Utilisation locale

Python 3 pour l’aperçu et Node.js 18+ pour les tests. Aucune installation de paquets ni compilation.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## État et périmètre

Les pages produits sur https://platform.lazying.art/ restent statiques et accessibles sans compte. Seul `public/` est servi comme fichiers publics ; le service de comptes isolé garde sa configuration et sa base de sessions chiffrée privées. Ni clés de paiement, ni suivi, ni administration publique. Les achats passent toujours par les processus existants de Stripe et des boutiques d’applications.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## Intégration des comptes

`server/` relie le portail au service de comptes partagé d’EchoMind, avec un nom d’utilisateur ou une adresse e-mail et un mot de passe. Google, Apple et GitHub ne sont pas activés pour ce parcours. Chaque application conserve son espace et ses achats ; les lectures Coin nécessitent un consentement et une validation distincts. Les notes de l’adaptateur précisent l’état vérifié de la mise en ligne.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Citation

Métadonnées de citation du dépôt : [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
