-- ============================================================
-- 002_cortex_ai_classify.sql
-- Cortex AI_CLASSIFY 기반 이사 수요 등급 분류 뷰
-- 이슈: #27 (feat: Cortex AI Functions — AI_COMPLETE/CLASSIFY/EMBED)
-- 의존성: MART_MOVE_ANALYSIS (#21, pipelines/preprocessing.py)
-- 멱등성: CREATE OR REPLACE VIEW — 반복 실행 안전 (AI 호출은 SELECT 시점)
-- 리전: US West (Oregon, us-west-2)
--
-- ⚠ 비용 주의: SELECT마다 AI_CLASSIFY 호출
--   V_AI_DEMAND_GRADE: 850행 × claude-4-sonnet 호출 위험
--   → 반드시 WHERE (CITY_CODE, STANDARD_YEAR_MONTH) 필터 또는
--     src/app/cortex.py:classify_demand 경유. SELECT * 금지.
-- ============================================================
-- AI_CLASSIFY 라벨 제약 (V6 실측 확정):
--   짧은 라벨만 허용: '긴급' / '주의' / '안정'
--   em-dash 긴 라벨('긴급 — 즉시 마케팅 투입' 등)은 empty array 반환 → 금지
--   추출 경로: :labels[0]::STRING (dev_spec ':label::STRING' 표기는 오류)
-- ============================================================

-- Step 0: 컨텍스트
USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- ============================================================
-- V_AI_DEMAND_GRADE — 25구 × 월 단위 3등급 분류
--   입력: 서울 구명 + STANDARD_YEAR_MONTH + 신규개통 건수 + 전월 대비 변화율
--   출력 DEMAND_GRADE: '긴급' | '주의' | '안정' (NULL이면 '알수없음' fallback)
-- ============================================================
CREATE OR REPLACE VIEW V_AI_DEMAND_GRADE
  COMMENT = 'Cortex AI_CLASSIFY 기반 25구 월별 이사 수요 등급 — #27'
AS
-- YOY_PCT는 SELECT 프로젝션과 AI_CLASSIFY 프롬프트 양쪽에서 사용되므로
-- 중간 CTE에서 한 번만 계산해 drift를 방지한다.
WITH with_yoy AS (
    SELECT
        m.CITY_CODE,
        m.CITY_KOR_NAME,
        m.STANDARD_YEAR_MONTH,
        m.DATA_TIER,
        m.OPEN_COUNT,
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
    wy.CITY_CODE,
    wy.CITY_KOR_NAME,
    wy.STANDARD_YEAR_MONTH,
    wy.DATA_TIER,
    wy.OPEN_COUNT,
    wy.PREV_OPEN_COUNT,
    wy.YOY_PCT,
    COALESCE(
        AI_CLASSIFY(
            CONCAT(
                '서울 ', wy.CITY_KOR_NAME, ', ',
                wy.STANDARD_YEAR_MONTH, ', 신규개통 ',
                COALESCE(TO_CHAR(wy.OPEN_COUNT), '0'), '건, 전월 대비 ',
                COALESCE(TO_CHAR(wy.YOY_PCT), 'N/A'), '%'
            ),
            ARRAY_CONSTRUCT('긴급', '주의', '안정')
        ):labels[0]::STRING,
        '알수없음'
    ) AS DEMAND_GRADE
FROM with_yoy wy
WHERE wy.OPEN_COUNT IS NOT NULL;
