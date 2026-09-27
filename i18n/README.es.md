[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*Una pequeña puerta de entrada a herramientas útiles.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform reúne L & N, Bunko, productos artesanales y una comunidad Coin independiente. Enlaza las tiendas de aplicaciones y el pago Stripe de la tienda existente, sin crear otro sistema de cobro.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## Qué ofrece

Los enlaces llevan a aplicaciones publicadas; los productos físicos conservan sus páginas de opciones. Coin es opcional, la distribución está inactiva y las compras no generan premios.

## Contenido

| Path | Description |
| --- | --- |
| `public/` | HTML, CSS y recursos propios públicos |
| `docs/` | Límites de integración y procedencia de recursos |
| `tests/` | Comprobaciones de contenido y destinos |

## Uso local

Requiere Python 3 para la vista previa y Node.js 18+ para las pruebas. Sin instalación de paquetes ni compilación.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## Estado y alcance

Las páginas de productos en https://platform.lazying.art/ siguen siendo estáticas y no requieren cuenta. Sirve únicamente `public/` como archivos públicos; el servicio de cuentas aislado mantiene privados su configuración y su base de sesiones cifrada. Sin claves de pago, rastreadores ni administración pública. Las compras siguen los flujos existentes de Stripe y las tiendas de aplicaciones.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## Integración de cuentas

`server/` conecta el portal con el servicio de cuentas compartidas de EchoMind mediante nombre de usuario o correo y contraseña. Google, Apple y GitHub no están habilitados para este flujo. Cada aplicación conserva su espacio y sus compras; las consultas de Coin requieren consentimiento y validación independientes. Las notas del adaptador indican el estado de publicación verificado.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Cita

Metadatos para citar el repositorio: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
