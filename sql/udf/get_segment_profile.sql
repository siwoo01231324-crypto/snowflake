-- =============================================================================
-- GET_SEGMENT_PROFILE(city_code VARCHAR) -> VARCHAR (JSON)
-- 구(시군구) 세그먼트 프로파일 JSON 반환
-- Issue #25 / dev_spec B3-3
--
-- Dual-Tier 분기:
--   MULTI_SOURCE  (중구 11140 · 영등포구 11560 · 서초구 11650)
--     → 4섹션 풀 프로필 반환
--       population (거주/직장/방문인구)
--       income     (평균소득/중위소득)
--       consumption (업종별 TOP5 카드매출)
--       housing    (평당 매매가/전세가)
--       data_tier  = 'MULTI_SOURCE'
--
--   TELECOM_ONLY (나머지 22구)
--     → telecom_summary 경량 프로필만 반환
--       data_tier  = 'TELECOM_ONLY'
--
-- 인자:
--   city_code : 5자리 CITY_CODE (예: '11140')
--
-- 참조 뷰:
--   V_SPH_REGION_MASTER   — 구 마스터 (M_SCCO_MST 기반, CITY_CODE 단위)
--   V_SPH_FLOATING_POP    — 유동인구 (MULTI_SOURCE 3구만 실존)
--   V_SPH_CARD_SALES      — 카드매출 (MULTI_SOURCE 3구만 실존)
--   V_SPH_ASSET_INCOME    — 자산소득 (MULTI_SOURCE 3구만 실존)
--   V_RICHGO_MARKET_PRICE — 아파트 시세 (SGG 텍스트 매핑)
-- =============================================================================

-- ── Step 0: V_SPH_REGION_MASTER 뷰 (TC-04 조회용) ──────────────────────────
-- M_SCCO_MST에서 CITY_CODE 단위 구 마스터를 추출한다.
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER AS
SELECT DISTINCT
    PROVINCE_CODE,
    CITY_CODE,
    CITY_KOR_NAME
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST;

-- ── Step 1: GET_SEGMENT_PROFILE UDF ─────────────────────────────────────────
CREATE OR REPLACE FUNCTION MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(
    city_code VARCHAR   -- 5자리 CITY_CODE (예: '11140')
)
RETURNS VARCHAR        -- JSON 문자열
AS
$$
WITH
-- 1) MULTI_SOURCE 여부 판정
tier AS (
    SELECT
        IFF(city_code IN ('11140', '11560', '11650'),
            'MULTI_SOURCE',
            'TELECOM_ONLY') AS data_tier
),

-- 2) 구 이름 조회
city_meta AS (
    SELECT DISTINCT CITY_CODE, CITY_KOR_NAME
    FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
    WHERE CITY_CODE = city_code
    LIMIT 1
),

-- 3) 유동인구 집계 (MULTI_SOURCE 3구만 실존 데이터)
pop_agg AS (
    SELECT
        AVG(RESIDENTIAL_POPULATION) AS avg_residential,
        AVG(WORKING_POPULATION)     AS avg_working,
        AVG(VISITING_POPULATION)    AS avg_visiting
    FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP
    WHERE CITY_CODE = city_code
),

-- 4) 자산소득 집계 (MULTI_SOURCE 3구만 실존 데이터)
income_agg AS (
    SELECT
        AVG(AVERAGE_INCOME)           AS avg_income,
        AVG(MEDIAN_INCOME)            AS median_income,
        AVG(AVERAGE_HOUSEHOLD_INCOME) AS avg_household_income,
        AVG(AVERAGE_ASSET_AMOUNT)     AS avg_asset_amount,
        AVG(RATE_HIGHEND)             AS rate_highend
    FROM MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME
    WHERE CITY_CODE = city_code
),

-- 5) 업종별 카드매출 TOP5 (MULTI_SOURCE 3구만 실존 데이터)
card_agg AS (
    SELECT
        AVG(FOOD_SALES)               AS food_sales,
        AVG(COFFEE_SALES)             AS coffee_sales,
        AVG(BEAUTY_SALES)             AS beauty_sales,
        AVG(MEDICAL_SALES)            AS medical_sales,
        AVG(EDUCATION_ACADEMY_SALES)  AS education_sales,
        AVG(HOME_LIFE_SERVICE_SALES)  AS home_life_sales,
        AVG(TOTAL_SALES)              AS total_sales
    FROM MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES
    WHERE CITY_CODE = city_code
),

