-- ============================================================
-- 005_telecom_district_mapped.sql
-- 아정당 지역명 → SPH 시군구 코드 매핑 뷰 생성
-- 이슈: #21 (feat: 통합 마트 뷰 생성)
-- 의존성: V_TELECOM_NEW_INSTALL (#19), M_SCCO_MST (SPH Marketplace)
-- 멱등성: CREATE OR REPLACE — 반복 실행 안전
-- ============================================================

-- Step 0: 컨텍스트 설정
USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- Step 1: V_TELECOM_DISTRICT_MAPPED — 아정당 지역명 → SPH 시군구 코드 매핑
CREATE OR REPLACE VIEW V_TELECOM_DISTRICT_MAPPED
  COMMENT = '아정당 지역명 → SPH 시군구 코드 매핑 (서울 25개 구) (#21)'
AS
SELECT
    t.YEAR_MONTH,
    TO_CHAR(t.YEAR_MONTH, 'YYYYMM') AS STANDARD_YEAR_MONTH,
    t.INSTALL_STATE,
    t.INSTALL_CITY,
    t.CONTRACT_COUNT,
    t.OPEN_COUNT,
    t.PAYEND_COUNT,
    t.BUNDLE_COUNT,
    t.STANDALONE_COUNT,
    t.AVG_NET_SALES,
    m.CITY_CODE,
    m.PROVINCE_CODE
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL t
LEFT JOIN (
    SELECT DISTINCT PROVINCE_CODE, CITY_CODE, CITY_KOR_NAME
    FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
) m ON t.INSTALL_CITY = m.CITY_KOR_NAME
WHERE t.INSTALL_STATE = '서울';
