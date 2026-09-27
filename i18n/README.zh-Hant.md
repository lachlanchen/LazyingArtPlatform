[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*通往實用小工具的簡單入口。*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform 是輕量產品主頁，介紹 L & N、Bunko、手工產品及獨立的 Coin 社群。它連接現有應用商店和網店的 Stripe 結帳流程，不另建一套支付系統。

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## 提供甚麼

應用連結指向已發佈產品，實物商品保留規格選擇頁面。Coin 參與完全自願，分發尚未開放；購買不會獲得獎勵。

## 內容

| Path | Description |
| --- | --- |
| `public/` | 公開 HTML、CSS 與專案自有素材 |
| `docs/` | 整合邊界與素材來源 |
| `tests/` | 內容及連結目標檢查 |

## 本機執行

預覽需要 Python 3，測試需要 Node.js 18+。無需安裝依賴或建置。

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## 狀態與範圍

https://platform.lazying.art/ 的產品頁面保持靜態，無需帳戶即可瀏覽。公開檔案僅來自 `public/`；獨立帳戶服務的設定與加密工作階段資料庫保持私有。不包含付款金鑰、追蹤腳本或公開管理後台。購買仍使用現有 Stripe 與應用程式商店流程。

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## 帳戶整合

`server/` 透過使用者名稱或電郵加密碼連接 EchoMind 的共用帳戶服務。此共用登入流程尚未啟用 Google、Apple 或 GitHub。各應用保留獨立的工作區和購買紀錄；Coin 讀取需要個別同意與驗收。已驗證的發佈狀態見帳戶適配器文件。

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## 引用

儲存庫引用資訊： [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
