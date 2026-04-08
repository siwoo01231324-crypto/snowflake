"""
test_06_snowpark.py — MART_MOVE_ANALYSIS 통합 마트 Snowpark 단위 테스트
이슈: #21
"""
import pytest
import snowflake.snowpark.functions as F


def test_build_integrated_mart_row_count(session):
    """TC-01: 마트에 데이터가 존재하는지"""
    from pipelines.preprocessing import build_integrated_mart
    result = build_integrated_mart(session)
    assert result.count() > 0, "마트에 데이터 없음"


def test_build_integrated_mart_25_districts(session):
    """TC-02: 25개 구 전체 커버"""
    from pipelines.preprocessing import build_integrated_mart
    result = build_integrated_mart(session)
    gu_count = result.select("CITY_CODE").distinct().count()
    assert gu_count == 25, f"25개 구 미달: {gu_count}"


def test_build_integrated_mart_no_null_keys(session):
    """TC-03: 키 컬럼 NULL 0건"""
    from pipelines.preprocessing import build_integrated_mart
    result = build_integrated_mart(session)
    null_count = result.filter(
        F.col("CITY_CODE").is_null() | F.col("STANDARD_YEAR_MONTH").is_null()
    ).count()
    assert null_count == 0, f"키 컬럼 NULL {null_count}건"


def test_build_integrated_mart_data_tier(session):
    """TC-06: DATA_TIER 분포 (MULTI_SOURCE=3, TELECOM_ONLY=22)"""
    from pipelines.preprocessing import build_integrated_mart
    result = build_integrated_mart(session)
    multi = result.filter(F.col("DATA_TIER") == "MULTI_SOURCE") \
                  .select("CITY_CODE").distinct().count()
    telecom = result.filter(F.col("DATA_TIER") == "TELECOM_ONLY") \
                    .select("CITY_CODE").distinct().count()
    assert multi == 3, f"MULTI_SOURCE 구 수 {multi} != 3"
    assert telecom == 22, f"TELECOM_ONLY 구 수 {telecom} != 22"
