"""cortex.py — Snowflake Cortex AI Functions 헬퍼 (이슈 #27)"""
from __future__ import annotations
from typing import TypedDict
from snowflake.snowpark import Session

# 서울 25구 CITY_CODE allowlist (실데이터 검증 기반)
# Tier 분류(MULTI_SOURCE 3구 vs TELECOM_ONLY 22구)는 MART_MOVE_ANALYSIS.DATA_TIER
# 컬럼에서 읽어오므로 Python 측에서는 별도 리스트로 보관하지 않는다.
SEOUL_CITY_CODES: frozenset[str] = frozenset({
    "11110", "11140", "11170", "11200", "11215", "11230", "11260", "11290", "11305",
    "11320", "11350", "11380", "11410", "11440", "11470", "11500", "11530", "11545",
    "11560", "11590", "11620", "11650", "11680", "11710", "11740",
})

TIER_BADGE: dict[str, str] = {
    "MULTI_SOURCE": "정밀 Tier (4종 시그널)",
    "TELECOM_ONLY": "근사 Tier (통신 단일)",
}


def _validate_city_code(city_code: str) -> str:
    if city_code not in SEOUL_CITY_CODES:
        raise ValueError(f"Invalid city_code: {city_code!r}")
    return city_code


def _validate_year_month(ym: str) -> str:
    # 형식: YYYYMM (6자리 ASCII 숫자, 월 01-12)
    if not (isinstance(ym, str) and len(ym) == 6 and ym.isascii() and ym.isdigit()):
        raise ValueError(f"Invalid year_month: {ym!r} (expected YYYYMM)")
    month = int(ym[4:])
    if not 1 <= month <= 12:
        raise ValueError(f"Invalid year_month: {ym!r} (month must be 01-12)")
    return ym


class DistrictInsight(TypedDict):
    city_code: str
    city_name: str
    data_tier: str
    tier_badge: str
    year_month: str
    open_count: int | None
    yoy_pct: float | None
    ai_insight: str


class DemandGrade(TypedDict):
    city_code: str
    city_name: str
    data_tier: str
    tier_badge: str
    year_month: str
    demand_grade: str


class SimilarDistrict(TypedDict):
    city_code: str
    city_name: str
    data_tier: str
    tier_badge: str
    similarity: float


def get_district_insight(session: Session, city_code: str, year_month: str) -> DistrictInsight:
    """V_AI_DISTRICT_INSIGHTS 단일 행 조회."""
    city_code = _validate_city_code(city_code)
    year_month = _validate_year_month(year_month)
    rows = session.sql(
        """
        SELECT CITY_CODE, CITY_KOR_NAME, DATA_TIER, STANDARD_YEAR_MONTH,
               OPEN_COUNT, YOY_PCT, AI_INSIGHT
        FROM MOVING_INTEL.ANALYTICS.V_AI_DISTRICT_INSIGHTS
        WHERE CITY_CODE = ? AND STANDARD_YEAR_MONTH = ?
        """,
        params=[city_code, year_month],
    ).collect()
    if not rows:
        raise RuntimeError(f"No insight for {city_code} / {year_month}")
    r = rows[0]
    tier = r["DATA_TIER"]
    return DistrictInsight(
        city_code=r["CITY_CODE"],
        city_name=r["CITY_KOR_NAME"],
        data_tier=tier,
        tier_badge=TIER_BADGE[tier],
        year_month=r["STANDARD_YEAR_MONTH"],
        open_count=r["OPEN_COUNT"],
        yoy_pct=r["YOY_PCT"],
        ai_insight=r["AI_INSIGHT"],
    )


def classify_demand(session: Session, city_code: str, year_month: str) -> DemandGrade:
    """V_AI_DEMAND_GRADE 단일 행 조회."""
    city_code = _validate_city_code(city_code)
    year_month = _validate_year_month(year_month)
    rows = session.sql(
        """
        SELECT CITY_CODE, CITY_KOR_NAME, DATA_TIER, STANDARD_YEAR_MONTH, DEMAND_GRADE
        FROM MOVING_INTEL.ANALYTICS.V_AI_DEMAND_GRADE
        WHERE CITY_CODE = ? AND STANDARD_YEAR_MONTH = ?
        """,
        params=[city_code, year_month],
    ).collect()
    if not rows:
        raise RuntimeError(f"No grade for {city_code} / {year_month}")
    r = rows[0]
    tier = r["DATA_TIER"]
    return DemandGrade(
        city_code=r["CITY_CODE"],
        city_name=r["CITY_KOR_NAME"],
        data_tier=tier,
        tier_badge=TIER_BADGE[tier],
        year_month=r["STANDARD_YEAR_MONTH"],
        demand_grade=r["DEMAND_GRADE"] or "알수없음",
    )


def find_similar_districts(
    session: Session, city_code: str, top_k: int = 5
) -> list[SimilarDistrict]:
    """SP_FIND_SIMILAR_DISTRICTS(target, top_k) 호출."""
    city_code = _validate_city_code(city_code)
    if not (1 <= top_k <= 24):
        raise ValueError(f"top_k must be 1..24, got {top_k}")
    rows = session.sql(
        "CALL MOVING_INTEL.ANALYTICS.SP_FIND_SIMILAR_DISTRICTS(?, ?)",
        params=[city_code, top_k],
    ).collect()
    result: list[SimilarDistrict] = []
    for r in rows:
        tier = r["DATA_TIER"]
        result.append(SimilarDistrict(
            city_code=r["CITY_CODE"],
            city_name=r["CITY_KOR_NAME"],
            data_tier=tier,
            tier_badge=TIER_BADGE[tier],
            similarity=float(r["SIMILARITY"]),
        ))
    return result


def aggregate_state_summary(
    session: Session, year_month: str, install_state: str = "서울"
) -> str:
    """V_AI_STATE_SUMMARY 단일 월 조회."""
    year_month = _validate_year_month(year_month)
    if install_state not in {"서울"}:
        raise ValueError(f"install_state not supported: {install_state!r}")
    rows = session.sql(
        """SELECT STATE_SUMMARY FROM MOVING_INTEL.ANALYTICS.V_AI_STATE_SUMMARY
           WHERE STANDARD_YEAR_MONTH = ?""",
        params=[year_month],
    ).collect()
    if not rows:
        raise RuntimeError(f"No state summary for {year_month}")
    return rows[0]["STATE_SUMMARY"]
