# 무빙 인텔리전스 (Moving Intelligence) — 개발 명세서 (Dev Spec)

> Snowflake AI & Data Hackathon 2026 Korea — 테크 트랙  
> 작성일: 2026-04-06 | 마감: 2026-04-12 (6일)  
> 1인 개발 | Snowflake 올인원 아키텍처

---

## 개발 철학: 일론 머스크의 5원칙

본 프로젝트의 모든 설계는 아래 5원칙을 순서대로 적용한다.

| # | 원칙 | 적용 |
|---|------|------|
| 1 | **요구사항을 더 단순하게** (Make the requirements less dumb) | MVP In-Scope 5개 기능만 구현. 테이블 5개, UDF 3개, 탭 3개로 제한 |
| 2 | **불필요한 부분 삭제** (Delete the part) | 별도 REST 서버 삭제, 인증/인가 삭제, NextTrade 호가 10단계 삭제, 관리자 UI 삭제 |
| 3 | **단순화/최적화** (Simplify/Optimize) | Marketplace 뷰 직접 참조 (ETL 복사 없음), 조인 키 2개로 통일, 2컬럼 레이아웃 통일 |
| 4 | **속도 높이기** (Accelerate) | Claude Code가 DDL/UDF/Streamlit 코드 자동 생성. 데이터 검증 쿼리 템플릿화 |
| 5 | **자동화** (Automate — 마지막에) | Snowpark 파이프라인 일괄 실행. Cortex Analyst 자연어 질의는 MVP 완성 후 |

> **원칙**: 1→2→3→4→5 순서대로 적용한다. 자동화(5)는 수동 프로세스가 작동한 이후에만 도입한다.

---

## 목차

