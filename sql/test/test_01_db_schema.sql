-- ============================================================
-- test_01_db_schema.sql
-- DB/스키마/웨어하우스 검증 쿼리 (이슈 #16 AC 검증)
-- ============================================================

-- TC-01: 데이터베이스 존재 확인
SELECT COUNT(*) AS db_exists
FROM INFORMATION_SCHEMA.DATABASES
WHERE DATABASE_NAME = 'MOVING_INTEL';
-- EXPECTED: db_exists = 1

-- TC-02: 스키마 존재 확인
SHOW SCHEMAS IN DATABASE MOVING_INTEL;
-- EXPECTED: ANALYTICS 스키마가 목록에 존재

-- TC-03: 웨어하우스 접근 확인
SELECT CURRENT_WAREHOUSE();
-- EXPECTED: MOVING_INTEL_WH

-- TC-04: 스키마 컨텍스트 전환 가능 확인
USE SCHEMA MOVING_INTEL.ANALYTICS;
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
-- EXPECTED: MOVING_INTEL, ANALYTICS

-- TC-05: Marketplace 크로스 DB 접근 확인 (RICHGO)
SELECT COUNT(*) AS richgo_rows
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H
LIMIT 1;
-- EXPECTED: richgo_rows >= 1

-- TC-06: Marketplace 크로스 DB 접근 확인 (SPH)
SELECT COUNT(*) AS sph_rows
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO
LIMIT 1;
-- EXPECTED: sph_rows >= 1
