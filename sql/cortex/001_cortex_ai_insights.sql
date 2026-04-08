-- ============================================================
-- 001_cortex_ai_insights.sql
-- Cortex AI_COMPLETE + AI_AGG 기반 이사 인사이트 뷰
-- 이슈: #27 (feat: Cortex AI Functions — AI_COMPLETE/CLASSIFY/EMBED)
-- 의존성: MART_MOVE_ANALYSIS (#21, pipelines/preprocessing.py)
--   * AVG_MEME_PRICE 는 MART 내 pre-aggregated 컬럼 — RICHGO 재JOIN 불필요
-- 멱등성: CREATE OR REPLACE VIEW — 반복 실행 안전 (AI 호출은 SELECT 시점)
-- 리전: US West (Oregon, us-west-2) — Cortex AI Functions 제한 없음
--
-- ⚠ 비용 주의: 뷰 SELECT마다 AI_COMPLETE/AI_AGG 호출 발생
--   V_AI_DISTRICT_INSIGHTS: 850행 × claude-4-sonnet 호출 위험
--   V_AI_STATE_SUMMARY:     34월 × AI_AGG 호출 위험
--   → 반드시 WHERE (CITY_CODE, STANDARD_YEAR_MONTH) 필터 또는
--     src/app/cortex.py 헬퍼 경유. SELECT * 금지.
-- ============================================================

-- Step 0: 컨텍스트
USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- ============================================================
-- Step 1: V_AI_DISTRICT_INSIGHTS — 25구 × 월 단위 AI 인사이트
--   DATA_TIER별 분기 프롬프트:
--     - MULTI_SOURCE(3구): OPEN_COUNT + ELECTRONICS_FURNITURE_SALES
--                         + TOTAL_RESIDENTIAL_POP + NEW_HOUSING_BALANCE_COUNT
--                         + 전월 대비 + RICHGO 평당가 → 3줄 정밀 액션
--     - TELECOM_ONLY(22구): OPEN_COUNT + 전월 대비 + RICHGO 평당가
--                          → 2줄 경량 + '근사' 신뢰도 고지
-- ============================================================
CREATE OR REPLACE VIEW V_AI_DISTRICT_INSIGHTS
  COMMENT = 'Cortex AI_COMPLETE 기반 구 단위 월별 B2B 인사이트 (Tier 분기) — #27'
AS
WITH mart_with_yoy AS (
    SELECT
        m.CITY_CODE,
        m.CITY_KOR_NAME,
        m.STANDARD_YEAR_MONTH,
        m.DATA_TIER,
        m.OPEN_COUNT,
        m.ELECTRONICS_FURNITURE_SALES,
        m.TOTAL_RESIDENTIAL_POP,
        m.NEW_HOUSING_BALANCE_COUNT,
        m.AVG_MEME_PRICE,
        LAG(m.OPEN_COUNT) OVER (
            PARTITION BY m.CITY_CODE ORDER BY m.STANDARD_YEAR_MONTH
        ) AS PREV_OPEN_COUNT,
        ROUND(
            (m.OPEN_COUNT - LAG(m.OPEN_COUNT) OVER (
                PARTITION BY m.CITY_CODE ORDER BY m.STANDARD_YEAR_MONTH
            )) / NULLIF(LAG(m.OPEN_COUNT) OVER (
                PARTITION BY m.CITY_CODE ORDER BY m.STANDARD_YEAR_MONTH
            ), 0) * 100, 1
        ) AS YOY_PCT
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS m
)
SELECT
    mwy.CITY_CODE,
    mwy.CITY_KOR_NAME,
    mwy.STANDARD_YEAR_MONTH,
    mwy.DATA_TIER,
    mwy.OPEN_COUNT,
    mwy.PREV_OPEN_COUNT,
    mwy.YOY_PCT,
    mwy.AVG_MEME_PRICE,
    AI_COMPLETE(
        'claude-4-sonnet',
        CASE mwy.DATA_TIER
          WHEN 'MULTI_SOURCE' THEN
            CONCAT(
                '[정밀 Tier] 서울 ', mwy.CITY_KOR_NAME, ' ',
                mwy.STANDARD_YEAR_MONTH, ' 기준 이사 시그널 ',
                '종합 분석: 신규 통신 개통(이사 프록시) ', COALESCE(mwy.OPEN_COUNT, 0), '건, ',
                '전월 대비 ', COALESCE(TO_CHAR(mwy.YOY_PCT), 'N/A'), '%, ',
                '가전/가구 카드매출 ', COALESCE(TO_CHAR(mwy.ELECTRONICS_FURNITURE_SALES), '0'), '원, ',
                '상주 인구 ', COALESCE(TO_CHAR(mwy.TOTAL_RESIDENTIAL_POP), '0'), '명, ',
                '신규 주거 잔고 ', COALESCE(TO_CHAR(mwy.NEW_HOUSING_BALANCE_COUNT), '0'), '건, ',
                '평당 아파트 매매가 ', COALESCE(TO_CHAR(ROUND(mwy.AVG_MEME_PRICE)), 'N/A'), '원. ',
                '4종 시그널을 종합해 B2B 마케팅 담당자(가전 렌탈·이사·인테리어)에게 ',
                '정확히 3줄의 액션 아이템을 한국어로 제안하세요. ',
                '각 줄은 번호(1., 2., 3.)로 시작하고, 구체적 수치·세그먼트·채널을 포함하세요.'
            )
          ELSE  -- 'TELECOM_ONLY'
            CONCAT(
                '[근사 Tier] 서울 ', mwy.CITY_KOR_NAME, ' ',
                mwy.STANDARD_YEAR_MONTH, ' 기준 이사 시그널 ',
                '경량 분석 (데이터 신뢰도: 근사 — 통신 신호 단일 소스): ',
                '신규 통신 개통(이사 프록시) ', COALESCE(mwy.OPEN_COUNT, 0), '건, ',
                '전월 대비 ', COALESCE(TO_CHAR(mwy.YOY_PCT), 'N/A'), '%, ',
                '평당 아파트 매매가 ', COALESCE(TO_CHAR(ROUND(mwy.AVG_MEME_PRICE)), 'N/A'), '원. ',
                '통신 신호만을 기반으로 한 경량 인사이트를 정확히 2줄의 한국어로 제시하세요. ',
                '첫 줄에 반드시 "데이터 신뢰도: 근사 (통신 단일 소스)"를 포함하고, ',
                '두 번째 줄에 실행 가능한 액션 아이템 1개를 제시하세요.'
            )
        END
    ) AS AI_INSIGHT
FROM mart_with_yoy mwy;

-- ============================================================
-- Step 2: V_AI_STATE_SUMMARY — AI_AGG 시/도 단위 자연어 트렌드 요약
--   서울 25구 전체를 한 번에 집약 (월별)
-- ============================================================
CREATE OR REPLACE VIEW V_AI_STATE_SUMMARY
  COMMENT = 'Cortex AI_AGG 기반 서울 25구 월별 트렌드 자연어 요약 — #27'
AS
SELECT
    '서울' AS INSTALL_STATE,
    m.STANDARD_YEAR_MONTH,
    COUNT(DISTINCT m.CITY_CODE) AS DISTRICT_COUNT,
    SUM(m.OPEN_COUNT) AS TOTAL_OPEN_COUNT,
    AI_AGG(
        CONCAT(
            m.CITY_KOR_NAME, ' (', m.DATA_TIER, '): 신규개통 ',
            COALESCE(TO_CHAR(m.OPEN_COUNT), '0'), '건'
        ),
        '이 시/도의 구별 이사 수요(신규 통신 개통 기준) 트렌드를 ' ||
        '2~3문장의 한국어로 요약하세요. ' ||
        '반드시 (1) 수요가 가장 높은 구 1개, (2) 수요가 가장 낮은 구 1개, ' ||
        '(3) MULTI_SOURCE Tier 3구의 특징 한 줄을 포함하세요.'
    ) AS STATE_SUMMARY
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS m
GROUP BY m.STANDARD_YEAR_MONTH;
