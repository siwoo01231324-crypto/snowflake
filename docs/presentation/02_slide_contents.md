# 02 — PPT 슬라이드 확정 콘텐츠 (Slide 1·4~7)

> 이슈 #62 산출물. Snowflake Hackathon 2026 (External) 템플릿 기준.
> 작성: 2026-04-10 | 동기화: `03_speech_script.md` §대본 교차참조 테이블

---

## 슬라이드-대본 교차참조 테이블

| 슬라이드 | 대본 구간 | 시작 | 종료 | 핵심 수치 |
|---|---|---|---|---|
| Slide 1 (Title) | §1 오프닝 | 0:00 | 0:45 | 628만명, 200~500만원 |
| Slide 4 (Problem) | §2 Problem Statement | 0:45 | 2:15 | D+14, D+30~45, 90일 |
| Slide 5 (Insight #1) | §3 증거 체인 | 2:15 | 4:00 | r=0.895, r≈0.002, 28~30% |
| Slide 6 (Insight #2) | §4 B2B 세그먼트 | 4:00 | 5:30 | 5.226, 5.17%, 46,874만원 |
| Slide 7 (Insight #3) | §5 기술+데모 + §6 확장 | 5:30 | 9:30 | MAPE<25%·<20%, 0 외부서버 |

---

## Slide 1 — Title

### 헤드라인
**Moving Intelligence**
이사 수요 1개월 선행 예측 플랫폼

### 서브타이틀
통신 신규 계약 시그널로 이사 골든 윈도우를 포착한다

### 메타 정보
- **팀명**: 무빙 인텔리전스 (Moving Intelligence)
- **조직**: Snowflake AI & Data Hackathon 2026 Korea — 테크 트랙
- **날짜**: 2026-04-10

### 발표자 노트
> 오프닝 훅: "한국에서 매년 628만 명이 이사합니다. 이 거대한 소비 결정이 일어나는 순간, 기업들은 아무것도 모릅니다."

---

## Slide 4 — Problem Statement (문제정의 · 가설 · 아키텍처 · 기술스택)

### Theme (슬라이드 상단 제목)
**Signal Gap in Moving Market**
이사 시장의 시그널 공백 — 통신 신규 계약으로 1개월 선행 포착

---

### 섹션 1: 문제 정의 (Problem Definition)

**헤드라인**: 이사는 브랜드-고객 관계가 초기화되는 "리셋 버튼" — 그런데 아무도 이사를 미리 모른다

#### 시장 규모

| 지표 | 수치 | 출처 |
|---|---|---|
| 연간 이사 가구 수 | **~628만 명** | KOSIS 주민등록 인구이동 (2024) |
| 이사 1건당 평균 소비 | **200~500만원** | `docs/background/16_research-pricing-benchmarks.md` |
| 이사 연관 B2B 시장 | **1.5조원+** | `docs/specs/dev_spec.md` C7 비즈니스 모델 |

#### 왜 이사가 이렇게 큰 기회인가?

> 이사는 단순한 주소 변경이 아니다. **기존 브랜드-고객 관계가 일괄 초기화되는 리셋 버튼**이다.

| 지표 | 수치 | 의미 |
|---|---|---|
| 이사자의 브랜드 전환 의향 | **90%** | 이사자 10명 중 9명이 새 브랜드를 시도할 의사 |
| 이사자 vs 비이사자 소비 | **13배** | 이사 후 3개월 소비 = 일반인 3년 소비 |
| 트리거 캠페인 전환율 | 일반 대비 **200% 상승** | 이사 시점 타겟팅 = 기존 마케팅의 2배 효과 |

*(출처: V12/Porch Group Media 2022 New Mover Trends Report, Harris Poll n=1,009; Deluxe New Mover Data)*

#### 데이터 신선도 — 1주 지나면 가치가 급락한다

| 데이터 경과 시간 | 마케팅 응답률 | 효과 감소 |
|---|---|---|
| **1주 이내** | **4.47%** | 기준 |
| 2주 | ~3.1% | ▼ 30% |
| 3주 | ~2.4% | ▼ 46% |
| 4~5주 | 1.82% | ▼ **59%** |

*(출처: Deluxe New Mover/Pre-Mover Data; Specialists Marketing Services)*

→ **1주 늦으면 응답률 30% 하락, 한 달 늦으면 절반 이하.** 그런데 전입신고 데이터는 이사 후 최소 2주~45일 뒤에나 잡힌다.

#### 기존 시그널이 전부 후행하는 이유

| 기존 시그널 | 집계 시점 | 한계 |
|---|---|---|
| 전입신고 | 이사 후 최대 D+14 (주민등록법§16) | 사후 측정, 월 1회 공개 |
| KOSIS 월간 집계 | D+30~45 | 1~2개월 후행 |
| 기존 DMP 세그먼트 (IGAWorks 등) | 90일 윈도우 | AI 추정, 광고 채널 한정, CRM 연동 불가 |
| SKT 지오비전 | 사후 집계 | CRM 직접 주입 불가 |
| 부동산 플랫폼 (직방RED) | 거래 확정 후 | 이사 예정자 타겟팅 기능 없음 |

#### B2B 고객의 진짜 페인 (Pain)

| 고객 | Pain | 현재 상태 |
|---|---|---|
| **코웨이·쿠쿠** (가전 렌탈) | 이사 완료 후에야 인지 → 경쟁사 선점 → CAC 상승 | 판관비 55~60%, 타겟팅 정밀도 낮음 |
| **오늘의집·집닥** (인테리어) | 이사 완료 후 광고 → 이미 경쟁사에 선점된 상태 | 전환율 저조 |
| **짐싸·다이사** (이사 O2O) | 수요 예측 불가 → 성수기 과부하·비수기 유휴 | 관행적 차량·인력 배치 |
| **KT·SKT·LGU+** (통신사) | 이사 시 해지 고객을 사전 파악 불가 | 해지 신청 들어와야 인지 |
| **직방·다방** (부동산) | 이사 수요와 무관한 광고 → 낭비 | 전환율 낮음 |

> **결론**: 이사자 10명 중 9명이 새 브랜드를 시도할 의사가 있고, 이사 후 소비는 일반의 13배인데 — 이 골든 윈도우가 열려 있는 75~90일 동안 어떤 B2B 사업자도 이사를 미리 모른다. **한국에 이사 2~4주 전 예측 데이터를 B2B로 제공하는 서비스는 현재 존재하지 않는다.**

---

### 섹션 2: 가설 (Hypothesis)

**가설**: 이사 예정자는 새집 입주 전 인터넷·TV를 예약한다
→ 통신 신규 계약(CONTRACT)이 이사 실행(OPEN)보다 **구조적으로 선행**

**검증 결과**: 서울 25구 38개월 패널 — CONTRACT → OPEN lag k=+1 **r=0.895** (p<0.001, n=841)
매달 계약의 **28~30%가 당월 미개통(carryover)** = 골든 윈도우

---

### 섹션 3: 아키텍처 구조 (Solution Architecture)

```
[Snowflake Marketplace]
  아정당 V_TELECOM_NEW_INSTALL  ──┐
  SPH 유동인구·카드·자산          ──┼→ [MART_MOVE_ANALYSIS]
  RICHGO 부동산 시세              ──┘     (DATA_TIER: MULTI_SOURCE / TELECOM_ONLY)
                                               │
                                    ┌──────────┴──────────┐
                               Track A (25구)        Track B (3구)
                               LinearRegression       Ridge / LightGBM
                               MAPE 목표 <25%         MAPE 목표 <20%
                                    └──────────┬──────────┘
                                               │
                              PREDICT_MOVE_DEMAND(city_code, ym)  ← 단일 UDF 자동 분기
                                               │
                              ┌────────────────┴────────────────┐
                         Cortex AI                        Streamlit in Snowflake
                    AI_COMPLETE 인사이트               히트맵 · ROI · 자연어 질의
                    Cortex Analyst 자연어
                    AI_EMBED 유사도 검색
```
  | # | 기술 | 어디에 썼나 | 핵심 결과 |
  |---|------|-----------|----------|
  | 1 | Marketplace (4종) | 데이터 수집 | ETL 0, 클릭 한 번으로 4사 데이터 연결 |
  | 2 | Snowpark Python | 피처 엔지니어링 | MART_MOVE_ANALYSIS 850행 통합 마트 |
  | 3 | Snowpark ML + Registry | 모델 학습·배포 | Track A/B 듀얼 모델, 버전 관리 |
  | 4 | SQL UDF | 예측 서비스 | PREDICT_MOVE_DEMAND 단일 함수로 25구 커버 |
  | 5 | Cortex AI (4종) | AI 인사이트 | 자연어 질의 + 자동 전략 생성, 외부 API 0 |
  | 6 | Streamlit in Snowflake | 대시보드 | 히트맵·ROI·AI 3탭, 외부 서버 0 |
---

### 섹션 4: 사용된 기술 스택 (Tech Stack)

| 레이어 | 기술 | 역할 |
|---|---|---|
| **데이터** | Snowflake Marketplace (4종) | ETL 없이 참조 뷰 직결 |
| **피처 엔지니어링** | Snowpark Python | MART_MOVE_ANALYSIS 구축, MOVE_SIGNAL_INDEX 산출 |
| **ML 학습·배포** | Snowpark ML + UDF | Track A/B 학습, PREDICT_MOVE_DEMAND 단일 진입점 |
| **AI** | Cortex AI (AI_COMPLETE, Analyst, AI_EMBED) | 자연어 질의·인사이트 자동 생성·유사 구 검색 |
| **대시보드** | Streamlit in Snowflake | 히트맵·ROI·Cortex 탭, 외부 서버 0 |
| **데이터 마트** | Dynamic Table (예정) + Snowflake Task (예정) | 자동 갱신·월간 스케줄 |

> **핵심 차별화**: Snowflake 단일 계정 내 ML→UDF→대시보드 완결 — 데이터 외부 이동 0

### 발표자 노트
> 아키텍처 도식을 가리키며: "Marketplace 데이터가 ETL 없이 들어오고, 단일 UDF 하나가 25구를 커버합니다. 모든 게 Snowflake 안에서 끝납니다."
> 전환 멘트: "이제 각 인사이트를 하나씩 보겠습니다."

---

## Slide 5 — Insight #1: 데이터 선행성 3중 증거

### 슬라이드 제목
**Insight #1: 통신 계약이 이사보다 1개월 앞선다**

### 부제목
서울 25구 38개월 패널 실증 — 4중 근거 체인

### 본문 불릿 3개

**Bullet 1 — 내부 실증 (Layer 1)** ⭐
> CONTRACT → OPEN lag k=+1: **r=0.895** (p<0.001, n=841), 매월 계약의 **28~30%가 당월 미개통(carryover)** — 구조적 선행 일관 확인
> *(출처: 서울 25구 × 38개월 패널, 아정당 V_TELECOM_NEW_INSTALL)*

**Bullet 2 — KOSIS 교차검증 역설 (Layer 2)**
> CONTRACT vs KOSIS 주민등록 전입신고: r≈**0.002** (p=0.949) — 무상관. 이유: KOSIS는 이사 후 D+30~45 집계. CONTRACT가 KOSIS보다 훨씬 앞선 시점을 측정하기 때문 → 공공 통계로는 구조적으로 포착 불가능한 선행성
> *(출처: TMP_KOSIS_MOVE_REF 550행 교차검증, 2026-04-09)*

**Bullet 3 — 법률·업계 상한 (Layer 3·4, 슬라이드 참고용)**
> 주민등록법§16 전입신고 D+14 이내 + 부동산 계약~잔금 2~3개월(국토부 RTMS) → CONTRACT(D-30)는 전입신고 평균보다 **44일(≈6주) 선행**, "2~4주"는 최보수적 하한

### 발표자 노트 (선제 방어 멘트 — 반드시 포함)
> "상관계수가 같은 통신 시스템 내 처리 지연 아닌가 물으실 수 있습니다. 맞습니다. 그 28~30% carryover가 바로 골든 윈도우입니다 — 고객이 이사를 결정했지만 아직 이사하지 않은 그 구간."

---

## Slide 6 — Insight #2: B2B 비즈니스 기회

### 슬라이드 제목
**Insight #2: 3구 도시 유형 × B2B 세그먼트**

### 부제목
이사 패턴이 극단적으로 다른 세 가지 도시 유형 — 다른 메시지, 다른 타이밍

### 본문 불릿 3개

**Bullet 1 — 중구(11140): 도심 단신 직장인**
> 거주 70명 vs 유동 360명 (유동비 **5.226**, 3구 최고) → 이사 수요는 가족 아닌 **단신직장인·단기체류** 주력 → 타깃 메시지: "오피스 인근, 단기 계약 가능"
> *(신규개통 88.44/월, AVG_INCOME 40,742만원)*

**Bullet 2 — 영등포(11560): 이사 직후 소비 폭발**
> 신규개통 **259.56/월(3구 최다)** + 가전·가구 카드 매출 비중 **5.17%(중구·서초의 20배)** → 이사 시그널과 소비 시그널이 동시 정점 → 타깃 타이밍: "이사 후 30일 윈도우"
> *(AVG_INCOME 39,876만원, WORKING_VISIT 1.07)*

**Bullet 3 — 서초(11650): 학군지 장기 정착**
> 거주인구 **1,221명(3구 1위)** + 평균소득 **46,874만원(1위)** + 매매가 **6,413만원/평(1위)** → 가족 단위 학군지 이동, 장기 정착 → 타깃 서비스: "학군 정보·이사 후 정착 패키지"
> *(GAP_RATIO 0.5607, AVG_ASSET 683,147만원)*

### 발표자 노트
> "서초는 '사는 곳', 영등포는 '이사 직후 소비하는 곳', 중구는 '일하는 곳'. 세 가지 도시 유형이 서로 다른 광고 타깃·메시지·타이밍을 요구합니다."

---

## Slide 7 — Insight #3: Snowflake 기술 차별화

### 슬라이드 제목
**Insight #3: End-to-End Snowflake Native**

### 부제목
Dual-Tier × Cortex AI × Streamlit — 외부 서버 0, 단일 계정 완결

### 본문 불릿 3개

**Bullet 1 — Dual-Tier 프레임워크**
> Track A: 서울 **25구** 경량 예측 (MAPE 목표 <25%, 통신 단일 피처) + Track B: **3구** 정밀 예측 (MAPE 목표 <20%, 4종 교차 피처) → 단일 UDF `PREDICT_MOVE_DEMAND(city_code, ym)` 내부 자동 분기 → Marketplace 구독 확장 시 모델 재설계 없이 전국 전환

**Bullet 2 — Cortex AI 네이티브**
> `AI_COMPLETE` B2B 인사이트 자동 생성 + **Cortex Analyst** 자연어 질의 ("다음 달 서초구 이사 수요?") + `AI_EMBED` 유사 구 벡터 검색 → 분석가 없이도 의사결정 가능

**Bullet 3 — Snowflake Native E2E**
> Marketplace ETL 없이 참조 뷰 직결 → Snowpark ML 학습·UDF 배포 → Streamlit in Snowflake 대시보드 → **외부 서버 0**, 데이터 이동 0

### Snowflake 기능 활용도 (6개 레이어 단일 계정 완결)

> *(이재면 SuperHero 심사 가이드 — "Snowflake 기능 활용도" 항목 대응)*

| # | 레이어 | 활용 기능 | 우리 구현 |
|---|---|---|---|
| 1 | **데이터 통합** | Snowflake Marketplace (4종 구독) | ETL 없이 참조 뷰 직결 — 아정당·SPH·RICHGO·BJD |
| 2 | **피처 엔지니어링** | Snowpark Python | `MART_MOVE_ANALYSIS` 850행, DATA_TIER 자동 분기 |
| 3 | **ML 학습·배포** | Snowpark ML + Model Registry | Track A(22구 XGBoost) + Track B(3구 XGBoost) |
| 4 | **예측 서비스** | Snowflake SQL UDF | `PREDICT_MOVE_DEMAND` + `CALC_ROI` — 단일 진입점 |
| 5 | **AI 인사이트** | Cortex AI **4종** | AI_COMPLETE · AI_CLASSIFY · Cortex Analyst · AI_EMBED |
| 6 | **대시보드** | Streamlit in Snowflake | 히트맵 · ROI · Cortex AI 3탭 네이티브 |

### 확장 방향 (슬라이드 하단 또는 별도 박스)

| 기능 | 설명 |
|---|---|
| **Dynamic Table** | MART_MOVE_ANALYSIS 변경 감지 자동 갱신 (현재 Snowpark 수동) |
| **Snowflake Task** | 월간 모델 재예측 + 마트 갱신 cron 자동화 |
| **Cortex Agents** | Cortex Search(RAG) + Analyst + Custom UDF 멀티툴 오케스트레이션 |
| **전국 확장** | Marketplace 구독 확대 → 25구 → 6대 광역시 → 전국 즉시 전환 |

### 발표자 노트 (데모 시연 가이드)
```
[데모 흐름 — 약 2분 15초]
1. Streamlit 히트맵 탭 → 서울 25구 이사 수요 히트맵 (Track A 결과)
2. ROI 탭 → 영등포 클릭 → 이사 후 30일 ROI 예측
3. Cortex AI 탭 → "다음 달 서초구 이사 수요 예측해줘" 자연어 입력 → 결과 출력
핵심 자막: "1개월 앞서 예측 · carryover 28~30% · r=0.895"
```

---

## 데이터 출처 요약

| 수치 | 출처 문서 | 위치 |
|---|---|---|
| r=0.895, n=841, carryover 28~30% | `00_pitch_story.md` | §4.1 Layer 1 |
| KOSIS r≈0.002, p=0.949 | `00_pitch_story.md` | §4.2 Layer 2 |
| 중구 유동비 5.226 | `01_district_profiles.md` | §1 카드 숫자 |
| 영등포 개통 259.56, 가전 5.17% | `01_district_profiles.md` | §2 카드 숫자 |
| 서초 거주 1,221, 소득 46,874 | `01_district_profiles.md` | §3 카드 숫자 |
| MAPE 목표 <25%/<20% | `00_pitch_story.md` | §3.1/3.2 |


  Layer 2 — KOSIS 교차검증

  | 지표 | 설명 | 실측 결과 | 의미 |
  |------|------|----------|------|
  | 구내 demeaned lag k=+1 r (각 구의 크기 효과를 빼고, 1개월 시차 비교) | CONTRACT(D-30)와 KOSIS(D+30~45)의 실제 시차는 60~75일 | 0.002 (p=0.949) | 월 단위로는 포착 불가 —      
  시차가 너무 크다 |
  | 구내 demeaned lag k=+2 r (2개월 시차로 비교) | 2개월로 넓혀도 60~75일을 정확히 걸치지 못함 | ~0.0 | 동일 — 월 단위 집계의 구조적 한계 |
  | 샘플 수 n | 25구 × 22개월 | 550쌍 | 데이터 양은 충분 |