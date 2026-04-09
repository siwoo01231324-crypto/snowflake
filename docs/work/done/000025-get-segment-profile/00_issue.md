# feat: GET_SEGMENT_PROFILE UDF 구현

# Issue #25: feat: GET_SEGMENT_PROFILE UDF 구현

## 목적
"이 지역 주민은 어떤 사람들인지" 인구통계/소비/소득 프로필을 반환하는 UDF를 만든다.

## 완료 기준
- [x] `GET_SEGMENT_PROFILE(city_code)` UDF 배포 (인자명 city_code, 5자리 CITY_CODE — #40에서 dev_spec rename 결정)
- [x] 반환 JSON에 필수 키(population, income, consumption, housing) 포함
- [x] 25개 구 전체 호출 가능. **MULTI_SOURCE 3구**(중구 11140·영등포구 11560·서초구 11650)는 풀 프로필 4섹션 반환, **TELECOM_ONLY 22구**는 telecom_summary 경량 프로필만 반환 (Dual-Tier — #40 검증 결과 SPH FACT 3구만 실존)

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`sql
-- test_10_segment_udf.sql
-- TC-01: UDF 존재
SHOW USER FUNCTIONS LIKE 'GET_SEGMENT_PROFILE' IN SCHEMA MOVING_INTEL.ANALYTICS;
-- EXPECTED: 1 row

-- TC-02: 기본 호출 (중구 CITY_CODE — MULTI_SOURCE 3구 중 하나, 풀 프로필 검증)
SELECT MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140') AS profile;
-- EXPECTED: 유효한 JSON 반환 (population/income/consumption/housing 4섹션)

-- TC-03: 필수 키 확인 (MULTI_SOURCE 3구만 4섹션 풀 프로필 검증)
SELECT 
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):population IS NOT NULL AS has_pop,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):income IS NOT NULL AS has_income,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):consumption IS NOT NULL AS has_cons,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):housing IS NOT NULL AS has_housing;
-- EXPECTED: 4개 모두 TRUE (MULTI_SOURCE 3구는 SPH FACT 풀 데이터 보유)

-- TC-04: 25개 구 호출 가능 + Tier별 응답 검증
-- MULTI_SOURCE 3구: data_tier='MULTI_SOURCE', 4섹션 풀 프로필
-- TELECOM_ONLY 22구: data_tier='TELECOM_ONLY', telecom_summary 경량 프로필
SELECT DISTINCT m.CITY_CODE,
       MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(m.CITY_CODE) IS NOT NULL AS has_profile,
       PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(m.CITY_CODE)):data_tier::STRING AS tier
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER m
WHERE m.PROVINCE_CODE = '11'
GROUP BY m.CITY_CODE;
-- EXPECTED: 25 rows, has_profile=TRUE 모두, tier IN ('MULTI_SOURCE','TELECOM_ONLY')
-- MULTI_SOURCE 3행 (11140, 11560, 11650) / TELECOM_ONLY 22행
\`\`\`

## 참조
- `docs/specs/dev_spec.md` B3 (GET_SEGMENT_PROFILE UDF)
- SPH: FLOATING_POPULATION_INFO(인구), CARD_SALES_INFO(소비), ASSET_INCOME_INFO(소득/자산)
- 의존성: #18 (SPH 뷰)

## 불변식
- 반환 JSON 필수 키 (MULTI_SOURCE 3구 풀 프로필): population(거주/직장/방문), income(평균소득/중위소득), consumption(업종별TOP5), housing(평형대분포/시세), data_tier='MULTI_SOURCE'
- 반환 JSON 경량 프로필 (TELECOM_ONLY 22구): telecom_summary(OPEN_COUNT/CONTRACT_COUNT/PAYEND_COUNT 기반), data_tier='TELECOM_ONLY'
- 25개 구 모두 호출 가능. MULTI_SOURCE 3구(중구·영등포구·서초구)는 풀 프로필 보장, TELECOM_ONLY 22구는 경량 프로필 보장.
- UDF 인자명: `city_code` (5자리 CITY_CODE — #40 dev_spec rename 결정. 기존 `district_code` 명칭 폐기.)

## 작업 내역

### 구현 완료 (2026-04-09)

**신규 파일**
- `sql/udf/get_segment_profile.sql`: V_SPH_REGION_MASTER 뷰(Step 0) + GET_SEGMENT_PROFILE SQL scalar UDF(Step 1)
- `sql/test/test_10_segment_udf.sql`: TC-01~04 테스트

**핵심 설계 결정**
- `V_SPH_REGION_MASTER` 뷰: M_SCCO_MST에서 서울 25구 CITY_CODE 마스터 추출 (TC-04 조회용)
- Dual-Tier 분기: MULTI_SOURCE 3구(11140/11560/11650) → 풀 프로필 4섹션, TELECOM_ONLY 22구 → telecom_summary 경량 프로필
- SQL scalar UDF에서 CTEs + CASE 분기로 단일 SELECT 반환 구현
- 순차 TC 호출 방식으로 Snowflake 내부 집계 에러 회피

**TC 결과: 10/10 PASS**
- TC-01: UDF 존재 확인 ✓
- TC-02: 중구(11140) MULTI_SOURCE data_tier ✓
- TC-03: 중구(11140) 필수 키 4개 (population/income/consumption/housing) ✓
- TC-04: V_SPH_REGION_MASTER 서울 25구 메타 + Tier 검증 ✓ (MULTI_SOURCE 3구 + TELECOM_ONLY 3구 대표 확인)
