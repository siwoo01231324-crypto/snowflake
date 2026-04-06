# 무빙 인텔리전스 — 경쟁 분석 종합 (Competitive Landscape)

> 작성일: 2026-04-06
> 목적: Snowflake 해커톤 2026 Korea — "무빙 인텔리전스" 플랫폼의 경쟁 구도 파악, 전략 프레임워크 기반 실행 가이드
> 범위: 한국 경쟁사(직접/간접), 글로벌 Pre-Mover 벤치마크, 10개 전략 프레임워크 적용

---

## Executive Summary

한국 시장에서 **"이사 2~4주 전 예측 데이터를 B2B로 판매"하는 서비스는 현재 존재하지 않는다.** 12개 한국 경쟁사/유사 서비스를 조사한 결과, 가장 근접한 경쟁자인 IGAWorks 모바일인덱스 AUDIENCE도 90일 윈도우의 AI 추정 기반 광고 오디언스에 불과하며, 원시 데이터 판매나 CRM 직접 주입은 제공하지 않는다. 글로벌 시장에서는 미국의 Porch Group Media, Deluxe, SpeedeonData 등이 USPS 주소변경 데이터 기반 Pre-Mover 데이터를 이미 상용화하고 있으나, APAC 전역에는 이 카테고리의 전문 서비스가 부재하다.

**핵심 결론:**
1. **시장 공백 확인**: 한국/APAC에 Pre-Mover 데이터 B2B 서비스 전무
2. **가장 가까운 경쟁자**: IGAWorks "3개월 내 이사 예정자" 세그먼트 (광고 오디언스만, 원시 데이터 아님)
3. **핵심 모트**: 통신 주소변경 데이터 독점/준독점 파트너십 확보가 최대 차별화 요인
4. **글로벌 시장 검증**: 미국 Pre-Mover 시장이 이미 성숙 단계 — 사업 모델 자체는 검증됨
5. **#1 리스크**: 통신사가 직접 내재화할 가능성 (공급자 교섭력 높음)

---

## 1. 한국 경쟁사 비교표

### 1.1 종합 비교 매트릭스

| 회사 | 데이터 유형 | 이사 관련 기능 | 이사 2~4주 전 예측 | B2B 판매 모델 | 경쟁 강도 |
|------|-----------|-------------|-------------------|-------------|----------|
| **IGAWorks 모바일인덱스 AUDIENCE** | 모바일 행동 DMP (4,300만 ADID) | "3개월 내 이사 예정자" 세그먼트 | **없음** (90일 윈도우, AI 추정) | 광고 CPM 과금 | **가장 높음** |
| SKT 지오비전 퍼즐 | 통신 기지국 집계 (2,700만 가입자) | 전입·전출 순위, 거주 통계 | **없음** (사후 집계) | API 상품 판매 | 중간 |
| KT K-Ads | 통신+행동 DMP (1,200만 옵트인) | 2,600개 세그먼트, 라이프스테이지 | **없음** | 광고 집행 (LMS 100원/건) | 낮음~중간 |
| KT 잘나가게 | 상권분석 | 없음 | **N/A** (2024.06 종료) | 종료 | 없음 |
| LG U+ | 통신+AI | 없음 | **없음** | 외부 데이터 상품 없음 | 없음 |
| 직방RED | 부동산 시장 90개 지표 | 분양 분석, 타겟팅 광고 | **없음** | SaaS (2025 매출 116억) | 낮음 |
| 부동산R114 REPS | 부동산 시세·거래 | 시장 분석 도구 | **없음** | SaaS (500개 기업) | 낮음 |
| 리치고 MAS | 부동산 AI 분석 | 분양 사업성 | **없음** | SaaS (25개사, 재구독 90.7%) | 낮음 |
| 짐싸 | 이사 견적 (240만 건, 거래액 2,600억) | 이사 확정 수요 연결 | **없음** (수요 확정 후) | B2B 데이터 판매 없음 | **잠재적 높음** |
| 로플랫 DMP | 오프라인 Wi-Fi/BLE/GPS (500만 MAU) | 거주지 추정 | **없음** | 광고 플랫폼 | 낮음 |
| 인크로스 (SKT 계열) | SKT 통신 데이터 기반 | 지역 타겟팅 문자 | **없음** | 문자 광고 발송 | 낮음 |
| NHN DATA | SNS 마케팅 자동화 | 없음 | **없음** | SaaS | 없음 |

### 1.2 가장 가까운 경쟁자: IGAWorks 모바일인덱스 AUDIENCE

