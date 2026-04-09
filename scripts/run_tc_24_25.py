"""
TC 배포 + 실행 스크립트 — Issue #24 (CALC_ROI) & #25 (GET_SEGMENT_PROFILE)
연결 정보: ~/.snowflake/connections.toml [default]
"""

import snowflake.connector
import json, sys
from pathlib import Path

# ── 연결 (connections.toml에서 직접 읽기) ───────────────────────────────────
try:
    import tomllib
    with open(Path.home() / ".snowflake" / "connections.toml", "rb") as f:
        cfg = tomllib.load(f)["default"]
except ImportError:
    import re
    raw = (Path.home() / ".snowflake" / "connections.toml").read_text()
    cfg = dict(re.findall(r'(\w+)\s*=\s*"([^"]+)"', raw))

conn = snowflake.connector.connect(
    account   = cfg["account"],
    user      = cfg["user"],
    password  = cfg["password"],
    warehouse = cfg["warehouse"],
    role      = cfg.get("role", "ACCOUNTADMIN"),
    database  = "MOVING_INTEL",
    schema    = "ANALYTICS",
)
cur = conn.cursor()
cur.execute("ALTER SESSION SET USE_CACHED_RESULT = FALSE")  # 캐시 무효화

PASS = "✓ PASS"
FAIL = "✗ FAIL"

def run(sql, label=""):
    try:
        cur.execute(sql)
        rows = cur.fetchall()
        cols = [d[0] for d in cur.description] if cur.description else []
        return rows, cols
    except Exception as e:
        print(f"  ERROR [{label}]: {e}")
        return None, None

def check(cond, label):
    status = PASS if cond else FAIL
    print(f"  {status}  {label}")
    return cond

# ══════════════════════════════════════════════════════════════════════════════
# STEP 1: 배포
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("DEPLOY — Issue #24: CALC_ROI UDF")
print("="*60)

base = Path("D:/project/Snowflake/my-project/.worktree")
sql_24 = (base / "000024-calc-roi-udf/sql/udf/calc_roi.sql").read_text(encoding="utf-8")
rows, _ = run(sql_24, "deploy CALC_ROI")
if rows is not None:
    print(f"  ✓ CALC_ROI 배포 완료")
else:
    print(f"  ✗ CALC_ROI 배포 실패 — 중단")
    sys.exit(1)

print("\n" + "="*60)
print("DEPLOY — Issue #25: V_SPH_REGION_MASTER + GET_SEGMENT_PROFILE UDF")
print("="*60)

sql_25_full = (base / "000025-get-segment-profile/sql/udf/get_segment_profile.sql").read_text(encoding="utf-8")

# Step 0 (VIEW) / Step 1 (UDF) 분리 — CREATE OR REPLACE 기준
parts = sql_25_full.split("-- ── Step 1:")
view_sql = parts[0].strip()
udf_sql  = "-- ── Step 1:" + parts[1].strip()

rows, _ = run(view_sql, "deploy V_SPH_REGION_MASTER")
if rows is not None:
    print(f"  ✓ V_SPH_REGION_MASTER 뷰 배포 완료")

rows, _ = run(udf_sql, "deploy GET_SEGMENT_PROFILE")
if rows is not None:
    print(f"  ✓ GET_SEGMENT_PROFILE 배포 완료")
else:
    print(f"  ✗ GET_SEGMENT_PROFILE 배포 실패 — 중단")
    sys.exit(1)

# ══════════════════════════════════════════════════════════════════════════════
# TC #24 — CALC_ROI
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("TC #24 — CALC_ROI UDF")
print("="*60)
results_24 = []

# TC-01
print("\n[TC-01] UDF 존재 확인")
rows, _ = run("SHOW USER FUNCTIONS LIKE 'CALC_ROI' IN SCHEMA MOVING_INTEL.ANALYTICS", "TC-01")
ok = rows is not None and len(rows) >= 1
results_24.append(check(ok, f"CALC_ROI 존재 ({len(rows) if rows else 0} row)"))

