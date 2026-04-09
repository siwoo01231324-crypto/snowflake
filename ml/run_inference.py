"""
ml/run_inference.py — Registry에서 모델 로드 → 예측 → PREDICTED_MOVE_DEMAND 갱신

사용법:
  ml_venv\Scripts\python ml\run_inference.py
"""
import math, sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

import numpy as np
import pandas as pd
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
from snowflake.snowpark.types import IntegerType
from snowflake.snowpark.window import Window
from snowflake.ml.registry import Registry

from pathlib import Path

def _load_connection() -> dict:
    try:
        import tomllib
        with open(Path.home() / ".snowflake" / "connections.toml", "rb") as f:
            cfg = tomllib.load(f)["default"]
    except ImportError:
        import re
        raw = (Path.home() / ".snowflake" / "connections.toml").read_text()
        cfg = dict(re.findall(r'(\w+)\s*=\s*"([^"]+)"', raw))
    return dict(
        account=cfg["account"], user=cfg["user"], password=cfg["password"],
        warehouse=cfg.get("warehouse", "MOVING_INTEL_WH"),
        database="MOVING_INTEL", schema="ANALYTICS",
    )

CONNECTION = _load_connection()

_CITY_W     = Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
_CITY_ALL_W = Window.partition_by("CITY_CODE")

FEATURE_A = [
    "OPEN_COUNT_RATE", "CONTRACT_COUNT_RATE", "PAYEND_COUNT_RATE",
    "MOVE_SIGNAL_INDEX", "MONTH_SIN", "MONTH_COS", "IS_PEAK_SEASON",
    "OPEN_RATE_LAG1", "OPEN_RATE_LAG2", "OPEN_RATE_LAG3", "OPEN_RATE_LAG12",
    "CONTRACT_RATE_LAG1", "CONTRACT_RATE_LAG12", "OPEN_RATE_ROLL3",
]
FEATURE_B = FEATURE_A + [
    "AVG_INCOME_RATE", "TOTAL_RESIDENTIAL_POP_RATE",
    "TOTAL_CARD_SALES_RATE", "NEW_HOUSING_BALANCE_RATE",
    "AVG_MEME_PRICE_RATE", "AVG_JEONSE_PRICE_RATE",
]


def _safe_rate(col, mean_col):
    return F.iff(F.col(mean_col) > F.lit(0), F.col(col) / F.col(mean_col), F.lit(0.0))


