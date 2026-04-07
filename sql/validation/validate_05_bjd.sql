-- ============================================================
-- validate_05_bjd.sql
-- V_BJD_DISTRICT_MAP 데이터 정합성 검증
-- ============================================================

-- 1. 기본 통계
SELECT
    'V_BJD_DISTRICT_MAP' AS view_name,
    COUNT(*) AS row_cnt,
    COUNT(DISTINCT BJD_CODE_8) AS distinct_prefix,
    COUNT(DISTINCT BJD_CODE) AS distinct_bjd_code,
    COUNT(DISTINCT DISTRICT_CODE) AS distinct_district
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP;

-- 2. 구별 커버리지 상세
SELECT
    m.CITY_KOR_NAME,
    COUNT(DISTINCT m.BJD_CODE) AS bjd_count,
    COUNT(DISTINCT m.DISTRICT_CODE) AS district_count
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m
GROUP BY m.CITY_KOR_NAME
ORDER BY bjd_count DESC;

-- 3. 미매핑 BJD_CODE 확인 (서울 내)
SELECT COUNT(DISTINCT r.BJD_CODE) AS unmapped_bjd
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
WHERE NOT EXISTS (
    SELECT 1 FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m
    WHERE r.BJD_CODE = m.BJD_CODE
  );
-- EXPECTED: 0 (100% 커버리지)