| 비교 항목 | IGAWorks AUDIENCE | 무빙 인텔리전스 (목표) |
|----------|-------------------|---------------------|
| 예측 윈도우 | 90일 (3개월 내) | **14~28일 (2~4주 전)** |
| 데이터 원천 | 앱 행동·검색 기반 AI 추정 | 통신 네트워크 물리적 신호 (기지국 접속 패턴 변화) |
| 정확도 | "추정 데이터로 실제와 차이 있을 수 있음" (자체 면책) | 통신 주소변경 = 공식 신고 기반 선행지표 |
| 납품 형태 | 디지털 광고 오디언스 (CPM) | **고객사 CRM 직접 주입 API/대시보드** |
| 활용 채널 | 디지털 광고 (배너·앱 푸시)에 한정 | 방문 영업·전화·DM·디지털 전 채널 |
| 가격 모델 | 세그먼트 조합 무료, 광고 집행 시 CPM | SaaS 구독 + CPA + 엔터프라이즈 라이선스 |
| 주요 고객 | 삼성/LG/롯데/신세계 등 | 가전렌탈/인테리어/이사O2O/통신사 |
| 카탈로그 | audience.mobileindex.com/catalog/ca1085 | — |

**경쟁 위협 평가**: 현재 가장 근접한 경쟁자. 그러나 예측 윈도우(90일 vs 14~28일), 데이터 원천(추정 vs 물리적 신호), 납품 방식(광고 플랫폼 vs CRM API) 모두에서 구조적 차별화가 가능하다.

### 1.3 잠재적 위협 요인

| 위협 주체 | 위협 내용 | 현실화 가능성 | 대응 |
|----------|---------|-------------|------|
| KT 나스미디어 | 2,600개 세그먼트에 이사 세그먼트 추가 가능 | 중 (규제 리스크·수익성 미검증으로 미출시 상태) | 장기 독점 데이터 계약 선점 |
| SKT 지오비전 | 거주인구 데이터 보유, 이사 탐지 알고리즘 추가 가능 | 중 | SKT와 파트너십 우선 추진 |
| 오늘의집 | 이사 인텐트 데이터 누적 중, B2B 확장 가능 | 낮~중 (플랫폼 내 활용 우선) | 이사 전 단계 선행 데이터로 차별화 |
| 짐싸 | 240만 건 이사 데이터 보유, B2B 피벗 가능 | 낮 (데이터 사업 역량 부재) | 파트너십 협력 대상으로 접근 |

---

## 2. 글로벌 Pre-Mover 벤치마크

### 2.1 주요 글로벌 경쟁사 비교

| 기업 | 지역 | 예측 선행 기간 | 데이터 소스 | 매출 규모 | 이사 전 예측 |
|------|------|-------------|-----------|----------|------------|
| Porch Group Media | 미국 | 2~8주 | 유틸리티 14개사, 홈서비스 30,700개 업체 | ~$438M (모회사) | **핵심 상품** |
| Deluxe | 미국 | 매물 등재~이사 완료 | 다중 수십 종 소스 | ~$2.1B (모회사) | **다중 소스** |
| Speedeon Data | 미국 | 매물 등재~계약 단계 | 통신사, 부동산, 공공 레코드 | ~$6.3M | **Yes** |
| Alesco Data | 미국 | 계약 후 30~45일 | 부동산 계약 레코드 | 소규모 | **Yes** |
| Revaluate | 미국 | 6~12개월 | AI+이메일 기반 추론 | 소규모 | **CRM 기반** |
| SmartZip | 미국 | 12개월 | 24개 소스 | 비공개 | **장기 예측** |
| WhenFresh/PriceHubble | 영국 | 매물 등재 6개월 전 | Royal Mail + Zoopla + 200개 소스 | 비공개 | **핵심 상품** |
| Royal Mail NCOA | 영국 | 이사 6주 전~후 | 우편 전환 신청 | 비공개 | **제한적** |
| Cleanlist | 캐나다 | 매물 등재 시점 | 부동산 매물 | 소규모 | **Yes** |
| APAC (한국/일본/호주) | — | — | — | — | **서비스 없음** |

### 2.2 글로벌 시장 핵심 수치

| 지표 | 수치 | 출처 |
|------|------|------|
| 이사자 vs 비이사자 소비 배율 | **13배** | USPS/업계 보고서 |
| 핵심 마케팅 윈도우 | 이사 전후 **17주** | 업계 연구 |
| 생활 이벤트 트리거 캠페인 전환율 | 일반 대비 **200% 높음** | 마케팅 연구 |
| 통신 데이터 수익화 시장 (2025) | **$493.8억** | 시장 보고서 |
| 통신 데이터 수익화 시장 (2035 전망) | **$1,344억** (CAGR 10.53%) | 시장 보고서 |
| 위치 인텔리전스 시장 (2025) | **$250억** | 시장 보고서 |
| 위치 인텔리전스 시장 (2030 전망) | **$470억** | 시장 보고서 |
| Pre-Mover 데이터 레코드 단가 (미국) | **$0.02~$0.25/건** | Alesco Data/Datarade |
| 연간 DB 라이선스 (미국) | 최대 **$250,000** | Alesco Data |