-- 6) 아파트 시세 집계 (SGG 텍스트 매핑, MULTI_SOURCE 3구만 실존 데이터)
housing_agg AS (
    SELECT
        AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG)   AS avg_meme_price,
        AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG) AS avg_jeonse_price,
        SUM(r.TOTAL_HOUSEHOLDS)                AS total_households
    FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
    JOIN city_meta m
        ON r.SGG = m.CITY_KOR_NAME
    WHERE r.SD = '서울'
),

-- 7) 아정당 통신 집계 (TELECOM_ONLY 경량 프로필용, 25구 전체 가능)
-- INSTALL_CITY 는 CITY_KOR_NAME 과 동일한 텍스트 (예: '중구')
telecom_agg AS (
    SELECT
        SUM(OPEN_COUNT)     AS total_open,
        SUM(CONTRACT_COUNT) AS total_contract,
        SUM(PAYEND_COUNT)   AS total_payend,
        AVG(OPEN_COUNT)     AS avg_open,
        AVG(CONTRACT_COUNT) AS avg_contract,
        AVG(PAYEND_COUNT)   AS avg_payend
    FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL t
    JOIN city_meta m
        ON t.INSTALL_CITY = m.CITY_KOR_NAME
    WHERE t.INSTALL_STATE = '서울'
)

-- ── 최종 JSON 조립 ────────────────────────────────────────────────────────
SELECT
    CASE (SELECT data_tier FROM tier)
        WHEN 'MULTI_SOURCE' THEN
            OBJECT_CONSTRUCT(
                'city_code',   city_code,
                'city_name',   (SELECT CITY_KOR_NAME FROM city_meta),
                'data_tier',   'MULTI_SOURCE',
                'population',  OBJECT_CONSTRUCT(
                    'avg_residential', (SELECT avg_residential FROM pop_agg),
                    'avg_working',     (SELECT avg_working     FROM pop_agg),
                    'avg_visiting',    (SELECT avg_visiting    FROM pop_agg)
                ),
                'income',      OBJECT_CONSTRUCT(
                    'avg_income',           (SELECT avg_income           FROM income_agg),
                    'median_income',        (SELECT median_income        FROM income_agg),
                    'avg_household_income', (SELECT avg_household_income FROM income_agg),
                    'avg_asset_amount',     (SELECT avg_asset_amount     FROM income_agg),
                    'rate_highend',         (SELECT rate_highend         FROM income_agg)
                ),
                'consumption', OBJECT_CONSTRUCT(
                    'food_sales',      (SELECT food_sales      FROM card_agg),
                    'coffee_sales',    (SELECT coffee_sales    FROM card_agg),
                    'beauty_sales',    (SELECT beauty_sales    FROM card_agg),
                    'medical_sales',   (SELECT medical_sales   FROM card_agg),
                    'education_sales', (SELECT education_sales FROM card_agg),
                    'home_life_sales', (SELECT home_life_sales FROM card_agg),
                    'total_sales',     (SELECT total_sales     FROM card_agg)
                ),
                'housing',     OBJECT_CONSTRUCT(
                    'avg_meme_price_per_pyeong',   (SELECT avg_meme_price    FROM housing_agg),
                    'avg_jeonse_price_per_pyeong', (SELECT avg_jeonse_price  FROM housing_agg),
                    'total_households',            (SELECT total_households  FROM housing_agg)
                ),
                'telecom_summary', OBJECT_CONSTRUCT(
                    'total_open',     (SELECT total_open     FROM telecom_agg),
                    'total_contract', (SELECT total_contract FROM telecom_agg),
                    'total_payend',   (SELECT total_payend   FROM telecom_agg)
                )
            )::VARCHAR
        ELSE
            OBJECT_CONSTRUCT(
                'city_code',       city_code,
                'city_name',       (SELECT CITY_KOR_NAME FROM city_meta),
                'data_tier',       'TELECOM_ONLY',
                'telecom_summary', OBJECT_CONSTRUCT(
                    'total_open',     (SELECT total_open     FROM telecom_agg),
                    'total_contract', (SELECT total_contract FROM telecom_agg),
                    'total_payend',   (SELECT total_payend   FROM telecom_agg),
                    'avg_open',       (SELECT avg_open       FROM telecom_agg),
                    'avg_contract',   (SELECT avg_contract   FROM telecom_agg),
                    'avg_payend',     (SELECT avg_payend     FROM telecom_agg)
                )
            )::VARCHAR
    END
$$
;
