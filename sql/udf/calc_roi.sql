-- =============================================================================
-- CALC_ROI(city_code, budget, industry) -> VARCHAR (JSON)
-- ROI 시뮬레이션 — 지역·업종·예산 기반 예상 매출 및 ROI 반환
-- Issue #24 / dev_spec B3-2
--
-- 반환 JSON 키:
--   roi_pct             FLOAT  — ROI % = (예상매출 - 투입비용) / 투입비용 × 100
--   estimated_revenue   FLOAT  — 예상 매출 (원)
--   avg_price_pyeong    FLOAT  — RICHGO 평당 매매가 (원/평)
--   industry            VARCHAR — 입력 업종 코드
--   city_code           VARCHAR — 입력 시군구코드
--   confidence          VARCHAR — 'high' (MULTI_SOURCE 3구) / 'approximate' (TELECOM_ONLY 22구)
--
-- 계산 로직:
--   1. M_SCCO_MST → CITY_CODE로 CITY_KOR_NAME 조회
--   2. V_RICHGO_MARKET_PRICE → SGG 매칭으로 평당 매매가·가구수 집계
--   3. 업종별 전환율(내장 상수) 선택
--   4. estimated_revenue = budget × (1 + move_trigger_multiplier) × conversion_rate_ratio
--      - move_trigger_multiplier = MOVE_SIGNAL_INDEX 기반 가중치 (없으면 글로벌 벤치마크 3.0 사용)
--      - conversion_rate_ratio = 업종 전환율 / 기본 전환율 (0.01)
--   5. roi_pct = (estimated_revenue - budget) / budget × 100
--
-- 조인 키:
--   CITY_CODE(5자리) → M_SCCO_MST.CITY_KOR_NAME → V_RICHGO_MARKET_PRICE.SGG
--
-- 스키마: MOVING_INTEL.ANALYTICS
-- =============================================================================

CREATE OR REPLACE FUNCTION MOVING_INTEL.ANALYTICS.CALC_ROI(
    p_city_code VARCHAR,  -- 5자리 시군구코드 (예: '11680' = 강남구)
    p_budget    FLOAT,    -- 투입 예산 (원)
    p_industry  VARCHAR   -- 업종 코드 (CARD_SALES_INFO 20개 업종 중 하나)
)
RETURNS VARCHAR           -- JSON 문자열
AS
$$
WITH
-- ── Step 1: CITY_CODE → 한국어 시군구명 ──────────────────────────────────────
-- p_city_code 스칼라 서브쿼리: FROM 없는 서브쿼리는 컬럼 컨텍스트 없으므로
--   파라미터 참조가 보장됨 (컬럼명 CITY_CODE와 충돌 방지)
-- MAX() 집계: 미존재 city_code도 항상 1행 반환 (CITY_KOR_NAME=NULL)
city_meta AS (
    SELECT
        MAX(CITY_KOR_NAME) AS CITY_KOR_NAME
    FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
    WHERE CITY_CODE = p_city_code
),

-- ── Step 2: RICHGO 시세 집계 (구 단위 평균) ──────────────────────────────────
richgo_price AS (
    SELECT
        AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG)   AS avg_meme_price,
        AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG) AS avg_jeonse_price,
        SUM(r.TOTAL_HOUSEHOLDS)               AS total_households
    FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H r
    INNER JOIN city_meta m
        ON r.SGG = m.CITY_KOR_NAME
    WHERE r.TOTAL_HOUSEHOLDS > 0
),

-- ── Step 3: 이사 수요 프록시 (MART_MOVE_ANALYSIS 최근 3개월 평균) ───────────
move_demand AS (
    SELECT AVG(MOVE_SIGNAL_INDEX) AS avg_signal
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
    WHERE CITY_CODE = p_city_code
      AND STANDARD_YEAR_MONTH IN (
          SELECT DISTINCT STANDARD_YEAR_MONTH
          FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
          ORDER BY STANDARD_YEAR_MONTH DESC
          LIMIT 3
      )
),