### 2.3 APAC 공백의 구체적 근거

- APAC 전역에 걸쳐 Pre-Mover 데이터 전문 B2B 서비스가 **단 한 곳도 확인되지 않음**
- 한국은 연간 **628만 명**이 이동하며 (인구 대비 높은 이사율), 이사 연관 소비 시장은 **연 50조원 이상**
- 한국 특유의 전세·월세 이동은 부동산 매물 등재(MLS) 없이 발생하므로 미국식 접근법 직접 적용 불가 — 통신 데이터가 유일한 대안

---

## 3. Lean Canvas

| 블록 | 내용 |
|------|------|
| **Customer Segments** | Tier 1: 가전렌탈(코웨이/쿠쿠/LG/SK매직), 인테리어 플랫폼(오늘의집/집닥), 이사 O2O(짐싸/다이사), 통신사(KT/SKT/LGU+) |
| **Problem** | (1) 이사 고객을 사전에 알 방법이 없음 — 현재 무작위 방문 영업/광고에 의존 (2) 이사 후 마케팅 = 이미 경쟁사에 빼앗긴 후 (3) 가전렌탈사 판관비 55~60%이나 타겟팅 정밀도 낮음 |
| **UVP** | **"이사 2~4주 전 예측 — 통신 주소변경 데이터 기반 유일한 선행지표"** |
| **Solution** | API/대시보드로 이사 예정 지역·시기·세그먼트(가구 규모, 아파트 가격대) 제공. 고객사 CRM에 직접 주입 가능 |
| **Channels** | 직접 영업 (엔터프라이즈), Snowflake Marketplace (클라우드 네이티브 고객), KDX 한국데이터거래소 |
| **Revenue Streams** | SaaS 구독(월 100~1,000만), CPA(건당 3~50만), 엔터프라이즈 라이선스(연 1~3억) |
| **Cost Structure** | 통신 데이터 라이선스, 클라우드 인프라(Snowflake), 데이터 사이언스 팀, 세일즈 |
| **Key Metrics** | B2B 활성 고객 수, API 콜/월, 예측 정확도(%), CAC, LTV/CAC, MRR/ARR |
| **Unfair Advantage** | 통신 주소변경 데이터 독점/준독점 파트너십 (원천 데이터 모트). 한국 전세·월세 이동은 매물 데이터 없이 통신 신호로만 포착 가능 |

**무빙 인텔리전스에 대한 시사점**: Lean Canvas의 핵심은 Unfair Advantage 블록이다. ML 모델이나 API는 누구나 만들 수 있으나, 통신 주소변경 데이터 접근권은 복제 불가능한 모트(moat)다. 이 파트너십 확보가 사업 전체의 성패를 결정한다.

---

## 4. JTBD (Jobs-to-be-Done)

### B2B 구매자 3가지 역할별 "Job" 정의

| 역할 | Job Statement | Pain (현재) | Gain (기대) |
|------|-------------|------------|------------|
| **Job Executor** (CRM/그로스 매니저) | "경쟁사보다 먼저 이사 예정 가구를 식별해서 적시에 캠페인을 실행하게 해줘" | 이사 완료 후에야 알게 됨 → 경쟁사에 이미 선점됨. 무작위 방문 영업 효율 낮음 | 이사 2~4주 전 리드 확보 → 선제 접촉으로 전환율 2배+ |
| **Buyer** (CMO / VP Growth) | "CAC를 줄이면서 캠페인 전환율을 높여줘" | 가전렌탈 판관비 55~60%, 타겟팅 정밀도 낮아 CAC 높음 | 이사 예측 타겟팅으로 CAC 50% 절감, 전환율 200% 향상 (글로벌 벤치마크) |
| **Support/IT** (데이터 엔지니어) | "안정적이고 유지보수 안 해도 되는 데이터 피드를 줘" | 데이터 소싱·전처리·정합성 관리에 시간 소모 | 표준 API + Snowflake 네이티브 데이터 셰어 → 별도 파이프라인 불필요 |

**무빙 인텔리전스에 대한 시사점**: 세 역할 모두 다른 언어로 다른 가치를 요구한다. 영업 자료·데모·가격표를 역할별로 분리 설계해야 한다. Job Executor에게는 "전환율", Buyer에게는 "CAC/ROI", IT에게는 "통합 용이성"을 강조한다.

