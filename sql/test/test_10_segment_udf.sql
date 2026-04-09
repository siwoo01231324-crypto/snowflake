-- =============================================================================
-- test_10_segment_udf.sql
-- GET_SEGMENT_PROFILE UDF 테스트 (TC-01 ~ TC-04)
-- Issue #25 / dev_spec B3-3
-- =============================================================================

-- TC-01: UDF 존재 확인
-- EXPECTED: 1 row
SHOW USER FUNCTIONS LIKE 'GET_SEGMENT_PROFILE' IN SCHEMA MOVING_INTEL.ANALYTICS;

-- TC-02: MULTI_SOURCE 3구 호출 — 중구 (11140)
-- EXPECTED: 유효한 JSON (population/income/consumption/housing 4섹션 포함)
SELECT MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140') AS profile;

-- TC-03: 필수 키 4개 존재 확인 (중구 11140)
-- EXPECTED: has_pop=TRUE, has_income=TRUE, has_cons=TRUE, has_housing=TRUE
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):population   IS NOT NULL AS has_pop,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):income        IS NOT NULL AS has_income,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):consumption   IS NOT NULL AS has_cons,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):housing       IS NOT NULL AS has_housing;

-- TC-04: 서울 25개 구 전체 + Tier 검증
-- EXPECTED: 25 rows
--   data_tier = 'MULTI_SOURCE'  → 3행 (11140 중구, 11560 영등포구, 11650 서초구)
--   data_tier = 'TELECOM_ONLY'  → 22행 (나머지)
SELECT
    m.CITY_CODE,
    MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(m.CITY_CODE) IS NOT NULL       AS has_profile,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(m.CITY_CODE)):data_tier::STRING AS tier
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER m
WHERE m.PROVINCE_CODE = '11'
GROUP BY m.CITY_CODE
ORDER BY m.CITY_CODE;