-- ── Step 4: 업종별 전환율 내장 상수 ─────────────────────────────────────────
-- CARD_SALES_INFO 20개 업종 코드 기반
-- 기본 전환율 = dev_spec B3-2 내장 상수 테이블 기준
industry_params AS (
    SELECT
        CASE UPPER(p_industry)  -- p_industry: 파라미터 (industry 컬럼과 충돌 없음)
            WHEN 'HOME_LIFE_SERVICE'         THEN 0.020   -- 가전 렌탈 / 이사 O2O 복합
            WHEN 'ELECTRONICS_FURNITURE'     THEN 0.018   -- 가전·가구 (이사 직후 구매)
            WHEN 'FOOD'                      THEN 0.030   -- 음식 (이사 후 배달/식당)
            WHEN 'COFFEE'                    THEN 0.025   -- 카페
            WHEN 'BEAUTY'                    THEN 0.015   -- 미용
            WHEN 'MEDICAL'                   THEN 0.012   -- 의료
            WHEN 'EDUCATION_ACADEMY'         THEN 0.022   -- 교육
            WHEN 'CLOTHING_ACCESSORIES'      THEN 0.014   -- 의류
            WHEN 'ENTERTAINMENT'             THEN 0.016   -- 엔터테인먼트
            WHEN 'SPORTS_CULTURE_LEISURE'    THEN 0.015   -- 스포츠·문화
            WHEN 'ACCOMMODATION'             THEN 0.010   -- 숙박
            WHEN 'TRAVEL'                    THEN 0.010   -- 여행
            WHEN 'DEPARTMENT_STORE'          THEN 0.012   -- 백화점
            WHEN 'LARGE_DISCOUNT_STORE'      THEN 0.018   -- 대형마트
            WHEN 'SMALL_RETAIL_STORE'        THEN 0.020   -- 소매점
            WHEN 'CAR'                       THEN 0.008   -- 자동차
            WHEN 'CAR_SERVICE_SUPPLIES'      THEN 0.010   -- 자동차 서비스
            WHEN 'GAS_STATION'               THEN 0.012   -- 주유소
            WHEN 'E_COMMERCE'                THEN 0.025   -- 이커머스
            ELSE                                  0.010   -- 기본값 (알 수 없는 업종)
        END AS conversion_rate,
        -- 이사 트리거 캠페인 승수 (글로벌 벤치마크, dev_spec B3-2: 3배)
        3.0 AS move_trigger_multiplier
),

-- ── Step 5: ROI 계산 ─────────────────────────────────────────────────────────
calc AS (
    SELECT
        m.CITY_KOR_NAME,
        p.avg_meme_price,
        p.avg_jeonse_price,
        p.total_households,
        i.conversion_rate,
        i.move_trigger_multiplier,
        -- 이사 수요 가중치: MOVE_SIGNAL_INDEX는 0~1 스케일 — 그대로 사용 (NULL이면 0.5)
        COALESCE(d.avg_signal, 0.5) AS demand_weight,
        -- 예상 매출 = 예산 × 승수 × (전환율/기준전환율 0.01) × 수요 가중치
        -- conversion_rate/0.01: 업종 상대 전환율 비율 (>1이면 ROI 양수 보장)
        p_budget * i.move_trigger_multiplier * (i.conversion_rate / 0.01) * COALESCE(d.avg_signal, 0.5) AS estimated_revenue,
        -- Tier 분류 (SPH FACT는 3구만 실존: 중구/영등포구/서초구)
        CASE
            WHEN p_city_code IN ('11140', '11560', '11650') THEN 'MULTI_SOURCE'
            ELSE 'TELECOM_ONLY'
        END AS data_tier
    FROM richgo_price p
    CROSS JOIN industry_params i
    CROSS JOIN city_meta m
    LEFT JOIN move_demand d ON 1=1
)

-- ── Step 6: JSON 직렬화 ───────────────────────────────────────────────────────
-- CITY_KOR_NAME IS NULL = 존재하지 않는 city_code
-- avg_meme_price IS NULL = RICHGO 데이터 없는 구 (22구) → ROI는 계산, avg_price_pyeong만 NULL
SELECT
    CASE
        WHEN CITY_KOR_NAME IS NULL THEN
            OBJECT_CONSTRUCT(
                'error',             'city_code not found',
                'city_code',         p_city_code,
                'roi_pct',           NULL,
                'estimated_revenue', NULL,
                'avg_price_pyeong',  NULL
            )::VARCHAR
        ELSE
            OBJECT_CONSTRUCT(
                'roi_pct',              ROUND((estimated_revenue - p_budget) / NULLIF(p_budget, 0) * 100.0, 2),
                'estimated_revenue',    ROUND(estimated_revenue, 0),
                'avg_price_pyeong',     ROUND(avg_meme_price, 0),
                'avg_jeonse_price_pyeong', ROUND(avg_jeonse_price, 0),
                'total_households',     total_households,
                'conversion_rate',      conversion_rate,
                'demand_weight',        ROUND(demand_weight, 4),
                'city_code',            p_city_code,
                'city_name',            CITY_KOR_NAME,
                'industry',             UPPER(p_industry),
                'confidence',           CASE data_tier WHEN 'MULTI_SOURCE' THEN 'high' ELSE 'approximate' END,
                'data_tier',            data_tier
            )::VARCHAR
    END
FROM calc
$$
;