- [Part A. 데이터 레이어 & ML 파이프라인](#part-a-데이터-레이어--ml-파이프라인)
  - [A1. 데이터 모델 스키마](#a1-데이터-모델-스키마-mvp)
  - [A2. Snowflake Marketplace 데이터 연동](#a2-snowflake-marketplace-데이터-연동)
  - [A3. 데이터 전처리 파이프라인](#a3-데이터-전처리-파이프라인-snowpark-python)
  - [A4. Feature Engineering](#a4-feature-engineering)
  - [A5. ML 모델 설계](#a5-ml-모델-설계)
  - [A6. MVP vs 고도화 요약](#a6-mvp-vs-고도화-요약-테이블)
  - [A7. 일별 구현 마일스톤 (데이터/ML)](#a7-일별-구현-마일스톤-데이터ml-파트)
- [Part B. 서빙 레이어 (API & Cortex AI)](#part-b-서빙-레이어-api--cortex-ai)
  - [B1. 서빙 전략](#b1-서빙-전략)
  - [B2. B2B API 엔드포인트 설계](#b2-b2b-api-엔드포인트-설계-mvp)
  - [B3. Snowflake UDF 설계](#b3-snowflake-udfudtf-설계)
  - [B4. Cortex AI Functions (MVP)](#b4-cortex-ai-functions-mvp)
  - [B5. Cortex Analyst 시맨틱 모델](#b5-cortex-analyst-시맨틱-모델-설계-mvp)
  - [B6. Cortex Search & Agents](#b6-cortex-search--agents-설계-고도화)
  - [B7. 작업 구분 (🤖/👤)](#b7-작업-구분-claude-code-vs-사용자)
  - [B8. MVP vs 고도화 요약](#b8-mvp-vs-고도화-요약-테이블)
  - [B9. 일별 구현 마일스톤 (서빙)](#b9-일별-구현-마일스톤-서빙-레이어-파트)
- [Part C. 프레젠테이션 레이어 (Streamlit 대시보드)](#part-c-프레젠테이션-레이어-streamlit-대시보드)
  - [C1. 대시보드 구조](#c1-대시보드-구조--mvp-3탭--고도화-1탭)
  - [C2. 이사 수요 예측 히트맵](#c2-이사-수요-예측-히트맵-mvp-핵심)
  - [C3. 세그먼트 필터 & 분석](#c3-세그먼트-필터--분석-mvp)
  - [C4. ROI 계산기](#c4-roi-계산기-mvp)
  - [C5. AI 자연어 질의 (고도화)](#c5-ai-자연어-질의-고도화--phase-2)
  - [C6. GIS 데이터 & 환경 제약](#c6-gis-데이터--지도-렌더링)
  - [C7. 작업 구분 (🤖/👤)](#c7-작업-구분-claude-code-vs-사용자)
  - [C8. 해커톤 발표 데모 시나리오](#c8-해커톤-발표용-데모-시나리오)
  - [C9. MVP vs 고도화 요약](#c9-mvp-vs-고도화-요약-테이블)
  - [C10. 일별 구현 마일스톤 (UI) + 리스크 대응](#c10-일별-구현-마일스톤-ui-파트)
- [Part D. 통합 마일스톤 & 작업 구분](#part-d-통합-마일스톤--작업-구분)
  - [D1. 통합 일별 마일스톤](#d1-통합-일별-마일스톤-04-06--04-12)
  - [D2. 🤖 Claude Code vs 👤 사용자 전체 작업 구분](#d2--claude-code-vs--사용자--전체-작업-구분)
  - [D3. MVP vs 고도화 전체 요약](#d3-mvp-vs-고도화-전체-요약)
- [출처](#출처)

---


# Part A. 데이터 레이어 & ML 파이프라인

## 데이터 설계 철학 (일론머스크 5원칙 적용)

| 원칙 | 데이터 레이어 적용 |
|------|-------------------|
| **1. 요구사항을 더 단순하게** | 핵심 테이블만 사용. 데이터셋별 조인 키 체계를 명확히 정의. 복잡한 크로스 조인 최소화 |
| **2. 불필요한 부분 삭제** | NextTrade 호가 10단계 → MVP에서 체결가·거래량·등락률만 사용. SPH 시간대별 유동인구 → 월별 집계만. RICHGO 인구이동(전입/전출) 없음 → 인구 성별연령 데이터로 대체 |
| **3. 단순화/최적화** | Marketplace 데이터를 뷰(VIEW)로 직접 참조. 별도 ETL 복사 없이 Snowpark에서 바로 전처리 |
| **4. 속도 높이기** | DDL + 뷰 생성 SQL을 Claude Code가 자동 생성. 데이터 검증 쿼리도 템플릿화 |
| **5. 자동화** | Snowpark Python 파이프라인으로 전처리→피처→학습→배포 일괄 실행. 수동 개입 최소화 |

---

## A1. 데이터 모델 스키마 (MVP)

### 조인 전략

데이터셋별로 조인 키 체계가 다르다. 통합을 위해 SPH `M_SCCO_MST`를 지역 마스터 기준으로 삼고, BJD_CODE ↔ DISTRICT_CODE 매핑 뷰를 통해 연결한다.

```
DIM_REGION (SPH M_SCCO_MST 기반, 서울 25개 구 467개 법정동 — 마스터 코드북만. FACT 테이블은 3개 구(중·영등포·서초) 한정)
  ├── FACT_HOUSING_PRICE   (RICHGO: BJD_CODE → CITY_CODE 매핑, 법정동(BJD) 기준)
  ├── FACT_POPULATION      (RICHGO: 인구 성별/연령/영유아비율)
  ├── FACT_LIFESTYLE       (SPH: PROVINCE_CODE+CITY_CODE+DISTRICT_CODE 직접 조인)
  ├── FACT_MOVE_SIGNAL     (아정당: INSTALL_STATE+INSTALL_CITY 텍스트 조인)
  └── FACT_MARKET          (NextTrade: ISU_CD+DWDD — 시간축 조인만)
```

**데이터셋별 조인 키 체계:**

| 데이터셋 | 조인 키 | 공간 단위 | 시간 키 |
|---------|---------|----------|--------|
| SPH | `PROVINCE_CODE`(2) + `CITY_CODE`(5) + `DISTRICT_CODE`(8) | 법정동(BJD) 단위 (467개) | `STANDARD_YEAR_MONTH` (VARCHAR 'YYYYMM') |
| RICHGO | `BJD_CODE` (법정동코드 10자리) | 동 단위 | `YYYYMMDD` (DATE) |
| 아정당 | `INSTALL_STATE` + `INSTALL_CITY` (텍스트) | 시/군/구 단위 | `YEAR_MONTH` (DATE) |
| NextTrade | `ISU_CD` (종목코드) + `DWDD` (일자) | 종목 단위 | `DWDD` (DATE) |

> ⚠️ RICHGO `BJD_CODE`와 SPH `DISTRICT_CODE`는 서로 다른 코드 체계. 매핑 뷰(`V_BJD_DISTRICT_MAP`) 필수.

### A1-1. DIM_REGION — 행정동 마스터 (SPH M_SCCO_MST 기반)

> 출처: `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST` (467건, 서울 25개 구 — 마스터 코드북. FACT 테이블은 3개 구(중·영등포·서초) 한정)

| 컬럼명 | 타입 | 설명 | PK/FK |
|--------|------|------|-------|
| PROVINCE_CODE | VARCHAR(2) | 시도코드 | **PK** |
| CITY_CODE | VARCHAR(5) | 시군구코드 | **PK** |
| DISTRICT_CODE | VARCHAR(8) | 행정동코드 | **PK** |
| PROVINCE_KOR_NAME | VARCHAR(50) | 시도명 (한국어) | |
| CITY_KOR_NAME | VARCHAR(50) | 시군구명 (한국어) | |
| DISTRICT_KOR_NAME | VARCHAR(50) | 행정동명 (한국어) | |
| PROVINCE_ENG_NAME | VARCHAR(50) | 시도명 (영어) | |
| CITY_ENG_NAME | VARCHAR(50) | 시군구명 (영어) | |
| DISTRICT_ENG_NAME | VARCHAR(50) | 행정동명 (영어) | |
| DISTRICT_GEOM | GEOGRAPHY | 행정동 폴리곤 (공간분석용) | |

> ⚠️ LAT/LNG 컬럼 없음. 공간 좌표가 필요하면 `DISTRICT_GEOM`(GEOGRAPHY)에서 ST_X/ST_Y로 추출.

### A1-2. V_BJD_DISTRICT_MAP — RICHGO BJD_CODE ↔ SPH DISTRICT_CODE 매핑 뷰

RICHGO와 SPH 데이터를 동 단위로 연결하기 위한 코드 매핑 뷰.

**매핑 전략 (2단계)**:
1. **동 단위** (BJD_CODE 끝 4자리 ≠ 0000): `LEFT(BJD_CODE, 8) = DISTRICT_CODE` — 행정동 직접 매핑
2. **구 단위 fallback** (BJD_CODE 끝 4자리 = 0000): `LEFT(BJD_CODE, 5) = CITY_CODE` — 시군구 매핑

**변경 이력 (2026-04-07, #20)**:
- 초기 설계: 동 단위 단일 JOIN만 존재 → RICHGO 구 레벨 집계행 3개(중구/영등포구/서초구) 매핑 실패 (89.7%)
- 원인: RICHGO에 BJD_CODE 끝 4자리가 `0000`인 시군구 레벨 집계행 존재. SPH는 동 단위(DISTRICT_CODE)만 보유하여 1:1 대응 불가
- 해결: UNION ALL로 구 단위 fallback 추가 → `MATCH_LEVEL` 컬럼으로 동/구 구분 → **100% 커버리지 달성**
- SD 필터 수정: `'서울특별시'` → RICHGO 실데이터 SD 값이 `'서울'`이었으므로, `V_RICHGO_MARKET_PRICE` 뷰 참조 + `RIGHT(BJD_CODE, 4) != '0000'` 필터로 대체

```sql
-- BJD_CODE(10자리) ↔ DISTRICT_CODE(8자리) 매핑 뷰 (동 + 구 fallback)
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP AS
-- 동 단위 매핑 (BJD_CODE 끝4자리 != 0000)
SELECT
    m.PROVINCE_CODE,
    m.CITY_CODE,
    m.DISTRICT_CODE,
    m.DISTRICT_KOR_NAME,
    m.CITY_KOR_NAME,
    LEFT(r.BJD_CODE, 8) AS BJD_CODE_8,
    r.BJD_CODE,
    r.EMD AS RICHGO_EMD_NAME,
    'DONG' AS MATCH_LEVEL
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
JOIN (
    SELECT DISTINCT BJD_CODE, EMD
    FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE
    WHERE RIGHT(BJD_CODE, 4) != '0000'
) r ON LEFT(r.BJD_CODE, 8) = m.DISTRICT_CODE

UNION ALL

-- 구 단위 fallback 매핑 (BJD_CODE 끝4자리 = 0000)
SELECT DISTINCT
    m.PROVINCE_CODE,
    m.CITY_CODE,
    NULL AS DISTRICT_CODE,
    NULL AS DISTRICT_KOR_NAME,
    m.CITY_KOR_NAME,
    LEFT(r.BJD_CODE, 5) AS BJD_CODE_8,
    r.BJD_CODE,
    r.EMD AS RICHGO_EMD_NAME,
    'GU' AS MATCH_LEVEL
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
JOIN (
    SELECT DISTINCT BJD_CODE, EMD
    FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE
    WHERE RIGHT(BJD_CODE, 4) = '0000'
) r ON LEFT(r.BJD_CODE, 5) = m.CITY_CODE;
```

> **컬럼 추가**: `MATCH_LEVEL` — `'DONG'`(동 단위) 또는 `'GU'`(구 단위 fallback). 소비자가 동 단위만 필요하면 `WHERE MATCH_LEVEL = 'DONG'`으로 필터.
>
> **검증 결과 (2026-04-07)**: 총 29개 BJD_CODE 중 동 26개 + 구 3개 = **100% 매핑**. 미매핑 0건.

### A1-3. FACT_HOUSING_PRICE — RICHGO 아파트 시세

> 출처: `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H`
> 범위: 2012-01 ~ 2024-12 (4,356건, 월·지역 단위 집계)

| 컬럼명 | 타입 | 설명 | 원본 컬럼 |
|--------|------|------|----------|
| BJD_CODE | VARCHAR | 법정동코드 (10자리) | `BJD_CODE` |
| REGION_LEVEL | VARCHAR | 지역 단계 | `REGION_LEVEL` |
| SD | VARCHAR | 시도명 | `SD` |
| SGG | VARCHAR | 시군구명 | `SGG` |
| EMD | VARCHAR | 읍면동명 | `EMD` |
| YYYYMMDD | DATE | 기준년월 | `YYYYMMDD` |
| TOTAL_HOUSEHOLDS | NUMBER(38,0) | 총 세대수 | `TOTAL_HOUSEHOLDS` |
| MEME_PRICE_PER_SUPPLY_PYEONG | FLOAT | 매매 공급평당 가격 | `MEME_PRICE_PER_SUPPLY_PYEONG` |
| JEONSE_PRICE_PER_SUPPLY_PYEONG | FLOAT | 전세 공급평당 가격 | `JEONSE_PRICE_PER_SUPPLY_PYEONG` |

### A1-4. FACT_POPULATION — RICHGO 인구 성별/연령

> 출처 1: `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_GENDER_AGE_M_H`
> 범위: 2025-01 (118건)
>
> 출처 2: `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_AGE_UNDER5_PER_FEMALE_20TO40_M_H`
> 범위: 2025-01 (118건)

**인구 성별/연령 (REGION_MOIS_POPULATION_GENDER_AGE_M_H):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| BJD_CODE | VARCHAR | 법정동코드 |
| SD / SGG / EMD | VARCHAR | 지역명 |
| YYYYMMDD | DATE | 기준년월 |
| TOTAL | NUMBER(38,0) | 총 인구 |
| MALE | NUMBER(38,0) | 남성 인구 |
| FEMALE | NUMBER(38,0) | 여성 인구 |
| AGE_UNDER20 ~ AGE_OVER70 | NUMBER(38,0) | 연령대별 인구 (6구간) |

**영유아비율 (REGION_MOIS_POPULATION_AGE_UNDER5_PER_FEMALE_20TO40_M_H):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| BJD_CODE | VARCHAR(10) | 법정동코드 |
| YYYYMMDD | DATE | 기준년월 |
| AGE_UNDER5 | NUMBER(38,0) | 5세 미만 인구 |
| FEMALE_20TO40 | NUMBER(38,0) | 20~40대 여성 인구 |
| AGE_UNDER5_PER_FEMALE_20TO40 | FLOAT | 영유아/가임여성 비율 |

> ⚠️ 인구이동(전입/전출) 데이터는 없음. RICHGO에는 인구 성별·연령 스냅샷만 존재. 순이동(NET_MIGRATION) 피처 계산 불가.

### A1-5. FACT_LIFESTYLE — SPH 유동인구 + 소비 + 소득

> 출처: `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA`
> 범위: **M_SCCO_MST 마스터 25개 구 467개 법정동** (코드북). FACT 테이블(FLOATING_POPULATION_INFO, CARD_SALES_INFO, ASSET_INCOME_INFO)은 **3개 구(중구·영등포구·서초구) 한정** (해커톤 Marketplace 샘플). (2021-01 ~ 2025-12)

**FLOATING_POPULATION_INFO (유동인구, 2,577,120건):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| PROVINCE_CODE | VARCHAR(2) NOT NULL | 시도코드 |
| CITY_CODE | VARCHAR(5) NOT NULL | 시군구코드 |
| DISTRICT_CODE | VARCHAR(8) NOT NULL | 행정동코드 |
| STANDARD_YEAR_MONTH | VARCHAR(6) NOT NULL | 기준년월 (YYYYMM) |
| WEEKDAY_WEEKEND | VARCHAR(1) NOT NULL | 평일/주말 구분 |
| GENDER | VARCHAR(1) NOT NULL | 성별 |
| AGE_GROUP | VARCHAR(2) NOT NULL | 연령대 |
| TIME_SLOT | VARCHAR(3) NOT NULL | 시간대 |
| RESIDENTIAL_POPULATION | FLOAT | 거주 인구 |
| WORKING_POPULATION | FLOAT | 직장 인구 |
| VISITING_POPULATION | FLOAT | 방문 인구 |

**CARD_SALES_INFO (카드매출, 6,208,957건):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| PROVINCE_CODE | VARCHAR(2) NOT NULL | 시도코드 |
| CITY_CODE | VARCHAR(5) NOT NULL | 시군구코드 |
| DISTRICT_CODE | VARCHAR(8) NOT NULL | 행정동코드 |
| STANDARD_YEAR_MONTH | VARCHAR(6) NOT NULL | 기준년월 (YYYYMM) |
| CARD_TYPE | VARCHAR(1) NOT NULL | 카드 유형 |
| WEEKDAY_WEEKEND | VARCHAR(1) NOT NULL | 평일/주말 구분 |
| GENDER | VARCHAR(1) NOT NULL | 성별 |
| AGE_GROUP | VARCHAR(2) NOT NULL | 연령대 |
| TIME_SLOT | VARCHAR(3) NOT NULL | 시간대 |
| LIFESTYLE | VARCHAR(3) NOT NULL | 생활 유형 |
| FOOD_SALES ~ E_COMMERCE_SALES | NUMBER(38,0) | 업종별 매출액 (19개) |
| FOOD_COUNT ~ E_COMMERCE_COUNT | FLOAT | 업종별 건수 (19개) |

> 업종: FOOD, COFFEE, ENTERTAINMENT, DEPARTMENT_STORE, LARGE_DISCOUNT_STORE, SMALL_RETAIL_STORE, CLOTHING_ACCESSORIES, SPORTS_CULTURE_LEISURE, ACCOMMODATION, TRAVEL, BEAUTY, HOME_LIFE_SERVICE, EDUCATION_ACADEMY, MEDICAL, ELECTRONICS_FURNITURE, CAR, CAR_SERVICE_SUPPLIES, GAS_STATION, E_COMMERCE

**ASSET_INCOME_INFO (자산소득, 269,159건):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| PROVINCE_CODE | VARCHAR(2) NOT NULL | 시도코드 |
| CITY_CODE | VARCHAR(5) NOT NULL | 시군구코드 |
| DISTRICT_CODE | VARCHAR(8) NOT NULL | 행정동코드 |
| STANDARD_YEAR_MONTH | VARCHAR(6) NOT NULL | 기준년월 (YYYYMM) |
| INCOME_TYPE | VARCHAR(1) | 소득 유형 |
| GENDER | VARCHAR(1) NOT NULL | 성별 |
| AGE_GROUP | VARCHAR(2) NOT NULL | 연령대 |
| CUSTOMER_COUNT | NUMBER(38,0) | 고객 수 |
| RATE_MODEL_GROUP_* | FLOAT | 직업군 비율 (7개) |
| PYEONG_*_COUNT | NUMBER(38,0) | 아파트 평형대별 수 (4구간) |
| AVERAGE_PRICE_GAP / AVERAGE_LEASE_GAP | FLOAT | 매매/전세 갭 |
| AVERAGE_INCOME / MEDIAN_INCOME / AVERAGE_HOUSEHOLD_INCOME | NUMBER(38,0) | 소득 |
| RATE_INCOME_*M | FLOAT | 소득구간 비율 (7개) |
| CARD_COUNT / CREDIT_CARD_COUNT / CHECK_CARD_COUNT | NUMBER(38,0) | 카드 보유 현황 |
| OWN_HOUSING_COUNT / MULTIPLE_HOUSING_COUNT | NUMBER(38,0) | 주택 보유 현황 |
| AVERAGE_ASSET_AMOUNT / RATE_HIGHEND | NUMBER/FLOAT | 자산 현황 |

### A1-6. FACT_MOVE_SIGNAL — 아정당 통신 계약 (이사 시그널 간접 추정)

> 출처: `SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS`
> 단위: **시/도 + 시/군/구** (동 단위 아님)

> ⚠️ 아정당에는 이사추정 직접 데이터 없음. 신규설치(V05) + 계약통계(V01)로 이사 시그널을 간접 추정.

**V05_REGIONAL_NEW_INSTALL (신규설치 — 이사 시그널 핵심):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| YEAR_MONTH | DATE | 기준년월 |
| INSTALL_STATE | VARCHAR | 설치 시도 |
| INSTALL_CITY | VARCHAR | 설치 시군구 |
| CONTRACT_COUNT | NUMBER(18,0) | 계약 건수 |
| OPEN_COUNT | NUMBER(38,0) | 개통 건수 |
| PAYEND_COUNT | NUMBER(38,0) | 결제완료 건수 |
| BUNDLE_COUNT | NUMBER(13,0) | 묶음상품 건수 |
| STANDALONE_COUNT | NUMBER(13,0) | 단독상품 건수 |
| AVG_NET_SALES | NUMBER(38,0) | 평균 순매출 |

**V01_MONTHLY_REGIONAL_CONTRACT_STATS (월별 계약 통계):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| YEAR_MONTH | DATE | 기준년월 |
| INSTALL_STATE | VARCHAR | 설치 시도 |
| INSTALL_CITY | VARCHAR | 설치 시군구 |
| MAIN_CATEGORY_NAME | VARCHAR | 상품 카테고리 |
| CONTRACT_COUNT | NUMBER(18,0) | 계약 건수 |
| CONSULT_REQUEST_COUNT | NUMBER(38,0) | 상담 요청 건수 |
| REGISTEND_COUNT | NUMBER(38,0) | 등록완료 건수 |
| OPEN_COUNT | NUMBER(38,0) | 개통 건수 |
| PAYEND_COUNT | NUMBER(38,0) | 결제완료 건수 |
| REGISTEND_CVR | NUMBER(38,2) | 등록전환율 |
| OPEN_CVR | NUMBER(38,2) | 개통전환율 |
| PAYEND_CVR | NUMBER(38,2) | 결제전환율 |
| AVG_NET_SALES | NUMBER(38,0) | 평균 순매출 |
| TOTAL_NET_SALES | NUMBER(38,0) | 총 순매출 |

> 이사 시그널 추정 로직: 신규 통신 설치(V05_REGIONAL_NEW_INSTALL.CONTRACT_COUNT)가 급증하는 지역/시기 = 이사 집중 구역으로 간주. 아정당의 지역 단위는 시/군/구이므로 SPH 동 단위 데이터와는 집계 수준을 맞춰서 조인.

### A1-7. FACT_MARKET — NextTrade 주식 시계열

> 출처: `NEXTRADE_EQUITY_MARKET_DATA.FIN`
> 주요 테이블: `NX_HT_BAT_REFER_A0` (종목참조) + `NX_HT_ONL_MKTPR_A3` (체결가)

**NX_HT_BAT_REFER_A0 (종목 참조정보):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| DWDD | DATE NOT NULL | 데이터일자 |
| ISU_CD | VARCHAR(12) NOT NULL | 종목코드 (ISIN) |
| ISU_SRT_CD | VARCHAR(9) | 단축코드 |
| ISU_ABWD_NM | VARCHAR(80) | 종목약어명(한) |
| ISU_ENAW_NM | VARCHAR(80) | 종목약어명(영) |
| IND_ID | VARCHAR(10) | 업종코드 |
| BASE_PRC | NUMBER(38,0) | 기준가 |
| LSST_CT | NUMBER(38,0) | 상장주수 |
| CAPT_AMT | NUMBER(38,0) | 자본금 |

**NX_HT_ONL_MKTPR_A3 (체결가):**

| 컬럼명 | 타입 | 설명 |
|--------|------|------|
| DWDD | DATE NOT NULL | 데이터일자 |
| MKT_ID | VARCHAR(3) NOT NULL | 시장구분 |
| ISU_CD | VARCHAR(12) NOT NULL | 종목코드 |
| TD_PRC | NUMBER(38,0) | 당일가(체결가) |
| TRD_QTY | NUMBER(38,0) | 거래량 |
| PRDY_CMP_PRC | NUMBER(38,0) | 전일대비가격 |
| OPPR / HGPR / LWPR | NUMBER(38,0) | 시가/고가/저가 |
| ACC_TRD_QTY | NUMBER(38,0) | 누적거래량 |
| ACC_TRVAL | NUMBER(38,0) | 누적거래대금 |

> NextTrade는 행정동 조인이 아닌 **시간축(DWDD → 월별 집계)** 으로 FACT_HOUSING_PRICE와 상관분석에 활용. 건설/리츠 업종 종목 필터링 후 사용.

---

## A2. Snowflake Marketplace 데이터 연동

### A2-1. 4종 데이터셋 연동

| 데이터셋 | 제공사 | 실제 Database | Schema | 주요 데이터 |
|----------|--------|--------------|--------|-------------|
| RICHGO | 데이터노우즈 | `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA` | `HACKATHON_2025Q2` | 아파트 시세(2012-2024), 인구 성별/연령(2025-01) |
| SPH | SPH | `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS` | `GRANDATA` | 유동인구, 소비, 소득 (서울 전체 25구 467동, 2021-2025) |
| 아정당 | 아정네트웍스 | `SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION` | `TELECOM_INSIGHTS` | 지역별 통신 계약/신규설치 (시/군/구 단위) |
| NextTrade | 넥스트레이드 | `NEXTRADE_EQUITY_MARKET_DATA` | `FIN` | 주식 체결가, 거래량 (KRX) |

### A2-2. 👤 사용자 수동 작업 (Marketplace 구독)

1. **Snowflake 계정 생성** — Trial 계정 (30일 무료, $400 크레딧, US West Oregon)
2. **웨어하우스 생성** — `MOVING_INTEL_WH` (X-Small, auto-suspend 60초)
3. **Marketplace에서 4종 데이터셋 구독(Get)**
   - Snowsight → Marketplace → 각 데이터셋 검색 → "Get" 클릭
   - 공유 데이터베이스가 계정에 마운트됨 (데이터 복사 없음)
4. **데이터베이스·스키마 접근 권한 확인**

### A2-3. 🤖 Claude Code 자동화 — 뷰 생성 SQL

```sql
-- 1) 프로젝트 데이터베이스·스키마 생성
CREATE DATABASE IF NOT EXISTS MOVING_INTEL;
CREATE SCHEMA IF NOT EXISTS MOVING_INTEL.ANALYTICS;

-- 2) RICHGO: 아파트 시세 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE AS
SELECT
    REGION_LEVEL, BJD_CODE, SD, SGG, EMD,
    YYYYMMDD, TOTAL_HOUSEHOLDS,
    MEME_PRICE_PER_SUPPLY_PYEONG,
    JEONSE_PRICE_PER_SUPPLY_PYEONG
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H;

-- 3) RICHGO: 인구 성별/연령 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_RICHGO_POPULATION AS
SELECT
    BJD_CODE, SD, SGG, EMD, YYYYMMDD,
    TOTAL, MALE, FEMALE,
    AGE_UNDER20, AGE_20S, AGE_30S, AGE_40S, AGE_50S, AGE_60S, AGE_OVER70
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_GENDER_AGE_M_H;

-- 4) RICHGO: 영유아비율 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_RICHGO_YOUNG_CHILDREN AS
SELECT
    BJD_CODE, SD, SGG, EMD, YYYYMMDD,
    AGE_UNDER5, FEMALE_20TO40, AGE_UNDER5_PER_FEMALE_20TO40
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_AGE_UNDER5_PER_FEMALE_20TO40_M_H;

-- 5) SPH: 유동인구 뷰 (서울 전체 25구 467동)
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP AS
SELECT
    PROVINCE_CODE, CITY_CODE, DISTRICT_CODE, STANDARD_YEAR_MONTH,
    WEEKDAY_WEEKEND, GENDER, AGE_GROUP, TIME_SLOT,
    RESIDENTIAL_POPULATION, WORKING_POPULATION, VISITING_POPULATION
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO;

-- 6) SPH: 카드매출 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES AS
SELECT
    PROVINCE_CODE, CITY_CODE, DISTRICT_CODE, STANDARD_YEAR_MONTH,
    CARD_TYPE, WEEKDAY_WEEKEND, GENDER, AGE_GROUP, TIME_SLOT, LIFESTYLE,
    FOOD_SALES, COFFEE_SALES, BEAUTY_SALES, MEDICAL_SALES,
    EDUCATION_ACADEMY_SALES, HOME_LIFE_SERVICE_SALES,
    TOTAL_SALES, TOTAL_COUNT
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.CARD_SALES_INFO;

-- 7) SPH: 자산소득 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME AS
SELECT
    PROVINCE_CODE, CITY_CODE, DISTRICT_CODE, STANDARD_YEAR_MONTH,
    GENDER, AGE_GROUP, CUSTOMER_COUNT,
    AVERAGE_INCOME, MEDIAN_INCOME, AVERAGE_HOUSEHOLD_INCOME,
    AVERAGE_ASSET_AMOUNT, RATE_HIGHEND,
    OWN_HOUSING_COUNT, MULTIPLE_HOUSING_COUNT,
    AVERAGE_PRICE_GAP, AVERAGE_LEASE_GAP
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.ASSET_INCOME_INFO;

-- 8) 아정당: 신규설치(이사 시그널) 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL AS
SELECT
    YEAR_MONTH, INSTALL_STATE, INSTALL_CITY,
    CONTRACT_COUNT, OPEN_COUNT, PAYEND_COUNT,
    BUNDLE_COUNT, STANDALONE_COUNT, AVG_NET_SALES
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL;

-- 9) 아정당: 월별 지역 계약통계 뷰
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_TELECOM_CONTRACT_STATS AS
SELECT
    YEAR_MONTH, INSTALL_STATE, INSTALL_CITY, MAIN_CATEGORY_NAME,
    CONTRACT_COUNT, CONSULT_REQUEST_COUNT, OPEN_COUNT, PAYEND_COUNT,
    OPEN_CVR, PAYEND_CVR, AVG_NET_SALES, TOTAL_NET_SALES
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V01_MONTHLY_REGIONAL_CONTRACT_STATS;

-- 10) NextTrade: 체결가 뷰 (건설/리츠 업종 필터링)
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_NEXTTRADE_PRICE AS
SELECT
    p.DWDD, p.ISU_CD, r.ISU_ABWD_NM, r.IND_ID,
    p.TD_PRC, p.TRD_QTY, p.PRDY_CMP_PRC,
    p.OPPR, p.HGPR, p.LWPR,
    p.ACC_TRD_QTY, p.ACC_TRVAL
FROM NEXTRADE_EQUITY_MARKET_DATA.FIN.NX_HT_ONL_MKTPR_A3 p
JOIN NEXTRADE_EQUITY_MARKET_DATA.FIN.NX_HT_BAT_REFER_A0 r
    ON p.ISU_CD = r.ISU_CD AND p.DWDD = r.DWDD;

-- 11) 데이터 검증 쿼리
SELECT 'RICHGO_PRICE' AS SRC, COUNT(*) AS ROW_CNT,
    MIN(YYYYMMDD) AS MIN_DATE, MAX(YYYYMMDD) AS MAX_DATE
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE
UNION ALL
SELECT 'RICHGO_POP', COUNT(*), MIN(YYYYMMDD), MAX(YYYYMMDD)
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_POPULATION
UNION ALL
SELECT 'SPH_FLOAT_POP', COUNT(*),
    TO_DATE(MIN(STANDARD_YEAR_MONTH), 'YYYYMM'),
    TO_DATE(MAX(STANDARD_YEAR_MONTH), 'YYYYMM')
FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP
UNION ALL
SELECT 'TELECOM_INSTALL', COUNT(*), MIN(YEAR_MONTH), MAX(YEAR_MONTH)
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
UNION ALL
SELECT 'NEXTTRADE', COUNT(*), MIN(DWDD), MAX(DWDD)
FROM MOVING_INTEL.ANALYTICS.V_NEXTTRADE_PRICE;
```

---

## A3. 데이터 전처리 파이프라인 (Snowpark Python)

### A3-1. 파이프라인 개요

```
Marketplace 뷰 → BJD_CODE↔DISTRICT_CODE 매핑 → 결측값 처리 → 공간 집계 → 이상치 제거 → 통합 마트
```

### A3-2. 결측값 처리 전략

| 데이터 | 결측 유형 | 처리 방법 |
|--------|----------|----------|
| 아파트 시세 | 특정 월 시세 없음 | 직전월 값으로 forward-fill |
| 유동인구 | 행정동별 일부 월 누락 | 전후 월 선형 보간 (interpolate) |
| 아정당 신규설치 | 0건인 경우 | 0은 유효값으로 유지 (결측이 아님) |
| 소득/소비 | 월별 갱신 지연 | 직전 가용 월 값 carry-forward |
| 인구 데이터 | 단일 시점(2025-01)만 존재 | 전 기간 동일값 사용 (스냅샷으로 간주) |

### A3-3. 실제 테이블 기반 Snowpark 통합 마트 생성

```python
# Snowpark Python — 실제 DB/Schema/Table 사용
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F

def build_integrated_mart(session: Session):
    """
    PR #41 동기화 — 아정당 + SPH(3구) + RICHGO 구(CITY_CODE) 단위 통합 마트 생성.
    조인 키: CITY_CODE + STANDARD_YEAR_MONTH
    DATA_TIER: MULTI_SOURCE(중·영등포·서초 3구) / TELECOM_ONLY(나머지 22구)
    """
    MULTI_SOURCE_CITIES = ["11140", "11560", "11650"]  # 중구, 영등포구, 서초구

    # 아정당 spine (서울 25구 × 월별)
    telecom = (
        session.table("MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED")
        .filter(F.col("INSTALL_STATE") == "서울")
        .group_by("CITY_CODE", "CITY_KOR_NAME", "PROVINCE_CODE", "STANDARD_YEAR_MONTH")
        .agg(
            F.sum("OPEN_COUNT").alias("OPEN_COUNT"),
            F.sum("CONTRACT_COUNT").alias("CONTRACT_COUNT"),
            F.sum("PAYEND_COUNT").alias("PAYEND_COUNT"),
        )
    )

    # SPH 유동인구 (3구만 실존)
    sph_pop = (
        session.table("MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP")
        .group_by("CITY_CODE", "STANDARD_YEAR_MONTH")
        .agg(
            F.sum("TOTAL_RESIDENTIAL_POP").alias("TOTAL_RESIDENTIAL_POP"),
            F.sum("TOTAL_WORKING_POP").alias("TOTAL_WORKING_POP"),
            F.sum("TOTAL_VISITING_POP").alias("TOTAL_VISITING_POP"),
        )
    )

    # SPH 카드매출 (3구만 실존)
    sph_card = (
        session.table("MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES")
        .group_by("CITY_CODE", "STANDARD_YEAR_MONTH")
        .agg(
            F.sum("TOTAL_CARD_SALES").alias("TOTAL_CARD_SALES"),
            F.sum("ELECTRONICS_FURNITURE_SALES").alias("ELECTRONICS_FURNITURE_SALES"),
        )
    )

    # SPH 자산소득 (3구만 실존)
    sph_asset = (
        session.table("MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME")
        .group_by("CITY_CODE", "STANDARD_YEAR_MONTH")
        .agg(
            F.avg("AVG_INCOME").alias("AVG_INCOME"),
            F.avg("AVG_ASSET").alias("AVG_ASSET"),
            F.sum("NEW_HOUSING_BALANCE_COUNT").alias("NEW_HOUSING_BALANCE_COUNT"),
        )
    )

    # RICHGO 시세 (3구만 실존, YYYYMMDD → STANDARD_YEAR_MONTH 변환)
    richgo = (
        session.table("MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE")
        .filter(F.col("SD") == "서울")
        .select(
            F.col("CITY_CODE"),
            F.to_char(F.col("YYYYMMDD"), "YYYYMM").alias("STANDARD_YEAR_MONTH"),
            F.avg("MEME_PRICE_PER_SUPPLY_PYEONG").alias("AVG_MEME_PRICE"),
            F.avg("JEONSE_PRICE_PER_SUPPLY_PYEONG").alias("AVG_JEONSE_PRICE"),
            F.sum("TOTAL_HOUSEHOLDS").alias("TOTAL_HOUSEHOLDS"),
        )
        .group_by("CITY_CODE", "STANDARD_YEAR_MONTH")
    )

    # 통합 조인 (아정당 spine 기준, 조인 키: CITY_CODE + STANDARD_YEAR_MONTH)
    mart = (
        telecom
        .join(sph_pop, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_card, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_asset, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(richgo, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .with_column(
            "DATA_TIER",
            F.when(F.col("CITY_CODE").isin(MULTI_SOURCE_CITIES), F.lit("MULTI_SOURCE"))
             .otherwise(F.lit("TELECOM_ONLY"))
        )
    )

    mart.write.save_as_table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS", mode="overwrite")  # PR #41 동기화
    return mart
```

> 🤖 Claude Code: Snowpark 코드 생성, 테스트 쿼리 작성
> 👤 사용자: Snowflake 세션 연결 정보 설정, 실행 확인

### A3-4. 아정당 ↔ SPH 지역 텍스트 매핑

아정당의 `INSTALL_STATE`/`INSTALL_CITY`(텍스트)를 SPH의 `CITY_KOR_NAME`으로 매핑.

```sql
-- 아정당 지역명 → SPH 시군구 코드 매핑
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED AS
SELECT
    t.YEAR_MONTH,
    t.INSTALL_STATE,
    t.INSTALL_CITY,
    t.CONTRACT_COUNT,
    t.OPEN_COUNT,
    t.PAYEND_COUNT,
    t.AVG_NET_SALES,
    m.CITY_CODE,
    m.PROVINCE_CODE
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL t
LEFT JOIN (
    SELECT DISTINCT PROVINCE_CODE, CITY_CODE, CITY_KOR_NAME
    FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
) m ON t.INSTALL_CITY = m.CITY_KOR_NAME
WHERE t.INSTALL_STATE = '서울';
```

> ⚠️ 아정당 지역명과 SPH 코드명 불일치 가능. 매핑 실패 건은 수동 확인 필요.

### A3-5. 시계열 월별 집계/정규화

- **RICHGO 시세**: `YYYYMMDD` (DATE) → 월별 AVG/MAX/MIN 집계 후 `YYYYMM` 포맷으로 변환
- **NextTrade 주식**: `DWDD` (DATE) 일별 체결가 → 월별 AVG/MAX/MIN 집계
- **SPH**: `STANDARD_YEAR_MONTH` (VARCHAR 'YYYYMM') 이미 월별 집계
- **정규화**: Min-Max 스케일링 (0~1 범위) — 이종 데이터 간 비교 가능하도록

### A3-6. 이상치 제거 기준

| 항목 | 이상치 기준 | 처리 |
|------|-----------|------|
| 아파트 시세 | 전월 대비 ±50% 이상 변동 | 해당 행 플래그 후 제외 |
| 유동인구 | IQR 방식 Q1-1.5×IQR ~ Q3+1.5×IQR 밖 | 경계값으로 클리핑 |
| 아정당 신규설치 | 해당 지역 12개월 평균의 5배 초과 | 경계값으로 클리핑 |

> 해커톤 MVP에서는 공격적 이상치 제거보다 **플래그 + 시각적 확인** 우선. 과도한 전처리는 6일 일정에 비해 ROI 낮음.

---

## A4. Feature Engineering

### A4-1. 이사 시그널 지수 (MOVE_SIGNAL_INDEX) — 다중 시그널 융합

이사 수요를 간접 추정하는 핵심 합성 피처. 아정당에 직접 이사추정 데이터가 없으므로, **4종 독립 데이터셋에서 이사와 상관되는 시그널 4개를 융합**하여 단일 프록시의 한계를 극복한다.

#### 이사 프록시 시그널 4종

| # | 시그널 | 데이터 소스 | 논리 (왜 이사와 상관?) | 단위 |
|---|--------|-----------|----------------------|------|
| S1 | **통신 신규설치** | 아정당 V05 `OPEN_COUNT` | 이사하면 인터넷/TV 신규 개통 | 시/군/구 × 월 |
| S2 | **거주인구 변동** | SPH `RESIDENTIAL_POPULATION` (전월 대비 Δ) | 이사 유입 → 거주인구 증가 | 행정동 × 월 |
| S3 | **신규 주택담보대출** | SPH `NEW_HOUSING_BALANCE_COUNT` | 이사 시 주택 매매/전세 대출 발생 | 행정동 × 월 |
| S4 | **이사 관련 소비 급증** | SPH `ELECTRONICS_FURNITURE_SALES` (전월 대비 Δ) | 이사 후 가전/가구 구매 급증 | 행정동 × 월 |

#### 복합 지표 산출식

```
-- DATA_TIER 기반 분기 (MART_MOVE_ANALYSIS.DATA_TIER 컬럼)
MOVE_SIGNAL_INDEX =
  CASE
    WHEN DATA_TIER = 'TELECOM_ONLY' THEN
        norm(OPEN_COUNT)                          -- S1만: 아정당 22구, SPH FACT 없음
    WHEN DATA_TIER = 'MULTI_SOURCE' THEN
        w1 × norm(OPEN_COUNT)                     -- S1: 통신 신규설치 (선행지표)
      + w2 × norm(ΔRESIDENTIAL_POPULATION)        -- S2: 거주인구 전월 대비 변동
      + w3 × norm(NEW_HOUSING_BALANCE_COUNT)      -- S3: 신규 주택담보대출 건수
      + w4 × norm(ΔELECTRONICS_FURNITURE_SALES)   -- S4: 가전/가구 소비 전월 대비 변동
  END

초기 가중치 (MULTI_SOURCE): w1=0.35, w2=0.25, w3=0.25, w4=0.15
```

- `norm()` = Min-Max 정규화 (0~1), 시군구 단위 집계 후 적용
- `Δ` = 전월 대비 변화율 `(당월 - 전월) / 전월`
- 가중치 초기값은 도메인 지식 기반 → 시차 상관분석 결과로 튜닝
- S1 25구 / S2~S4 3구만 실존 → `MART_MOVE_ANALYSIS.DATA_TIER` 컬럼 기반 분기 (전처리는 #21에서 완료)

#### 교차검증: 시그널 간 상관 행렬

4개 시그널이 "이사"라는 공통 원인에 의해 동시 변동한다면, 시그널 간 상관계수가 유의미해야 한다.

```python
# Snowpark Python — 이사 시그널 교차검증
import snowflake.snowpark.functions as F
from scipy.stats import pearsonr
import pandas as pd
import numpy as np

def validate_move_signals(session):
    """4개 이사 프록시 시그널 간 상관 행렬 계산 (MULTI_SOURCE 3구 한정 — SPH FACT 실존 구역)"""
    
    # MULTI_SOURCE 3구만 필터 (SPH FACT는 중구·영등포구·서초구만 실존)
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
    mart_multi = mart.filter(F.col("DATA_TIER") == "MULTI_SOURCE")

    # S1: 아정당 신규설치 (MULTI_SOURCE 구만)
    s1 = (
        mart_multi
        .select("STANDARD_YEAR_MONTH", "CITY_CODE", "OPEN_COUNT")
        .rename("OPEN_COUNT", "S1_NEW_INSTALL")
        .to_pandas()
    )
    
    # S2: SPH 거주인구 변동 (시군구 집계)
    s2 = (
        session.table("SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO")
        .group_by("STANDARD_YEAR_MONTH", "CITY_CODE")
        .agg(F.sum("RESIDENTIAL_POPULATION").alias("S2_RESIDENTIAL_POP"))
        .to_pandas()
    )
    
    # S3: SPH 신규 주택담보대출 (시군구 집계)
    s3 = (
        session.table("SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.ASSET_INCOME_INFO")
        .group_by("STANDARD_YEAR_MONTH", "CITY_CODE")
        .agg(F.sum("NEW_HOUSING_BALANCE_COUNT").alias("S3_NEW_HOUSING"))
        .to_pandas()
    )
    
    # S4: SPH 가전/가구 소비 (시군구 집계)
    s4 = (
        session.table("SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.CARD_SALES_INFO")
        .group_by("STANDARD_YEAR_MONTH", "CITY_CODE")
        .agg(F.sum("ELECTRONICS_FURNITURE_SALES").alias("S4_ELEC_FURNITURE"))
        .to_pandas()
    )
    
    # 조인 (YEAR_MONTH + CITY_CODE)
    merged = s1.merge(s2, left_on=["YEAR_MONTH", "CITY_CODE"], 
                       right_on=["STANDARD_YEAR_MONTH", "CITY_CODE"])
    merged = merged.merge(s3, on=["STANDARD_YEAR_MONTH", "CITY_CODE"])
    merged = merged.merge(s4, on=["STANDARD_YEAR_MONTH", "CITY_CODE"])
    
    # Δ 변동률 계산
    for col in ["S2_RESIDENTIAL_POP", "S4_ELEC_FURNITURE"]:
        merged[f"D_{col}"] = merged.groupby("CITY_CODE")[col].pct_change()
    
    # 상관 행렬
    signal_cols = ["S1_NEW_INSTALL", "D_S2_RESIDENTIAL_POP", "S3_NEW_HOUSING", "D_S4_ELEC_FURNITURE"]
    corr_matrix = merged[signal_cols].corr()
    
    return corr_matrix
```

#### 검증 기준

> ⚠️ 기준: MULTI_SOURCE 3구 한정, 관측 샘플 54~102행, 통계 유의성 한계 고려

| 검증 항목 | 통과 기준 | 실패 시 대응 |
|----------|----------|------------|
| S1↔S2 상관 (통신설치 vs 거주인구) | r > 0.3 | 가중치 w1 하향 |
| S1↔S3 상관 (통신설치 vs 신규대출) | r > 0.3 | 대출 시그널 제외 |
| S1↔S4 상관 (통신설치 vs 가전소비) | r > 0.3 | 소비 시그널 제외 |
| 4개 시그널 평균 상관 | r̄ > 0.35 | 전체 프록시 전략 재검토 |
| 시차 최적 lag | S1이 S2보다 1~3개월 선행 | 선행지표 가정 기각 → 동행지표로 재설정 |

> **해커톤 심사 포인트**: "단일 프록시가 아닌 4종 독립 데이터 교차검증 기반 다중 시그널 융합" — 데이터 신뢰도 향상의 근거.

> ⚠️ RICHGO 인구이동(전입/전출) 없음. 순이동(NET_MIGRATION) 피처 계산 불가. 인구 성별/연령은 2025-01 스냅샷만 존재하여 S1~S4 시계열 검증에 활용 불가.

### A4-2. 시차 상관분석 (Lag Correlation)

아정당 신규설치(S1)가 RICHGO 시세 변동 및 다른 시그널(S2~S4)보다 몇 달 앞서는지 검증.

```
분석 대상 1: S1(OPEN_COUNT) vs RICHGO MEME_PRICE_PER_SUPPLY_PYEONG (시세)
분석 대상 2: S1(OPEN_COUNT) vs S2(ΔRESIDENTIAL_POPULATION) (거주인구)
분석 대상 3: S1(OPEN_COUNT) vs S3(NEW_HOUSING_BALANCE_COUNT) (신규대출)
Lag 범위: 0개월 ~ 6개월
측정: 피어슨 상관계수 (Pearson r)
기대 결과: lag 1~3개월에서 r > 0.3 → S1이 선행지표로 유효
```

```python
# Snowpark Python — 시차 상관분석 (시군구 단위)
import snowflake.snowpark.functions as F
from scipy.stats import pearsonr
import pandas as pd

def lag_correlation_sgg(session, max_lag_months=6):
    """아정당 신규설치 vs RICHGO 시세 시차 상관분석 (시군구 단위)"""
    telecom = (
        session.table("MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED")
        .group_by("YEAR_MONTH", "CITY_CODE")
        .agg(F.sum("CONTRACT_COUNT").alias("TOTAL_INSTALL"))
        .to_pandas()
    )
    richgo = (
        session.table("MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE")
        .join(
            session.table("MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP"),
            "BJD_CODE"
        )
        .group_by("YYYYMMDD", "CITY_CODE")
        .agg(F.avg("MEME_PRICE_PER_SUPPLY_PYEONG").alias("AVG_PRICE"))
        .to_pandas()
    )

    results = []
    for lag in range(max_lag_months + 1):
        shifted = telecom["TOTAL_INSTALL"].shift(lag)
        mask = shifted.notna() & richgo["AVG_PRICE"].notna()
        if mask.sum() > 10:
            r, p = pearsonr(shifted[mask], richgo["AVG_PRICE"][mask])
            results.append({"lag_months": lag, "pearson_r": round(r, 4), "p_value": round(p, 6)})
    return pd.DataFrame(results)
```

### A4-3. 라이프스타일 매력도 지수 (LIFE_ATTRACTIVENESS) — SPH 서울 전체

```
LIFE_ATTRACTIVENESS = 
    0.35 × norm(TOTAL_VISITING_POP)   -- 유동인구 (지역 활성도)
  + 0.30 × norm(TOTAL_CARD_SALES)     -- 소비 규모 (경제 활동)
  + 0.20 × norm(AVG_INCOME)           -- 소득수준 (구매력)
  + 0.15 × norm(AVG_ASSET_AMOUNT)     -- 자산수준 (거주 안정성)
```

- **SPH FACT는 3개 구(중구·영등포구·서초구)에서만 계산 가능** (해커톤 Marketplace 샘플 한정. M_SCCO_MST 마스터 25구와 혼동 주의)
- 이 피처가 높은 행정동 = "살기 좋은 동네" → Phase 2 지역 생활 점수 모델의 입력값
- 이사 수요 예측 모델의 보조 피처로 활용

### A4-4. 영유아 가구 수요 지수 (YOUNG_FAMILY_INDEX)

```
YOUNG_FAMILY_INDEX =
    0.5 × norm(AGE_UNDER5_PER_FEMALE_20TO40)   -- RICHGO 영유아/가임여성 비율
  + 0.3 × norm(AGE_20S + AGE_30S)              -- RICHGO 젊은 인구 비율
  + 0.2 × norm(EDUCATION_ACADEMY_SALES)         -- SPH 학원 소비 (교육 수요 대리지표)
```

- 육아/교육 수요가 높은 지역 이사 수요 예측에 유효
- RICHGO 영유아비율은 2025-01 스냅샷 → 전 기간 고정값으로 사용

### A4-5. 계절성 피처

```
IS_PEAK_SEASON = CASE WHEN MONTH(BASE_DATE) IN (2, 3, 8, 9) THEN 1 ELSE 0 END
MONTH_SIN = SIN(2 * PI() * MONTH(BASE_DATE) / 12)   -- 연속적 계절성 인코딩
MONTH_COS = COS(2 * PI() * MONTH(BASE_DATE) / 12)
```

- 이사 성수기: 3월 (신학기), 9월 (하반기 전환)
- 준성수기: 2월, 8월 (성수기 직전 사전 이동)

---

## A5. ML 모델 설계

### A5-1. MVP: 이사 수요 예측 모델

**목표**: 시군구 단위, 향후 1개월 이사 수요(신규설치 건수) 예측. DATA_TIER 기반 두 Track으로 분리.

**Track A — 25구 경량 모델**

| 항목 | 내용 |
|------|------|
| 대상 | `DATA_TIER` 무관 25구 전체 |
| 샘플 수 | 850 (25구 × 34개월) |
| 피처 | `OPEN_COUNT`, `CONTRACT_COUNT`, `PAYEND_COUNT`, `IS_PEAK_SEASON`, `MONTH_SIN`, `MONTH_COS` |
| 알고리즘 | LinearRegression 또는 지수이동평균 |
| 학습 기간 | 202307 ~ 202604 (34개월) |
| 평가 | walk-forward 최종 6개월 |
| MAPE 목표 | **< 25%** |

**Track B — MULTI_SOURCE 3구 풀 모델**

| 항목 | 내용 |
|------|------|
| 대상 | `DATA_TIER = 'MULTI_SOURCE'` (중·영등포·서초) |
| 샘플 수 | 102 (3구 × 34개월), RICHGO∩아정당 교집합 시 54 |
| 피처 | Track A 피처 + `MOVE_SIGNAL_INDEX` + `TOTAL_RESIDENTIAL_POP` + `AVG_INCOME` + `TOTAL_CARD_SALES` + `NEW_HOUSING_BALANCE_COUNT` + `AVG_MEME_PRICE` + `AVG_JEONSE_PRICE` |
| 알고리즘 | **Ridge(α=1.0)** 또는 **LightGBM(min_data_in_leaf=5)** — ⚠️ XGB 금지 (소샘플 과적합) |
| 학습 기간 | 202307 ~ 202412 (RICHGO 상한) |
| 평가 | walk-forward 최종 6개월 |
| MAPE 목표 | **< 20%** |

> ⚠️ Track B 샘플 54~102행은 통계적으로 매우 소규모 — Ridge/LightGBM의 정규화 필수. XGBRegressor 금지.

### A5-2. 고도화 모델 (Phase 2+)

| 모델 | 설명 | 추가 데이터 |
|------|------|------------|
| 지역 생활 점수 | 유동인구×소비×소득×시세 가중합 스코어링 | SPH 서울 전체 (이미 가용) |
| 주식-부동산 상관 | 건설/리츠 주가 ↔ 부동산 시세 시차 분석 | NextTrade 섹터별 |
| 영유아 가구 이사 방향 | 영유아비율 높은 지역 → 학군지 이동 예측 | RICHGO + SPH 교육 소비 |
| 전세/매매 갭 기반 이사 예측 | 갭 확대 지역 이사 수요 증가 패턴 | SPH AVERAGE_PRICE_GAP |

### A5-3. 모델 학습/배포 파이프라인

```
[Snowpark ML 학습]
    MART_MOVE_ANALYSIS → Feature 추출 → walk_forward_split → 모델 학습()
        ↓
[모델 저장]
    Snowpark Model Registry에 모델 버전 저장
        ↓
[UDF 등록]
    CREATE FUNCTION predict_move_demand(...)
    RETURNS FLOAT
    AS $$ ... $$
        ↓
[서빙]
    Streamlit 대시보드에서 UDF 호출 → 예측 결과 시각화
    B2B API에서 UDF 호출 → JSON 응답
```

```python
# Snowpark ML — Track A/B 분리 학습 & UDF 등록 (PR #41 동기화)
from snowflake.ml.modeling.linear_model import LinearRegression, Ridge
from snowflake.ml.registry import Registry
from snowflake.snowpark import Window
import snowflake.snowpark.functions as F

def walk_forward_split(mart, train_months: int = 28, test_months: int = 6):
    """시계열 walk-forward split — random_split 대신 사용 (시계열에 random split 부적합)"""
    all_months = sorted([r["STANDARD_YEAR_MONTH"] for r in mart.select("STANDARD_YEAR_MONTH").distinct().collect()])
    train_cutoff = all_months[train_months - 1]
    train = mart.filter(F.col("STANDARD_YEAR_MONTH") <= train_cutoff)
    test = mart.filter(F.col("STANDARD_YEAR_MONTH") > train_cutoff)
    return train, test

def train_track_a(session):
    """Track A — 25구 경량 모델 (LinearRegression, DATA_TIER 무관)"""
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")

    # 타겟 파생: 다음 달 OPEN_COUNT
    mart = mart.with_column(
        "TARGET_NEXT_OPEN_COUNT",
        F.lead("OPEN_COUNT", 1).over(
            Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
        )
    ).filter(F.col("TARGET_NEXT_OPEN_COUNT").is_not_null())

    feature_cols = ["OPEN_COUNT", "CONTRACT_COUNT", "PAYEND_COUNT", "IS_PEAK_SEASON", "MONTH_SIN", "MONTH_COS"]
    target = "TARGET_NEXT_OPEN_COUNT"

    train, test = walk_forward_split(mart, train_months=28, test_months=6)

    model = LinearRegression(input_cols=feature_cols, label_cols=[target], output_cols=["PREDICTED_OPEN_COUNT"])
    model.fit(train)

    registry = Registry(session=session)
    mv = registry.log_model(model, model_name="move_demand_track_a", version_name="v1",
                             sample_input_data=train.select(feature_cols))
    mv.create_service(service_name="predict_track_a_service", service_compute_pool="MOVING_INTEL_POOL")
    return model.predict(test)

def train_track_b(session):
    """Track B — MULTI_SOURCE 3구 풀 모델 (Ridge α=1.0, XGB 금지)"""
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
    mart = mart.filter(F.col("DATA_TIER") == "MULTI_SOURCE")

    # 타겟 파생: 다음 달 OPEN_COUNT
    mart = mart.with_column(
        "TARGET_NEXT_OPEN_COUNT",
        F.lead("OPEN_COUNT", 1).over(
            Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
        )
    ).filter(F.col("TARGET_NEXT_OPEN_COUNT").is_not_null())

    feature_cols = [
        "OPEN_COUNT", "CONTRACT_COUNT", "PAYEND_COUNT", "IS_PEAK_SEASON", "MONTH_SIN", "MONTH_COS",
        "MOVE_SIGNAL_INDEX", "TOTAL_RESIDENTIAL_POP", "AVG_INCOME",
        "TOTAL_CARD_SALES", "NEW_HOUSING_BALANCE_COUNT", "AVG_MEME_PRICE", "AVG_JEONSE_PRICE",
    ]
    target = "TARGET_NEXT_OPEN_COUNT"

    train, test = walk_forward_split(mart, train_months=28, test_months=6)

    model = Ridge(alpha=1.0, input_cols=feature_cols, label_cols=[target], output_cols=["PREDICTED_OPEN_COUNT"])
    model.fit(train)

    registry = Registry(session=session)
    mv = registry.log_model(model, model_name="move_demand_track_b", version_name="v1",
                             sample_input_data=train.select(feature_cols))
    mv.create_service(service_name="predict_track_b_service", service_compute_pool="MOVING_INTEL_POOL")
    return model.predict(test)
```

> 🤖 Claude Code: 모델 코드 생성, 하이퍼파라미터 탐색 스크립트 작성
> 👤 사용자: 컴퓨팅 풀 생성, 모델 학습 실행 및 결과 확인

---

## A6. MVP vs 고도화 요약 테이블

| 항목 | MVP (해커톤 04-12 마감) | 고도화 (Phase 2+) |
|------|------------------------|-------------------|
| **데이터 범위** | Track A: 25구 × 아정당 2023-2026 (850행) / Track B: 3구(중·영등포·서초) × 아정당+SPH+RICHGO 교집합 (54~102행) | 수도권 확대, 전국 SPH |
| **핵심 모델** | Track A: LinearRegression(25구 경량) / Track B: Ridge α=1.0(MULTI_SOURCE 3구 풀, **XGB 금지**) | LSTM/Prophet 시계열, 앙상블 |
| **피처** | MOVE_SIGNAL_INDEX + 계절성 + 시세 + 라이프스타일 | 영유아 피처, 주식 상관 피처 추가 |
| **데이터 조인** | MART_MOVE_ANALYSIS DATA_TIER 컬럼 기반 Tier별 피처 선택 | 4종 전체 크로스 조인 |
| **전처리** | forward-fill + 기본 클리핑 + BJD↔DISTRICT 매핑 | 고급 보간, 이상치 자동 탐지 |
| **배포** | UDF 등록 → Streamlit 호출 | Model Registry 버전 관리, A/B 테스트 |
| **시각화** | 히트맵 1개 + 예측 차트 | 지도 대시보드 + AI 에이전트 챗봇 |
| **Cortex AI** | AI_COMPLETE 인사이트 생성 | Cortex Agents 멀티툴 오케스트레이션 |
| **Cortex AI Functions** | AI_COMPLETE (인사이트), AI_CLASSIFY (등급), AI_AGG (요약), AI_EMBED+VECTOR (유사 단지) | AI_SENTIMENT, AI_TRANSLATE, AI_EXTRACT, AI_REDACT |
| **평가 기준** | Track A MAPE < 25% · Track B MAPE < 20% | MAPE < 10%, 시차 상관 r > 0.7 |

---

## A7. 일별 구현 마일스톤 (데이터/ML 파트)

| 날짜 | 목표 | 산출물 | 🤖/👤 |
|------|------|--------|-------|
| **04-06 (일)** | 데이터 모델 설계 확정 + DDL 작성 | 이 문서 + DDL SQL 파일 | 🤖 DDL 생성, 👤 설계 리뷰 |
| **04-07 (월)** | Marketplace 데이터셋 4종 구독 + 뷰 생성 + 데이터 탐색 | 뷰 11개 + 데이터 프로파일 리포트 | 👤 구독(Get), 🤖 뷰·검증 SQL |
| **04-08 (화)** | 전처리 파이프라인 구현 + BJD↔DISTRICT 매핑 검증 + 통합 마트 생성 | Snowpark 전처리 코드 + MART_MOVE_ANALYSIS 테이블 | 🤖 코드 생성, 👤 실행·확인 |
| **04-09 (수)** | Feature Engineering + 시차 상관분석 | 피처 테이블 + lag correlation 결과 | 🤖 피처 코드, 👤 결과 해석 |
| **04-10 (목)** | ML 모델 학습 + 평가 + UDF 배포 | 학습된 모델 + UDF + 성능 리포트 | 🤖 학습 코드, 👤 실행·평가 |
| **04-11 (금)** | 대시보드 연동 + E2E 통합 테스트 | 예측 결과가 Streamlit에 표시 | 🤖+👤 통합 |
| **04-12 (토)** | 최종 검증 + 발표 자료 데이터 파트 | 데모 시나리오 데이터 확인 | 👤 최종 확인 |

> **핵심 리스크**: 04-07 Marketplace 구독이 지연되면 전체 일정이 밀림. Trial 계정 생성과 데이터셋 구독을 최우선으로 처리할 것.
> **추가 리스크**: BJD_CODE ↔ DISTRICT_CODE 매핑 실패 시 RICHGO-SPH 동 단위 조인 불가. 매핑 정합성 04-08에 우선 검증.

---

# Part B. 서빙 레이어 (API & Cortex AI)

## 서빙 레이어 설계 철학 (일론 머스크 5원칙 적용)

| 원칙 | 적용 |
|------|------|
| **1. 요구사항을 더 단순하게** | REST API 서버를 별도로 띄우지 않는다. Streamlit in Snowflake 내부에서 UDF 호출로 모든 데이터 서빙을 처리한다. MVP에서 외부 API Gateway는 삭제 대상이다. |
| **2. 불필요한 부분 삭제** | 인증/인가 레이어, Rate Limiting, API 버저닝 인프라 — MVP에서 전부 삭제. Snowflake RBAC이 접근 제어를 대신한다. |
| **3. 단순화/최적화** | 엔드포인트 4개 → UDF 3개로 축소. 모든 비즈니스 로직은 SQL UDF/UDTF로 구현하여 Snowflake 컴퓨트 안에서 실행한다. |
| **4. 속도 높이기** | Snowflake 웨어하우스 캐시 + 결과 캐시를 활용한다. 동일 쿼리는 두 번째부터 즉시 반환. |
| **5. 자동화** | Cortex Analyst 시맨틱 모델로 자연어 → SQL 자동 변환. 심사위원이 직접 자연어로 질의하는 데모가 가능하다. |

**핵심 결정**: Streamlit in Snowflake 환경에서는 별도 REST API 서버를 띄울 수 없다. 따라서 MVP에서는 **Streamlit 앱 내부에서 UDF를 직접 호출**하는 방식으로 서빙한다. B2B API는 고도화 Phase에서 Snowflake SQL API 또는 External Function으로 외부 노출한다.

---

## B1. 서빙 전략

### B1-1. 환경 제약 사항

Streamlit in Snowflake(SiS)는 완전 관리형 호스팅이므로:
- 자체 HTTP 서버(Flask, FastAPI 등)를 띄울 수 없다
- 외부 네트워크 인바운드 요청을 받을 수 없다
- 모든 데이터 접근은 Snowflake SQL/Snowpark 세션을 통해야 한다

### B1-2. MVP 서빙 전략: Streamlit 내부 함수 호출

MVP에서는 REST API 대신 **Streamlit 앱 내에서 Python 함수로 UDF를 호출**하여 동일한 데이터를 제공한다.

**실제 데이터소스 매핑**

| 서빙 항목 | 실제 테이블/뷰 | 비고 |
|-----------|---------------|------|
| 이사 시그널 | `SOUTH_KOREA_TELECOM_...TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL` | OPEN_COUNT + CONTRACT_COUNT |
| 아파트 시세 | `KOREAN_POPULATION__...HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H` | MEME/JEONSE_PRICE_PER_SUPPLY_PYEONG |
| 유동인구 | `SEOUL_DISTRICTLEVEL_...GRANDATA.FLOATING_POPULATION_INFO` | RESIDENTIAL/WORKING/VISITING_POPULATION |
| 카드매출 | `SEOUL_DISTRICTLEVEL_...GRANDATA.CARD_SALES_INFO` | 20개 업종 매출 |
| 자산소득 | `SEOUL_DISTRICTLEVEL_...GRANDATA.ASSET_INCOME_INFO` | AVERAGE_INCOME, AVERAGE_ASSET_AMOUNT |
| 지역 코드 | `SEOUL_DISTRICTLEVEL_...GRANDATA.M_SCCO_MST` | PROVINCE/CITY/DISTRICT_CODE |
| 주식 시장 | `NEXTRADE_EQUITY_MARKET_DATA.FIN.NX_HT_ONL_MKTPR_A3` | 건설/리츠 종목 체결가 |

```python
# Streamlit 앱 내부에서 UDF 호출 패턴
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

def get_move_demand(district_code: str, start_month: str, end_month: str, segment: str = None):
    """이사 수요 예측 조회 — UDF 호출 래퍼
    
    district_code: SPH DISTRICT_CODE (8자리, 예: '11650101')
    start_month / end_month: 'YYYYMM' 형식
    """
    query = f"""
        SELECT * FROM TABLE(
            PREDICT_MOVE_DEMAND('{district_code}', '{start_month}', '{end_month}')
        )
    """
    if segment:
        query += f" WHERE segment = '{segment}'"
    return session.sql(query).to_pandas()
```

---

## B2. B2B API 엔드포인트 설계 (MVP)

고도화 Phase에서 B2B 고객사에 외부 API를 노출할 때는 **Snowflake SQL API**(`/api/v2/statements`)를 활용한다. 고객사가 Snowflake 계정 없이도 데이터를 조회할 수 있도록 External Function + API Gateway(AWS API Gateway 등) 구성이 필요하다.

아래는 논리적 API 스펙이다. MVP에서는 Streamlit 내부 함수로 동일 로직을 구현한다.

---

### B2-1. GET /api/v1/move-demand — 지역별 이사 수요 예측

| 항목 | 값 |
|------|-----|
| **Method** | GET |
| **URL** | `/api/v1/move-demand` |
| **설명** | 특정 지역의 이사 수요 지표를 반환 (아정당 신규개통 기반 이사 프록시) |

**Request Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `district_code` | string | Y | SPH DISTRICT_CODE 8자리 (예: `11650101` — 서초동) |
| `start_month` | string | Y | 조회 시작월 (`YYYYMM`, 예: `202604`) |
| `end_month` | string | Y | 조회 종료월 (`YYYYMM`, 예: `202606`) |
| `segment` | string | N | 세그먼트 필터 (`high_income`, `family`, `single` 등) |

> **[이사 프록시 추정]** 아정당 데이터에는 직접적인 이사추정건수 컬럼이 없다. V05_REGIONAL_NEW_INSTALL의 `OPEN_COUNT`(신규개통)와 V01_MONTHLY_REGIONAL_CONTRACT_STATS의 `CONTRACT_COUNT`를 이사 선행지표 프록시로 활용한다. 실제 이사 건수와의 상관관계는 검증 필요.

**내부 SQL 로직 (MVP)**

```sql
-- 이사 프록시: 아정당 신규개통 기반
SELECT
    v.INSTALL_STATE,
    v.INSTALL_CITY,
    v.YEAR_MONTH,
    v.OPEN_COUNT                          AS move_proxy_count,      -- 신규개통: 이사 후 통신 재개설 프록시
    v.CONTRACT_COUNT                      AS contract_count,
    v.BUNDLE_COUNT,
    v.STANDALONE_COUNT,
    v.AVG_NET_SALES,
    -- 아파트 시세 교차 참조
    r.MEME_PRICE_PER_SUPPLY_PYEONG        AS apt_매매가_평당,
    r.JEONSE_PRICE_PER_SUPPLY_PYEONG      AS apt_전세가_평당,
    r.TOTAL_HOUSEHOLDS
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
LEFT JOIN KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H r
    ON v.INSTALL_STATE = r.SD
    AND v.INSTALL_CITY = r.SGG
    AND DATE_TRUNC('MONTH', v.YEAR_MONTH) = DATE_TRUNC('MONTH', r.YYYYMMDD)
WHERE v.YEAR_MONTH BETWEEN TO_DATE(:start_month, 'YYYYMM') AND TO_DATE(:end_month, 'YYYYMM')
  AND (v.INSTALL_STATE || v.INSTALL_CITY) IN (
      SELECT PROVINCE_KOR_NAME || CITY_KOR_NAME
      FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
      WHERE DISTRICT_CODE = :district_code
  )
ORDER BY v.YEAR_MONTH;
```

**Response Schema (200 OK)**

```json
{
  "district_code": "11650101",
  "district_name": "서초구 서초동",
  "predictions": [
    {
      "month": "202604",
      "move_proxy_count": 342,
      "contract_count": 410,
      "yoy_change": 0.15,
      "apt_매매가_평당": 85000000,
      "apt_전세가_평당": 52000000,
      "segments": {
        "high_income": { "count": 128, "ratio": 0.37 },
        "family": { "count": 195, "ratio": 0.57 },
        "single": { "count": 147, "ratio": 0.43 }
      },
      "note": "[추정] OPEN_COUNT를 이사 프록시로 사용. 실제 이사 건수 아님."
    }
  ],
  "data_freshness": "2026-04-05T09:00:00Z",
  "model_version": "v1.0"
}
```

**예시 요청**

```
GET /api/v1/move-demand?district_code=11650101&start_month=202604&end_month=202606&segment=high_income
```

---

### B2-2. GET /api/v1/regions — 지원 지역 목록

| 항목 | 값 |
|------|-----|
| **Method** | GET |
| **URL** | `/api/v1/regions` |
| **설명** | 지원 가능한 행정구역 목록 반환 (SPH M_SCCO_MST 기반) |

**내부 SQL 로직**

```sql
-- SPH M_SCCO_MST 기반 행정구역 마스터 (서울 25개 구, 467개 법정동(BJD))
SELECT
    m.DISTRICT_CODE,
    m.PROVINCE_KOR_NAME,
    m.CITY_KOR_NAME,
    m.DISTRICT_KOR_NAME,
    m.PROVINCE_CODE,
    m.CITY_CODE,
    TRUE AS sph_coverage      -- 실제 서울 전체 25개 구 커버 (기존 "3개 구 한정" 오류 수정)
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
ORDER BY m.PROVINCE_CODE, m.CITY_CODE, m.DISTRICT_CODE;
```

**Response Schema (200 OK)**

```json
{
  "regions": [
    {
      "district_code": "11650101",
      "province": "서울특별시",
      "city": "서초구",
      "district": "서초동",
      "sph_coverage": true,
      "data_available": true
    },
    {
      "district_code": "11650102",
      "province": "서울특별시",
      "city": "서초구",
      "district": "잠원동",
      "sph_coverage": true,
      "data_available": true
    }
  ],
  "total_count": 467,
  "note": "SPH M_SCCO_MST 마스터는 25개 구 467개 법정동. FACT 테이블(FLOATING_POPULATION_INFO/CARD_SALES_INFO/ASSET_INCOME_INFO)은 3개 구(중·영등포·서초)만 실존. 22구 요청 시 아정당 경량 프로필만 반환. [이력: 기존 '3개 구 한정' → 2026-04-07 #20 에서 25구로 잘못 정정 → 2026-04-08 #40 #21 Snowflake 검증으로 MULTI_SOURCE 3구로 재롤백]"
}
```

---

### B2-3. GET /api/v1/segments — 세그먼트 필터 옵션

| 항목 | 값 |
|------|-----|
| **Method** | GET |
| **URL** | `/api/v1/segments` |
| **설명** | 사용 가능한 세그먼트 필터 목록 반환 (SPH ASSET_INCOME_INFO 기반) |

> **[세그먼트 도출 방식]** SPH ASSET_INCOME_INFO의 `AVERAGE_INCOME`, `AVERAGE_ASSET_AMOUNT`, `AVERAGE_SCORE`, `AGE_GROUP`, `GENDER` 컬럼에서 파생한다.

**Response Schema (200 OK)**

```json
{
  "segments": [
    { "code": "high_income", "label": "고소득 가구", "description": "AVERAGE_INCOME 상위 30% (ASSET_INCOME_INFO 기반)" },
    { "code": "family", "label": "가족 가구", "description": "AGE_GROUP 30~40대 + PYEONG_대형_COUNT 보유" },
    { "code": "single", "label": "1인 가구", "description": "AGE_GROUP 20~30대 + PYEONG_소형_COUNT 비중 높음" },
    { "code": "young_adult", "label": "청년층", "description": "AGE_GROUP '20' 또는 '30' 코드" }
  ],
  "source_table": "SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.ASSET_INCOME_INFO"
}
```

---

### B2-4. GET /api/v1/roi-calc — ROI 시뮬레이션

| 항목 | 값 |
|------|-----|
| **Method** | GET |
| **URL** | `/api/v1/roi-calc` |
| **설명** | 업종별 이사 수요 예측 데이터 활용 시 ROI 시뮬레이션 |

**Request Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| `industry` | string | Y | 업종 코드 (`rental`, `interior`, `moving`, `telecom`, `realestate`) |
| `district_code` | string | Y | SPH DISTRICT_CODE 8자리 |
| `budget` | integer | Y | 월 마케팅 예산 (원) |
| `conversion_rate` | float | N | 기존 전환율 (기본값: 업종 평균) |

**내부 SQL 로직 (카드매출 업종 데이터 활용)**

```sql
-- 업종별 카드매출 현황 조회 (CARD_SALES_INFO 20개 업종)
SELECT
    c.DISTRICT_CODE,
    c.STANDARD_YEAR_MONTH,
    c.FOOD_SALES,
    c.ACCOMMODATION_SALES,
    c.HOME_LIFE_SERVICE_SALES,        -- 이사/생활서비스 관련
    c.EDUCATION_ACADEMY_SALES,
    c.BEAUTY_SALES,
    c.TOTAL_SALES,
    -- 이사 프록시 (아정당 신규개통)
    v.OPEN_COUNT AS move_proxy_count
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.CARD_SALES_INFO c
JOIN SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
    ON c.DISTRICT_CODE = m.DISTRICT_CODE
JOIN SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
    ON m.CITY_KOR_NAME = v.INSTALL_CITY
    AND c.STANDARD_YEAR_MONTH = TO_CHAR(v.YEAR_MONTH, 'YYYYMM')
WHERE c.DISTRICT_CODE = :district_code
ORDER BY c.STANDARD_YEAR_MONTH DESC
LIMIT 12;
```

**Response Schema (200 OK)**

```json
{
  "industry": "rental",
  "industry_name": "가전 렌탈",
  "district_code": "11650101",
  "district_name": "서초구 서초동",
  "simulation": {
    "budget": 10000000,
    "baseline_conversion_rate": 0.02,
    "predicted_conversion_rate": 0.06,
    "expected_leads": 45,
    "cost_per_lead": 222222,
    "predicted_cost_per_lead": 74074,
    "roi_improvement_pct": 200,
    "monthly_move_proxy_count": 342,
    "addressable_market": 128
  },
  "assumptions": [
    "이사 이벤트 트리거 캠페인 전환율 = 일반 대비 3배 (글로벌 벤치마크 기반) [추정]",
    "OPEN_COUNT를 이사 건수 프록시로 사용 [추정]",
    "고소득 세그먼트: ASSET_INCOME_INFO.AVERAGE_INCOME 상위 30% [추정]"
  ]
}
```

**예시 요청**

```
GET /api/v1/roi-calc?industry=rental&district_code=11650101&budget=10000000&conversion_rate=0.02
```

---

## B3. Snowflake UDF/UDTF 설계

모든 비즈니스 로직은 Snowflake UDF로 구현한다. Streamlit 앱과 Cortex Agents 모두 동일한 UDF를 호출하여 로직 중복을 방지한다.

### B3-0. UDF 커버리지 매트릭스 (Dual-Tier)

`MART_MOVE_ANALYSIS.DATA_TIER` 컬럼 기반으로 UDF 내부 로직이 Tier별 분기한다.

| UDF | MULTI_SOURCE (3구: 중·영등포·서초) | TELECOM_ONLY (22구) |
|---|---|---|
| `PREDICT_MOVE_DEMAND` | Track B 풀 피처 모델 (Ridge, 15+ 컬럼) | Track A 경량 모델 (선형, 3 컬럼) |
| `CALC_ROI` | RICHGO 평당가 + SPH 업종 분포 정밀 ROI | OPEN_COUNT × 평균 단가 근사 ROI (low confidence) |
| `GET_SEGMENT_PROFILE` | population/income/consumption/housing 4섹션 풀 프로필 | telecom_summary 경량 프로필만 |

모든 UDF는 반환에 `tier` 또는 `data_tier` 필드를 포함한다.
UDF 호출 시 내부 로직: `CITY_CODE` → `DATA_TIER` 조회 → Tier별 분기 실행.

### B3-1. PREDICT_MOVE_DEMAND — 이사 수요 예측

```sql
CREATE OR REPLACE FUNCTION PREDICT_MOVE_DEMAND(
    city_code VARCHAR,       -- CITY_CODE (5자리 시군구코드, Dual-Tier 마트 조인 키)
    start_month VARCHAR,     -- 'YYYYMM'
    end_month VARCHAR        -- 'YYYYMM'
)
RETURNS TABLE (
    city_code VARCHAR,
    city_name VARCHAR,
    district_name VARCHAR,
    target_month VARCHAR,
    move_proxy_count INTEGER,    -- 아정당 OPEN_COUNT (이사 프록시)
    contract_count INTEGER,      -- 아정당 CONTRACT_COUNT
    yoy_change FLOAT,
    apt_매매가_평당 FLOAT,         -- RICHGO MEME_PRICE_PER_SUPPLY_PYEONG
    apt_전세가_평당 FLOAT,         -- RICHGO JEONSE_PRICE_PER_SUPPLY_PYEONG
    total_households INTEGER,    -- RICHGO TOTAL_HOUSEHOLDS
    segment_high_income_ratio FLOAT,
    segment_family_ratio FLOAT,
    segment_single_ratio FLOAT,
    data_tier VARCHAR,        -- 'MULTI_SOURCE' 또는 'TELECOM_ONLY'
    confidence FLOAT          -- 교차검증 R² 값 (TELECOM_ONLY는 낮음)
)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pandas', 'scikit-learn')
HANDLER = 'predict_move_demand'
AS
$$
def predict_move_demand(city_code, start_month, end_month):
    """
    내부 로직 개요:
    0. CITY_CODE 기반 DATA_TIER 감지 → Track A/B 모델 선택
    1. M_SCCO_MST에서 CITY_CODE → INSTALL_CITY 매핑
    2. V05_REGIONAL_NEW_INSTALL에서 OPEN_COUNT 조회 (이사 프록시)
       - OPEN_COUNT: 신규 통신 개통 = 이사 후 통신 재개설 선행지표
    3. REGION_APT_RICHGO_MARKET_PRICE_M_H에서 아파트 시세 조회 (교차 검증용)
       - MEME_PRICE_PER_SUPPLY_PYEONG, JEONSE_PRICE_PER_SUPPLY_PYEONG, TOTAL_HOUSEHOLDS
    4. 시계열 모델(선형회귀 또는 Prophet)로 미래 월 예측
    5. ASSET_INCOME_INFO에서 세그먼트 비율 계산
       - high_income: AVERAGE_INCOME 상위 30%
       - family: AGE_GROUP 30~40대 비중
       - single: AGE_GROUP 20~30대 + 소형 평형 비중
    6. confidence = 교차 검증 R² 값
    """
    pass  # 구현 예정
$$;
```

**입력/출력 스키마**

| 구분 | 필드 | 타입 | 원본 컬럼 | 설명 |
|------|------|------|-----------|------|
| 입력 | `district_code` | VARCHAR | M_SCCO_MST.DISTRICT_CODE | SPH 8자리 행정동 코드 |
| 입력 | `start_month` | VARCHAR | — | 조회 시작월 (`YYYYMM`) |
| 입력 | `end_month` | VARCHAR | — | 조회 종료월 (`YYYYMM`) |
| 출력 | `move_proxy_count` | INTEGER | V05.OPEN_COUNT | 이사 프록시 (신규개통) |
| 출력 | `contract_count` | INTEGER | V05.CONTRACT_COUNT | 계약 건수 |
| 출력 | `yoy_change` | FLOAT | — | 전년 동월 대비 변화율 |
| 출력 | `apt_매매가_평당` | FLOAT | REGION_APT_RICHGO_MARKET_PRICE_M_H.MEME_PRICE_PER_SUPPLY_PYEONG | 아파트 평당 매매가 |
| 출력 | `apt_전세가_평당` | FLOAT | REGION_APT_RICHGO_MARKET_PRICE_M_H.JEONSE_PRICE_PER_SUPPLY_PYEONG | 아파트 평당 전세가 |
| 출력 | `total_households` | INTEGER | REGION_APT_RICHGO_MARKET_PRICE_M_H.TOTAL_HOUSEHOLDS | 총 세대수 |
| 출력 | `segment_*_ratio` | FLOAT | ASSET_INCOME_INFO 파생 | 세그먼트별 비율 [추정] |

**내부 로직 흐름**

```
M_SCCO_MST (DISTRICT_CODE → INSTALL_STATE/INSTALL_CITY 변환)
    ↓
아정당 V05_REGIONAL_NEW_INSTALL (OPEN_COUNT, CONTRACT_COUNT 조회)
    → 시계열 특성 추출 (계절성, 추세, 잔차)
    → RICHGO 아파트시세와 시차 상관 검증
    → 예측 모델 실행
    → ASSET_INCOME_INFO에서 세그먼트 비율 추가
    → 결과 반환

조인 키 주의:
  - 아정당: INSTALL_STATE(시도명), INSTALL_CITY(시군구명) — 텍스트
  - RICHGO: SD(시도), SGG(시군구) — 텍스트
  - SPH: PROVINCE_CODE(2자리), CITY_CODE(5자리), DISTRICT_CODE(8자리) — 코드
  → M_SCCO_MST를 브릿지 테이블로 사용하여 코드↔텍스트 변환
```

### B3-2. CALC_ROI — ROI 계산

```sql
CREATE OR REPLACE FUNCTION CALC_ROI(
    industry VARCHAR,
    district_code VARCHAR,    -- SPH DISTRICT_CODE (기존 region_code → district_code 변경)
    budget INTEGER,
    conversion_rate FLOAT DEFAULT NULL
)
RETURNS TABLE (
    industry VARCHAR,
    district_code VARCHAR,
    budget INTEGER,
    baseline_conversion_rate FLOAT,
    predicted_conversion_rate FLOAT,
    expected_leads INTEGER,
    cost_per_lead INTEGER,
    roi_improvement_pct FLOAT,
    tier VARCHAR,             -- 'MULTI_SOURCE' 또는 'TELECOM_ONLY'
    confidence VARCHAR        -- 'high' (MULTI_SOURCE) / 'approximate' (TELECOM_ONLY)
)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python')
HANDLER = 'calc_roi'
AS
$$
def calc_roi(industry, district_code, budget, conversion_rate=None):
    """
    내부 로직 개요:
    0. MART_MOVE_ANALYSIS.DATA_TIER 조회 → Tier 분기 (MULTI_SOURCE 정밀 / TELECOM_ONLY 근사)
    1. 업종별 기본 전환율 테이블 조회 (없으면 기본값 사용)
    2. PREDICT_MOVE_DEMAND 호출하여 해당 지역 이사 프록시 건수 조회
       (OPEN_COUNT 기반)
    3. CARD_SALES_INFO에서 해당 업종 카드매출 현황 조회
       - rental → HOME_LIFE_SERVICE_SALES (가정생활서비스)
       - interior → HOME_LIFE_SERVICE_SALES
       - moving → HOME_LIFE_SERVICE_SALES + FOOD_SALES
       - telecom → 아정당 V01.AVG_NET_SALES 참조
    4. 이사 이벤트 트리거 캠페인 전환율 승수 적용 (글로벌 벤치마크: 3배) [추정]
    5. expected_leads = move_proxy_count × addressable_ratio × predicted_conversion_rate
    6. ROI 개선율 = (predicted_conversion_rate / baseline_conversion_rate - 1) × 100
    """
    pass  # 구현 예정
$$;
```

**업종별 기본 전환율 (내장 상수)**

| 업종 코드 | 업종명 | 기본 전환율 | CARD_SALES_INFO 컬럼 | 비고 |
|-----------|--------|------------|---------------------|------|
| `rental` | 가전 렌탈 | 2% | HOME_LIFE_SERVICE_SALES | 코웨이 등 |
| `interior` | 인테리어 | 1.5% | HOME_LIFE_SERVICE_SALES | 오늘의집 등 |
| `moving` | 이사 O2O | 5% | HOME_LIFE_SERVICE_SALES | 짐싸 등 |
| `telecom` | 통신사 | 3% | V01.AVG_NET_SALES 참조 | KT, SKT 등 |
| `realestate` | 부동산 중개 | 1% | — | 직방 등 |

**업종별 LTV**

| 업종 | 기본 전환율 | LTV (만원) |
|------|------------|-----------|
| 가전 렌탈 | 2% | 108~300 |
| 인테리어 | 1.5% | 500~3,000 |
| 이사 O2O | 5% | 110~130 |
| 통신사 | 3% | 72~120 |

### B3-3. GET_SEGMENT_PROFILE — 세그먼트 프로파일

```sql
CREATE OR REPLACE FUNCTION GET_SEGMENT_PROFILE(
    district_code VARCHAR    -- SPH DISTRICT_CODE (기존 region_code → district_code 변경)
)
RETURNS TABLE (
    district_code VARCHAR,
    city_name VARCHAR,
    district_name VARCHAR,
    avg_income FLOAT,             -- ASSET_INCOME_INFO.AVERAGE_INCOME
    median_income FLOAT,          -- ASSET_INCOME_INFO.MEDIAN_INCOME
    avg_asset_amount FLOAT,       -- ASSET_INCOME_INFO.AVERAGE_ASSET_AMOUNT
    avg_credit_score FLOAT,       -- ASSET_INCOME_INFO.AVERAGE_SCORE
    residential_population FLOAT, -- FLOATING_POPULATION_INFO.RESIDENTIAL_POPULATION
    working_population FLOAT,     -- FLOATING_POPULATION_INFO.WORKING_POPULATION
    visiting_population FLOAT,    -- FLOATING_POPULATION_INFO.VISITING_POPULATION
    dominant_segment VARCHAR,
    high_income_ratio FLOAT,
    family_ratio FLOAT,
    avg_apt_매매가_평당 FLOAT,      -- REGION_APT_RICHGO_MARKET_PRICE_M_H.MEME_PRICE_PER_SUPPLY_PYEONG
    avg_apt_전세가_평당 FLOAT,      -- REGION_APT_RICHGO_MARKET_PRICE_M_H.JEONSE_PRICE_PER_SUPPLY_PYEONG
    income_to_price_ratio FLOAT   -- avg_income / avg_apt_매매가 [추정]
)
LANGUAGE PYTHON
RUNTIME_VERSION = '3.11'
PACKAGES = ('snowflake-snowpark-python', 'pandas')
HANDLER = 'get_segment_profile'
AS
$$
def get_segment_profile(district_code):
    """
    내부 로직 개요:
    1. M_SCCO_MST에서 DISTRICT_CODE로 지역 메타데이터 조회
       (PROVINCE_CODE, CITY_CODE, DISTRICT_CODE, 한국어/영어명)
    2. FLOATING_POPULATION_INFO에서 유동인구 조회
       - RESIDENTIAL_POPULATION: 거주인구
       - WORKING_POPULATION: 직장인구
       - VISITING_POPULATION: 방문인구
       필터: CITY_CODE = city_code. SPH FLOATING_POPULATION_INFO/CARD_SALES_INFO/ASSET_INCOME_INFO는 MULTI_SOURCE 3구(중구/영등포구/서초구)만 실존이므로, TELECOM_ONLY 22구 요청 시 아정당 기반 경량 프로필만 반환
    3. ASSET_INCOME_INFO에서 자산소득 데이터 조회
       - AVERAGE_INCOME, MEDIAN_INCOME, AVERAGE_HOUSEHOLD_INCOME
       - AVERAGE_ASSET_AMOUNT, AVERAGE_SCORE (신용점수)
       - OWN_HOUSING_COUNT, MULTIPLE_HOUSING_COUNT (주택보유)
    4. REGION_APT_RICHGO_MARKET_PRICE_M_H에서 아파트 시세 조회
       - MEME_PRICE_PER_SUPPLY_PYEONG: 평당 매매가
       - JEONSE_PRICE_PER_SUPPLY_PYEONG: 평당 전세가
       - TOTAL_HOUSEHOLDS: 총 세대수
       조인: SD/SGG 텍스트 매칭 (M_SCCO_MST 브릿지)
    5. 소득 대비 아파트 가격 부담 지수 계산 [추정]
    6. 지배적 세그먼트 판별
    """
    pass  # 구현 예정
$$;
```

**입력/출력 스키마**

| 구분 | 필드 | 타입 | 원본 컬럼 | 설명 |
|------|------|------|-----------|------|
| 입력 | `district_code` | VARCHAR | M_SCCO_MST.DISTRICT_CODE | SPH 8자리 행정동 코드 |
| 출력 | `avg_income` | FLOAT | ASSET_INCOME_INFO.AVERAGE_INCOME | 평균 소득 |
| 출력 | `avg_asset_amount` | FLOAT | ASSET_INCOME_INFO.AVERAGE_ASSET_AMOUNT | 평균 자산 |
| 출력 | `avg_credit_score` | FLOAT | ASSET_INCOME_INFO.AVERAGE_SCORE | 평균 신용점수 |
| 출력 | `residential_population` | FLOAT | FLOATING_POPULATION_INFO.RESIDENTIAL_POPULATION | 거주인구 |
| 출력 | `working_population` | FLOAT | FLOATING_POPULATION_INFO.WORKING_POPULATION | 직장인구 |
| 출력 | `visiting_population` | FLOAT | FLOATING_POPULATION_INFO.VISITING_POPULATION | 방문인구 |
| 출력 | `avg_apt_매매가_평당` | FLOAT | REGION_APT_RICHGO_MARKET_PRICE_M_H.MEME_PRICE_PER_SUPPLY_PYEONG | 평당 매매가 |
| 출력 | `avg_apt_전세가_평당` | FLOAT | REGION_APT_RICHGO_MARKET_PRICE_M_H.JEONSE_PRICE_PER_SUPPLY_PYEONG | 평당 전세가 |
| 출력 | `income_to_price_ratio` | FLOAT | 파생 | 소득 대비 주택 가격 비율 [추정] |

> **커버리지**: SPH M_SCCO_MST는 서울 25개 구 467개 법정동(마스터 코드북). FACT 테이블은 3개 구(중구·영등포구·서초구)만 실존(해커톤 샘플). 22구에서 SPH FACT 조회 시 NULL 반환. (기존 "3개 구 한정" → 2026-04-07 #20에서 25구로 잘못 정정 → 2026-04-08 #40 #21 Snowflake 검증으로 MULTI_SOURCE 3구로 재롤백)

---

## B4. Cortex AI Functions (MVP)

Snowflake Cortex AI Functions는 SQL 한 줄로 LLM 기반 분석을 수행하는 내장 함수다. 별도 인프라 없이 SELECT 문에서 바로 호출 가능하며, 해커톤 가산점(Snowflake 활용도)에 직결된다.

> 리전: US West (Oregon, us-west-2) — 모든 Cortex AI Functions 제한 없이 사용 가능

### B4-1. MVP에서 활용하는 함수

#### AI_COMPLETE — 이사 인사이트 자동 생성

B2B 고객에게 제공하는 지역별 이사 인사이트 텍스트를 자동 생성한다.

```sql
-- 지역별 이사 인사이트 자동 생성 (실제 테이블 참조)
SELECT
    m.INSTALL_STATE,
    m.INSTALL_CITY,
    m.OPEN_COUNT                          AS move_proxy_count,
    LAG(m.OPEN_COUNT) OVER (
        PARTITION BY m.INSTALL_STATE, m.INSTALL_CITY
        ORDER BY m.YEAR_MONTH
    )                                     AS prev_open_count,
    AI_COMPLETE(
        'claude-4-sonnet',
        CONCAT(
            m.INSTALL_STATE, ' ', m.INSTALL_CITY, '의 ',
            '이번 달 신규 통신 개통(이사 프록시): ', m.OPEN_COUNT, '건, ',
            '전월 대비 변화: ',
            ROUND(
                (m.OPEN_COUNT - LAG(m.OPEN_COUNT) OVER (
                    PARTITION BY m.INSTALL_STATE, m.INSTALL_CITY
                    ORDER BY m.YEAR_MONTH
                )) / NULLIF(LAG(m.OPEN_COUNT) OVER (
                    PARTITION BY m.INSTALL_STATE, m.INSTALL_CITY
                    ORDER BY m.YEAR_MONTH
                ), 0) * 100, 1
            ), '%. ',
            '평당 아파트 매매가: ', r.MEME_PRICE_PER_SUPPLY_PYEONG, '원. ',
            'B2B 마케팅 담당자에게 3줄 이내로 액션 아이템을 제안하세요. 한국어로 답변.'
        )
    ) AS ai_insight
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL m
LEFT JOIN KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H r
    ON m.INSTALL_STATE = r.SD
    AND m.INSTALL_CITY = r.SGG
    AND DATE_TRUNC('MONTH', m.YEAR_MONTH) = DATE_TRUNC('MONTH', r.YYYYMMDD)
WHERE m.YEAR_MONTH = '2026-05-01';
```

**Streamlit 연동**: 히트맵에서 행정동 클릭 시 상세 패널에 AI 인사이트 표시

```python
# Streamlit에서 AI_COMPLETE 결과 표시
if selected_dong:
    insight = session.sql(f"""
        SELECT AI_COMPLETE('claude-4-sonnet',
            '{selected_dong}의 신규 통신 개통(이사 프록시) 수요가 {demand_count}건입니다.
             평당 아파트 매매가는 {apt_price}원입니다.
             가전 렌탈사 마케팅 담당자에게 3줄 액션 아이템을 제안하세요.')
    """).collect()[0][0]
    st.info(f"🤖 AI 인사이트: {insight}")
```

#### AI_CLASSIFY — 이사 수요 등급 자동 분류

이사 수요 지수를 LLM 기반으로 등급 분류한다.

```sql
-- 이사 수요 등급 자동 분류 (고/중/저) — 실제 테이블 참조
SELECT
    v.INSTALL_STATE,
    v.INSTALL_CITY,
    v.YEAR_MONTH,
    v.OPEN_COUNT,
    AI_CLASSIFY(
        CONCAT(
            '신규개통(이사프록시): ', v.OPEN_COUNT, '건, ',
            '전월 대비 변화율: ',
            ROUND(
                (v.OPEN_COUNT - LAG(v.OPEN_COUNT) OVER (
                    PARTITION BY v.INSTALL_STATE, v.INSTALL_CITY
                    ORDER BY v.YEAR_MONTH
                )) / NULLIF(LAG(v.OPEN_COUNT) OVER (
                    PARTITION BY v.INSTALL_STATE, v.INSTALL_CITY
                    ORDER BY v.YEAR_MONTH
                ), 0) * 100, 1
            ), '%'
        ),
        ARRAY_CONSTRUCT('긴급 — 즉시 마케팅 투입', '주의 — 모니터링 필요', '안정 — 일반 운영')
    ) AS demand_grade
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
WHERE v.YEAR_MONTH = '2026-05-01';
```

#### AI_AGG — 다중 지역 이사 트렌드 요약

여러 지역의 이사 데이터를 집계하여 자연어 요약을 생성한다.

```sql
-- 시/도 단위 이사 트렌드 자연어 요약 (실제 테이블 참조)
SELECT
    v.INSTALL_STATE,
    AI_AGG(
        CONCAT(v.INSTALL_CITY, ': 신규개통 ', v.OPEN_COUNT, '건'),
        '이 지역의 이사(신규개통 기준) 트렌드를 2~3문장으로 요약하고, 이사 수요가 가장 높은 시/군/구와 낮은 곳을 지목하세요.'
    ) AS district_summary
FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
WHERE v.YEAR_MONTH = '2026-05-01'
GROUP BY v.INSTALL_STATE;
```

#### AI_EMBED + VECTOR — 아파트 단지 유사도 검색

아파트 단지 특성을 벡터화하여 유사 단지를 추천한다.

```sql
-- 1) 아파트 시세 데이터 벡터화 (실제 컬럼명 사용)
ALTER TABLE KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
    ADD COLUMN IF NOT EXISTS EMBEDDING VECTOR(FLOAT, 1024);

UPDATE KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
SET EMBEDDING = AI_EMBED(
    'snowflake-arctic-embed-l-v2.0',
    CONCAT(
        '시도: ', SD,
        ', 시군구: ', SGG,
        ', 읍면동: ', EMD,
        ', 총세대수: ', TOTAL_HOUSEHOLDS,
        ', 평당매매가: ', MEME_PRICE_PER_SUPPLY_PYEONG, '원',
        ', 평당전세가: ', JEONSE_PRICE_PER_SUPPLY_PYEONG, '원',
        ', 기준월: ', TO_CHAR(YYYYMMDD, 'YYYY-MM')
    )
);

-- 2) 유사 지역 검색 (코사인 유사도)
SELECT
    target.SGG || ' ' || target.EMD   AS 기준지역,
    similar.SGG || ' ' || similar.EMD AS 유사지역,
    similar.MEME_PRICE_PER_SUPPLY_PYEONG,
    similar.JEONSE_PRICE_PER_SUPPLY_PYEONG,
    similar.TOTAL_HOUSEHOLDS,
    VECTOR_COSINE_SIMILARITY(target.EMBEDDING, similar.EMBEDDING) AS similarity
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H target
CROSS JOIN KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H similar
WHERE target.BJD_CODE = '대상_법정동코드'
  AND similar.BJD_CODE != target.BJD_CODE
  AND target.YYYYMMDD = similar.YYYYMMDD   -- 동일 기준월 비교
ORDER BY similarity DESC
LIMIT 5;
```

**Streamlit 연동**: 세그먼트 탭에서 특정 지역 선택 시 유사 지역 5개 추천 표시

### B4-2. 고도화에서 추가 활용할 함수

| 함수 | 용도 | Phase |
|------|------|-------|
| `AI_SENTIMENT` | 지역 커뮤니티 리뷰 감성 분석 (네이버 카페 등 크롤링 데이터) | Phase 2 |
| `AI_TRANSLATE` | 해커톤 심사위원용 영문 리포트 자동 생성 | Phase 2 |
| `AI_EXTRACT` | 비정형 데이터에서 이사 관련 정보 추출 | Phase 3 |
| `AI_REDACT` | PII 제거 후 B2B 데이터 제공 | Phase 3 |

### B4-3. 🤖 Claude Code vs 👤 사용자

| 작업 | 담당 |
|------|------|
| AI Functions SQL 쿼리 작성 | 🤖 Claude Code |
| Streamlit에서 AI 결과 표시 코드 | 🤖 Claude Code |
| Cross-region inference 활성화 (서울 리전인 경우) | 👤 사용자 — Oregon이므로 불필요 |
| AI Functions 실행 비용 모니터링 | 👤 사용자 |

---

## B5. Cortex Analyst 시맨틱 모델 설계 (MVP)

### B5-1. 시맨틱 모델 구조

Cortex Analyst는 YAML 시맨틱 모델을 통해 자연어 질의를 SQL로 변환한다. 4종 데이터셋 각각에 시맨틱 뷰를 정의한다.

```yaml
# moving_intelligence_semantic_model.yaml
name: moving_intelligence
description: "이사 수요 예측 플랫폼 — 통신 신규개통 기반 이사 선행지표 분석"

tables:
  # === 이사 수요 예측 (핵심) ===
  - name: v05_regional_new_install
    description: >
      아정당 통신 신규개통 기반 이사 프록시 데이터.
      OPEN_COUNT(신규개통)를 이사 후 통신 재개설의 선행지표로 활용.
      [추정] 실제 이사 건수와의 상관관계는 검증 필요.
    base_table: SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL
    dimensions:
      - name: install_state
        description: "설치 시도명 (예: 서울특별시)"
        expr: INSTALL_STATE
      - name: install_city
        description: "설치 시군구명 (예: 서초구)"
        expr: INSTALL_CITY
      - name: year_month
        description: "이사 신호 발생 월"
        expr: YEAR_MONTH
    measures:
      - name: open_count
        description: "신규개통 건수 — 이사 후 통신 재개설 프록시 [추정]"
        expr: SUM(OPEN_COUNT)
      - name: contract_count
        description: "총 계약 건수"
        expr: SUM(CONTRACT_COUNT)
      - name: bundle_count
        description: "결합 상품 계약 건수"
        expr: SUM(BUNDLE_COUNT)
      - name: avg_net_sales
        description: "평균 순매출 (원)"
        expr: AVG(AVG_NET_SALES)

  # === 아파트 시세 (부동산) ===
  - name: region_apt_richgo_market_price
    description: >
      RICHGO 아파트 시세 데이터. 서울 지역 아파트 평당 매매가/전세가.
      2012-01~2024-12, 4,356건. BJD_CODE(법정동코드) 기준.
    base_table: KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
    dimensions:
      - name: bjd_code
        description: "법정동 코드 (10자리)"
        expr: BJD_CODE
      - name: sd
        description: "시도명 (예: 서울특별시)"
        expr: SD
      - name: sgg
        description: "시군구명 (예: 서초구)"
        expr: SGG
      - name: emd
        description: "읍면동명 (예: 서초동)"
        expr: EMD
      - name: price_month
        description: "시세 기준 월"
        expr: YYYYMMDD
    measures:
      - name: meme_price_per_supply_pyeong
        description: "평당 매매가 (공급면적 기준, 원)"
        expr: AVG(MEME_PRICE_PER_SUPPLY_PYEONG)
      - name: jeonse_price_per_supply_pyeong
        description: "평당 전세가 (공급면적 기준, 원)"
        expr: AVG(JEONSE_PRICE_PER_SUPPLY_PYEONG)
      - name: total_households
        description: "총 세대수"
        expr: SUM(TOTAL_HOUSEHOLDS)

  # === 지역 생활 빅데이터 ===
  - name: floating_population_info
    description: >
      SPH 유동인구 데이터. FACT는 3개 구(중구·영등포구·서초구) 한정. M_SCCO_MST 마스터는 25구 467개 법정동.
      2021-01~2025-12. DISTRICT_CODE(8자리) 기준.
    base_table: SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO
    dimensions:
      - name: province_code
        description: "시도 코드 (2자리)"
        expr: PROVINCE_CODE
      - name: city_code
        description: "시군구 코드 (5자리)"
        expr: CITY_CODE
      - name: district_code
        description: "행정동 코드 (8자리)"
        expr: DISTRICT_CODE
      - name: standard_year_month
        description: "기준 연월 (YYYYMM)"
        expr: STANDARD_YEAR_MONTH
      - name: gender
        description: "성별 코드"
        expr: GENDER
      - name: age_group
        description: "연령대 코드"
        expr: AGE_GROUP
      - name: weekday_weekend
        description: "평일/주말 구분 (1=평일, 2=주말)"
        expr: WEEKDAY_WEEKEND
      - name: time_slot
        description: "시간대 코드 (3자리)"
        expr: TIME_SLOT
    measures:
      - name: residential_population
        description: "거주인구 (일 평균)"
        expr: SUM(RESIDENTIAL_POPULATION)
      - name: working_population
        description: "직장인구 (일 평균)"
        expr: SUM(WORKING_POPULATION)
      - name: visiting_population
        description: "방문인구 (일 평균)"
        expr: SUM(VISITING_POPULATION)

  # === 주식 시장 ===
  - name: nx_ht_onl_mktpr_a3
    description: "NextTrade 주식 체결가 데이터. 건설/리츠/소비재 섹터 집중."
    base_table: NEXTRADE_EQUITY_MARKET_DATA.FIN.NX_HT_ONL_MKTPR_A3
    dimensions:
      - name: isu_cd
        description: "종목코드 (ISIN 12자리)"
        expr: ISU_CD
      - name: dwdd
        description: "거래일자"
        expr: DWDD
      - name: mkt_id
        description: "시장구분 코드"
        expr: MKT_ID
    measures:
      - name: td_prc
        description: "당일 체결가 (원)"
        expr: AVG(TD_PRC)
      - name: trd_qty
        description: "거래량"
        expr: SUM(TRD_QTY)
      - name: acc_trval
        description: "누적거래대금 (원)"
        expr: SUM(ACC_TRVAL)
      - name: prdy_cmp_prc
        description: "전일대비 가격 변동 (원)"
        expr: AVG(PRDY_CMP_PRC)

joins:
  # 아정당 ↔ SPH: 텍스트명 → 코드 브릿지 (M_SCCO_MST 경유) [추정 조인]
  - from: v05_regional_new_install
    to: floating_population_info
    on: >
      v05_regional_new_install.install_city = (
        SELECT CITY_KOR_NAME FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
        WHERE CITY_CODE = floating_population_info.city_code LIMIT 1
      )
    type: left
    note: "[추정] 아정당 텍스트명↔SPH 코드 직접 조인 불가. M_SCCO_MST 브릿지 필요."
  # 아정당 ↔ RICHGO: 시도/시군구 텍스트 매칭 [추정 조인]
  - from: v05_regional_new_install
    to: region_apt_richgo_market_price
    on: >
      v05_regional_new_install.install_state = region_apt_richgo_market_price.sd
      AND v05_regional_new_install.install_city = region_apt_richgo_market_price.sgg
      AND DATE_TRUNC('MONTH', v05_regional_new_install.year_month) = DATE_TRUNC('MONTH', region_apt_richgo_market_price.price_month)
    type: left

verified_queries:
  - question: "다음 달 서초구 이사 수요 예측해줘"
    sql: >
      SELECT
        INSTALL_CITY,
        YEAR_MONTH,
        SUM(OPEN_COUNT) AS move_proxy_count,
        SUM(CONTRACT_COUNT) AS total_contracts
      FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL
      WHERE INSTALL_CITY = '서초구'
        AND YEAR_MONTH >= DATEADD(MONTH, -12, CURRENT_DATE())
      GROUP BY INSTALL_CITY, YEAR_MONTH
      ORDER BY YEAR_MONTH DESC

  - question: "강남구 최근 이사 수요가 높은 시기는?"
    sql: >
      SELECT
        YEAR_MONTH,
        SUM(OPEN_COUNT) AS move_proxy_count,
        RATIO_TO_REPORT(SUM(OPEN_COUNT)) OVER() AS ratio
      FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL
      WHERE INSTALL_CITY = '강남구'
      GROUP BY YEAR_MONTH
      ORDER BY move_proxy_count DESC

  - question: "서초구 아파트 평당 매매가 추이"
    sql: >
      SELECT
        YYYYMMDD,
        SGG,
        AVG(MEME_PRICE_PER_SUPPLY_PYEONG) AS avg_매매가_평당,
        AVG(JEONSE_PRICE_PER_SUPPLY_PYEONG) AS avg_전세가_평당,
        SUM(TOTAL_HOUSEHOLDS) AS total_households
      FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
      WHERE SGG = '서초구'
      GROUP BY YYYYMMDD, SGG
      ORDER BY YYYYMMDD DESC

  - question: "영등포구 유동인구가 가장 많은 행정동은?"
    sql: >
      SELECT
        f.DISTRICT_CODE,
        m.DISTRICT_KOR_NAME,
        SUM(f.RESIDENTIAL_POPULATION + f.WORKING_POPULATION + f.VISITING_POPULATION) AS total_population
      FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO f
      JOIN SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
        ON f.DISTRICT_CODE = m.DISTRICT_CODE
      WHERE m.CITY_KOR_NAME = '영등포구'
        AND f.STANDARD_YEAR_MONTH >= TO_CHAR(DATEADD(MONTH, -3, CURRENT_DATE()), 'YYYYMM')
      GROUP BY f.DISTRICT_CODE, m.DISTRICT_KOR_NAME
      ORDER BY total_population DESC

  - question: "이사 수요 증가 지역의 건설주 수익률은?"
    sql: >
      -- [추정] 아정당 지역명과 주식 섹터 직접 조인 불가. 시장 전반 건설주 추이 참조.
      SELECT
        DWDD,
        ISU_CD,
        AVG(TD_PRC) AS avg_price,
        SUM(TRD_QTY) AS total_volume,
        AVG(PRDY_CMP_PRC) / NULLIF(AVG(TD_PRC - PRDY_CMP_PRC), 0) * 100 AS price_change_pct
      FROM NEXTRADE_EQUITY_MARKET_DATA.FIN.NX_HT_ONL_MKTPR_A3
      WHERE DWDD >= DATEADD(MONTH, -3, CURRENT_DATE())
      GROUP BY DWDD, ISU_CD
      ORDER BY DWDD DESC, total_volume DESC
```

### B5-2. 자연어 질의 예시

| 자연어 질의 | 기대 동작 |
|------------|----------|
| "다음 달 서초구 이사 수요 예측해줘" | `V05_REGIONAL_NEW_INSTALL` 조회 → 서초구 OPEN_COUNT 시계열 집계 |
| "강남구 최근 이사 수요가 높은 시기는?" | `V05_REGIONAL_NEW_INSTALL` OPEN_COUNT 기준 월별 정렬 |
| "서초구 아파트 평당 매매가 추이" | `REGION_APT_RICHGO_MARKET_PRICE_M_H` 조회 → MEME_PRICE_PER_SUPPLY_PYEONG 시계열 |
| "영등포구 유동인구가 가장 많은 행정동은?" | `FLOATING_POPULATION_INFO` + `M_SCCO_MST` 조인 → 인구합계 기준 정렬 |
| "이사 수요 증가 지역의 건설주 수익률은?" | `NX_HT_ONL_MKTPR_A3` TD_PRC/TRD_QTY 조회 [조인 한계 주의] |

### B5-3. Streamlit 연동

```python
# Streamlit 앱에서 Cortex Analyst 호출
import streamlit as st
from snowflake.snowpark.context import get_active_session

session = get_active_session()

user_question = st.text_input("데이터에 대해 질문하세요:")
if user_question:
    response = session.sql(f"""
        SELECT SNOWFLAKE.CORTEX.ANALYST(
            'moving_intelligence',
            '{user_question}'
        )
    """).collect()
    st.write(response)
```

---

## B6. Cortex Search & Agents 설계 (고도화)

### B6-1. Cortex Search — 아파트/지역 정보 RAG

**목적**: RICHGO 아파트 시세 데이터와 SPH 지역 마스터(M_SCCO_MST)를 시맨틱 검색으로 조회할 수 있게 한다.

```sql
-- Cortex Search 서비스 생성 (실제 테이블 참조)
CREATE OR REPLACE CORTEX SEARCH SERVICE apt_search_service
  ON KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
  WAREHOUSE = MOVING_INTEL_WH
  TARGET_LAG = '1 hour'
AS (
  SELECT
    BJD_CODE,
    SD,
    SGG,
    EMD,
    TOTAL_HOUSEHOLDS,
    YYYYMMDD,
    MEME_PRICE_PER_SUPPLY_PYEONG,
    JEONSE_PRICE_PER_SUPPLY_PYEONG,
    -- 검색 대상 텍스트 컬럼
    CONCAT(
      SD, ' ', SGG, ' ', EMD, ' ',
      '세대수 ', TOTAL_HOUSEHOLDS, ' ',
      '매매가 평당 ', MEME_PRICE_PER_SUPPLY_PYEONG, '원 ',
      '전세가 평당 ', JEONSE_PRICE_PER_SUPPLY_PYEONG, '원 ',
      '기준월 ', TO_CHAR(YYYYMMDD, 'YYYY-MM')
    ) AS search_text
  FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
  WHERE YYYYMMDD = (
    SELECT MAX(YYYYMMDD)
    FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
  )
);
```

**검색 예시**:
- "서초구 전세가 낮은 지역" → JEONSE_PRICE_PER_SUPPLY_PYEONG 기준 정렬
- "2024년 최신 기준 영등포구 아파트 세대수" → TOTAL_HOUSEHOLDS 조회

### B6-2. Cortex Agents — 멀티툴 오케스트레이션

**목적**: Cortex Analyst(정형 데이터 질의) + Cortex Search(아파트/지역 정보 RAG) + Custom UDF(이사 수요 예측, ROI 계산)를 하나의 AI 에이전트로 통합한다.

```sql
-- Cortex Agent 생성 (고도화 Phase) — 실제 테이블 참조
CREATE OR REPLACE AGENT moving_intelligence_agent
  COMMENT = '이사 수요 예측 플랫폼 통합 AI 에이전트'
FROM SPECIFICATION $$
models:
  orchestration: claude-4-sonnet

orchestration:
  budget:
    seconds: 120
    tokens: 50000

instructions:
  system: |
    당신은 무빙 인텔리전스의 AI 분석 에이전트입니다.
    이사 수요 예측(아정당 신규개통 프록시), 지역 분석(SPH 유동인구/자산소득), ROI 시뮬레이션을 수행합니다.
    데이터 한계: 아정당 데이터는 직접 이사건수가 아닌 통신 신규개통 프록시임을 항상 명시하세요.
    항상 한국어로 답변하세요.
  response: |
    데이터 근거를 반드시 포함하고,
    B2B 마케팅 담당자가 즉시 활용할 수 있는 액션 아이템을 제시하세요.
    추정 사항은 [추정] 표시를 명시하세요.

tools:
  - tool_spec:
      type: cortex_analyst_text_to_sql
      name: move_analyst
      description: '이사 수요 예측 데이터 SQL 조회 (아정당 V05 + RICHGO + SPH)'
  - tool_spec:
      type: cortex_search
      name: apt_search
      description: '아파트 시세 및 지역 정보 검색 (RICHGO REGION_APT_RICHGO_MARKET_PRICE_M_H)'

tool_resources:
  move_analyst:
    semantic_model: '@MOVING_INTEL.ANALYTICS.STAGE/moving_intelligence_semantic_model.yaml'
  apt_search:
    cortex_search_service: MOVING_INTEL.ANALYTICS.APT_SEARCH_SERVICE
$$;
```

**에이전트 동작 흐름**

```
사용자 질의: "서초구 다음 달 이사 수요가 많은 동네에서 렌탈 사업 ROI를 알려줘"

1. [Orchestration] 질의 파싱 → budget(120초/50k토큰) 내 태스크 분할
2. [Tool: move_analyst] V05_REGIONAL_NEW_INSTALL OPEN_COUNT로 서초구 시군구별 이사 프록시 SQL 조회
3. [Tool: apt_search] Cortex Search로 상위 지역의 RICHGO 아파트 시세 정보 검색
4. [Response] ASSET_INCOME_INFO 기반 세그먼트 분석 + ROI 계산 + 액션 아이템 생성
```

### B6-3. 고도화 구현 계획

| Phase | 기능 | 일정 (해커톤 이후) |
|-------|------|-------------------|
| Phase 2-1 | Cortex Search 서비스 생성 + RICHGO 데이터 인덱싱 | Week 1 |
| Phase 2-2 | Cortex Analyst 시맨틱 모델 고도화 (verified_queries 추가) | Week 1~2 |
| Phase 2-3 | Cortex Agent 생성 + 멀티툴 오케스트레이션 | Week 2~3 |
| Phase 2-4 | Streamlit 챗봇 UI + Agent 연동 | Week 3~4 |

---

## B7. 작업 구분: Claude Code vs 사용자

| 작업 | 담당 | 설명 |
|------|------|------|
| SQL DDL (테이블, 뷰 생성) | 🤖 Claude Code | 실제 Marketplace DB 참조 뷰 작성 |
| UDF 코드 작성 | 🤖 Claude Code | `PREDICT_MOVE_DEMAND`, `CALC_ROI`, `GET_SEGMENT_PROFILE` |
| YAML 시맨틱 모델 | 🤖 Claude Code | `moving_intelligence_semantic_model.yaml` 작성 (실제 테이블명 반영) |
| API 스펙 문서 | 🤖 Claude Code | 본 문서 작성 및 유지 |
| Streamlit 앱 코드 | 🤖 Claude Code | 대시보드 UI, UDF 호출 로직 |
| Snowflake 웨어하우스 설정 | 👤 사용자 | `MOVING_INTEL_WH` 사이즈 설정 |
| Cortex AI 기능 활성화 | 👤 사용자 | Snowsight에서 Cortex AI 활성화 확인 |
| 권한(GRANT) 설정 | 👤 사용자 | `GRANT USAGE ON FUNCTION`, 역할 할당 |
| Marketplace 데이터 연동 | 👤 사용자 | 4종 데이터셋 구독 및 계정 연결 (완료) |
| External Function 설정 | 👤 사용자 | API Gateway 연동 (고도화 Phase) |
| Cortex Search 서비스 시작 | 👤 사용자 | `MOVING_INTEL_WH` 할당 및 서비스 활성화 |

---

## B8. MVP vs 고도화 요약 테이블

| 항목 | MVP (해커톤 04-06~04-12) | 고도화 (Phase 2+) |
|------|--------------------------|-------------------|
| **서빙 방식** | Streamlit 내부 UDF 호출 | Snowflake SQL API + External Function |
| **이사 수요 예측** | V05.OPEN_COUNT 프록시 (선형회귀/간단 시계열) [추정] | V05 + V01 앙상블 (Prophet/XGBoost) |
| **ROI 계산** | UDF (벤치마크 상수 기반, CARD_SALES_INFO 참조) | UDF (업종별 실제 전환율 학습) |
| **세그먼트 분석** | MULTI_SOURCE 3구(중·영등포·서초) 풀 프로필 (ASSET_INCOME_INFO 기반, FACT 3구만 실존) / TELECOM_ONLY 22구는 아정당 경량 프로필 | 전국 확대 (Marketplace 추가 데이터 소싱) |
| **자연어 질의** | Cortex Analyst (4종 실제 테이블 시맨틱 모델) | Cortex Agents (멀티툴 오케스트레이션) |
| **검색** | SQL 기반 필터링 | Cortex Search RAG (RICHGO 인덱싱) |
| **Cortex AI Functions** | AI_COMPLETE (인사이트), AI_CLASSIFY (등급), AI_AGG (요약), AI_EMBED+VECTOR (유사 지역) | AI_SENTIMENT, AI_TRANSLATE, AI_EXTRACT, AI_REDACT |
| **인증** | Snowflake RBAC | OAuth 2.0 + API Key |
| **외부 API** | 없음 (Streamlit 내부) | REST API (API Gateway) |
| **모니터링** | Streamlit 로그 | Snowflake Query History + 커스텀 대시보드 |
| **지역 코드 체계** | SPH DISTRICT_CODE (8자리) | 통합 코드 체계 (M_SCCO_MST 브릿지) |

---

## B9. 일별 구현 마일스톤 (서빙 레이어 파트)

| 날짜 | 목표 | 산출물 |
|------|------|--------|
| **04-06 (일)** | 실제 Marketplace 테이블 탐색 + UDF 스켈레톤 | M_SCCO_MST 지역코드 매핑 확인, UDF 빈 껍데기 |
| **04-07 (월)** | `PREDICT_MOVE_DEMAND` UDF 구현 | V05.OPEN_COUNT 기반 이사 프록시 로직 완성 (실데이터 테스트) |
| **04-08 (화)** | `CALC_ROI`, `GET_SEGMENT_PROFILE` UDF 구현 | CARD_SALES_INFO + ASSET_INCOME_INFO 기반 ROI + 세그먼트 프로파일 완성 |
| **04-09 (수)** | Cortex Analyst YAML + Cortex AI Functions 구현 | 실제 테이블명 반영 YAML 완성, AI_COMPLETE/AI_CLASSIFY/AI_AGG 쿼리 검증 |
| **04-10 (목)** | Streamlit UDF 연동 + AI_EMBED 벡터화 + 대시보드 통합 | 이사 수요 예측 탭, ROI 시뮬레이터 탭, AI 인사이트 표시 동작 |
| **04-11 (금)** | 통합 테스트 + 데모 시나리오 리허설 | 엔드투엔드 시나리오 3개 검증 |
| **04-12 (토)** | 버그 수정 + 데모 영상 촬영 | 최종 제출 |

---

# Part C. 프레젠테이션 레이어 (Streamlit 대시보드)

## UI 설계 철학 (일론 머스크 5원칙 적용)

| 원칙 | 적용 |
|------|------|
| **1. 요구사항을 더 단순하게** | 대시보드 탭을 3개로 제한 (히트맵, 세그먼트, ROI). AI 질의는 고도화 Phase로 분리 |
| **2. 불필요한 부분 삭제** | 로그인/회원가입 없음. 설정 페이지 없음. 관리자 기능 없음. 데모에 불필요한 모든 UI 제거 |
| **3. 남은 것을 단순화** | 각 탭은 좌측 필터 + 우측 결과의 2컬럼 레이아웃으로 통일. 컴포넌트 재사용 |
| **4. 속도 높이기** | Snowflake 캐싱(`st.cache_data`) 활용. 쿼리 결과 세션 캐시. 초기 로딩 3초 이내 목표 |
| **5. 자동화 (마지막에)** | Cortex AI 자연어 질의는 MVP 이후. 먼저 수동 필터 기반 대시보드를 완성한 뒤 자동화 |

**핵심 원칙**: 해커톤 3분 데모에서 심사위원이 "이것이 작동하는 제품이다"라고 느끼게 만드는 것이 목표. 기능 수보다 완성도 우선.

---

## C1. 대시보드 구조 — MVP 기준 3탭 + 고도화 1탭

### 페이지(탭) 구성

```
┌─────────────────────────────────────────────────────┐
│  🏠 이사 수요 예측 히트맵  │  🔍 세그먼트 분석  │  💰 ROI 계산기  │  🤖 AI 질의(고도화)  │
│       (메인 탭)          │     (MVP)        │    (MVP)       │    (Phase 2)       │
└─────────────────────────────────────────────────────┘
```

| 탭 | 우선순위 | 핵심 가치 | Phase |
|----|---------|----------|-------|
| 이사 수요 예측 히트맵 | P0 (필수) | "어느 지역에서 이사가 많이 일어날 예정인가" — B2B 핵심 가치 시각화 | MVP |
| 세그먼트 분석 | P0 (필수) | "어떤 고객군이 이사하는가" — 타겟 마케팅 근거 | MVP |
| ROI 계산기 | P1 (권장) | "이 데이터를 쓰면 얼마나 절약되는가" — 비즈니스 임팩트 증명 | MVP |
| AI 자연어 질의 | P2 (선택) | "다음 달 서초구 이사 수요는?" — Cortex Analyst 연동 데모 | 고도화 |

### Streamlit 앱 진입점 구조

```python
# app.py (Streamlit in Snowflake 메인)
import streamlit as st

st.set_page_config(page_title="무빙 인텔리전스", layout="wide")

tab1, tab2, tab3 = st.tabs([
    "🏠 이사 수요 예측",
    "🔍 세그먼트 분석",
    "💰 ROI 계산기"
])

with tab1:
    render_heatmap_tab()
with tab2:
    render_segment_tab()
with tab3:
    render_roi_tab()
```

---

## C2. 이사 수요 예측 히트맵 (MVP 핵심)

**목적**: B2B 고객이 "어느 지역에서 향후 2~4주 내 이사 수요가 높은가"를 한눈에 파악

### 화면 레이아웃

```
┌──────────────┬─────────────────────────────────────┐
│  📋 필터     │                                     │
│              │                                     │
│ [기간 선택]  │          🗺️ 지도 (pydeck)           │
│ [구 선택]    │       구(區) 단위 choropleth 히트맵   │
│ [수요 등급]  │                                     │
│              │                                     │
│──────────────│─────────────────────────────────────│
│              │  📊 선택 지역 상세 패널              │
│              │  - 이사 수요 지수 (KPI 카드)         │
│              │  - 월별 추이 차트                    │
│              │  - 상위 구 TOP 5 테이블              │
│              │                                     │
└──────────────┴─────────────────────────────────────┘
```

> **변경**: 아정당 V05_REGIONAL_NEW_INSTALL의 OPEN_COUNT(신규개통)는 시/도+시/군/구 단위로 제공됨. 따라서 히트맵은 **구(區) 단위** 표시로 변경 (행정동 단위 불가).

### 컴포넌트 명세

| 컴포넌트 | Streamlit API | 데이터 소스 | 설명 |
|---------|---------------|-----------|------|
| 기간 필터 | `st.sidebar.selectbox` | 고정 옵션 (이번 달 / 다음 달 / 2개월) | 예측 기간 선택 |
| 지역 필터 | `st.sidebar.multiselect` | `M_SCCO_MST` (CITY_KOR_NAME) | 구(區) 단위 선택 |
| 수요 등급 필터 | `st.sidebar.radio` | 전체 / 고 / 중 / 저 | 이사 수요 예측 지수 등급 |
| 지도 시각화 | `st.pydeck_chart` | `V05_REGIONAL_NEW_INSTALL` + `M_SCCO_MST` JOIN | 구 경계 choropleth (DISTRICT_GEOM 활용) |
| KPI 카드 | `st.metric` | 집계 쿼리 | 선택 지역 이사 수요 지수, 전월 대비 변화 |
| 월별 추이 | `st.line_chart` | 시계열 쿼리 | 최근 6개월 이사 수요 추이 |
| TOP 5 테이블 | `st.dataframe` | 집계 쿼리 | 이사 수요 상위 구 TOP 5 |

### 지도 시각화 상세

```python
# pydeck choropleth 레이어 (M_SCCO_MST.DISTRICT_GEOM 활용)
import pydeck as pdk
import json

# Snowflake에서 GeoJSON 직접 추출 — 외부 파일 불필요
@st.cache_data(ttl=86400)
def get_district_geojson():
    query = """
        SELECT
            m.CITY_KOR_NAME,
            m.DISTRICT_CODE,
            ST_ASGEOJSON(m.DISTRICT_GEOM) AS geojson
        FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
        WHERE m.PROVINCE_CODE = '11'  -- 서울
    """
    return session.sql(query).to_pandas()

layer = pdk.Layer(
    "GeoJsonLayer",
    data=geojson_with_scores,     # 구 경계 + 이사 수요 지수
    get_fill_color="[255, 255 - score * 2.55, 0, 160]",  # 저(초록)→고(빨강)
    get_line_color=[255, 255, 255],
    pickable=True,
    auto_highlight=True,
)

view = pdk.ViewState(latitude=37.5665, longitude=126.978, zoom=11)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view))
```

> **핵심 변경**: M_SCCO_MST.DISTRICT_GEOM (GEOGRAPHY 타입)을 ST_ASGEOJSON()으로 추출하여 직접 렌더링. 외부 GeoJSON 파일 다운로드/업로드 불필요.

**컬러 스케일**:

| 등급 | 이사 수요 지수 | 색상 | 의미 |
|------|-------------|------|------|
| 고 | 70~100 | 빨강 (#FF4444) | 이사 수요 급증 예상 — 즉시 마케팅 투입 권장 |
| 중 | 40~69 | 주황 (#FFA500) | 평균 이상 수요 — 모니터링 권장 |
| 저 | 0~39 | 초록 (#44AA44) | 평균 이하 — 일반 운영 |

**인터랙션**: 구 클릭 시 `st.session_state`에 선택 지역 저장 → 하단 상세 패널에 해당 지역 데이터 표시

### 데이터 쿼리 (Snowpark)

```python
# 이사 수요 예측 히트맵 데이터 조회
# 아정당 V05_REGIONAL_NEW_INSTALL.OPEN_COUNT = 신규개통 건수 (이사 프록시)
@st.cache_data(ttl=3600)
def get_move_demand_data(year_month, cities):
    query = """
        SELECT
            v.INSTALL_STATE,
            v.INSTALL_CITY,
            v.YEAR_MONTH,
            v.OPEN_COUNT,
            v.CONTRACT_COUNT,
            v.AVG_NET_SALES,
            -- 이사 수요 지수: OPEN_COUNT를 전체 기간 대비 정규화 (0~100)
            ROUND(
                (v.OPEN_COUNT - MIN(v.OPEN_COUNT) OVER (PARTITION BY v.INSTALL_CITY))
                / NULLIF(MAX(v.OPEN_COUNT) OVER (PARTITION BY v.INSTALL_CITY)
                       - MIN(v.OPEN_COUNT) OVER (PARTITION BY v.INSTALL_CITY), 0)
                * 100, 1
            ) AS move_demand_index,
            ST_ASGEOJSON(m.DISTRICT_GEOM) AS geojson
        FROM SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
        LEFT JOIN SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
            ON v.INSTALL_CITY = m.CITY_KOR_NAME
        WHERE v.YEAR_MONTH = :1
          AND v.INSTALL_STATE = '서울'
          AND (:2 IS NULL OR v.INSTALL_CITY IN (:2))
        ORDER BY move_demand_index DESC
    """
    return session.sql(query, params=[year_month, cities]).to_pandas()
```

---

## C3. 세그먼트 필터 & 분석 (MVP)

**목적**: B2B 고객이 "어떤 유형의 인구가 이 지역에 거주/유동하는가"를 파악하여 타겟 마케팅에 활용

### 화면 레이아웃

```
┌──────────────┬─────────────────────────────────────┐
│  📋 필터     │  📊 세그먼트별 분포 바 차트          │
│              │                                     │
│ [연령대]     │                                     │
│ [성별]       │─────────────────────────────────────│
│ [지역(구)]   │  📋 상세 데이터 테이블               │
│ [소득 유형]  │  - 구 | 세그먼트 | 유동인구/매출     │
│              │  - 다운로드(CSV) 버튼                │
└──────────────┴─────────────────────────────────────┘
```

### 컴포넌트 명세

| 컴포넌트 | Streamlit API | 설명 |
|---------|---------------|------|
| 연령대 필터 | `st.sidebar.multiselect` | AGE_GROUP (10대~60대+) |
| 성별 필터 | `st.sidebar.selectbox` | 전체 / 남성 / 여성 |
| 지역 필터 | `st.sidebar.multiselect` | 서울 25개 구 (M_SCCO_MST 기반) |
| 소득 유형 필터 | `st.sidebar.selectbox` | INCOME_TYPE 기반 |
| 세그먼트 바 차트 | `st.bar_chart` | 세그먼트별 유동인구/매출 집계 |
| 상세 테이블 | `st.dataframe` | 필터 결과 원본 데이터 |
| CSV 다운로드 | `st.download_button` | 필터링 결과 CSV 내보내기 |

### 세그먼트 정의

| 세그먼트 | 기준 컬럼 | 데이터 소스 |
|---------|----------|-----------|
| 연령대 | `AGE_GROUP` | `FLOATING_POPULATION_INFO` |
| 성별 | `GENDER` | `FLOATING_POPULATION_INFO` |
| 라이프스타일 | `LIFESTYLE` | `CARD_SALES_INFO` |
| 소득 유형 | `INCOME_TYPE` | `ASSET_INCOME_INFO` |
| 소비 패턴 | 20개 업종별 매출 (FOOD, COFFEE, BEAUTY 등) | `CARD_SALES_INFO` |
| 지역 | `CITY_KOR_NAME` (서울 25개 구 전체) | `M_SCCO_MST` |

> **커버리지**: M_SCCO_MST 마스터는 서울 25개 구 467개 법정동. FACT 테이블은 3개 구(중·영등포·서초)만 실존. 지역 선택 25구 전체 가능하나, SPH FACT 기반 지표는 3구에서만 non-NULL. (기존 "3개 구만 커버" → 2026-04-07 #20에서 25구로 잘못 정정 → 2026-04-08 #40 #21 Snowflake 검증으로 MULTI_SOURCE 3구로 재롤백)

### 세그먼트 쿼리 (Snowpark)

```python
@st.cache_data(ttl=3600)
def get_segment_data(year_month, age_groups, gender, city_codes):
    query = """
        SELECT
            f.CITY_CODE,
            m.CITY_KOR_NAME,
            f.AGE_GROUP,
            f.GENDER,
            SUM(f.VISITING_POPULATION) AS total_visiting,
            SUM(f.RESIDENTIAL_POPULATION) AS total_residential,
            AVG(a.AVERAGE_INCOME) AS avg_income,
            AVG(a.AVERAGE_ASSET_AMOUNT) AS avg_asset
        FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO f
        JOIN SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
            ON f.CITY_CODE = m.CITY_CODE
        LEFT JOIN SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.ASSET_INCOME_INFO a
            ON f.CITY_CODE = a.CITY_CODE
            AND f.STANDARD_YEAR_MONTH = a.STANDARD_YEAR_MONTH
            AND f.AGE_GROUP = a.AGE_GROUP
            AND f.GENDER = a.GENDER
        WHERE f.STANDARD_YEAR_MONTH = :1
          AND (:2 IS NULL OR f.AGE_GROUP IN (:2))
          AND (:3 IS NULL OR f.GENDER = :3)
          AND (:4 IS NULL OR f.CITY_CODE IN (:4))
        GROUP BY 1, 2, 3, 4
        ORDER BY total_visiting DESC
    """
    return session.sql(query, params=[year_month, age_groups, gender, city_codes]).to_pandas()
```

---

## C4. ROI 계산기 (MVP)

**목적**: "이사 예측 데이터를 쓰면 마케팅 비용을 얼마나 절감하는가"를 정량적으로 증명 — 비즈니스 임팩트 심사 항목 직접 대응

### 화면 레이아웃

```
┌──────────────────────────┬──────────────────────────┐
│  📝 입력 폼              │  📊 결과                 │
│                          │                          │
│ [업종 선택]              │  ┌──────┐ ┌──────┐       │
│ [지역 선택]              │  │ 예상  │ │ CPA  │       │
│ [월 마케팅 예산]          │  │리드 수│ │      │       │
│ [예상 전환율]             │  └──────┘ └──────┘       │
│                          │  ┌──────┐ ┌──────┐       │
│ [📊 계산하기] 버튼        │  │ ROI% │ │개선율│       │
│                          │  │      │ │      │       │
│                          │  └──────┘ └──────┘       │
│                          │                          │
│                          │  [🟢 MULTI_SOURCE 정밀]   │
│                          │  또는                    │
│                          │  [🟡 TELECOM_ONLY 근사]  │
│                          │                          │
│                          │  📈 Before/After 비교 차트 │
└──────────────────────────┴──────────────────────────┘
```

### 컴포넌트 명세

| 컴포넌트 | Streamlit API | 설명 |
|---------|---------------|------|
| 업종 선택 | `st.selectbox` | 가전 렌탈 / 인테리어 / 이사 서비스 / 통신사 |
| 지역 선택 | `st.selectbox` | 서울 25개 구 (M_SCCO_MST 기반) — 선택한 구의 `MART_MOVE_ANALYSIS.DATA_TIER` 조회 → 배지/문구 렌더링 |
| 월 마케팅 예산 | `st.number_input` | 단위: 만원 (기본값 1,000만원) |
| 예상 전환율 | `st.slider` | 0.5% ~ 10% (기본값 2%) |
| 계산 버튼 | `st.form_submit_button` | `st.form` 내부 |
| KPI 카드 | `st.metric` | 예상 리드 수, CPA, ROI%, 기존 대비 개선율 |
| Before/After 차트 | `st.plotly_chart` 또는 `st.bar_chart` | 기존 방식 vs 무빙 인텔리전스 비교 |

### ROI 계산 로직

```python
# 업종별 기준 데이터 (백서 섹션 5 기반)
INDUSTRY_PARAMS = {
    "가전 렌탈": {"ltv": 200, "base_cpa": 50, "conv_uplift": 2.0},   # 만원 단위
    "인테리어":  {"ltv": 1000, "base_cpa": 100, "conv_uplift": 2.0},
    "이사 서비스": {"ltv": 120, "base_cpa": 30, "conv_uplift": 2.0},
    "통신사":    {"ltv": 96, "base_cpa": 40, "conv_uplift": 2.0},
}

def calculate_roi(industry, budget, conv_rate, city_code=None):
    data_tier = query_mart_tier(city_code) if city_code else "TELECOM_ONLY"
    if data_tier == "MULTI_SOURCE":
        # RICHGO 시세 + SPH 업종 분포 기반 정밀 ROI
        pass  # 정밀 계산 구현 예정
    else:
        # OPEN_COUNT 기반 근사 ROI (TELECOM_ONLY 22구)
        pass  # 근사 계산 구현 예정
    params = INDUSTRY_PARAMS[industry]
    # 기존 방식
    base_leads = budget / params["base_cpa"]
    base_revenue = base_leads * params["ltv"] * (conv_rate / 100)
    # 무빙 인텔리전스 활용 시 (전환율 200% 향상)
    mi_conv_rate = conv_rate * params["conv_uplift"]
    mi_leads = base_leads * 1.5  # 정밀 타겟팅으로 리드 50% 증가
    mi_revenue = mi_leads * params["ltv"] * (mi_conv_rate / 100)
    mi_cpa = budget / mi_leads
    roi_pct = ((mi_revenue - budget) / budget) * 100
    improvement = ((mi_revenue - base_revenue) / base_revenue) * 100
    return {
        "leads": mi_leads,
        "cpa": mi_cpa,
        "roi_pct": roi_pct,
        "improvement": improvement,
    }
```

### 지역별 아파트 시세 참조 (RICHGO 연동)

```python
# RICHGO 실제 아파트 시세 데이터로 지역 선택 시 시세 정보 표시
@st.cache_data(ttl=86400)
def get_apt_price_by_region(sgg_name):
    query = """
        SELECT
            SGG,
            ROUND(AVG(MEME_PRICE_PER_SUPPLY_PYEONG), 0) AS avg_meme_price,
            ROUND(AVG(JEONSE_PRICE_PER_SUPPLY_PYEONG), 0) AS avg_jeonse_price,
            SUM(TOTAL_HOUSEHOLDS) AS total_households
        FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
        WHERE SGG = :1
          AND YYYYMMDD >= DATEADD('month', -6, CURRENT_DATE())
        GROUP BY SGG
    """
    result = session.sql(query, params=[sgg_name]).to_pandas()
    if result.empty:
        return {"avg_meme_price": None, "avg_jeonse_price": None, "total_households": 0,
                "fallback": True, "note": "TELECOM_ONLY 22구 — RICHGO 시세 3구 제한, 시세 근사 미지원"}
    return result
```

**데이터 근거**:
- 전환율 200% 향상: 글로벌 Pre-Mover 마케팅 벤치마크 (백서 섹션 7)
- 업종별 LTV/CPA: 백서 섹션 5 수익 모델 기반
- 아파트 시세: RICHGO `REGION_APT_RICHGO_MARKET_PRICE_M_H` (2012-01~2024-12)
- TELECOM_ONLY 22구는 RICHGO 시세 없음 → 전환율 벤치마크의 상한 근사만 가능, 정밀도 ↓

---

## C5. AI 자연어 질의 (고도화 — Phase 2)

**목적**: "다음 달 서초구 이사 수요 예측해줘"와 같은 자연어 질의로 데이터 탐색

> MVP에서는 구현하지 않는다. 시간 여유가 있을 경우에만 기본 골격 추가.

### 구현 시 설계

| 컴포넌트 | Streamlit API | 설명 |
|---------|---------------|------|
| 챗 입력 | `st.chat_input` | 자연어 질의 입력 |
| 챗 메시지 | `st.chat_message` | 질의/응답 대화 이력 |
| Cortex Analyst 호출 | Snowflake Cortex Analyst API | 시맨틱 모델 기반 자연어 → SQL 변환 |

```python
# 고도화 Phase — Cortex Analyst 연동 (골격)
# 참조 테이블: V05_REGIONAL_NEW_INSTALL, M_SCCO_MST, REGION_APT_RICHGO_MARKET_PRICE_M_H
if prompt := st.chat_input("이사 수요에 대해 질문하세요"):
    with st.chat_message("user"):
        st.write(prompt)
    with st.chat_message("assistant"):
        # Cortex Analyst API 호출
        response = call_cortex_analyst(prompt, semantic_model="move_intelligence.yaml")
        st.write(response["text"])
        if response.get("sql"):
            result = session.sql(response["sql"]).to_pandas()
            st.dataframe(result)
```

**시맨틱 모델 참조 테이블 (실제)**:
- `V05_REGIONAL_NEW_INSTALL` — 신규개통(이사 프록시)
- `M_SCCO_MST` — 행정구역 마스터
- `REGION_APT_RICHGO_MARKET_PRICE_M_H` — 아파트 시세
- `FLOATING_POPULATION_INFO` — 유동인구
- `ASSET_INCOME_INFO` — 자산소득

---

## C6. GIS 데이터 & 지도 렌더링

### 행정구역 경계 데이터 소스

| 소스 | 설명 | 비고 |
|------|------|------|
| **M_SCCO_MST.DISTRICT_GEOM** | Snowflake 내장 GEOGRAPHY 타입 경계 데이터 | **MVP 채택 — 외부 파일 불필요** |
| 통계청 SGIS | 행정동 경계 SHP/GeoJSON (공식) | 고도화 시 더 세밀한 동 단위 필요할 경우 |
| 공공데이터포털 | 행정구역 경계 GeoJSON | 대안 |

> **핵심 변경**: 별도 GeoJSON 파일 다운로드/업로드 불필요. SPH `M_SCCO_MST.DISTRICT_GEOM` (GEOGRAPHY 타입)에 서울 25개 구(467개 법정동) 경계가 내장됨. `ST_ASGEOJSON(DISTRICT_GEOM)` 함수로 pydeck용 GeoJSON 바로 추출.

### GIS 파이프라인 (변경 후)

```
🤖 Claude Code: Snowflake에서 ST_ASGEOJSON(DISTRICT_GEOM) 쿼리
    ↓
🤖 Claude Code: GeoJSON + 이사 수요 지수 병합
    ↓
🤖 Claude Code: pydeck GeoJsonLayer 코드 생성
    ↓
    Streamlit 지도 렌더링 (외부 파일 의존성 없음)
```

### GeoJSON 추출 쿼리

```python
@st.cache_data(ttl=86400)
def get_seoul_geojson_with_demand(year_month):
    query = """
        SELECT
            m.CITY_KOR_NAME AS gu_name,
            m.CITY_CODE,
            ST_ASGEOJSON(m.DISTRICT_GEOM) AS geojson,
            COALESCE(v.OPEN_COUNT, 0) AS open_count,
            COALESCE(v.CONTRACT_COUNT, 0) AS contract_count
        FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
        LEFT JOIN SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL v
            ON m.CITY_KOR_NAME = v.INSTALL_CITY
            AND v.YEAR_MONTH = :1
            AND v.INSTALL_STATE = '서울'
        WHERE m.PROVINCE_CODE = '11'
        GROUP BY 1, 2, 3, 4, 5
    """
    return session.sql(query, params=[year_month]).to_pandas()
```

### Streamlit in Snowflake 환경 제약

| 제약 | 대응 |
|------|------|
| 외부 라이브러리 설치 제한 | `pydeck`은 Streamlit 기본 내장. `folium`은 사용 불가할 수 있음 → `st.pydeck_chart` 우선 |
| 별도 서버 불가 | 모든 로직은 Streamlit 앱 내부에서 실행. API 엔드포인트는 Snowflake UDF/UDTF로 구현 |
| 파일 시스템 접근 제한 | **M_SCCO_MST.DISTRICT_GEOM으로 GeoJSON 외부 파일 의존성 제거** |
| 세션 상태 | `st.session_state`로 관리. 영속적 저장은 Snowflake 테이블 사용 |

### pydeck vs folium 선택

| 항목 | pydeck | folium (st_folium) |
|------|--------|-------------------|
| Streamlit 내장 | O (`st.pydeck_chart`) | X (별도 설치 필요) |
| SiS 호환성 | 높음 | 불확실 — 외부 패키지 의존 |
| choropleth 지원 | GeoJsonLayer | 기본 지원 |
| 인터랙션 | pickable, auto_highlight | 클릭 이벤트 |
| **결론** | **MVP 채택** | Phase 2 검토 |

---

## C7. 작업 구분: Claude Code vs 사용자

| 작업 | 담당 | 설명 |
|------|------|------|
| Streamlit 페이지 코드 작성 | 🤖 Claude Code | `app.py` + 탭별 모듈 코드 생성 |
| 차트/시각화 구현 | 🤖 Claude Code | pydeck, bar_chart, metric, plotly 코드 |
| 레이아웃 & CSS 스타일링 | 🤖 Claude Code | `st.columns`, `st.tabs`, 커스텀 CSS |
| 데이터 쿼리 (Snowpark) | 🤖 Claude Code | SQL 쿼리 (실제 테이블: V05_REGIONAL_NEW_INSTALL, M_SCCO_MST, REGION_APT_RICHGO_MARKET_PRICE_M_H 등) + 캐싱 로직 |
| ROI 계산 로직 | 🤖 Claude Code | 업종별 파라미터 + 계산 함수 |
| GeoJSON 추출 코드 | 🤖 Claude Code | ST_ASGEOJSON(DISTRICT_GEOM) 쿼리 + pydeck 렌더링 (외부 파일 불필요) |
| Streamlit in Snowflake 앱 생성 | 👤 사용자 | Snowsight UI → Streamlit 앱 생성 |
| Snowflake 웨어하우스 설정 | 👤 사용자 | 컴퓨트 리소스 크기 설정 |
| Snowsight에서 앱 실행/테스트 | 👤 사용자 | 브라우저에서 Streamlit 앱 동작 확인 |

> **변경**: 기존 "GIS 데이터 다운로드" / "Snowflake 스테이지 설정" 사용자 작업 항목 제거. M_SCCO_MST.DISTRICT_GEOM으로 외부 GeoJSON 의존성 완전 제거.

---

## C8. 해커톤 발표용 데모 시나리오

### 3분 데모 플로우

**스토리라인**: "코웨이 마케팅 팀장 김과장이 다음 달 이사 수요를 확인하고 캠페인을 기획하는 시나리오"

| 순서 | 시간 | 화면 | 내레이션 |
|------|------|------|---------|
| 1 | 0:00~0:30 | 히트맵 탭 (전체 뷰) | "코웨이 마케팅팀에 다음 달 이사 수요 예측 대시보드가 도착했습니다. 아정당(통신사) 신규개통 데이터로 서울 전역의 이사 수요를 한눈에 봅니다." |
| 2 | 0:30~1:00 | 히트맵 탭 (강남구 클릭) | "강남구를 클릭하면 이사 수요 지수가 나옵니다. 전월 대비 신규개통 23% 상승 — 이사 수요 급증 신호입니다." |
| 3 | 1:00~1:30 | 세그먼트 탭 | "어떤 고객이 이사하는지 봅시다. SPH FACT 데이터(중·영등포·서초 MULTI_SOURCE 3구)로 연령대·성별·소득 분포를 확인합니다. 30대 여성, 중소득 세그먼트가 이사 수요 1위 — 코웨이 정수기 핵심 타겟과 일치합니다. (TELECOM_ONLY 22구는 아정당 경량 프로필로 보완)" |
| 4 | 1:30~2:15 | ROI 계산기 탭 | "이 데이터로 캠페인을 돌리면? 업종 '가전 렌탈', 월 예산 1,000만원 입력. 기존 방식 대비 리드 50% 증가, 전환율 200% 향상, CPA 33% 절감." |
| 5 | 2:15~2:45 | 히트맵 탭 복귀 | "무빙 인텔리전스는 통신 신규개통 데이터로 이사 2~4주 전에 수요를 예측합니다. 한국 최초, APAC 최초입니다." |
| 6 | 2:45~3:00 | 정리 슬라이드 | "감사합니다. B2B SaaS로 Year 1 ARR 13억원, 이사 연관 시장 1.5조원을 공략합니다." |

**데모 핵심 포인트**:
- 실제 작동하는 대시보드를 보여준다 (목업 아님)
- 숫자가 실시간으로 변한다 (필터 조작 시)
- "이사 2~4주 전 예측"이라는 핵심 가치를 반복 강조
- 데이터 출처를 자연스럽게 언급 (통신사 신규개통, SPH 유동인구, RICHGO 시세)

---

## C9. MVP vs 고도화 요약 테이블

| 항목 | MVP (해커톤) | 고도화 (Phase 2+) |
|------|------------|-----------------|
| **탭 구성** | 3탭 (히트맵, 세그먼트, ROI) | 4탭+ (AI 질의 추가) |
| **지도** | pydeck choropleth (서울 25개 구, M_SCCO_MST.DISTRICT_GEOM) | folium 검토, 전국 확대 |
| **이사 수요 프록시** | V05_REGIONAL_NEW_INSTALL.OPEN_COUNT (신규개통) | 다중 시그널 앙상블 |
| **세그먼트 데이터** | SPH MULTI_SOURCE 3구(중·영등포·서초)만 (FLOATING_POPULATION_INFO, ASSET_INCOME_INFO 실존). TELECOM_ONLY 22구는 아정당 경량 프로필 | 수도권→전국 확대 (Marketplace 추가) |
| **아파트 시세** | REGION_APT_RICHGO_MARKET_PRICE_M_H (2012-2024) | 실시간 시세 연동 |
| **필터** | 기간, 구, 수요 등급, 연령/성별 세그먼트 | 커스텀 필터 저장, 알림 설정 |
| **AI 기능** | 없음 | Cortex Analyst 자연어 질의 |
| **인터랙션** | 구 클릭 → 상세 패널 | 드릴다운 3단계 (구→동→단지) |
| **내보내기** | CSV 다운로드 | PDF 리포트, API 연동 |
| **인증** | 없음 (Snowsight 내 앱) | Snowflake 역할 기반 접근 제어 |
| **성능** | `st.cache_data` 기본 캐싱 | 머티리얼라이즈드 뷰, 쿼리 최적화 |
| **스타일** | Streamlit 기본 테마 + 최소 CSS | 브랜드 커스텀 테마 |

---

## C10. 일별 구현 마일스톤 (UI 파트)

| 일자 | 목표 | 산출물 | 완료 기준 |
|------|------|--------|----------|
| **04-06 (일)** | UI 설계 확정 + 프로젝트 구조 생성 | `app.py` 스켈레톤, 탭 구조, 더미 데이터 렌더링 | 3개 탭이 빈 화면이라도 전환 가능 |
| **04-07 (월)** | M_SCCO_MST GeoJSON 추출 + 히트맵 기본 렌더링 | pydeck 지도 + 더미 choropleth 표시 (외부 파일 없이 ST_ASGEOJSON 활용) | 서울 구(區) 경계가 지도에 표시됨 |
| **04-08 (화)** | 히트맵 실데이터 연동 + 필터 동작 | V05_REGIONAL_NEW_INSTALL 쿼리 연동, 필터 작동 | 필터 변경 시 지도 색상 변경됨 |
| **04-09 (수)** | 세그먼트 탭 완성 + ROI 계산기 기본 | 바 차트 + 테이블 + ROI 입력 폼 | 세그먼트 필터 작동, ROI 계산 결과 표시 |
| **04-10 (목)** | ROI 계산기 완성 + 전체 통합 | KPI 카드, Before/After 차트, 스타일링 | 3개 탭 모두 실데이터로 작동 |
| **04-11 (금)** | 데모 리허설 + 버그 수정 + 폴리싱 | 최종 앱, 데모 시나리오 확인 | 3분 데모 플로우 끊김 없이 작동 |
| **04-12 (토)** | 최종 제출 | 제출용 최종 버전 | 해커톤 마감 전 제출 완료 |

### 리스크 & 대응

| 리스크 | 확률 | 대응 |
|--------|------|------|
| pydeck이 SiS에서 동작 안 함 | 중 | `st.map` + 마커 방식으로 폴백. 히트맵 대신 테이블 뷰 제공 |
| DISTRICT_GEOM 데이터 품질 이슈 | 낮음 | M_SCCO_MST 467건 확인됨. 구 단위 25개만 사용하므로 리스크 낮음 |
| V05_REGIONAL_NEW_INSTALL 지역 매핑 불일치 | 중 | INSTALL_CITY(텍스트) ↔ CITY_KOR_NAME 매핑 수동 보정 필요 |
| 데이터 파이프라인 지연 | 높음 | 더미 데이터로 UI 먼저 완성. 실데이터 연동은 04-08 이후 |

---

# Part D. 통합 마일스톤 & 작업 구분

## D1. 통합 일별 마일스톤 (04-06 ~ 04-12)

| 일자 | 데이터/ML | 서빙 레이어 | UI/대시보드 |
|------|----------|-----------|-----------|
| **04-06 (일)** | 데이터 모델 설계 + DDL 작성 | UDF 스켈레톤 | UI 설계 확정 + app.py 스켈레톤 |
| **04-07 (월)** | 👤 Marketplace 4종 구독 확인 + M_SCCO_MST / V05_REGIONAL_NEW_INSTALL 뷰 생성 | PREDICT_MOVE_DEMAND 구현 | ST_ASGEOJSON(DISTRICT_GEOM) 활용 히트맵 기본 |
| **04-08 (화)** | V05_REGIONAL_NEW_INSTALL 전처리 + FLOATING_POPULATION_INFO 통합 마트 | CALC_ROI, GET_SEGMENT 구현 | 히트맵 실데이터 + 필터 |
| **04-09 (수)** | Feature Engineering + OPEN_COUNT lag 분석 | Cortex Analyst YAML 작성 (실제 테이블 참조) + Cortex AI Functions 구현 (AI_COMPLETE, AI_CLASSIFY, AI_AGG) | 세그먼트 탭 + ROI 기본 |
| **04-10 (목)** | ML 모델 학습 + UDF 배포 | Streamlit ↔ UDF 연동 + AI_EMBED 벡터화 + 유사 단지 검색 (REGION_APT_RICHGO_MARKET_PRICE_M_H) | ROI 완성 + 전체 통합 |
| **04-11 (금)** | E2E 통합 테스트 | 통합 테스트 + 데모 리허설 | 데모 리허설 + 폴리싱 |
| **04-12 (토)** | 최종 검증 | 최종 검증 | **제출 마감** |

## D2. 🤖 Claude Code vs 👤 사용자 — 전체 작업 구분

### 👤 사용자가 직접 해야 하는 작업 (Claude Code 불가)

| 작업 | 시점 | 설명 |
|------|------|------|
| Snowflake Trial 계정 생성 | 04-06 | snowflake.com에서 30일 무료 계정 (US West Oregon, us-west-2) |
| 웨어하우스 생성 | 04-06 | `MOVING_INTEL_WH` (X-Small) |
| Marketplace 4종 데이터셋 구독 | 04-07 | Snowsight → Marketplace → "Get" (RICHGO, SPH, 아정당, NextTrade) |
| Cortex AI 기능 활성화 확인 | 04-07 | Snowsight에서 활성화 상태 확인 |
| Streamlit in Snowflake 앱 생성 | 04-09 | Snowsight UI에서 앱 생성 |
| 권한(GRANT) 설정 | 04-07 | UDF/테이블 접근 권한 |
| 모델 학습 실행 확인 | 04-10 | 컴퓨팅 풀 생성 + 실행 |
| Snowsight에서 앱 동작 확인 | 04-10~12 | 브라우저에서 테스트 |
| 최종 제출 | 04-12 | 해커톤 제출 |

> **변경**: 기존 "행정동 경계 GeoJSON 다운로드" / "GeoJSON → Snowflake 스테이지 업로드" 항목 제거. M_SCCO_MST.DISTRICT_GEOM 내장 데이터 활용으로 사용자 GIS 작업 불필요.

### 🤖 Claude Code가 자동화하는 작업

| 작업 | 산출물 |
|------|--------|
| DDL SQL 생성 | 뷰 및 마트 테이블 DDL |
| 뷰 생성 SQL | V05_REGIONAL_NEW_INSTALL, M_SCCO_MST, REGION_APT_RICHGO_MARKET_PRICE_M_H 등 참조 뷰 |
| 데이터 검증 쿼리 | 행수, 기간, 결측 확인 SQL (실제 테이블 기준) |
| Snowpark 전처리 코드 | `build_integrated_mart()` (SPH 3개 테이블 + 아정당 V05 조인) |
| Feature Engineering 코드 | `MOVE_SIGNAL_INDEX` (OPEN_COUNT 기반 정규화), lag 분석 |
| ML 학습 코드 | `train_track_a()` / `train_track_b()` / `walk_forward_split()` (Snowpark ML, Dual-Tier) |
| UDF 코드 3개 | `PREDICT_MOVE_DEMAND`, `CALC_ROI`, `GET_SEGMENT_PROFILE` |
| YAML 시맨틱 모델 | `moving_intelligence_semantic_model.yaml` (V05_REGIONAL_NEW_INSTALL, M_SCCO_MST, REGION_APT_RICHGO_MARKET_PRICE_M_H 참조) |
| Cortex AI Functions SQL | AI_COMPLETE, AI_CLASSIFY, AI_AGG, AI_EMBED 쿼리 + Streamlit 연동 코드 |
| Streamlit 앱 코드 | `app.py` + 탭별 모듈 |
| pydeck 지도 코드 | GeoJsonLayer choropleth (ST_ASGEOJSON(DISTRICT_GEOM) 활용) |
| ROI 계산 로직 | 업종별 파라미터 + 계산 함수 (REGION_APT_RICHGO_MARKET_PRICE_M_H 연동) |

## D3. MVP vs 고도화 전체 요약

| 항목 | MVP (해커톤 04-12 마감) | 고도화 (Phase 2+) |
|------|------------------------|-------------------|
| **데이터** | V05_REGIONAL_NEW_INSTALL(이사 프록시) + SPH 서울 전체 25개 구 + RICHGO(2012-2024) | 수도권→전국 확대 |
| **ML 모델** | Track A LinearRegression(25구, MAPE<25%) / Track B Ridge α=1.0(MULTI_SOURCE 3구, MAPE<20%, XGB 금지) | LSTM/Prophet 앙상블 (MAPE < 10%) |
| **서빙** | Streamlit 내부 UDF 호출 | Snowflake SQL API + External Function |
| **UI** | 3탭 (히트맵, 세그먼트, ROI) | 4탭+ (AI 챗봇 추가) |
| **지도** | pydeck choropleth (서울 25개 구, M_SCCO_MST.DISTRICT_GEOM 내장) | folium 검토, 전국 |
| **AI** | Cortex Analyst 시맨틱 모델 | Cortex Agents 멀티툴 |
| **Cortex AI Functions** | AI_COMPLETE (인사이트), AI_CLASSIFY (등급), AI_AGG (요약), AI_EMBED+VECTOR (유사 단지) | AI_SENTIMENT, AI_TRANSLATE, AI_EXTRACT, AI_REDACT |
| **인증** | Snowflake RBAC | OAuth 2.0 + API Key |
| **검색** | SQL 필터링 | Cortex Search RAG |
| **평가 기준** | MAPE < 20% | MAPE < 10%, 시차 상관 r > 0.7 |

---

## D4. 프로젝트 디렉토리 구조

> dev_spec Part A~D의 산출물을 매핑한 소스코드 디렉토리 구조. 모든 디렉토리에 `.ai.md` 필수.

```
snowflake/
├── AGENTS.md                    레포 전체 목차
├── CLAUDE.md                    불변식·규칙·작업 흐름
├── README.md                    프로젝트 소개
│
├── sql/                         Snowflake SQL 스크립트 (Part A2, B3, B4)
│   ├── ddl/                     DB·스키마·테이블 생성 DDL
│   │   └── 001_create_database_schema.sql   (#16)
│   ├── views/                   Marketplace 연동 뷰 생성 (A2-3)
│   │   ├── 002_richgo_views.sql             RICHGO 뷰 3개
│   │   ├── 003_sph_views.sql                SPH 뷰 3개
│   │   ├── 004_telecom_views.sql            아정당 뷰 2개
│   │   ├── 005_nexttrade_views.sql          NextTrade 뷰 1개
│   │   └── 006_bjd_district_map.sql         BJD↔DISTRICT 매핑 뷰
│   ├── udf/                     UDF·UDTF 정의 (B3)
│   │   ├── predict_move_demand.sql          B3-1
│   │   ├── calc_roi.sql                     B3-2
│   │   └── get_segment_profile.sql          B3-3
│   ├── cortex/                  Cortex AI Functions SQL (B4)
│   │   └── cortex_ai_functions.sql          AI_COMPLETE, AI_CLASSIFY 등
│   ├── validation/              데이터 검증 쿼리 (A2-3 #11)
│   │   └── validate_all_views.sql
│   └── test/                    AC 검증 테스트 쿼리
│       └── test_01_db_schema.sql            (#16)
│
├── src/                         Python 소스 코드
│   ├── pipeline/                Snowpark 전처리 파이프라인 (Part A3)
│   │   ├── __init__.py
│   │   ├── build_mart.py        build_integrated_mart() — A3-3
│   │   ├── region_mapping.py    아정당↔SPH 텍스트 매핑 — A3-4
│   │   └── time_series.py       시계열 월별 집계/정규화 — A3-5
│   ├── features/                Feature Engineering (Part A4)
│   │   ├── __init__.py
│   │   ├── move_signal.py       MOVE_SIGNAL_INDEX — A4-1
│   │   ├── lag_correlation.py   시차 상관분석 — A4-2
│   │   ├── life_attractiveness.py  라이프스타일 매력도 — A4-3
│   │   └── seasonal.py          계절성 피처 — A4-5
│   ├── ml/                      ML 모델 학습·배포 (Part A5)
│   │   ├── __init__.py
│   │   ├── train.py             train_track_a() / train_track_b() / walk_forward_split() — A5-3 Dual-Tier
│   │   └── evaluate.py          모델 평가 (MAPE 등)
│   └── app/                     Streamlit 대시보드 (Part C)
│       ├── app.py               앱 진입점 — C1
│       ├── tabs/                탭별 모듈
│       │   ├── heatmap.py       이사 수요 예측 히트맵 — C2
│       │   ├── segment.py       세그먼트 분석 — C3
│       │   ├── roi.py           ROI 계산기 — C4
│       │   └── ai_query.py      AI 자연어 질의 (고도화) — C5
│       ├── components/          재사용 컴포넌트
│       │   ├── map_renderer.py  pydeck 지도 렌더링 — C6
│       │   └── filters.py       공통 필터 위젯
│       └── utils/               유틸리티
│           ├── snowflake_conn.py  Snowflake 세션 관리
│           └── constants.py       상수 (업종별 ROI 파라미터 등)
│
├── config/                      설정 파일
│   └── semantic_model.yaml      Cortex Analyst 시맨틱 모델 — B5
│
├── tests/                       Python 테스트 (E2E 포함)
│   ├── test_pipeline.py         전처리 파이프라인 테스트
│   ├── test_features.py         Feature Engineering 테스트
│   └── test_app.py              Streamlit 앱 테스트
│
├── docs/                        프로젝트 문서 (SOT)
│   ├── specs/                   기능 명세 + AC
│   ├── background/              배경 리서치
│   ├── whitepaper/              백서
│   ├── onboarding/              환경 설정·기여 가이드
│   └── work/                    이슈별 작업 내역
│       ├── active/              진행 중
│       └── done/                완료
│
└── scripts/                     유틸리티 스크립트
    ├── check_invariants.py      아키텍처 불변식 검증
    └── check_forbidden_files.py 금지 파일 검사
```

### dev_spec 섹션 ↔ 디렉토리 매핑

| dev_spec 섹션 | 디렉토리 | 핵심 산출물 |
|--------------|----------|-----------|
| A2-3 DDL/뷰 | `sql/ddl/`, `sql/views/` | CREATE DB/SCHEMA, 뷰 10개 |
| A3 전처리 | `src/pipeline/` | build_integrated_mart() |
| A4 Feature Engineering | `src/features/` | MOVE_SIGNAL_INDEX, lag 분석 |
| A5 ML 모델 | `src/ml/` | train_track_a()(LinearRegression, 25구), train_track_b()(Ridge α=1.0, MULTI_SOURCE 3구), walk_forward_split() |
| B3 UDF/UDTF | `sql/udf/` | PREDICT_MOVE_DEMAND 등 3개 |
| B4 Cortex AI | `sql/cortex/` | AI_COMPLETE, AI_CLASSIFY 등 |
| B5 Cortex Analyst | `config/` | semantic_model.yaml |
| C1~C5 Streamlit | `src/app/` | app.py + 탭 4개 |
| C6 GIS | `src/app/components/` | map_renderer.py |
| D1 테스트 | `tests/`, `sql/test/` | E2E 통합 테스트 |

### 번호 규칙

- **SQL DDL**: `NNN_설명.sql` (001부터 이슈 순서대로)
- **SQL 뷰**: `NNN_데이터셋_views.sql` (002~006, 이슈별)
- **SQL UDF**: `함수명.sql` (함수명이 곧 파일명)
- **Python**: 모듈명은 snake_case, 기능 단위 분리

---

## 출처

- 무빙 인텔리전스 백서 v1.0 (`docs/whitepaper/v1.0-moving-intelligence.md`) — 섹션 3.4 시스템 아키텍처, 섹션 6 MVP & 로드맵
- 배경 리서치 18건 (`docs/background/`)
- 심사 기준별 점수 극대화 전략 (`docs/background/05_judging-criteria-strategy.md`) — Streamlit 데모 완성도, 비즈니스 임팩트 심사 항목
- 글로벌 Pre-Mover 마케팅 전환율 벤치마크: 이벤트 트리거 캠페인 전환율 일반 대비 200% (백서 섹션 7 출처, `docs/background/13_competitive-landscape.md`)
- Snowflake Marketplace 실제 스키마 레퍼런스 (`.omc/research/actual-schema-reference.md`)
  - RICHGO: `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H` (2012-01~2024-12, 4,356건)
  - SPH: `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA` — M_SCCO_MST 마스터(서울 25개 구 467개 법정동) + FLOATING_POPULATION_INFO·CARD_SALES_INFO·ASSET_INCOME_INFO FACT(MULTI_SOURCE 3구: 중구 11140·영등포구 11560·서초구 11650, 2021-2025) — 해커톤 Marketplace 샘플 실측 (#40 검증)
  - 아정당: `SOUTH_KOREA_TELECOM_SUBSCRIPTION_ANALYTICS__CONTRACTS_MARKETING_AND_CALL_CENTER_INSIGHTS_BY_REGION.TELECOM_INSIGHTS.V05_REGIONAL_NEW_INSTALL` (신규개통 = 이사 프록시, 시/도+시/군/구 단위)
  - SPH M_SCCO_MST.DISTRICT_GEOM (GEOGRAPHY 타입) — 별도 GeoJSON 파일 불필요
- Snowflake Cortex AI Functions 공식 문서: AI_COMPLETE, AI_CLASSIFY, AI_AGG, AI_EMBED 등 (GA, US West Oregon 전체 지원)
- Snowflake Cortex Analyst 공식 문서: Cortex Analyst (GA)
- Snowflake Cortex Agents 공식 문서: Cortex Agents (GA, 2025-11)
- Snowflake Cortex Search 공식 문서: Cortex Search (GA, 2026-03 다중 컬럼 업데이트)
- Snowpark Python UDF 공식 문서: Snowpark Python UDF/UDTF
- Streamlit in Snowflake 공식 문서: Streamlit in Snowflake (GA, 컨테이너 런타임 2026-03) — pydeck 지원, 환경 제약
- 프로젝트 기획서: `docs/whitepaper/v1.0-moving-intelligence.md`

---

## 변경 이력

> ⚠️ 이 파일은 **누적 이력**이다. 한 항목에 여러 엔트리가 있을 경우 **가장 아래(가장 최신) 엔트리가 현재 사실**이다. 과거 엔트리는 추적·디버깅 목적으로 보존된다.

### 2026-04-08 — #40 (#21 Snowflake 실데이터 검증 기반 12건+α 정정)

**배경**: #21 PR #41 머지로 `MART_MOVE_ANALYSIS` Dual-Tier 마트 확정 (`MULTI_SOURCE` 3구 / `TELECOM_ONLY` 22구). dev_spec 원본은 #20 cycle에서 잘못 "SPH 25구로 회귀" 한 상태였음. Snowflake Python connector 직검증 + PR #41 코드 직독 + 후속 이슈 body 검토 기반으로 다음 항목 정정.

**검증 출처**: `.omc/research/snowflake-ground-truth.md` (Snowflake 실쿼리 결과 + PR #41 `pipelines/preprocessing.py` 직독 + open 이슈 #22~#43 body 키워드 대조)

**핵심 정정 12건 + 추가 잔여 8건**:

| # | 항목 | 변경 전 (요약) | 변경 후 (요약) |
|---|------|---------------|---------------|
| 1 | INSTALL_STATE/RICHGO SD 필터 | `'서울특별시'` (3곳: A3-3 540, A3-4 629, B2 2292/2550) | `'서울'` (V_TELECOM_NEW_INSTALL.INSTALL_STATE, V_RICHGO_MARKET_PRICE.SD 실값) |
| 2 | 통합마트 테이블명 | `INTEGRATED_MART` (4곳: A3-3 600, A5-3 다이어그램 882, A5-3 코드 904, A7 마일스톤 976) | `MART_MOVE_ANALYSIS` (PR #41 머지 결과) |
| 3 | SPH 커버리지 다수 위치 | "SPH 서울 전체 25개 구 467개 동" | "M_SCCO_MST 마스터 25구 / FACT(FLOATING/CARD/ASSET) MULTI_SOURCE 3구(중·영등포·서초)만" |
| 4 | A3-3 통합마트 코드 | 동(DISTRICT_CODE) 단위 + YEAR_MONTH 변환 누락 | 구(CITY_CODE) 단위 + `TO_CHAR(YYYYMMDD,'YYYYMM')` + `MULTI_SOURCE_CITIES` 상수 + DATA_TIER 컬럼 (PR #41 동기화) |
| 5 | 행정동/법정동 표기 | "467개 동" (행정동 암시) | "467개 법정동(BJD)" (M_SCCO_MST.DISTRICT_CODE 8자리는 BJD) |
| 6 | A4-1 MOVE_SIGNAL_INDEX | 단일 산출식 (4종 가중합) | `CASE WHEN DATA_TIER='TELECOM_ONLY' THEN norm(OPEN_COUNT) WHEN 'MULTI_SOURCE' THEN 4종 융합 END` + 검증 기준에 샘플 한계 주석 |
| 7 | A4-1 validate_move_signals | SPH FACT 직참조 (25구 가정) | `MART_MOVE_ANALYSIS.filter(DATA_TIER=='MULTI_SOURCE')` |
| 8 | A5-1 MVP 학습 계획 | 단일 표 (XGBRegressor, MAPE<20%) | Track A(25구 경량 LinearRegression, MAPE<25%) + Track B(MULTI_SOURCE 3구 풀 Ridge α=1.0, MAPE<20%, **XGB 금지**) |
| 9 | A5-3 학습 파이프라인 | `train_and_deploy()` + `random_split` | `train_track_a()` + `train_track_b()` + `walk_forward_split(train_months=28, test_months=6)` + 타겟 파생 `F.lead("OPEN_COUNT", 1)` + 서비스 2개 분리 |
| 10 | A6 MVP vs 고도화 표 | 단일 모델/평가 | Track A/B 분리 (데이터 범위·핵심 모델·데이터 조인·평가 기준 행 수정) |
| 11 | B3-0 UDF 커버리지 매트릭스 | 없음 | B3-1 직전 신규 서브섹션 삽입 (Tier별 UDF 동작 매트릭스) |
| 12 | B3-1 PREDICT_MOVE_DEMAND | `district_code VARCHAR` 인자 + 단일 모델 | 인자명 `city_code` (5자리 CITY_CODE) rename + RETURNS에 `data_tier`/`confidence` 추가 + 내부 로직 0단계(Tier 감지) 추가 |
| 13 | B3-2 CALC_ROI | RETURNS 단일 | `tier`/`confidence` 컬럼 추가 + Tier 분기 |
| 14 | B3-3 GET_SEGMENT_PROFILE 허위 문장 | "필터: DISTRICT_CODE = district_code (서울 25개 구 모두 가능)" | "필터: CITY_CODE = city_code. SPH FACT는 MULTI_SOURCE 3구만 실존, TELECOM_ONLY 22구는 아정당 경량 프로필" |
| 15 | C4 ROI 계산기 | 단일 로직 | Tier 배지 + `query_mart_tier()` 분기 + `get_apt_price_by_region()` empty fallback + 데이터 근거 Tier 경고 |
| 16 | C3 세그먼트 분석 | "SPH 25개 구 전체" | "MULTI_SOURCE 3구 풀 / TELECOM_ONLY 22구 경량" |
| 17 | C7 발표 스크립트 | "SPH 데이터로 25구 전체 분포" | "SPH FACT MULTI_SOURCE 3구 + TELECOM_ONLY 22구 경량" |
| 18 | A8 디렉토리 매핑 | `train_and_deploy()`, XGBRegressor | `train_track_a/b()`, `walk_forward_split()` |
| 19 | A6+A8 ML 모델 행 | XGBRegressor (MAPE<20%) | Track A LinearRegression / Track B Ridge α=1.0 |
| 20 | 출처 SPH 설명 | "서울 전체 25개 구" | "마스터 25구 / FACT MULTI_SOURCE 3구" |

**중복/이력 처리**:
- 항목 2 (INTEGRATED_MART): 이슈 본문은 line 600만 명시했으나 882·904·976에도 잔존 → 4곳 모두 정정
- 항목 14 (line 1491 B3-3 허위 문장): 이슈 본문 SPH 커버리지 라인 목록 누락 → #40 작업 시 추가 발견 후 정정
- **#20 자기 정정 문구 보존**: 1165, 1193, 1523, 1779, 2342 등의 "기존 3개 구 한정 오류 수정됨" 문구는 2026-04-07 #20에서 잘못 25구로 회귀시킨 흔적. **삭제하지 않고** "→ 2026-04-08 #40 #21 Snowflake 검증으로 MULTI_SOURCE 3구로 재롤백" 형식으로 이력 보존

**유지 항목** (정정 대상 아님):
- line 134, 136 (#20 변경 이력 — 보존)
- line 1230, 1238 (JSON 응답 예시 `province` 필드 — '서울특별시'는 풀네임 명시 의도)
- line 1793, 1826 (Cortex Analyst YAML 컬럼 description "예: 서울특별시" — 컬럼 의미 설명)
- line 898 (`XGBRegressor 금지` — 의도적 금지 명시)

**후속 이슈 동기화 (Task #4)**:
#40 작업 범위에 backlog 이슈 #22, #23, #25, #26, #28, #29, #42 body 정정 포함. 상세는 `.omc/research/snowflake-ground-truth.md` 섹션 9 참조.

### 2026-04-07 — #20 (V_BJD_DISTRICT_MAP 매핑 뷰)

(line 132~136 #20 변경 이력 참조 — 동/구 2단계 매핑 + SD 필터 수정)
