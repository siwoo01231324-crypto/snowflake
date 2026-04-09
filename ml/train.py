"""
ml/train.py — Snowpark ML 이사 수요 예측 모델 학습
이슈: #23

Track A (TELECOM_ONLY, 22구): XGBRegressor, 7 피처
Track B (MULTI_SOURCE,  3구): XGBRegressor, 11 피처 (RICHGO null→0)

피처 엔지니어링:
  - 구별 평균 대비 비율(RATE)로 정규화: 구별 OPEN_COUNT 스케일 차이 제거
  - OPEN_COUNT_RATE = OPEN_COUNT / 해당 구 전체기간 평균 OPEN_COUNT
  - CONTRACT_COUNT, PAYEND_COUNT 동일 정규화
  - SPH/RICHGO 수치 피처도 구별 평균 대비 비율로 정규화
  - TARGET: LEAD(OPEN_COUNT_RATE, 1) — 다음 달 개통률 예측
  - 역변환: 예측률 × 구별 평균 OPEN_COUNT = 절대 예측값

Train/Test: walk_forward (앞 28개월 train, 뒤 6개월 test)
"""
import math

import numpy as np
import pandas as pd
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
from snowflake.snowpark.types import IntegerType, FloatType
from snowflake.snowpark.window import Window

from snowflake.ml.modeling.xgboost import XGBRegressor
from snowflake.ml.registry import Registry

_CITY_W     = Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
_CITY_ALL_W = Window.partition_by("CITY_CODE")   # 정렬 없음 — 구별 전체 평균용

FEATURE_A = [
    "OPEN_COUNT_RATE", "CONTRACT_COUNT_RATE", "PAYEND_COUNT_RATE",
    "MOVE_SIGNAL_INDEX", "MONTH_SIN", "MONTH_COS", "IS_PEAK_SEASON",
    # lag 피처 — 이전 달 / 작년 동월 패턴
    "OPEN_RATE_LAG1", "OPEN_RATE_LAG2", "OPEN_RATE_LAG3", "OPEN_RATE_LAG12",
    "CONTRACT_RATE_LAG1", "CONTRACT_RATE_LAG12",
    "OPEN_RATE_ROLL3",  # 3개월 이동평균
]
FEATURE_B = FEATURE_A + [
    "AVG_INCOME_RATE", "TOTAL_RESIDENTIAL_POP_RATE",
    "TOTAL_CARD_SALES_RATE", "NEW_HOUSING_BALANCE_RATE",
    "AVG_MEME_PRICE_RATE", "AVG_JEONSE_PRICE_RATE",
]
TARGET = "TARGET_NEXT_OPEN_RATE"   # 다음 달 개통률 (구별 평균 대비)


def _safe_rate(col_name: str, mean_col: str):
    """값 / 구별평균. 평균이 0이면 0 반환."""
    return F.iff(
        F.col(mean_col) > F.lit(0),
        F.col(col_name) / F.col(mean_col),
        F.lit(0.0),
    )


