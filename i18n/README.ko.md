[English](../README.md) · [العربية](README.ar.md) · [Español](README.es.md) · [Français](README.fr.md) · [日本語](README.ja.md) · [한국어](README.ko.md) · [Tiếng Việt](README.vi.md) · [中文 (简体)](README.zh-Hans.md) · [中文（繁體）](README.zh-Hant.md) · [Deutsch](README.de.md) · [Русский](README.ru.md)

[![LazyingArt banner](https://github.com/lachlanchen/lachlanchen/raw/main/figs/banner.png)](https://github.com/lachlanchen/lachlanchen/blob/main/figs/banner.png)

# LazyingArtPlatform

*유용한 도구로 들어가는 작은 입구.*

[![Website](https://img.shields.io/badge/Website-LazyingArt-1647bd)](https://platform.lazying.art/) [![GitHub Sponsors](https://img.shields.io/badge/GitHub-Sponsors-ea4aaa)](https://github.com/sponsors/lachlanchen)

LazyingArtPlatform은 L & N, Bunko, 수공예 제품과 별도의 Coin 커뮤니티를 소개하는 가벼운 제품 허브입니다. 새 결제 시스템을 만들지 않고 기존 앱 스토어와 상점의 Stripe 결제로 연결합니다.

| Donate | PayPal | Stripe |
| --- | --- | --- |
| [![Donate](https://img.shields.io/badge/Donate-LazyingArt-0EA5E9?style=for-the-badge&logo=kofi&logoColor=white)](https://chat.lazying.art/donate) | [![PayPal](https://img.shields.io/badge/PayPal-RongzhouChen-00457C?style=for-the-badge&logo=paypal&logoColor=white)](https://paypal.me/RongzhouChen) | [![Stripe](https://img.shields.io/badge/Stripe-Donate-635BFF?style=for-the-badge&logo=stripe&logoColor=white)](https://buy.stripe.com/aFadR8gIaflgfQV6T4fw400) |

![L & N](../public/assets/landn.png)

## 주요 기능

앱 링크는 출시된 제품으로, 실물 상품은 옵션 선택 페이지로 연결됩니다. Coin 참여는 선택 사항이며 배포는 비활성 상태입니다. 구매에 따른 보상은 없습니다.

## 구성

| Path | Description |
| --- | --- |
| `public/` | 공개 HTML, CSS 및 프로젝트 소유 자산 |
| `docs/` | 통합 범위와 자산 출처 |
| `tests/` | 콘텐츠 및 목적지 검사 |

## 로컬 실행

미리보기에는 Python 3, 테스트에는 Node.js 18+가 필요합니다. 패키지 설치나 빌드 단계가 없습니다.

```bash
python3 -m http.server 8080 --bind 127.0.0.1 --directory public
```

```bash
node --test
```

## 상태와 범위

첫 정적 버전이며 예정 주소는 https://platform.lazying.art/입니다. public/만 배포합니다. 계정 DB, 결제 키, 추적 스크립트, 공개 관리자 기능이 없습니다. 기존 Stripe 운영 흐름이 기준입니다. 호스팅과 구매 사이트에는 각자의 약관이 있으며 수익을 보장하지 않습니다.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## 인용

저장소 인용 정보: [CITATION.cff](../CITATION.cff).

```bibtex
@software{chen_lazyingartplatform_2026,
  author = {Chen, Lachlan},
  title = {LazyingArtPlatform: A lightweight product hub},
  year = {2026},
  url = {https://github.com/lachlanchen/LazyingArtPlatform}
}
```

