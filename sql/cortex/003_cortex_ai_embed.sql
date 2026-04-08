-- ============================================================
-- 003_cortex_ai_embed.sql
-- Cortex AI_EMBED 기반 지역 프로필 벡터 테이블 + 유사도 검색 SP
-- 이슈: #27 (feat: Cortex AI Functions — AI_COMPLETE/CLASSIFY/EMBED)
-- 의존성: MART_MOVE_ANALYSIS (#21, pipelines/preprocessing.py)
-- 전략: Marketplace 원본 ALTER 금지 (read-only) → MOVING_INTEL.ANALYTICS 에 별도 테이블
-- 멱등성: CREATE TABLE IF NOT EXISTS + CREATE OR REPLACE PROCEDURE + MERGE INTO
-- 리전: US West (Oregon, us-west-2) — snowflake-arctic-embed-l-v2.0 → VECTOR(FLOAT, 1024)
-- ============================================================

-- Step 0: 컨텍스트
USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- ============================================================
-- Step 1: T_DISTRICT_EMBEDDINGS — 25구 지역 프로필 벡터 저장 테이블
--   크기: 25행 × 1024 float ≈ 100 KB (부담 없음)
--   EMBEDDING 컬럼: VECTOR(FLOAT, 1024) — snowflake-arctic-embed-l-v2.0 차원
--   PROFILE_YM: 각 구 임베딩이 기반으로 한 월 — Tier별로 다를 수 있음
--     (MULTI_SOURCE: RICHGO/SPH 4종 시그널 non-null 최신월
--      TELECOM_ONLY: 통신 기준 최신월)
-- ============================================================
CREATE TABLE IF NOT EXISTS MOVING_INTEL.ANALYTICS.T_DISTRICT_EMBEDDINGS (
    CITY_CODE       VARCHAR(5)    NOT NULL,
    CITY_KOR_NAME   VARCHAR(50)   NOT NULL,
    DATA_TIER       VARCHAR(20)   NOT NULL,
    PROFILE_YM      VARCHAR(6),                 -- 임베딩 기준월 (Tier별 분기)
    PROFILE_TEXT    VARCHAR(4000),              -- 디버깅용 원문 텍스트
    EMBEDDING       VECTOR(FLOAT, 1024),        -- AI_EMBED 결과
    UPDATED_AT      TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT PK_T_DISTRICT_EMBEDDINGS PRIMARY KEY (CITY_CODE)
)
COMMENT = 'Cortex AI_EMBED 지역 프로필 벡터 (서울 25구) — #27';

-- ============================================================
-- Step 2: SP_REFRESH_DISTRICT_EMBEDDINGS
--   Tier별 기준월 분기 — 각 구에 가용한 최선의 월로 프로필 생성.
--
--   배경: RICHGO/SPH Marketplace 소스는 2024-12까지만 완전하고
--   통신(V_TELECOM_NEW_INSTALL)은 2026-04까지. MART_MOVE_ANALYSIS의
--   `MAX(STANDARD_YEAR_MONTH)`만 쓰면 MULTI_SOURCE 3구(중구·영등포·서초)의
--   평당가·인구·카드매출·신규주거잔고가 전부 NULL이 되어 "정밀Tier인데 0"인
--   이상한 프로필 텍스트가 생긴다.
--
--   분기 전략:
--     multi_ym   = MAX(YM WHERE DATA_TIER='MULTI_SOURCE' AND AVG_MEME_PRICE NOT NULL)
--     telecom_ym = MAX(YM WHERE DATA_TIER='TELECOM_ONLY')
--     MULTI_SOURCE 3구: multi_ym 의 4종 시그널 + 평당가 (정밀 프로필)
--     TELECOM_ONLY 22구: telecom_ym 의 신규개통 (근사 프로필)
--
--   멱등성: MERGE INTO (UPDATE/INSERT)
--   관측성: PROFILE_YM 컬럼에 각 구가 사용한 월 기록
-- ============================================================
CREATE OR REPLACE PROCEDURE MOVING_INTEL.ANALYTICS.SP_REFRESH_DISTRICT_EMBEDDINGS()
RETURNS STRING
LANGUAGE SQL
AS
$$
DECLARE
    multi_ym   VARCHAR;
    telecom_ym VARCHAR;
    row_count  INT;
BEGIN
    -- MULTI_SOURCE: 4종 시그널(평당가) 살아있는 최신월
    SELECT MAX(STANDARD_YEAR_MONTH) INTO :multi_ym
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
    WHERE DATA_TIER = 'MULTI_SOURCE'
      AND AVG_MEME_PRICE IS NOT NULL;

    -- TELECOM_ONLY: 통신 신규개통 기준 절대 최신월
    SELECT MAX(STANDARD_YEAR_MONTH) INTO :telecom_ym
    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
    WHERE DATA_TIER = 'TELECOM_ONLY';

    MERGE INTO MOVING_INTEL.ANALYTICS.T_DISTRICT_EMBEDDINGS tgt
    USING (
        WITH profile AS (
            SELECT
                m.CITY_CODE,
                m.CITY_KOR_NAME,
                m.DATA_TIER,
                m.STANDARD_YEAR_MONTH AS PROFILE_YM,
                CASE m.DATA_TIER
                  WHEN 'MULTI_SOURCE' THEN
                    CONCAT(
                        '서울 ', m.CITY_KOR_NAME,
                        ', 기준월 ', m.STANDARD_YEAR_MONTH,
                        ', 정밀Tier 4종시그널, 신규개통 ',
                        COALESCE(TO_CHAR(m.OPEN_COUNT), '0'), '건, ',
                        '상주인구 ',
                        COALESCE(TO_CHAR(ROUND(m.TOTAL_RESIDENTIAL_POP)), '0'), '명, ',
                        '가전가구매출 ',
                        COALESCE(TO_CHAR(m.ELECTRONICS_FURNITURE_SALES), '0'), '원, ',
                        '신규주거잔고 ',
                        COALESCE(TO_CHAR(m.NEW_HOUSING_BALANCE_COUNT), '0'), '건, ',
                        '평당매매가 ',
                        COALESCE(TO_CHAR(ROUND(m.AVG_MEME_PRICE)), 'N/A'), '원'
                    )
                  ELSE
                    CONCAT(
                        '서울 ', m.CITY_KOR_NAME,
                        ', 기준월 ', m.STANDARD_YEAR_MONTH,
                        ', 근사Tier 통신단일, 신규개통 ',
                        COALESCE(TO_CHAR(m.OPEN_COUNT), '0'), '건'
                    )
                END AS PROFILE_TEXT
            FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS m
            WHERE (m.DATA_TIER = 'MULTI_SOURCE' AND m.STANDARD_YEAR_MONTH = :multi_ym)
               OR (m.DATA_TIER = 'TELECOM_ONLY' AND m.STANDARD_YEAR_MONTH = :telecom_ym)
        )
        SELECT
            p.CITY_CODE,
            p.CITY_KOR_NAME,
            p.DATA_TIER,
            p.PROFILE_YM,
            p.PROFILE_TEXT,
            AI_EMBED('snowflake-arctic-embed-l-v2.0', p.PROFILE_TEXT) AS EMBEDDING
        FROM profile p
    ) src
    ON tgt.CITY_CODE = src.CITY_CODE
    WHEN MATCHED THEN UPDATE SET
        CITY_KOR_NAME = src.CITY_KOR_NAME,
        DATA_TIER     = src.DATA_TIER,
        PROFILE_YM    = src.PROFILE_YM,
        PROFILE_TEXT  = src.PROFILE_TEXT,
        EMBEDDING     = src.EMBEDDING,
        UPDATED_AT    = CURRENT_TIMESTAMP
    WHEN NOT MATCHED THEN INSERT
        (CITY_CODE, CITY_KOR_NAME, DATA_TIER, PROFILE_YM, PROFILE_TEXT, EMBEDDING, UPDATED_AT)
    VALUES
        (src.CITY_CODE, src.CITY_KOR_NAME, src.DATA_TIER, src.PROFILE_YM,
         src.PROFILE_TEXT, src.EMBEDDING, CURRENT_TIMESTAMP);

    SELECT COUNT(*) INTO :row_count
    FROM MOVING_INTEL.ANALYTICS.T_DISTRICT_EMBEDDINGS;

    RETURN 'T_DISTRICT_EMBEDDINGS refreshed (multi_ym=' || :multi_ym
           || ', telecom_ym=' || :telecom_ym
           || ', rows=' || :row_count || ')';
END;
$$;

-- ============================================================
-- Step 3: SP_FIND_SIMILAR_DISTRICTS(TARGET_CITY_CODE, TOP_K)
--   VECTOR_COSINE_SIMILARITY 기반 유사 구 top_k 반환 (타겟 자신 제외)
--   반환: TABLE(CITY_CODE, CITY_KOR_NAME, DATA_TIER, SIMILARITY)
-- ============================================================
CREATE OR REPLACE PROCEDURE MOVING_INTEL.ANALYTICS.SP_FIND_SIMILAR_DISTRICTS(
    TARGET_CITY_CODE VARCHAR,
    TOP_K NUMBER
)
RETURNS TABLE (
    CITY_CODE     VARCHAR,
    CITY_KOR_NAME VARCHAR,
    DATA_TIER     VARCHAR,
    SIMILARITY    FLOAT
)
LANGUAGE SQL
AS
$$
DECLARE
    res RESULTSET;
BEGIN
    res := (
        SELECT
            similar.CITY_CODE,
            similar.CITY_KOR_NAME,
            similar.DATA_TIER,
            VECTOR_COSINE_SIMILARITY(target.EMBEDDING, similar.EMBEDDING)::FLOAT AS SIMILARITY
        FROM MOVING_INTEL.ANALYTICS.T_DISTRICT_EMBEDDINGS target
        CROSS JOIN MOVING_INTEL.ANALYTICS.T_DISTRICT_EMBEDDINGS similar
        WHERE target.CITY_CODE = :TARGET_CITY_CODE
          AND similar.CITY_CODE <> target.CITY_CODE
        ORDER BY SIMILARITY DESC
        LIMIT :TOP_K
    );
    RETURN TABLE(res);
END;
$$;

-- ============================================================
-- Step 4: 초기 로드 — 배포 시 1회 실행
--   25구 × AI_EMBED 호출 → T_DISTRICT_EMBEDDINGS 25행 채움
-- ============================================================
CALL MOVING_INTEL.ANALYTICS.SP_REFRESH_DISTRICT_EMBEDDINGS();