def add_features(df):
    """인퍼런스용 피처 계산 (TARGET 파생·필터 없음)."""
    month = F.cast(F.substring(F.col("STANDARD_YEAR_MONTH"), 5, 2), IntegerType())
    return (
        df
        .with_column("MONTH_NUM", month)
        .with_column("IS_PEAK_SEASON",
            F.iff(F.col("MONTH_NUM").isin([3, 4, 9, 10]), F.lit(1.0), F.lit(0.0)))
        .with_column("MONTH_SIN", F.sin(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("MONTH_COS", F.cos(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("AVG_MEME_PRICE",           F.coalesce(F.col("AVG_MEME_PRICE"),           F.lit(0.0)))
        .with_column("AVG_JEONSE_PRICE",          F.coalesce(F.col("AVG_JEONSE_PRICE"),         F.lit(0.0)))
        .with_column("AVG_INCOME",                F.coalesce(F.col("AVG_INCOME"),               F.lit(0.0)))
        .with_column("TOTAL_RESIDENTIAL_POP",     F.coalesce(F.col("TOTAL_RESIDENTIAL_POP"),    F.lit(0.0)))
        .with_column("TOTAL_CARD_SALES",          F.coalesce(F.col("TOTAL_CARD_SALES"),         F.lit(0.0)))
        .with_column("NEW_HOUSING_BALANCE_COUNT", F.coalesce(F.col("NEW_HOUSING_BALANCE_COUNT"),F.lit(0.0)))
        .with_column("CITY_MEAN_OPEN",     F.avg("OPEN_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_CONTRACT", F.avg("CONTRACT_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_PAYEND",   F.avg("PAYEND_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_INCOME",   F.avg("AVG_INCOME").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_POP",      F.avg("TOTAL_RESIDENTIAL_POP").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_CARD",     F.avg("TOTAL_CARD_SALES").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_HOUSING",  F.avg("NEW_HOUSING_BALANCE_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_MEME",     F.avg("AVG_MEME_PRICE").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_JEONSE",   F.avg("AVG_JEONSE_PRICE").over(_CITY_ALL_W))
        .with_column("OPEN_COUNT_RATE",           _safe_rate("OPEN_COUNT",           "CITY_MEAN_OPEN"))
        .with_column("CONTRACT_COUNT_RATE",        _safe_rate("CONTRACT_COUNT",        "CITY_MEAN_CONTRACT"))
        .with_column("PAYEND_COUNT_RATE",          _safe_rate("PAYEND_COUNT",          "CITY_MEAN_PAYEND"))
        .with_column("AVG_INCOME_RATE",            _safe_rate("AVG_INCOME",            "CITY_MEAN_INCOME"))
        .with_column("TOTAL_RESIDENTIAL_POP_RATE", _safe_rate("TOTAL_RESIDENTIAL_POP", "CITY_MEAN_POP"))
        .with_column("TOTAL_CARD_SALES_RATE",      _safe_rate("TOTAL_CARD_SALES",      "CITY_MEAN_CARD"))
        .with_column("NEW_HOUSING_BALANCE_RATE",   _safe_rate("NEW_HOUSING_BALANCE_COUNT","CITY_MEAN_HOUSING"))
        .with_column("AVG_MEME_PRICE_RATE",        _safe_rate("AVG_MEME_PRICE",        "CITY_MEAN_MEME"))
        .with_column("AVG_JEONSE_PRICE_RATE",      _safe_rate("AVG_JEONSE_PRICE",      "CITY_MEAN_JEONSE"))
        .with_column("OPEN_RATE_LAG1",    F.lag("OPEN_COUNT_RATE",    1).over(_CITY_W))
        .with_column("OPEN_RATE_LAG2",    F.lag("OPEN_COUNT_RATE",    2).over(_CITY_W))
        .with_column("OPEN_RATE_LAG3",    F.lag("OPEN_COUNT_RATE",    3).over(_CITY_W))
        .with_column("OPEN_RATE_LAG12",   F.lag("OPEN_COUNT_RATE",   12).over(_CITY_W))
        .with_column("CONTRACT_RATE_LAG1",  F.lag("CONTRACT_COUNT_RATE", 1).over(_CITY_W))
        .with_column("CONTRACT_RATE_LAG12", F.lag("CONTRACT_COUNT_RATE",12).over(_CITY_W))
        .with_column("OPEN_RATE_ROLL3",
            (F.col("OPEN_COUNT_RATE")
             + F.coalesce(F.col("OPEN_RATE_LAG1"), F.col("OPEN_COUNT_RATE"))
             + F.coalesce(F.col("OPEN_RATE_LAG2"), F.col("OPEN_COUNT_RATE"))
            ) / F.lit(3.0))
        .with_column("OPEN_RATE_LAG1",     F.coalesce(F.col("OPEN_RATE_LAG1"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG2",     F.coalesce(F.col("OPEN_RATE_LAG2"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG3",     F.coalesce(F.col("OPEN_RATE_LAG3"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG12",    F.coalesce(F.col("OPEN_RATE_LAG12"),    F.lit(1.0)))
        .with_column("CONTRACT_RATE_LAG1", F.coalesce(F.col("CONTRACT_RATE_LAG1"), F.lit(1.0)))
        .with_column("CONTRACT_RATE_LAG12",F.coalesce(F.col("CONTRACT_RATE_LAG12"),F.lit(1.0)))
        .with_column("MOVE_SIGNAL_INDEX",  F.coalesce(F.col("MOVE_SIGNAL_INDEX"),  F.lit(1.0)))
    )


def main():
    print("연결 중...")
    session = Session.builder.configs(CONNECTION).create()
    print("연결 완료")

    reg = Registry(session=session, database_name="MOVING_INTEL", schema_name="ANALYTICS")

    print("\n[1/3] Registry에서 모델 로드...")
    mv_a = reg.get_model("MOVE_DEMAND_TRACK_A").version("v1")
    mv_b = reg.get_model("MOVE_DEMAND_TRACK_B").version("v1")
    print("  Track A, B 로드 완료")

    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
    all_months = sorted([r[0] for r in mart.select("STANDARD_YEAR_MONTH").distinct().collect()])
    latest = all_months[-1]
    print(f"  기준 월: {latest}")

    print("\n[2/3] 피처 계산 + 예측...")
    # Track A (TELECOM_ONLY 22구)
    feat_a = add_features(mart.filter(F.col("DATA_TIER") == F.lit("TELECOM_ONLY")))
    latest_a = feat_a.filter(F.col("STANDARD_YEAR_MONTH") == F.lit(latest))
    # to_pandas()로 전체 collect 후 pandas에서 처리
    df_a_raw = mv_a.run(latest_a, function_name="predict").to_pandas()
    print("  Track A 출력 컬럼:", list(df_a_raw.columns))
    pred_col_a = [c for c in df_a_raw.columns if "PRED" in c.upper() or "OUTPUT" in c.upper()][-1]
    print(f"  예측 컬럼: {pred_col_a}")
    df_a_raw["PREDICTED_OPEN_COUNT"] = (df_a_raw[pred_col_a] * df_a_raw["CITY_MEAN_OPEN"]).clip(lower=0)
    df_a = df_a_raw[["CITY_KOR_NAME", "OPEN_COUNT", "CITY_MEAN_OPEN", "PREDICTED_OPEN_COUNT"]]

    # Track B (MULTI_SOURCE 3구)
    feat_b = add_features(mart.filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE")))
    latest_b = feat_b.filter(F.col("STANDARD_YEAR_MONTH") == F.lit(latest))
    df_b_raw = mv_b.run(latest_b, function_name="predict").to_pandas()
    print("  Track B 출력 컬럼:", list(df_b_raw.columns))
    pred_col_b = [c for c in df_b_raw.columns if "PRED" in c.upper() or "OUTPUT" in c.upper()][-1]
    df_b_raw["PREDICTED_OPEN_COUNT"] = (df_b_raw[pred_col_b] * df_b_raw["CITY_MEAN_OPEN"]).clip(lower=0)
    df_b = df_b_raw[["CITY_KOR_NAME", "OPEN_COUNT", "CITY_MEAN_OPEN", "PREDICTED_OPEN_COUNT"]]

    all_preds = pd.concat([df_a, df_b], ignore_index=True)
    print(f"  예측 완료: {len(all_preds)}구")
    print(all_preds[["CITY_KOR_NAME", "OPEN_COUNT", "PREDICTED_OPEN_COUNT"]].to_string())

    print("\n[3/3] PREDICTED_MOVE_DEMAND 테이블 갱신...")
    rows = [[row["CITY_KOR_NAME"], float(row["PREDICTED_OPEN_COUNT"])]
            for _, row in all_preds.iterrows()]
    pred_sf = session.create_dataframe(rows, schema=["CITY_KOR_NAME", "DEMAND_SCORE"])
    pred_sf.write.mode("overwrite").save_as_table("MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND")
    print("  완료!")

    print(f"\n{'='*50}")
    print(f"  기준 월: {latest}")
    print(f"  예측 구 수: {len(all_preds)}")
    print(f"{'='*50}")
    session.close()


if __name__ == "__main__":
    main()
