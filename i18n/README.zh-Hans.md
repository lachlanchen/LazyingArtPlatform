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

https://platform.lazying.art/ 的产品页面保持静态，无需账户即可浏览。公开文件仅来自 `public/`；独立账户服务的配置与加密会话数据库保持私有。不包含支付密钥、追踪脚本或公开管理后台。购买仍使用现有 Stripe 与应用商店流程。

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## 账户集成

`server/` 通过用户名或邮箱加密码连接 EchoMind 的共享账户服务。此共享登录流程尚未启用 Google、Apple 或 GitHub。各应用保留独立的工作区和购买记录；Coin 读取需要单独同意与验收。已验证的发布状态见账户适配器文档。

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

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
