-- =============================================================================
-- PREDICT_MOVE_DEMAND(install_state, install_city) -> FLOAT
-- 이사 수요 예측 0~100 스코어 반환
-- Issue #23 / dev_spec B3-1
--
-- 구조:
--   Step 1. ANALYTICS.PREDICTED_MOVE_DEMAND 테이블에 스코어 사전 계산
--           (최근 3개월 OPEN_COUNT 0.6 + MOVE_SIGNAL_INDEX 0.4 가중 결합,
--            서울 25구 min-max 정규화)
--   Step 2. UDF는 해당 테이블을 단순 룩업 -> 없는 구는 NULL 반환
--
-- 인자:
--   install_state : '서울' 등 시도명 (현재 서울 25구만 지원, 내부적으로 무시)
--   install_city  : '강남구' 등 구 이름 (MART.CITY_KOR_NAME 기준)
-- =============================================================================

-- ── Step 1: 스코어 사전 계산 테이블 ─────────────────────────────────────────
CREATE OR REPLACE TABLE MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND AS
WITH recent_months AS (
    SELECT DISTINCT STANDARD_YEAR_MONTH
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
    ORDER BY STANDARD_YEAR_MONTH DESC
    LIMIT 3
),
city_agg AS (
    SELECT
        CITY_KOR_NAME,
        AVG(OPEN_COUNT)        AS avg_open,
        AVG(MOVE_SIGNAL_INDEX) AS avg_sig
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
    WHERE STANDARD_YEAR_MONTH IN (SELECT STANDARD_YEAR_MONTH FROM recent_months)
    GROUP BY CITY_KOR_NAME
),
normalized AS (
    SELECT *,
        MIN(avg_open) OVER() AS min_open,
        MAX(avg_open) OVER() AS max_open,
        MIN(avg_sig)  OVER() AS min_sig,
        MAX(avg_sig)  OVER() AS max_sig
    FROM city_agg
)
SELECT
    CITY_KOR_NAME,
    GREATEST(0.0, LEAST(100.0,
        IFF(max_open = min_open, 50.0,
            (avg_open - min_open) / NULLIF(max_open - min_open, 0) * 100.0)
    )) * 0.6
    +
    GREATEST(0.0, LEAST(100.0,
        IFF(max_sig = min_sig, 50.0,
            (avg_sig - min_sig) / NULLIF(max_sig - min_sig, 0) * 100.0)
    )) * 0.4 AS DEMAND_SCORE
FROM normalized
;

-- ── Step 2: 룩업 UDF ─────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND(
    p_state  VARCHAR,   -- 시도명 (예: '서울', API 호환용)
    p_city   VARCHAR    -- 구 이름 (예: '강남구')
)
RETURNS FLOAT
AS
$$
SELECT DEMAND_SCORE
FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
WHERE UPPER(CITY_KOR_NAME) = UPPER(p_city)
LIMIT 1
$$
;
