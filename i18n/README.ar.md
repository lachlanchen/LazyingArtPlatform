[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*مدخل بسيط إلى أدوات مفيدة.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform دليل خفيف لتطبيقَي L & N وBunko والمنتجات اليدوية ومجتمع Coin المستقل. يربط بمتاجر التطبيقات وبالدفع الحالي عبر Stripe في المتجر، بدلاً من إنشاء نظام دفع ثانٍ.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## ما يقدمه

روابط التطبيقات تخص المنتجات المنشورة، والمنتجات المادية تحتفظ بصفحات اختيار مواصفاتها. المشاركة في Coin اختيارية، والتوزيع غير نشط، ولا تمنح المشتريات مكافآت.

## المحتويات

| Path | Description |
| --- | --- |
| `public/` | ملفات HTML وCSS العامة وأصول المشروع |
| `docs/` | حدود التكامل ومصادر الأصول |
| `tests/` | فحوص المحتوى والروابط |

## التشغيل محلياً

يلزم Python 3 للمعاينة وNode.js 18+ للاختبارات. لا حاجة لتثبيت حزم أو خطوة بناء.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## الحالة والنطاق

الإصدار الأول موقع ثابت، وعنوانه المستهدف https://platform.lazying.art/. انشر public/ فقط. لا توجد قاعدة حسابات أو مفاتيح دفع أو نصوص تتبع أو لوحة إدارة عامة. يبقى سير عمل Stripe الحالي المرجع المعتمد. للاستضافة ووجهات الشراء شروطها الخاصة؛ هذا ليس ضماناً للدخل.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## الاستشهاد

بيانات الاستشهاد بالمستودع: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```

