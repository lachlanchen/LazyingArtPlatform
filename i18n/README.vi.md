[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*Một lối vào nhỏ cho những công cụ hữu ích.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform giới thiệu L & N, Bunko, sản phẩm thủ công và cộng đồng Coin riêng biệt. Trang liên kết tới các cửa hàng ứng dụng và thanh toán Stripe hiện có của cửa hàng, không tạo thêm hệ thống thanh toán.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## Chức năng

Liên kết ứng dụng dẫn tới sản phẩm đã phát hành; hàng vật lý giữ trang chọn tùy chọn. Coin là tùy chọn, phân phối chưa hoạt động và mua hàng không tạo phần thưởng.

## Nội dung

| Path | Description |
| --- | --- |
| `public/` | HTML, CSS và tài nguyên công khai của dự án |
| `docs/` | Phạm vi tích hợp và nguồn tài nguyên |
| `tests/` | Kiểm tra nội dung và đích liên kết |

## Chạy cục bộ

Cần Python 3 để xem trước và Node.js 18+ để chạy kiểm thử. Không cần cài gói hay biên dịch.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## Trạng thái và phạm vi

Các trang sản phẩm tại https://platform.lazying.art/ vẫn là trang tĩnh và không cần tài khoản. Chỉ phục vụ `public/` dưới dạng tệp công khai; dịch vụ tài khoản tách biệt giữ kín cấu hình và cơ sở dữ liệu phiên đã mã hóa. Không có khóa thanh toán, mã theo dõi hay trang quản trị công khai. Việc mua hàng vẫn theo quy trình Stripe và các cửa hàng ứng dụng hiện có.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## Tích hợp tài khoản

`server/` kết nối cổng sản phẩm với dịch vụ tài khoản dùng chung của EchoMind bằng tên người dùng hoặc email và mật khẩu. Google, Apple và GitHub chưa được bật cho luồng này. Mỗi ứng dụng giữ không gian làm việc và giao dịch mua riêng; đọc dữ liệu Coin cần sự đồng ý và kiểm chứng riêng. Ghi chú bộ kết nối nêu trạng thái phát hành đã được xác minh.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

## Trích dẫn

Siêu dữ liệu trích dẫn kho mã: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```