---

## 5. Porter's Five Forces

| Force | 강도 | 분석 |
|-------|------|------|
| **신규 진입자 위협** | 중~상 | ML 모델·API 구축 진입장벽은 낮음. 그러나 **통신 데이터 확보가 핵심 장벽** — 통신 3사와 데이터 라이선스 계약은 시간·신뢰·규제(PIPA) 장벽이 높음. 데이터 없이 모델만으로는 경쟁 불가 |
| **구매자 교섭력** | 중 | 초기 고객은 코웨이·오늘의집 등 대기업 소수 → 교섭력 높음. 그러나 CRM 통합 후 전환비용이 발생하면 교섭력 하락. 다수 SMB 확보가 교섭력 분산의 열쇠 |
| **공급자 교섭력** | **높음** | **#1 리스크**. 통신 데이터 제공자(SKT/KT/LGU+)가 단일 핵심 공급자. 라이선스 비용 인상·계약 해지·직접 사업화 전환 모두 가능. 복수 공급자 확보 및 대체 데이터(전입신고, 전기/가스 전환) 병행이 필수 |
| **대체재 위협** | 중 | 공공 전입신고 데이터(행정안전부), 부동산 거래 데이터, 앱 행동 추론(IGAWorks)으로 대체 가능하나, **정밀도(2~4주 전 개인 단위)와 실시간성에서 열위**. 대체재는 존재하지만 품질 격차가 모트 |
| **산업 내 경쟁** | 낮~중 | 직접 경쟁자 없음 (시장 공백). 그러나 IGAWorks·통신사 데이터 aggregator의 피벗 가능성, 짐싸의 데이터 사업화 가능성이 중기 위협 |

**무빙 인텔리전스에 대한 시사점**: 공급자 교섭력이 가장 큰 리스크다. 통신사와의 장기 독점 계약 확보, 복수 데이터 소스 확보(전기/가스/우편), 자체 데이터 자산 구축(고객사 피드백 루프)이 전략적 최우선 과제다.

---

## 6. TOWS 매트릭스 (전략적 SWOT)

### 내부 요인

| | 내용 |
|---|------|
| **강점(S)** | S1: 통신 주소변경 = 유일한 이사 선행지표, S2: APAC 최초 Pre-Mover 서비스 (시장 공백), S3: Snowflake 네이티브 → 클라우드 데이터 셰어링 즉시 가능, S4: 글로벌 검증 사업 모델 (미국 Porch/Deluxe 선례) |
| **약점(W)** | W1: 세일즈팀·고객 기반 제로 (스타트업), W2: 통신 데이터 커버리지 단일 통신사 의존 가능성, W3: 예측 모델 정확도 미검증, W4: 개인정보보호법(PIPA) 준수 체계 미구축 |

### 외부 요인

| | 내용 |
|---|------|
| **기회(O)** | O1: 가전렌탈 시장 12조+ / 인테리어 37조+ 고속 성장, O2: 통신사 B2B 비통신 매출 50% 목표 → 데이터 라이선스 의지 높음, O3: SMB 디지털 CRM 도입 가속, O4: Snowflake Marketplace 글로벌 유통 채널 |
| **위협(T)** | T1: 통신사 직접 내재화 (KT K-Ads에 이사 세그먼트 추가 등), T2: PIPA 규제 강화로 데이터 활용 범위 축소, T3: 경기 침체 시 기업 마케팅 예산 삭감, T4: IGAWorks 등 기존 DMP의 이사 세그먼트 고도화 |

### 전략 매트릭스

| | 기회(O) | 위협(T) |
|---|---------|---------|
| **강점(S)** | **SO 전략 (선점)**: S1×O1 — 통신 데이터 독점성을 레버리지로 가전렌탈·인테리어 시장 선점. S3×O4 — Snowflake Marketplace로 글로벌 데이터 유통 동시 진행 | **ST 전략 (방어)**: S1×T1 — 통신사와 장기 독점 데이터 라이선스 계약 확보 (내재화 방지). S4×T4 — 미국 선례 기반 정확도·윈도우 차별화로 기존 DMP와 경쟁 회피 |
| **약점(W)** | **WO 전략 (보완)**: W1×O3 — SMB 시장에 셀프서브 API + 프리미엄 모델로 세일즈 부담 최소화. W3×O2 — 통신사 파트너십 내 POC를 통해 정확도 검증 | **WT 전략 (방어적)**: W2×T2 — 국내 모트 우선 구축, 해외 진출 보류. W4×T2 — PIPA 준수 체계를 1순위로 구축하여 규제 리스크 차단 |