# TC-02
print("\n[TC-02] 기본 호출 — 강남구(11680), 1억, ELECTRONICS_FURNITURE")
rows, cols = run("""
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):roi_pct::FLOAT AS roi_pct,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):estimated_revenue::FLOAT AS estimated_revenue
""", "TC-02")
if rows:
    roi_pct = rows[0][0]
    est_rev = rows[0][1]
    est_rev_str = f"{est_rev:,.0f}" if est_rev is not None else "None"
    print(f"  roi_pct={roi_pct}, estimated_revenue={est_rev_str}")
    results_24.append(check(roi_pct is not None and roi_pct > 0, f"roi_pct > 0 (실제: {roi_pct})"))
else:
    results_24.append(check(False, "TC-02 실행 실패"))

# TC-03
print("\n[TC-03] JSON 키 구조 확인 (서초구 11650 — RICHGO 커버리지 있음)")
rows, cols = run("""
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11650', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):roi_pct             IS NOT NULL AS has_roi_pct,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11650', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):estimated_revenue   IS NOT NULL AS has_estimated_revenue,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11650', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):avg_price_pyeong    IS NOT NULL AS has_avg_price_pyeong,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11650', 100000000::FLOAT, 'ELECTRONICS_FURNITURE')):data_tier::VARCHAR  AS data_tier
""", "TC-03")
if rows:
    has_roi, has_rev, has_price, tier = rows[0]
    print(f"  has_roi_pct={has_roi}, has_estimated_revenue={has_rev}, has_avg_price_pyeong={has_price}, data_tier={tier}")
    results_24.append(check(has_roi and has_rev and has_price, "필수 키 3개 존재"))
else:
    results_24.append(check(False, "TC-03 실행 실패"))

# TC-04
print("\n[TC-04] 존재하지 않는 city_code → graceful 처리")
rows, cols = run("""
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000::FLOAT, 'FOOD')):roi_pct   IS NULL AS roi_pct_is_null,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000::FLOAT, 'FOOD')):error     IS NOT NULL AS has_error_key
""", "TC-04")
if rows:
    roi_null, has_err = rows[0]
    print(f"  roi_pct_is_null={roi_null}, has_error_key={has_err}")
    results_24.append(check(roi_null or has_err, "graceful 처리 확인"))
else:
    results_24.append(check(False, "TC-04 실행 실패"))

# TC-05 (보조) — 내부 에러 방지: 업종별 순차 호출
print("\n[TC-05] 업종별 ROI 비교 (보조 — 순차 호출)")
industries = [('FOOD', 0.030), ('ELECTRONICS_FURNITURE', 0.018), ('EDUCATION_ACADEMY', 0.022), ('HOME_LIFE_SERVICE', 0.020)]
tc05_ok = True
prev_roi = None
for ind, rate in industries:
    rows2, _ = run(f"""
SELECT PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, '{ind}')):roi_pct::FLOAT AS roi_pct
""", f"TC-05 {ind}")
    if rows2 and rows2[0][0] is not None:
        roi = float(rows2[0][0])
        print(f"  {ind:30s} roi_pct={roi:.1f}%")
    else:
        print(f"  {ind:30s} ERROR")
        tc05_ok = False
results_24.append(check(tc05_ok, "업종별 ROI 순차 반환 확인"))

# ══════════════════════════════════════════════════════════════════════════════
# TC #25 — GET_SEGMENT_PROFILE
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("TC #25 — GET_SEGMENT_PROFILE UDF")
print("="*60)
results_25 = []

# TC-01
print("\n[TC-01] UDF 존재 확인")
rows, _ = run("SHOW USER FUNCTIONS LIKE 'GET_SEGMENT_PROFILE' IN SCHEMA MOVING_INTEL.ANALYTICS", "TC-01")
ok = rows is not None and len(rows) >= 1
results_25.append(check(ok, f"GET_SEGMENT_PROFILE 존재 ({len(rows) if rows else 0} row)"))

