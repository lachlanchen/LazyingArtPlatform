[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*通往实用小工具的简单入口。*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform 是轻量产品主页，介绍 L & N、Bunko、手工产品及独立的 Coin 社区。它连接现有应用商店和网店的 Stripe 结账流程，不另建一套支付系统。

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## 提供什么

应用链接指向已发布产品，实物商品保留规格选择页面。Coin 参与完全自愿，分发尚未开放；购买不会获得奖励。

## 内容

| Path | Description |
| --- | --- |
| `public/` | 公开 HTML、CSS 与项目自有素材 |
| `docs/` | 集成边界与素材来源 |
| `tests/` | 内容及链接目标检查 |

## 本地运行

预览需要 Python 3，测试需要 Node.js 18+。无需安装依赖或构建。

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## 状态与范围

首个静态版本，目标地址为 https://platform.lazying.art/。只部署 public/。不包含账户数据库、支付密钥、追踪脚本或公开管理后台。支付管理仍使用现有 Stripe 流程。托管服务与购买网站各有其条款；本项目不保证收入。

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## 引用

仓库引用信息： [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```