**무빙 인텔리전스에 대한 시사점**: SO 전략(선점)이 가장 높은 ROI를 제공한다. 그러나 ST 전략(통신사 장기 독점 계약)을 병행하지 않으면 SO의 기반 자체가 무너질 수 있다. **"선점과 방어를 동시에"**가 핵심 원칙이다.

---

## 7. Strategy Canvas (Blue Ocean)

### 7.1 경쟁 요소별 가치 곡선

| 경쟁 요소 | SKT 지오비전 | IGAWorks AUDIENCE | 공공 전입신고 데이터 | **무빙 인텔리전스** |
|----------|------------|-------------------|------------------|-------------------|
| 예측 선행성 | 낮음 (사후 집계) | 중간 (90일 윈도우) | 낮음 (사후 데이터) | **높음 (2~4주 전)** |
| 데이터 정확도 | 중간 (집계 수준) | 낮음 (AI 추정, 면책 고지) | 높음 (공식 신고) | **높음 (통신 물리 신호)** |
| CRM 통합 깊이 | 낮음 (API만) | 없음 (광고 플랫폼 내) | 없음 (파일 다운로드) | **높음 (CRM 직접 주입 API)** |
| 지역 커버리지 | 높음 (전국) | 높음 (4,300만 ADID) | 높음 (전국) | 중간 (초기 파트너 통신사 커버리지) |
| 가격 투명성 | 낮음 (별도 계약) | 중간 (CPM 공개) | 높음 (무료/저가) | **높음 (공개 가격표)** |
| 온보딩 속도 | 중간 | 빠름 | 느림 (수동 처리) | **빠름 (API 키 즉시 발급)** |
| 컴플라이언스 | 높음 (국가승인) | 중간 | 높음 (공공 데이터) | 중간 (PIPA 준수 체계 구축 필요) |
| 셀프서브 | 중간 | 높음 | 낮음 | **높음** |
| 데이터 신선도 | 중간 (주간) | 중간 (일간~주간) | 낮음 (월간) | **높음 (일간/실시간)** |
| 고객 지원 | 낮음 | 중간 | 없음 | 높음 (전담 CSM) |

### 7.2 ERRC Grid

| 전략 | 요소 | 설명 |
|------|------|------|
| **Eliminate** (제거) | 범용 인구통계 오버레이 | 성별·연령 등 범용 데이터는 차별화 가치 없음. 이사 이벤트에 집중 |
| **Reduce** (축소) | 고가 컨설팅 / 커스텀 분석 | 초기에는 표준화된 데이터 피드에 집중. 컨설팅 서비스는 최소화 |
| **Raise** (강화) | 예측 선행성, 정확도 SLA | 2~4주 전 예측 + 정확도 SLA(예: 70%+) 명시. 경쟁사 대비 유일한 차별화 축 |
| **Create** (창조) | CRM 직접 주입 API | 기존 경쟁자 모두 광고 플랫폼 내 활용에 한정. CRM에 리드 데이터를 직접 투입하는 것은 시장에 없는 신규 가치 |

**무빙 인텔리전스에 대한 시사점**: Blue Ocean 전략의 핵심은 "CRM 직접 주입 API"라는 Create 요소다. 기존 경쟁자들이 광고 플랫폼 내에서만 활용 가능한 데이터를 제공하는 반면, 무빙 인텔리전스는 고객사의 영업·CS·마케팅 시스템에 직접 연동되어 오프라인 채널까지 포괄한다.

---

## 8. AARRR (B2B 적용)

| 단계 | 정의 | 핵심 활동 | 핵심 지표 |
|------|------|----------|----------|
| **Acquisition** | ICP 기업에 도달 | ICP 기반 ABM (코웨이, 오늘의집 등 Tier 1 직접 접촉), 해커톤 네트워크 활용, 콘텐츠 마케팅 (이사 데이터 인사이트 리포트 공개), Snowflake Marketplace 등재 | MQL 수, 데모 요청 건수 |
| **Activation** | 첫 가치 경험 (Aha moment) | **"첫 50건 이사 예측 매칭 완료"** = Aha moment. 무료 POC 2주 제공 → 예측 리드 vs 기존 리드 전환율 A/B 비교 | POC 완료율, 매칭 정확도, Time-to-Value |
| **Retention** | 지속 사용 | 월간 데이터 피드 품질 관리, 전담 CSM 배정, 정확도 리포트 월간 발송 | 월간 활성 고객 수, NPS > 40, API 콜 추이 |
| **Revenue** | 수익화 | SaaS 구독 전환, CPA 연동, 엔터프라이즈 업셀 | MRR, ARR, LTV:CAC >= 3:1, NRR > 100% |
| **Referral** | 추천 | 고객 케이스 스터디 발행 (코웨이 전환율 X% 향상 등) → 인바운드 리드. 산업 컨퍼런스 발표 | 인바운드 리드 비율, 레퍼럴 고객 수 |