# TC-02
print("\n[TC-02] 중구(11140) MULTI_SOURCE 호출")
rows, cols = run("SELECT MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140') AS profile", "TC-02")
if rows and rows[0][0]:
    profile = json.loads(rows[0][0])
    print(f"  data_tier={profile.get('data_tier')}, city_name={profile.get('city_name')}")
    results_25.append(check(profile.get("data_tier") == "MULTI_SOURCE", "data_tier=MULTI_SOURCE"))
else:
    results_25.append(check(False, "TC-02 실행 실패"))

# TC-03
print("\n[TC-03] 필수 키 4개 확인 (중구 11140)")
rows, cols = run("""
SELECT
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):population  IS NOT NULL AS has_pop,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):income       IS NOT NULL AS has_income,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):consumption  IS NOT NULL AS has_cons,
    PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('11140')):housing      IS NOT NULL AS has_housing
""", "TC-03")
if rows:
    has_pop, has_inc, has_cons, has_housing = rows[0]
    print(f"  population={has_pop}, income={has_inc}, consumption={has_cons}, housing={has_housing}")
    results_25.append(check(all([has_pop, has_inc, has_cons, has_housing]), "필수 키 4개 모두 존재"))
else:
    results_25.append(check(False, "TC-03 실행 실패"))

# TC-04 — GROUP BY 대신 대표 코드 순차 호출로 리소스 절약
print("\n[TC-04] Tier 검증 (MULTI_SOURCE 3구 + TELECOM_ONLY 대표 3구 순차 호출)")
# V_SPH_REGION_MASTER에서 서울 25개 구 목록 먼저 조회
rows_meta, _ = run("""
SELECT DISTINCT CITY_CODE FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER
WHERE PROVINCE_CODE = '11' ORDER BY CITY_CODE
""", "TC-04 meta")
if rows_meta:
    all_codes = [r[0] for r in rows_meta]
    print(f"  V_SPH_REGION_MASTER 서울 구 수: {len(all_codes)}")
    results_25.append(check(len(all_codes) == 25, f"25개 구 메타 존재 (실제: {len(all_codes)})"))
else:
    results_25.append(check(False, "TC-04 메타 조회 실패"))
    all_codes = []

# MULTI_SOURCE 3구 검증
for cc in ['11140', '11560', '11650']:
    rows2, _ = run(f"""
SELECT PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('{cc}')):data_tier::STRING AS tier
""", f"TC-04 {cc}")
    tier = rows2[0][0] if rows2 else None
    print(f"  {cc}  tier={tier}")
    results_25.append(check(tier == 'MULTI_SOURCE', f"{cc} tier=MULTI_SOURCE (실제: {tier})"))

# TELECOM_ONLY 대표 3구 (11110=종로구, 11680=강남구, 11740=강동구)
for cc in ['11110', '11680', '11740']:
    rows2, _ = run(f"""
SELECT PARSE_JSON(MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE('{cc}')):data_tier::STRING AS tier
""", f"TC-04 {cc}")
    tier = rows2[0][0] if rows2 else None
    print(f"  {cc}  tier={tier}")
    results_25.append(check(tier == 'TELECOM_ONLY', f"{cc} tier=TELECOM_ONLY (실제: {tier})"))

# ══════════════════════════════════════════════════════════════════════════════
# 최종 요약
# ══════════════════════════════════════════════════════════════════════════════
print("\n" + "="*60)
print("최종 결과 요약")
print("="*60)
pass24 = sum(results_24);  total24 = len(results_24)
pass25 = sum(results_25);  total25 = len(results_25)
print(f"  #24 CALC_ROI          : {pass24}/{total24} PASS")
print(f"  #25 GET_SEGMENT_PROFILE: {pass25}/{total25} PASS")
overall = (pass24 + pass25) == (total24 + total25)
print(f"\n  {'ALL PASS ✓' if overall else '일부 실패 ✗ — 위 로그 확인'}")

cur.close()
conn.close()
