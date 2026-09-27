[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*役立つ道具への、小さな入口。*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform は L & N、Bunko、手作り商品と独立した Coin コミュニティを紹介する軽量な製品ハブです。新しい決済システムを作らず、既存のアプリストアとショップの Stripe 決済につなぎます。

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## できること

アプリのリンクは公開済み製品へ、実物商品は仕様を選べる商品ページへ案内します。Coin への参加は任意で、配布は停止中です。購入による報酬はありません。

## 構成

| Path | Description |
| --- | --- |
| `public/` | 公開 HTML・CSS・プロジェクト所有の素材 |
| `docs/` | 連携範囲と素材の出典 |
| `tests/` | 内容とリンク先の検証 |

## ローカル実行

プレビューには Python 3、テストには Node.js 18 以降を使います。パッケージのインストールやビルドは不要です。

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## 状態と範囲

最初の静的版です。公開先の予定は https://platform.lazying.art/。デプロイ対象は public/ のみ。アカウント DB、決済キー、追跡スクリプト、公開管理画面はありません。既存の Stripe 運用が正式な決済管理手段です。ホスティングと購入先にはそれぞれの規約があり、収益を保証するものではありません。

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## アカウント連携

EchoMind は既存のチャットとネイティブアプリにつながります。`server/` のアカウント連携コードはローカルテスト済みですが、統合ログインは未公開です。認証プロバイダーと Coin の個人情報読み取りは各サービスの実環境での確認が必要です。

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## 引用

リポジトリの引用情報： [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