**무빙 인텔리전스에 대한 시사점**: B2B에서 Activation이 가장 중요하다. "첫 50건 매칭"이라는 구체적 Aha moment을 설계하고, POC 기간 내 고객사 기존 리드 대비 전환율 우위를 입증하는 것이 파이프라인 전환의 관건이다.

---

## 9. RICE 스코어링 (타겟 세그먼트 우선순위)

| 세그먼트 | Reach (1~10) | Impact (1~5) | Confidence (%) | Effort (1~10) | RICE 점수 |
|---------|-------------|-------------|---------------|-------------|----------|
| **가전렌탈** (코웨이/쿠쿠/LG/SK매직) | 8 | 5 | 80% | 4 | **8.0** |
| **인테리어 플랫폼** (오늘의집/집닥) | 6 | 4 | 70% | 3 | **5.6** |
| **이사 O2O** (짐싸/다이사) | 5 | 3 | 60% | 2 | **4.5** |
| **통신사** (KT/SKT/LGU+) | 3 | 5 | 50% | 8 | **0.9** |

> RICE = (Reach x Impact x Confidence) / Effort

**산출 근거:**

- **가전렌탈 (8.0)**: Reach 높음 (4대 기업 합산 고객 수천만), Impact 최고 (렌탈 LTV 108~300만원, 리드 1건 5~10만원 가치), Confidence 80% (판관비 55~60%, 지불 의사 명확), Effort 중간 (엔터프라이즈 영업 필요하나 의사결정 구조 명확)
- **인테리어 플랫폼 (5.6)**: Reach 중간 (오늘의집 중심), Impact 높음 (공사 건당 50~450만원 수익), Confidence 70% (오늘의집 첫 흑자 달성, CPA 기반 확장 전략), Effort 낮음 (API 통합 용이)
- **이사 O2O (4.5)**: Reach 중간 (짐싸/다이사 = 이사 시장 일부), Impact 중간 (이사 마진 낮음), Confidence 60% (B2B 데이터 구매 의지 미검증), Effort 낮음
- **통신사 (0.9)**: Reach 낮음 (3사만), Impact 최고 (데이터 확보와 고객 확보 동시), Confidence 낮음 (규제·내부 정치 복잡), Effort 최고 (장기 협상, 법무·규제 대응)

**무빙 인텔리전스에 대한 시사점**: 가전렌탈이 압도적 1순위다. 코웨이·쿠쿠의 방문판매(코디) 모델은 이사 예측 데이터와 최고의 궁합을 보이며, LTV가 높아 높은 CPA를 감당할 수 있다. 통신사는 RICE 점수는 낮지만, **데이터 공급자이면서 동시에 고객**이라는 이중 역할 때문에 전략적으로 병행 추진해야 한다.

---

## 10. TAM/SAM/SOM

### 10.1 Top-Down

| 시장 | 정의 | 규모 |
|------|------|------|
| **TAM** | 한국 이사 연관 B2B 마케팅 지출 시장 (가전렌탈 판관비 + 인테리어 마케팅 + 이사O2O 마케팅 + 통신 고객 유치) | **~5조원/년** (코웨이 판관비 2.7조 + 쿠쿠·LG·SK 합산 1조+ + 인테리어 마케팅 1조+) |
| **SAM** | 디지털 CRM/마케팅 인프라 보유 한국 기업 중 이사 데이터 활용 가능 기업의 데이터 마케팅 예산 | **~5,000억원/년** (TAM의 ~10%, 디지털 전환 완료 기업 한정) |
| **SOM** | Year 1~2 현실적 점유율 | **~50억원/년** (SAM의 1%) |

### 10.2 Bottom-Up 계산

| Tier | 기업 수 | ACV (연간 계약 금액) | 연 매출 |
|------|---------|---------------------|---------|
| Tier 1 (대기업: 코웨이, 오늘의집, KT 등) | 5개사 | 1.5억원 | 7.5억원 |
| Tier 2 (중견: 쿠쿠, 집닥, 짐싸, SK매직 등) | 10개사 | 5,000만원 | 5억원 |
| Tier 3 (중소/SMB: 지역 인테리어, 이사업체) | 50개사 | 600만원 | 3억원 |
| **Year 1 합계** | **65개사** | — | **15.5억원** |
| **Year 2 합계 (x3 성장)** | **~200개사** | — | **~50억원** |

