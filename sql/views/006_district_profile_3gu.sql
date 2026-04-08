-- ============================================================
-- 006_district_profile_3gu.sql
-- 이슈 #43 — 3구 권역 프로파일 카드 데이터셋 뷰 생성
-- 의존성: V_SPH_FLOATING_POP, V_SPH_ASSET_INCOME, V_SPH_CARD_SALES,
--         V_RICHGO_MARKET_PRICE, V_BJD_DISTRICT_MAP,
--         V_TELECOM_DISTRICT_MAPPED
-- 멱등성: CREATE OR REPLACE — 반복 실행 안전
-- ============================================================

USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

CREATE OR REPLACE VIEW V_DISTRICT_PROFILE_3GU
  COMMENT = '3구 권역 프로파일 카드 (중구·영등포구·서초구) — 인구·소비·시세·통신 집계 (#43)'
AS
WITH

-- PROFILE_TAG 수동 매핑 (3구 고정값, 통계 도출 불가 — 샘플 부족)
tag_map AS (
    SELECT '11140' AS CITY_CODE, '중구'    AS CITY_KOR_NAME, '도심 오피스·상업'   AS PROFILE_TAG
    UNION ALL
    SELECT '11560',              '영등포구',                 '금융·상업·주거 혼합'
    UNION ALL
    SELECT '11650',              '서초구',                  '고급 주거·학군지'
),

-- 유동인구 집계: 22개월(202303~202412) 평균 거주·직장·방문 인구
pop_agg AS (
    SELECT
        CITY_CODE,
        AVG(RESIDENTIAL_POPULATION) AS AVG_RESIDENTIAL_POP,
        AVG(
            (WORKING_POPULATION + VISITING_POPULATION)
            / NULLIF(RESIDENTIAL_POPULATION, 0)
        ) AS WORKING_VISIT_RATIO
    FROM V_SPH_FLOATING_POP
    WHERE CITY_CODE IN ('11140', '11560', '11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
),

-- 자산소득 집계: 22개월 평균 소득·자산
income_agg AS (
    SELECT
        CITY_CODE,
        AVG(AVERAGE_INCOME)       AS AVG_INCOME,
        AVG(AVERAGE_ASSET_AMOUNT) AS AVG_ASSET
    FROM V_SPH_ASSET_INCOME
    WHERE CITY_CODE IN ('11140', '11560', '11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
),

-- 카드매출 집계: 전자제품·가구 매출 비중 (22개월 누적 SUM → 비율)
card_agg AS (
    SELECT
        CITY_CODE,
        SUM(ELECTRONICS_FURNITURE_SALES) / NULLIF(SUM(TOTAL_SALES), 0)
            AS ELECTRONICS_FURNITURE_SHARE
    FROM V_SPH_CARD_SALES
    WHERE CITY_CODE IN ('11140', '11560', '11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
),

-- 아파트 시세 집계: BJD→CITY 매핑 후 22개월 평균 매매·전세 시세
richgo_agg AS (
    SELECT
        b.CITY_CODE,
        AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG)    AS AVG_MEME_PRICE,
        AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG)  AS AVG_JEONSE_PRICE,
        COUNT(DISTINCT r.BJD_CODE)             AS BJD_COUNT
    FROM V_RICHGO_MARKET_PRICE r
    JOIN V_BJD_DISTRICT_MAP    b ON r.BJD_CODE = b.BJD_CODE
    WHERE b.CITY_CODE IN ('11140', '11560', '11650')
      AND r.YYYYMMDD BETWEEN DATE '2023-03-01' AND DATE '2024-12-31'
    GROUP BY b.CITY_CODE
),

-- 통신 신규개통 집계: 동일(CITY_CODE, MONTH)에 다중 행 가능 → 월 SUM 후 구 AVG
telecom_agg AS (
    SELECT
        CITY_CODE,
        AVG(monthly_open) AS OPEN_COUNT_MONTHLY_AVG
    FROM (
        SELECT
            CITY_CODE,
            STANDARD_YEAR_MONTH,
            SUM(OPEN_COUNT) AS monthly_open
        FROM V_TELECOM_DISTRICT_MAPPED
        WHERE CITY_CODE IN ('11140', '11560', '11650')
          AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
        GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    )
    GROUP BY CITY_CODE
)

SELECT
    t.CITY_CODE,
    t.CITY_KOR_NAME,
    t.PROFILE_TAG,
    p.AVG_RESIDENTIAL_POP,
    p.WORKING_VISIT_RATIO,
    i.AVG_INCOME,
    i.AVG_ASSET,
    c.ELECTRONICS_FURNITURE_SHARE,
    r.AVG_MEME_PRICE,
    r.AVG_JEONSE_PRICE,
    (r.AVG_MEME_PRICE - r.AVG_JEONSE_PRICE)
        / NULLIF(r.AVG_MEME_PRICE, 0)          AS GAP_RATIO,
    tl.OPEN_COUNT_MONTHLY_AVG,
    r.BJD_COUNT
FROM tag_map       t
LEFT JOIN pop_agg     p  USING (CITY_CODE)
LEFT JOIN income_agg  i  USING (CITY_CODE)
LEFT JOIN card_agg    c  USING (CITY_CODE)
LEFT JOIN richgo_agg  r  USING (CITY_CODE)
LEFT JOIN telecom_agg tl USING (CITY_CODE)
ORDER BY t.CITY_CODE;
