-- =============================================================================
-- test_08_predict_udf.sql — PREDICT_MOVE_DEMAND UDF 검증
-- Issue #23 TC-01~TC-04
-- =============================================================================

-- ── TC-01: UDF 존재 확인 ────────────────────────────────────────────────────
-- EXPECTED: 1 row (PREDICT_MOVE_DEMAND 함수가 ANALYTICS 스키마에 존재)
SHOW USER FUNCTIONS LIKE 'PREDICT_MOVE_DEMAND' IN SCHEMA MOVING_INTEL.ANALYTICS;


-- ── TC-02: 유효한 스코어 반환 ───────────────────────────────────────────────
-- EXPECTED: 0 <= score <= 100  (NULL 불허)
-- 주의: INSTALL_STATE 실값 = '서울' (NOT '서울특별시') — #40 검증 결과
SELECT MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND('서울', '강남구') AS score;


-- ── TC-03: 25구 전체 스코어 검증 ───────────────────────────────────────────
-- SQL UDF(테이블 접근)는 GROUP BY 컨텍스트에서 correlated subquery 제한 있음
-- → PREDICTED_MOVE_DEMAND 테이블을 직접 조회해 25구 전체 스코어 검증
-- EXPECTED: 25 rows, 모든 score BETWEEN 0 AND 100
SELECT CITY_KOR_NAME, DEMAND_SCORE AS score
FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
ORDER BY score DESC;


-- ── TC-04: 존재하지 않는 지역 → NULL (graceful 처리) ─────────────────────────
-- EXPECTED: score IS NULL  (에러 없이 NULL 반환)
SELECT MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND('서울', '없는구') AS score;


-- ── TC-보조: 스코어 분포 검증 ───────────────────────────────────────────────
-- 25구 분포 — min/max/avg 확인 (min≈0, max≈100 기대)
SELECT
    COUNT(*)           AS total_cities,
    MIN(score)         AS min_score,
    MAX(score)         AS max_score,
    AVG(score)         AS avg_score,
    COUNT(CASE WHEN score BETWEEN 0 AND 100 THEN 1 END) AS valid_count,
    COUNT(CASE WHEN score IS NULL THEN 1 END)           AS null_count
FROM (
    SELECT MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND('서울', m.CITY_KOR_NAME) AS score
    FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER m
    WHERE m.PROVINCE_CODE = '11'
    GROUP BY m.CITY_KOR_NAME
);
