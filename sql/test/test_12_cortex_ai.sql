-- ============================================================
-- test_12_cortex_ai.sql
-- Cortex AI Functions 검증 (TC-01 ~ TC-06) — 이슈 #27
-- SoT: docs/specs/dev_spec.md B4 (#40 재작성본)
-- 모델: claude-4-sonnet, snowflake-arctic-embed-l-v2.0
-- 전제: Oregon, MART_MOVE_ANALYSIS(#21), V_TELECOM_NEW_INSTALL(#19)
-- ============================================================

USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- TC-01: AI_COMPLETE 기본 호출
SELECT LEFT(AI_COMPLETE('claude-4-sonnet', '한국어로 "안녕하세요"라고만 답하세요.'), 30) AS hello;
-- EXPECTED: LENGTH > 0

-- TC-02: AI_CLASSIFY 3등급 분류 + :labels[0]::STRING 추출
SELECT AI_CLASSIFY(
    '신규개통 150건, 전월 대비 25 퍼센트 증가',
    ARRAY_CONSTRUCT('긴급', '주의', '안정')
):labels[0]::STRING AS grade;
-- EXPECTED: {'긴급','주의','안정'} 중 하나

-- TC-03: AI_EMBED NOT NULL (TYPEOF/VECTOR_DIMENSION 미지원이므로 NOT NULL + 간접 확인)
SELECT AI_EMBED('snowflake-arctic-embed-l-v2.0', '서울 강남구 아파트 평당 1200만원') IS NOT NULL AS ok;
-- EXPECTED: TRUE (VECTOR(FLOAT, 1024))

-- TC-04: 실데이터 + AI_COMPLETE
SELECT v.INSTALL_CITY, v.OPEN_COUNT,
       LEFT(AI_COMPLETE('claude-4-sonnet',
            CONCAT('서울 ', v.INSTALL_CITY, ' 신규 통신 개통 ', v.OPEN_COUNT, '건. 2줄 액션 아이템을 한국어로.')), 100) AS insight
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL v
WHERE v.INSTALL_STATE = '서울'
  AND v.OPEN_COUNT IS NOT NULL
ORDER BY v.OPEN_COUNT DESC LIMIT 1;
-- EXPECTED: 1행, insight LENGTH > 0

-- TC-05: VECTOR_COSINE_SIMILARITY
WITH e AS (
    SELECT AI_EMBED('snowflake-arctic-embed-l-v2.0', '서울 강남구 아파트 단지') AS v1,
           AI_EMBED('snowflake-arctic-embed-l-v2.0', '서울 서초구 아파트 단지') AS v2,
           AI_EMBED('snowflake-arctic-embed-l-v2.0', '부산 해운대 오피스텔') AS v3
)
SELECT VECTOR_COSINE_SIMILARITY(v1, v2) AS sim_gn_sc,
       VECTOR_COSINE_SIMILARITY(v1, v3) AS sim_gn_hu
FROM e;
-- EXPECTED: 둘 다 FLOAT NOT NULL, sim_gn_sc >= sim_gn_hu (자연스러움)

-- TC-06: AI_AGG MART 기반
SELECT '서울' AS region, LEFT(
    AI_AGG(
        CONCAT(m.CITY_KOR_NAME, ' (', m.DATA_TIER, '): 신규개통 ', COALESCE(TO_CHAR(m.OPEN_COUNT),'0'), '건'),
        '서울 25구 월별 이사(신규개통) 트렌드를 2문장 한국어로 요약. 가장 높은 구와 낮은 구 지목.'
    ), 200) AS summary
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS m
WHERE m.STANDARD_YEAR_MONTH = '202603';
-- EXPECTED: 1행, summary LENGTH > 0
