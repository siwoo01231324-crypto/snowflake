"""
preprocessing.py — MART_MOVE_ANALYSIS 통합 마트 생성 파이프라인
이슈: #21
"""
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
from snowflake.snowpark.types import StringType


# SPH/RICHGO 데이터가 존재하는 3개 구 (해커톤 Marketplace 샘플)
MULTI_SOURCE_CITIES = ["11140", "11560", "11650"]  # 중구, 영등포구, 서초구


def build_integrated_mart(session: Session):
    """
    25개 구 × 월 spine 기반 통합 마트 생성.

    조인 전략:
    - Spine: M_SCCO_MST(25개 구) × 아정당 월(DATE→YYYYMM)
    - LEFT JOIN: 아정당(25구), SPH유동인구(3구), SPH카드(3구), SPH자산(3구), RICHGO(3구)
    - DATA_TIER: 'MULTI_SOURCE'(3구) / 'TELECOM_ONLY'(22구)
    """

    # 1. Spine: 25개 구 × 아정당 월 범위
    district_spine = session.sql(
        "SELECT DISTINCT CITY_CODE, CITY_KOR_NAME, PROVINCE_CODE "
        "FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER"
    )

    # 텔레콤 데이터가 25개 구 모두 존재하는 월만 사용 (불완전 월 제외)
    # 결과: 202307~202604 (34개월) — 양 끝 데이터 갭 제거
    month_spine = session.sql(
        "SELECT STANDARD_YEAR_MONTH "
        "FROM MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED "
        "WHERE CITY_CODE IS NOT NULL "
        "GROUP BY STANDARD_YEAR_MONTH "
        "HAVING COUNT(DISTINCT CITY_CODE) = 25"
    )

    spine = district_spine.cross_join(month_spine)

    # 2. 아정당 (25개 구)
    telecom = session.sql(
        "SELECT CITY_CODE, STANDARD_YEAR_MONTH, "
        "  SUM(OPEN_COUNT) AS OPEN_COUNT, "
        "  SUM(CONTRACT_COUNT) AS CONTRACT_COUNT, "
        "  SUM(PAYEND_COUNT) AS PAYEND_COUNT "
        "FROM MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED "
        "GROUP BY CITY_CODE, STANDARD_YEAR_MONTH"
    )

    # 3. SPH 유동인구 (3개 구, 동→구 집계)
    sph_pop = session.sql(
        "SELECT CITY_CODE, STANDARD_YEAR_MONTH, "
        "  SUM(RESIDENTIAL_POPULATION) AS TOTAL_RESIDENTIAL_POP, "
        "  SUM(WORKING_POPULATION) AS TOTAL_WORKING_POP, "
        "  SUM(VISITING_POPULATION) AS TOTAL_VISITING_POP "
        "FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP "
        "GROUP BY CITY_CODE, STANDARD_YEAR_MONTH"
    )

    # 4. SPH 카드매출 (3개 구, 동→구 집계)
    sph_card = session.sql(
        "SELECT CITY_CODE, STANDARD_YEAR_MONTH, "
        "  SUM(TOTAL_SALES) AS TOTAL_CARD_SALES, "
        "  SUM(ELECTRONICS_FURNITURE_SALES) AS ELECTRONICS_FURNITURE_SALES "
        "FROM MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES "
        "GROUP BY CITY_CODE, STANDARD_YEAR_MONTH"
    )

    # 5. SPH 자산소득 (3개 구, 동→구 집계)
    sph_income = session.sql(
        "SELECT CITY_CODE, STANDARD_YEAR_MONTH, "
        "  AVG(AVERAGE_INCOME) AS AVG_INCOME, "
        "  AVG(AVERAGE_ASSET_AMOUNT) AS AVG_ASSET, "
        "  SUM(NEW_HOUSING_BALANCE_COUNT) AS NEW_HOUSING_BALANCE_COUNT "
        "FROM MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME "
        "GROUP BY CITY_CODE, STANDARD_YEAR_MONTH"
    )

    # 6. RICHGO 시세 (3개 구, BJD→구 집계, DATE→YYYYMM)
    richgo = session.sql(
        "SELECT b.CITY_CODE, "
        "  TO_CHAR(r.YYYYMMDD, 'YYYYMM') AS STANDARD_YEAR_MONTH, "
        "  AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG) AS AVG_MEME_PRICE, "
        "  AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG) AS AVG_JEONSE_PRICE, "
        "  SUM(r.TOTAL_HOUSEHOLDS) AS TOTAL_HOUSEHOLDS "
        "FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r "
        "JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP b "
        "  ON r.BJD_CODE = b.BJD_CODE "
        "GROUP BY b.CITY_CODE, TO_CHAR(r.YYYYMMDD, 'YYYYMM')"
    )

    # 7. LEFT JOIN 조립
    mart = (
        spine
        .join(telecom, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_pop, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_card, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_income, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(richgo, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
    )

    # 8. DATA_TIER 컬럼
    mart = mart.with_column(
        "DATA_TIER",
        F.when(F.col("CITY_CODE").isin(MULTI_SOURCE_CITIES), F.lit("MULTI_SOURCE"))
         .otherwise(F.lit("TELECOM_ONLY"))
    )

    # 9. 저장
    mart.write.save_as_table(
        "MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS",
        mode="overwrite"
    )
    return mart