**무빙 인텔리전스에 대한 시사점**: Bottom-Up 기준 Year 1 목표 매출 15.5억원은 Tier 1 5개사 확보에 크게 의존한다. 코웨이 1개사만 확보해도 연 1.5억원이므로, **초기 세일즈는 Tier 1 대기업 5곳에 리소스를 집중**하는 것이 합리적이다.

---

## 11. ICP (Ideal Customer Profile)

### 11.1 ICP 정의

| 속성 | 조건 |
|------|------|
| **산업** | B2C 구독/거래 사업 (가전렌탈, 인테리어, 이사, 통신, 보험) |
| **규모** | 500+ 주거 고객 보유 |
| **인프라** | 디지털 마케팅팀 보유, CRM(Salesforce, HubSpot 등) 운영 |
| **Pain Signal** | 이사로 인한 높은 이탈률 (렌탈 해지, 보험 전환, 통신 해지) |
| **의사결정자** | CMO, VP Growth, CRM팀장 |
| **예산** | 연간 마케팅 예산 10억원 이상 |

### 11.2 ICP 매칭 기업 예시

| 기업 | ICP 적합도 | Pain Signal | 추정 ACV |
|------|----------|------------|---------|
| 코웨이 | **최고** | 판관비 2.7조, 코디 방문 영업 의존, 이사 시 해지/전환 집중 | 1~3억원 |
| 오늘의집 | **최고** | 시공 거래액 고속 성장, CPA 기반 확장 전략 | 1~2억원 |
| 쿠쿠홈시스 | 높음 | 297만 렌탈 계정, 코웨이와 점유율 경쟁 | 5,000만~1억원 |
| 짐싸 | 중간 | 이사 수요 데이터 보유하나 방어적 구매 가능 | 3,000만~5,000만원 |
| KT | 높음 (이중 역할) | 이사 시 통신 해지 방어 + 데이터 공급자 | 전략적 파트너십 |

**무빙 인텔리전스에 대한 시사점**: ICP의 핵심 Pain Signal은 "이사로 인한 고객 이탈"이다. 이 Pain이 강할수록 지불 의사가 높다. 코웨이·쿠쿠 등 렌탈사는 이사 시 해지·전환이 직접적 매출 손실이므로 가장 강한 Pain을 가진 세그먼트다.

---

## 12. PLG vs SLG 판단

### 12.1 판단 프레임워크

| 기준 | PLG 적합 | SLG 적합 | **무빙 인텔리전스** |
|------|---------|---------|------------------|
| 계약 규모 | 소액 (월 10만원 이하) | 대액 (연 1,000만원+) | **대액** (ACV 5,000만~3억) |
| 의사결정자 | 현업 담당자 | C-Level / VP | **CMO, VP Growth** |
| 데이터 민감도 | 낮음 | 높음 (보안 검토 필요) | **높음** (개인정보 연관) |
| 통합 복잡도 | 낮음 (SaaS 바로 사용) | 높음 (CRM 연동 필요) | **높음** |
| 구매 프로세스 | 셀프서브 | 협상·계약·법무 | **협상 필요** |

### 12.2 결론: SLG-First + PLG 요소 추가

**SLG-First (Sales-Led Growth)** 전략을 채택하되, PLG 요소를 추가하여 세일즈 사이클을 단축한다.

| 요소 | 내용 |
|------|------|
| **SLG 핵심** | 엔터프라이즈 세일즈 — Tier 1 기업 직접 영업, POC 제공, 계약 협상 |
| **PLG 보완 요소** | (1) 샘플 API + 샌드박스 환경 공개 → 기술팀의 자발적 평가 유도 (2) Snowflake Marketplace 무료 샘플 데이터셋 등재 → 디스커버리 확대 (3) 이사 데이터 인사이트 리포트 무료 공개 → 인바운드 리드 |
| **전환 경로** | PLG 트래픽(API 샘플 요청) → MQL → AE 영업 → POC → 계약 |

**무빙 인텔리전스에 대한 시사점**: 데이터 상품은 개인정보 민감도와 높은 ACV로 인해 순수 PLG는 불가능하다. 그러나 Snowflake Marketplace 샘플 + API 샌드박스라는 PLG 요소를 통해 잠재 고객이 "먼저 경험"하도록 유도하면, 세일즈 사이클을 3~6개월에서 1~2개월로 단축할 수 있다.

---

## 13. 출처

### 한국 경쟁사

