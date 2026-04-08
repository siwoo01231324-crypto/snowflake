"""
move_signal.py — MOVE_SIGNAL_INDEX 3종 시그널 융합 + 교차검증
이슈: #22

Dual-Tier 분기:
  TELECOM_ONLY (22구): norm(CONTRACT_COUNT) 단일 프록시
  MULTI_SOURCE  (3구): w1×norm(S1) + w2×norm(ΔS2) + w4×norm(ΔS4)
    S1=CONTRACT_COUNT, S2=TOTAL_RESIDENTIAL_POP, S4=ELECTRONICS_FURNITURE_SALES
    S3(NEW_HOUSING_BALANCE_COUNT) 제외: r(S1↔S3)=-0.215 (dev_spec 규칙: "대출 시그널 제외")
"""
import numpy as np
import pandas as pd
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
from snowflake.snowpark.window import Window

# 가중치 (dev_spec A4-1, MULTI_SOURCE 전용, 3종 융합 w1+w2+w4=1.0)
# S3 제외 후 비례 재조정: 0.35→0.45, 0.25→0.35, 0.15→0.20
W1, W2, W4 = 0.45, 0.35, 0.20

_CITY_W = Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
_GLOBAL_W = Window.partition_by(F.lit(1))


def _minmax(col_expr):
    min_v = F.min(col_expr).over(_GLOBAL_W)
    max_v = F.max(col_expr).over(_GLOBAL_W)
    return F.iff(max_v == min_v, F.lit(0.0), (col_expr - min_v) / (max_v - min_v))


def _pct_change(col_name, prev_col_name):
    """전월 대비 변화율. 전월/당월 NULL 또는 전월 0이면 0.0 반환."""
    return F.iff(
        F.col(prev_col_name).is_not_null()
        & (F.col(prev_col_name) != F.lit(0))
        & F.col(col_name).is_not_null(),
        (F.col(col_name) - F.col(prev_col_name)) / F.col(prev_col_name),
        F.lit(0.0),
    )


def _build_mart_with_signals(mart):
    """Δ 계산 + CARRYOVER_RATIO + MOVE_SIGNAL_INDEX 컬럼을 mart DataFrame에 추가해 반환."""
    mart = (
        mart
        .with_column("PREV_RES_POP", F.lag("TOTAL_RESIDENTIAL_POP").over(_CITY_W))
        .with_column("PREV_ELEC", F.lag("ELECTRONICS_FURNITURE_SALES").over(_CITY_W))
        .with_column("D_RESIDENTIAL_POP", _pct_change("TOTAL_RESIDENTIAL_POP", "PREV_RES_POP"))
        .with_column("D_ELEC_FURNITURE", _pct_change("ELECTRONICS_FURNITURE_SALES", "PREV_ELEC"))
        .with_column(
            "CARRYOVER_RATIO",
            F.iff(
                F.col("CONTRACT_COUNT") != F.lit(0),
                (F.col("CONTRACT_COUNT") - F.col("OPEN_COUNT")) / F.col("CONTRACT_COUNT"),
                F.lit(None),
            ),
        )
    )
    norm_s1 = _minmax(F.col("CONTRACT_COUNT"))
    norm_s2 = _minmax(F.col("D_RESIDENTIAL_POP"))
    norm_s4 = _minmax(F.col("D_ELEC_FURNITURE"))
    return mart.with_column(
        "MOVE_SIGNAL_INDEX",
        F.when(F.col("DATA_TIER") == F.lit("TELECOM_ONLY"), norm_s1)
         .when(
             F.col("DATA_TIER") == F.lit("MULTI_SOURCE"),
             F.lit(W1) * norm_s1 + F.lit(W2) * norm_s2 + F.lit(W4) * norm_s4,
         )
         .otherwise(F.lit(None)),
    )


def compute_move_signal_index(session: Session):
    """
    MART_MOVE_ANALYSIS에서 MOVE_SIGNAL_INDEX를 계산해 반환.
    반환: DataFrame (CITY_CODE, STANDARD_YEAR_MONTH, DATA_TIER, MOVE_SIGNAL_INDEX, CARRYOVER_RATIO)
    #23 ML UDF 입력 피처로 직접 사용 가능.
    """
    mart = _build_mart_with_signals(session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS"))
    return mart.select("CITY_CODE", "STANDARD_YEAR_MONTH", "DATA_TIER", "MOVE_SIGNAL_INDEX", "CARRYOVER_RATIO")


def update_mart_with_signal_index(session: Session) -> None:
    """MART_MOVE_ANALYSIS에 MOVE_SIGNAL_INDEX, CARRYOVER_RATIO 컬럼을 추가해 재저장."""
    mart = _build_mart_with_signals(session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS"))
    mart.drop("PREV_RES_POP", "PREV_ELEC", "D_RESIDENTIAL_POP", "D_ELEC_FURNITURE").write.save_as_table(
        "MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS",
        mode="overwrite",
    )


def validate_move_signals(session: Session) -> pd.DataFrame:
    """
    MULTI_SOURCE 3구 한정 — 3종 시그널 간 상관 행렬 반환 (S3 제외).
    반환: 3×3 pandas DataFrame (상관 행렬)
    """
    multi = (
        session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
        .filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE"))
        .select("STANDARD_YEAR_MONTH", "CITY_CODE",
                "CONTRACT_COUNT", "TOTAL_RESIDENTIAL_POP", "ELECTRONICS_FURNITURE_SALES")
        .order_by("CITY_CODE", "STANDARD_YEAR_MONTH")
        .to_pandas()
    )
    for col in ["TOTAL_RESIDENTIAL_POP", "ELECTRONICS_FURNITURE_SALES"]:
        multi[f"D_{col}"] = multi.groupby("CITY_CODE")[col].pct_change()

    signal_cols = {
        "S1_CONTRACT":  "CONTRACT_COUNT",
        "S2_D_RES_POP": "D_TOTAL_RESIDENTIAL_POP",
        "S4_D_ELEC":    "D_ELECTRONICS_FURNITURE_SALES",
    }
    subset = multi[list(signal_cols.values())].dropna()
    corr = subset.corr()
    corr.index = list(signal_cols.keys())
    corr.columns = list(signal_cols.keys())
    return corr
