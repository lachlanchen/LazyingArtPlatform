[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*Простой вход к полезным инструментам.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform объединяет L & N, Bunko, изделия ручной работы и отдельное сообщество Coin. Страница ведёт в существующие магазины приложений и к оплате Stripe в магазине, не создавая вторую платёжную систему.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## Возможности

Ссылки приложений ведут на выпущенные продукты; физические товары сохраняют страницы выбора параметров. Участие в Coin необязательно, распределение неактивно, покупки не дают наград.

## Содержание

| Path | Description |
| --- | --- |
| `public/` | Публичные HTML, CSS и собственные материалы |
| `docs/` | Границы интеграции и происхождение материалов |
| `tests/` | Проверки содержимого и ссылок |

## Локальный запуск

Для просмотра нужен Python 3, для тестов — Node.js 18+. Установка пакетов и сборка не требуются.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## Состояние и границы

Страницы продуктов на https://platform.lazying.art/ остаются статическими и доступны без аккаунта. Публично раздаются только файлы `public/`; изолированный сервис аккаунтов хранит настройки и зашифрованную базу сессий приватно. Нет платёжных ключей, трекеров или публичной админ-панели. Покупки по-прежнему проходят через существующие процессы Stripe и магазинов приложений.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## Интеграция аккаунтов

`server/` подключает портал к общему сервису аккаунтов EchoMind: вход по имени пользователя или электронной почте и паролю. Google, Apple и GitHub для этого процесса не включены. Каждое приложение сохраняет собственное рабочее пространство и покупки; чтение Coin требует отдельного согласия и проверки. Подтверждённый статус запуска указан в документации адаптера.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Цитирование

Метаданные для цитирования репозитория: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