def _add_features(df):
    """
    피처 파생 + 구별 평균 정규화:
    1. IS_PEAK_SEASON, MONTH_SIN/COS 파생
    2. null → 0 처리 (SPH/RICHGO 미보유 구간)
    3. 각 수치 피처를 구별 전체기간 평균으로 나눠 RATE 변환
    4. TARGET: LEAD(OPEN_COUNT_RATE, 1)
    """
    month = F.cast(F.substring(F.col("STANDARD_YEAR_MONTH"), 5, 2), IntegerType())

    df = (
        df
        .with_column("MONTH_NUM", month)
        .with_column(
            "IS_PEAK_SEASON",
            F.iff(F.col("MONTH_NUM").isin([3, 4, 9, 10]), F.lit(1.0), F.lit(0.0)),
        )
        .with_column("MONTH_SIN", F.sin(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("MONTH_COS", F.cos(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        # null → 0 (SPH/RICHGO 미보유 구간)
        .with_column("AVG_MEME_PRICE",            F.coalesce(F.col("AVG_MEME_PRICE"),            F.lit(0.0)))
        .with_column("AVG_JEONSE_PRICE",           F.coalesce(F.col("AVG_JEONSE_PRICE"),          F.lit(0.0)))
        .with_column("AVG_INCOME",                 F.coalesce(F.col("AVG_INCOME"),                F.lit(0.0)))
        .with_column("TOTAL_RESIDENTIAL_POP",      F.coalesce(F.col("TOTAL_RESIDENTIAL_POP"),     F.lit(0.0)))
        .with_column("TOTAL_CARD_SALES",           F.coalesce(F.col("TOTAL_CARD_SALES"),          F.lit(0.0)))
        .with_column("NEW_HOUSING_BALANCE_COUNT",  F.coalesce(F.col("NEW_HOUSING_BALANCE_COUNT"), F.lit(0.0)))
        # 구별 전체기간 평균 (역변환에도 사용)
        .with_column("CITY_MEAN_OPEN",       F.avg("OPEN_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_CONTRACT",   F.avg("CONTRACT_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_PAYEND",     F.avg("PAYEND_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_INCOME",     F.avg("AVG_INCOME").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_POP",        F.avg("TOTAL_RESIDENTIAL_POP").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_CARD",       F.avg("TOTAL_CARD_SALES").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_HOUSING",    F.avg("NEW_HOUSING_BALANCE_COUNT").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_MEME",       F.avg("AVG_MEME_PRICE").over(_CITY_ALL_W))
        .with_column("CITY_MEAN_JEONSE",     F.avg("AVG_JEONSE_PRICE").over(_CITY_ALL_W))
        # RATE 변환
        .with_column("OPEN_COUNT_RATE",           _safe_rate("OPEN_COUNT",           "CITY_MEAN_OPEN"))
        .with_column("CONTRACT_COUNT_RATE",        _safe_rate("CONTRACT_COUNT",        "CITY_MEAN_CONTRACT"))
        .with_column("PAYEND_COUNT_RATE",          _safe_rate("PAYEND_COUNT",          "CITY_MEAN_PAYEND"))
        .with_column("AVG_INCOME_RATE",            _safe_rate("AVG_INCOME",            "CITY_MEAN_INCOME"))
        .with_column("TOTAL_RESIDENTIAL_POP_RATE", _safe_rate("TOTAL_RESIDENTIAL_POP", "CITY_MEAN_POP"))
        .with_column("TOTAL_CARD_SALES_RATE",      _safe_rate("TOTAL_CARD_SALES",      "CITY_MEAN_CARD"))
        .with_column("NEW_HOUSING_BALANCE_RATE",   _safe_rate("NEW_HOUSING_BALANCE_COUNT", "CITY_MEAN_HOUSING"))
        .with_column("AVG_MEME_PRICE_RATE",        _safe_rate("AVG_MEME_PRICE",        "CITY_MEAN_MEME"))
        .with_column("AVG_JEONSE_PRICE_RATE",      _safe_rate("AVG_JEONSE_PRICE",      "CITY_MEAN_JEONSE"))
        # lag 피처 — RATE 기준 (구별 정규화 후 lag)
        .with_column("OPEN_RATE_LAG1",    F.lag("OPEN_COUNT_RATE",    1).over(_CITY_W))
        .with_column("OPEN_RATE_LAG2",    F.lag("OPEN_COUNT_RATE",    2).over(_CITY_W))
        .with_column("OPEN_RATE_LAG3",    F.lag("OPEN_COUNT_RATE",    3).over(_CITY_W))
        .with_column("OPEN_RATE_LAG12",   F.lag("OPEN_COUNT_RATE",   12).over(_CITY_W))
        .with_column("CONTRACT_RATE_LAG1",  F.lag("CONTRACT_COUNT_RATE", 1).over(_CITY_W))
        .with_column("CONTRACT_RATE_LAG12", F.lag("CONTRACT_COUNT_RATE",12).over(_CITY_W))
        # 3개월 이동평균 (직접 계산: lag0+lag1+lag2 / 3)
        .with_column(
            "OPEN_RATE_ROLL3",
            (F.col("OPEN_COUNT_RATE")
             + F.coalesce(F.col("OPEN_RATE_LAG1"), F.col("OPEN_COUNT_RATE"))
             + F.coalesce(F.col("OPEN_RATE_LAG2"), F.col("OPEN_COUNT_RATE"))
            ) / F.lit(3.0),
        )
        # lag null → 1.0 (구별 평균 = 1.0, 초기 몇 달 보완)
        .with_column("OPEN_RATE_LAG1",     F.coalesce(F.col("OPEN_RATE_LAG1"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG2",     F.coalesce(F.col("OPEN_RATE_LAG2"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG3",     F.coalesce(F.col("OPEN_RATE_LAG3"),     F.lit(1.0)))
        .with_column("OPEN_RATE_LAG12",    F.coalesce(F.col("OPEN_RATE_LAG12"),    F.lit(1.0)))
        .with_column("CONTRACT_RATE_LAG1", F.coalesce(F.col("CONTRACT_RATE_LAG1"), F.lit(1.0)))
        .with_column("CONTRACT_RATE_LAG12",F.coalesce(F.col("CONTRACT_RATE_LAG12"),F.lit(1.0)))
        # 타겟: 다음 달 개통률
        .with_column(TARGET, F.lead("OPEN_COUNT_RATE", 1).over(_CITY_W))
        .filter(F.col(TARGET).is_not_null())
    )
    return df


def walk_forward_split(df, train_months: int = 28, test_months: int = 6):
    """
    시계열 walk-forward split.
    앞 train_months개월 → train, 이후 test_months개월 → test.
    Returns: (train_df, test_df, train_cutoff_yyyymm)
    """
    all_months = sorted([
        r[0] for r in df.select("STANDARD_YEAR_MONTH").distinct().collect()
    ])
    total = len(all_months)
    if total < train_months + test_months:
        raise ValueError(f"월 수 부족: {total}개월 < train {train_months} + test {test_months}")

    train_cutoff = all_months[train_months - 1]
    test_end     = all_months[train_months + test_months - 1]
    train = df.filter(F.col("STANDARD_YEAR_MONTH") <= F.lit(train_cutoff))
    test  = df.filter(
        (F.col("STANDARD_YEAR_MONTH") >  F.lit(train_cutoff)) &
        (F.col("STANDARD_YEAR_MONTH") <= F.lit(test_end))
    )
    return train, test, train_cutoff


def _mape(y_true: pd.Series, y_pred: pd.Series) -> float:
    """MAPE. y_true == 0인 행 제외."""
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))


def train_track_a(session: Session) -> dict:
    """
    Track A: TELECOM_ONLY 22구, XGBRegressor.
    Returns: {"model": fitted_model, "mape": float, "train_cutoff": str}
    """
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
    df = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("TELECOM_ONLY")))

    train, test, cutoff = walk_forward_split(df)

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        input_cols=FEATURE_A,
        label_cols=[TARGET],
        output_cols=["PREDICTED_OPEN_COUNT"],
    )
    model.fit(train)

    preds = model.predict(test).select(TARGET, "PREDICTED_OPEN_COUNT").to_pandas()
    mape = _mape(preds[TARGET], preds["PREDICTED_OPEN_COUNT"])

    print(f"[Track A] cutoff={cutoff}  test_rows={len(preds)}  MAPE={mape:.2%}  (목표 <30%)")
    return {"model": model, "mape": mape, "train_cutoff": cutoff}


def train_track_b(session: Session) -> dict:
    """
    Track B: MULTI_SOURCE 3구(중·영등포·서초), XGBRegressor.
    RICHGO AVG_MEME_PRICE / AVG_JEONSE_PRICE null → 0 처리 후 학습.
    Returns: {"model": fitted_model, "mape": float, "train_cutoff": str}
    """
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")
    df = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE")))

    train, test, cutoff = walk_forward_split(df)

    model = XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        input_cols=FEATURE_B,
        label_cols=[TARGET],
        output_cols=["PREDICTED_OPEN_COUNT"],
    )
    model.fit(train)

    preds = model.predict(test).select(TARGET, "PREDICTED_OPEN_COUNT").to_pandas()
    mape = _mape(preds[TARGET], preds["PREDICTED_OPEN_COUNT"])

    print(f"[Track B] cutoff={cutoff}  test_rows={len(preds)}  MAPE={mape:.2%}  (목표 <25%)")
    return {"model": model, "mape": mape, "train_cutoff": cutoff}


def save_models(session: Session, result_a: dict, result_b: dict) -> None:
    """학습된 모델을 Snowflake Model Registry에 저장."""
    reg = Registry(
        session=session,
        database_name="MOVING_INTEL",
        schema_name="ANALYTICS",
    )

    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")

    df_a = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("TELECOM_ONLY")))
    train_a, _, _ = walk_forward_split(df_a)
    reg.log_model(
        result_a["model"],
        model_name="MOVE_DEMAND_TRACK_A",
        version_name="v1",
        sample_input_data=train_a.select(FEATURE_A),
        comment=f"Track A XGBRegressor  MAPE={result_a['mape']:.2%}",
    )

    df_b = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE")))
    train_b, _, _ = walk_forward_split(df_b)
    reg.log_model(
        result_b["model"],
        model_name="MOVE_DEMAND_TRACK_B",
        version_name="v1",
        sample_input_data=train_b.select(FEATURE_B),
        comment=f"Track B XGBRegressor  MAPE={result_b['mape']:.2%}",
    )

    print("[save_models] Track A/B Registry 저장 완료")


def train_move_demand_model(session: Session) -> tuple:
    """
    test_08_ml_training.py 호환 인터페이스.
    Returns: (model, {"mape": float})
      - model: Track B (더 풍부한 피처, 3구 전용)
      - mape: Track A/B 중 낮은 값
    """
    result_a = train_track_a(session)
    result_b = train_track_b(session)

    print(f"\n{'='*40}")
    print(f"  Track A MAPE: {result_a['mape']:.2%}  (목표 <30%)")
    print(f"  Track B MAPE: {result_b['mape']:.2%}  (목표 <25%)")
    print(f"{'='*40}")

    # Track A(TELECOM_ONLY)와 Track B(MULTI_SOURCE)는 피처셋이 달라 상호 대체 불가.
    # 인터페이스 호환용으로 Track B 모델(풀 피처)을 반환한다.
    return result_b["model"], {"mape": result_b["mape"]}
