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

https://platform.lazying.art/의 제품 페이지는 정적이며 계정 없이 둘러볼 수 있습니다. 공개 파일은 `public/`만 제공합니다. 분리된 계정 서비스의 설정과 암호화된 세션 DB는 비공개로 유지합니다. 결제 키, 추적 스크립트, 공개 관리자 기능은 없습니다. 구매는 기존 Stripe 및 앱 스토어 절차를 따릅니다.

[docs/integration.md](../docs/integration.md) · [docs/assets.md](../docs/assets.md)

## 계정 통합

`server/`는 사용자 이름 또는 이메일과 비밀번호로 EchoMind의 공통 계정 서비스에 연결합니다. 이 공통 로그인에는 Google, Apple, GitHub가 활성화되어 있지 않습니다. 각 앱은 자체 작업 공간과 구매 정보를 유지하며 Coin 조회에는 별도 동의와 검증이 필요합니다. 검증된 배포 상태는 계정 어댑터 문서에서 확인할 수 있습니다.

[docs/account-adapter.md](../docs/account-adapter.md)

```bash
python -m pytest server/tests -q
```

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
