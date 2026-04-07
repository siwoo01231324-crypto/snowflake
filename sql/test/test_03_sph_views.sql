-- ============================================================
-- test_03_sph_views.sql
-- SPH Marketplace 참조 뷰 4개 검증 쿼리 (이슈 #18 AC 검증)
-- ============================================================

-- TC-01: 유동인구 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP;
-- EXPECTED: cnt = 2577120

-- TC-02: 카드매출 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES;
-- EXPECTED: cnt = 6208957

-- TC-03: 자산소득 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME;
-- EXPECTED: cnt = 269159

-- TC-04: 행정구역 마스터 — 25개 구 확인
SELECT COUNT(DISTINCT CITY_CODE) AS gu_count, COUNT(*) AS dong_count
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER;
-- EXPECTED: gu_count = 25, dong_count = 467

-- TC-05: DISTRICT_GEOM NOT NULL 확인
SELECT COUNT(*) AS null_geom
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER
WHERE DISTRICT_GEOM IS NULL;
-- EXPECTED: null_geom = 0

-- TC-06: GeoJSON 추출 가능 확인
SELECT ST_ASGEOJSON(DISTRICT_GEOM) AS geojson
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER LIMIT 1;
-- EXPECTED: 유효한 GeoJSON 문자열 반환

-- TC-07: 날짜 범위 확인
SELECT MIN(STANDARD_YEAR_MONTH) AS min_ym, MAX(STANDARD_YEAR_MONTH) AS max_ym
FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP;
-- EXPECTED: min_ym = '202101', max_ym = '202512'
