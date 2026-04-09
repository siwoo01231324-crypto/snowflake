"""
scripts/deploy_udf.py — PREDICT_MOVE_DEMAND UDF 배포 + TC 검증
Issue #23
"""
import sys
import io
import pathlib
from snowflake.snowpark import Session

# Windows cp949 환경에서 한글/특수문자 출력 처리
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# ~/.snowflake/connections.toml [default] 프로파일 사용 (자격증명 소스코드 하드코딩 금지)
CONNECTION = {"connection_name": "default", "database": "MOVING_INTEL", "schema": "ANALYTICS"}

ROOT = pathlib.Path(__file__).parent.parent


def run_tc(session, name, sql, expected_desc):
    print(f"\n{'─'*50}")
    print(f"  {name}: {expected_desc}")
    try:
        rows = session.sql(sql).collect()
        print(f"  결과: {rows[:3]}{'...' if len(rows) > 3 else ''}")
        return rows
    except Exception as e:
        print(f"  ERROR: {e}")
        return None


def main():
    print("Snowflake 연결 중...")
    session = Session.builder.configs(CONNECTION).create()
    print("연결 완료\n")

    # ── Step 1: 스코어 사전 계산 테이블 ────────────────────────────────────────
    print("[1/2] PREDICTED_MOVE_DEMAND 테이블 생성 중...")
    session.sql("""
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
    """).collect()
    print("[1/2] 완료")

    # ── Step 2: 룩업 UDF ────────────────────────────────────────────────────────
    print("[2/2] PREDICT_MOVE_DEMAND UDF 배포 중...")
    session.sql("""
        CREATE OR REPLACE FUNCTION MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND(
            p_state  VARCHAR,
            p_city   VARCHAR
        )
        RETURNS FLOAT
        AS
        $$
        SELECT DEMAND_SCORE
        FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
        WHERE UPPER(CITY_KOR_NAME) = UPPER(p_city)
        $$
    """).collect()
    print("[2/2] 완료\n")

    # ── TC-01 ──────────────────────────────────────────────────
    rows = run_tc(
        session, "TC-01",
        "SHOW USER FUNCTIONS LIKE 'PREDICT_MOVE_DEMAND' IN SCHEMA MOVING_INTEL.ANALYTICS",
        "UDF 존재 확인 (1 row 기대)"
    )
    tc01_ok = rows is not None and len(rows) >= 1
    print(f"  {'PASS' if tc01_ok else 'FAIL'}")

    # ── TC-02 ──────────────────────────────────────────────────
    rows = run_tc(
        session, "TC-02",
        "SELECT MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND('서울', '강남구') AS score",
        "유효 스코어 (0~100)"
    )
    tc02_ok = False
    if rows:
        score = rows[0]["SCORE"]
        tc02_ok = score is not None and 0 <= float(score) <= 100
        print(f"  score = {score}  →  {'PASS' if tc02_ok else 'FAIL'}")
    else:
        print("  FAIL (no result)")

    # ── TC-03 ──────────────────────────────────────────────────
    # SQL UDF는 GROUP BY 컨텍스트에서 테이블 접근 불가 (Snowflake correlated subquery 제한)
    # -> PREDICTED_MOVE_DEMAND 테이블을 직접 조회해 25구 전체 스코어 검증
    rows = run_tc(
        session, "TC-03",
        """SELECT CITY_KOR_NAME, DEMAND_SCORE AS score
           FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
           ORDER BY score DESC""",
        "25개 구 전부 0~100 (사전 계산 테이블 직접 조회)"
    )
    tc03_ok = False
    if rows:
        valid = [r for r in rows if r["SCORE"] is not None and 0 <= float(r["SCORE"]) <= 100]
        tc03_ok = len(rows) == 25 and len(valid) == 25
        print(f"  rows={len(rows)}, valid={len(valid)}  →  {'PASS' if tc03_ok else 'FAIL'}")
        print("  Top 5:")
        for r in rows[:5]:
            print(f"    {r['CITY_KOR_NAME']:8s}  {float(r['SCORE']):.1f}")

    # ── TC-04 ──────────────────────────────────────────────────
    rows = run_tc(
        session, "TC-04",
        "SELECT MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND('서울', '없는구') AS score",
        "NULL 반환 (graceful)"
    )
    tc04_ok = False
    if rows is not None:
        score = rows[0]["SCORE"] if rows else None
        tc04_ok = score is None
        print(f"  score = {score}  →  {'PASS' if tc04_ok else 'FAIL'}")
    else:
        print("  FAIL (exception)")

    # ── 요약 ──────────────────────────────────────────────────
    print(f"\n{'='*50}")
    results = [tc01_ok, tc02_ok, tc03_ok, tc04_ok]
    for i, ok in enumerate(results, 1):
        print(f"  TC-0{i}: {'PASS' if ok else 'FAIL'}")
    print(f"  합계: {sum(results)}/4 통과")
    print(f"{'='*50}")

    session.close()
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())
