-- =============================================================================
-- test_09_roi_udf.sql — CALC_ROI UDF 테스트 (TC-01 ~ TC-04)
-- Issue #24 / dev_spec B3-2
-- =============================================================================

-- ── TC-01: UDF 존재 확인 ─────────────────────────────────────────────────────
-- EXPECTED: 1 row (CALC_ROI 함수가 MOVING_INTEL.ANALYTICS 스키마에 존재)
SHOW USER FUNCTIONS LIKE 'CALC_ROI' IN SCHEMA MOVING_INTEL.ANALYTICS;

-- ── TC-02: 기본 호출 — 강남구(11680), 1억 예산, 가전·가구 업종 ──────────────
-- EXPECTED: roi_pct > 0 (양수 ROI)
SELECT
    MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE') AS roi_raw,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE')):roi_pct::FLOAT AS roi_pct,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE')):roi_pct::FLOAT > 0 AS roi_is_positive;
-- ASSERTION: roi_is_positive = TRUE

-- ── TC-03: 반환 구조 확인 — JSON 키 존재 검증 ───────────────────────────────
-- EXPECTED: roi_pct, estimated_revenue, avg_price_pyeong 키 모두 존재 (NOT NULL)
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE')) AS result,
    result:roi_pct               IS NOT NULL AS has_roi_pct,
    result:estimated_revenue     IS NOT NULL AS has_estimated_revenue,
    result:avg_price_pyeong      IS NOT NULL AS has_avg_price_pyeong,
    result:data_tier::VARCHAR                AS data_tier,
    result:confidence::VARCHAR               AS confidence;
-- ASSERTION: has_roi_pct = TRUE, has_estimated_revenue = TRUE, has_avg_price_pyeong = TRUE

-- ── TC-04: 존재하지 않는 지역 → graceful 처리 ───────────────────────────────
-- EXPECTED: NULL 또는 에러 메시지 JSON (에러 키 포함 또는 roi_pct IS NULL)
SELECT
    MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000, 'FOOD') AS roi_raw,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000, 'FOOD')) AS result,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000, 'FOOD')):roi_pct IS NULL AS roi_pct_is_null,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000, 'FOOD')):error IS NOT NULL AS has_error_key;
-- ASSERTION: roi_pct_is_null = TRUE OR has_error_key = TRUE

-- ── TC-05 (보조): 여러 업종 ROI 비교 ────────────────────────────────────────
-- EXPECTED: 각 업종별 ROI가 반환되고 FOOD(3%) > ELECTRONICS_FURNITURE(1.8%) 순서
SELECT
    industry,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, industry)):roi_pct::FLOAT AS roi_pct,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, industry)):estimated_revenue::FLOAT AS estimated_revenue
FROM (VALUES ('FOOD'), ('ELECTRONICS_FURNITURE'), ('EDUCATION_ACADEMY'), ('HOME_LIFE_SERVICE')) v(industry)
ORDER BY roi_pct DESC;