1. SKT 지오비전 퍼즐 공식 사이트 — https://puzzle.geovision.co.kr/about
2. SKT 뉴스룸: 지오비전 퍼즐 출시 — https://news.sktelecom.com/179447
3. SK Open API: 지오비전 퍼즐 주거생활 상품 — https://openapi.sk.com/products/detail?svcSeq=66
4. KDX 한국데이터거래소: SKT 지오비전 퍼즐 상품 — https://kdx.kr/data/view/34094
5. KT Enterprise: K-Ads 빅데이터 타겟마케팅 — https://enterprise.kt.com/pd/P_PD_AI_BD_004.do
6. KT Enterprise: GrIP 상권분석 솔루션 — https://enterprise.kt.com/pd/P_PD_BD_SS_001.do
7. KT 잘나가게 종료 (뉴시스, 2024.04) — https://www.newsis.com/view/NISX20240422_0002708773
8. LG유플러스 All in AI B2B 전략 — https://www.etnews.com/20240702000215
9. 직방RED 출시 — https://www.unicornfactory.co.kr/article/2023032913335997503
10. 직방RED B2B Tableau 확대 — https://www.tableau.com/ko-kr/solutions/customer/zigbang-expands-b2b-tableau-embedded-real-estate-solution
11. 부동산R114 REPS — https://www.r114.com/?_c=solution&_m=solutiondefault&_a=reps
12. 리치고 BEP 달성·매출 급증 — https://www.tech42.co.kr/리치고-올인원-ai-부동산-서비스-bep-달성-및-매출-67-5-급증/
13. 짐싸 누적거래액 — https://platum.kr/archives/189698
14. 짐싸 기업정보 — https://thevc.kr/zimssa
15. 모바일인덱스 AUDIENCE: "3개월 내 이사 예정자" — https://audience.mobileindex.com/catalog/ca1085
16. IGAWorks AWS 데이터 기반 마케팅 사례 — https://aws.amazon.com/ko/blogs/korea/igaworks-empowers-digital-marketing-with-data/
17. 로플랫 DMP — https://www.loplat.com/loplat-dmp
18. NHN데이터 소셜비즈 — https://socialbiz.nhndata.com/post/news_260324_2
19. 인크로스 SKT 인수 — https://news.bizwatch.co.kr/article/mobile/2020/08/14/0009

### 글로벌 Pre-Mover

20. Porch Group Media — Precision Mover Audiences — https://porchgroupmedia.com/precision-mover-audiences/
21. Porch Group Q4 2024 Results — https://ir.porchgroup.com/investors/news/news-details/2025/Porch-Group-Reports-Fourth-Quarter-2024-Results/default.aspx
22. Speedeon Data — Mover Data — https://speedeondata.com/mover-data/
23. Speedeon on Datarade — https://datarade.ai/data-products/new-mover-data-on-u-s-consumers-pre-movers-homeowners-at-speedeon-data
24. Deluxe Pre-Mover Database — https://www.deluxe.com/data-driven-marketing/life-event-triggers/pre-mover/
25. Deluxe DLX Revenue — https://stockanalysis.com/stocks/dlx/revenue/
26. Alesco Data Pre-Mover on Datarade — https://datarade.ai/data-products/alesco-pre-mover-database-us-based-with-emails-and-phones-alesco-data
27. Revaluate — Validated AI White Paper — https://revaluate.com/blog/white-paper-validated-ai-predicting-residential-movers
28. SmartZip Data & Analytics — https://www.smartzip.help/en/articles/1971215-data-analytics
29. USPS NCOALink — https://postalpro.usps.com/mailing-and-shipping-services/NCOALink
30. Experian ConsumerView Triggers — https://www.experian.co.uk/assets/marketing-services/documents/consumerview-triggers-fact-sheet.pdf
31. Acxiom InfoBase — https://www.acxiom.com/customer-data/infobase/
32. TransUnion TruAudience — https://www.transunion.com/solution/truaudience
33. WhenFresh/PriceHubble Home Mover Alerts — https://www.pricehubble.com/uk/solution/home-mover-alerts/
34. Royal Mail Mover Marketing Data — https://www.royalmail.com/business/marketing/data/buy-marketing-data
35. Cleanlist Pre-Movers Canada — https://cleanlist.ca/cleanlist-reports-february-2024-pre-movers-in-canada/
36. Telefonica LUCA Brand Retired — https://www.telcotitans.com/telefonicawatch/telefonica-quietly-drops-luca-brand-as-telefonica-tech-takes-over/3504.article
37. BT Active Intelligence — https://business.bt.com/iot/active-intelligence/location-insights/

### 시장 데이터

38. 한국 이사 시장 규모 — docs/background/11_research-b2b-korea-market.md (내부 문서)
39. 글로벌 Pre-Mover 시장·통신 데이터 수익화 — docs/background/10_research-b2b-predictive-marketing.md (내부 문서)
40. 사업화 실행 플랜 — docs/background/12_business-execution-plan.md (내부 문서)
