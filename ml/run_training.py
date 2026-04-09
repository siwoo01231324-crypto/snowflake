"""
ml/run_training.py — ML 모델 학습 + 예측 테이블 업데이트 실행 스크립트

사용법:
  python ml/run_training.py

Python 3.11 venv 필요:
  ml_venv\Scripts\python ml\run_training.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import math
import numpy as np
import pandas as pd
from snowflake.snowpark import Session
import snowflake.snowpark.functions as F
from snowflake.snowpark.types import IntegerType
from snowflake.snowpark.window import Window
from snowflake.ml.modeling.xgboost import XGBRegressor
from snowflake.ml.registry import Registry

# ── 연결 설정 (~/.snowflake/connections.toml) ────────────────
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

# ── 피처 정의 ────────────────────────────────────────────────
_CITY_W     = Window.partition_by("CITY_CODE").order_by("STANDARD_YEAR_MONTH")
_CITY_ALL_W = Window.partition_by("CITY_CODE")

FEATURE_A = [
    "OPEN_COUNT_RATE", "CONTRACT_COUNT_RATE", "PAYEND_COUNT_RATE",
    "MOVE_SIGNAL_INDEX", "MONTH_SIN", "MONTH_COS", "IS_PEAK_SEASON",
    "OPEN_RATE_LAG1", "OPEN_RATE_LAG2", "OPEN_RATE_LAG3", "OPEN_RATE_LAG12",
    "CONTRACT_RATE_LAG1", "CONTRACT_RATE_LAG12",
    "OPEN_RATE_ROLL3",
]
FEATURE_B = FEATURE_A + [
    "AVG_INCOME_RATE", "TOTAL_RESIDENTIAL_POP_RATE",
    "TOTAL_CARD_SALES_RATE", "NEW_HOUSING_BALANCE_RATE",
    "AVG_MEME_PRICE_RATE", "AVG_JEONSE_PRICE_RATE",
]
TARGET = "TARGET_NEXT_OPEN_RATE"


def _safe_rate(col_name, mean_col):
    return F.iff(F.col(mean_col) > F.lit(0), F.col(col_name) / F.col(mean_col), F.lit(0.0))


def _add_features(df):
    month = F.cast(F.substring(F.col("STANDARD_YEAR_MONTH"), 5, 2), IntegerType())
    df = (
        df
        .with_column("MONTH_NUM", month)
        .with_column("IS_PEAK_SEASON",
            F.iff(F.col("MONTH_NUM").isin([3, 4, 9, 10]), F.lit(1.0), F.lit(0.0)))
        .with_column("MONTH_SIN", F.sin(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("MONTH_COS", F.cos(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("AVG_MEME_PRICE",            F.coalesce(F.col("AVG_MEME_PRICE"),            F.lit(0.0)))
        .with_column("AVG_JEONSE_PRICE",           F.coalesce(F.col("AVG_JEONSE_PRICE"),          F.lit(0.0)))
        .with_column("AVG_INCOME",                 F.coalesce(F.col("AVG_INCOME"),                F.lit(0.0)))
        .with_column("TOTAL_RESIDENTIAL_POP",      F.coalesce(F.col("TOTAL_RESIDENTIAL_POP"),     F.lit(0.0)))
        .with_column("TOTAL_CARD_SALES",           F.coalesce(F.col("TOTAL_CARD_SALES"),          F.lit(0.0)))
        .with_column("NEW_HOUSING_BALANCE_COUNT",  F.coalesce(F.col("NEW_HOUSING_BALANCE_COUNT"), F.lit(0.0)))
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
        .with_column("NEW_HOUSING_BALANCE_RATE",   _safe_rate("NEW_HOUSING_BALANCE_COUNT", "CITY_MEAN_HOUSING"))
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
        .with_column("MOVE_SIGNAL_INDEX",
            F.coalesce(F.col("MOVE_SIGNAL_INDEX"), F.lit(1.0)))
        .with_column(TARGET, F.lead("OPEN_COUNT_RATE", 1).over(_CITY_W))
        .filter(F.col(TARGET).is_not_null())
    )
    return df


def _add_features_no_target(df):
    """인퍼런스용: _add_features와 동일하지만 TARGET 파생·필터 없음."""
    month = F.cast(F.substring(F.col("STANDARD_YEAR_MONTH"), 5, 2), IntegerType())
    df = (
        df
        .with_column("MONTH_NUM", month)
        .with_column("IS_PEAK_SEASON",
            F.iff(F.col("MONTH_NUM").isin([3, 4, 9, 10]), F.lit(1.0), F.lit(0.0)))
        .with_column("MONTH_SIN", F.sin(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("MONTH_COS", F.cos(F.col("MONTH_NUM") * F.lit(2 * math.pi / 12)))
        .with_column("AVG_MEME_PRICE",            F.coalesce(F.col("AVG_MEME_PRICE"),            F.lit(0.0)))
        .with_column("AVG_JEONSE_PRICE",           F.coalesce(F.col("AVG_JEONSE_PRICE"),          F.lit(0.0)))
        .with_column("AVG_INCOME",                 F.coalesce(F.col("AVG_INCOME"),                F.lit(0.0)))
        .with_column("TOTAL_RESIDENTIAL_POP",      F.coalesce(F.col("TOTAL_RESIDENTIAL_POP"),     F.lit(0.0)))
        .with_column("TOTAL_CARD_SALES",           F.coalesce(F.col("TOTAL_CARD_SALES"),          F.lit(0.0)))
        .with_column("NEW_HOUSING_BALANCE_COUNT",  F.coalesce(F.col("NEW_HOUSING_BALANCE_COUNT"), F.lit(0.0)))
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
        .with_column("NEW_HOUSING_BALANCE_RATE",   _safe_rate("NEW_HOUSING_BALANCE_COUNT", "CITY_MEAN_HOUSING"))
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
    return df


def _mape(y_true, y_pred):
    mask = y_true != 0
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])))


def train_and_register(session: Session):
    mart = session.table("MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS")

    print("\n[1/4] 피처 엔지니어링 중...")

    # Track A: TELECOM_ONLY (22구)
    df_a = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("TELECOM_ONLY")))
    months_a = sorted([r[0] for r in df_a.select("STANDARD_YEAR_MONTH").distinct().collect()])
    print(f"  Track A: {len(months_a)}개월, {df_a.count()}행")

    if len(months_a) < 10:
        raise ValueError(f"학습 데이터 부족: {len(months_a)}개월")

    # walk-forward split (70% train, 30% test)
    split_idx = int(len(months_a) * 0.7)
    train_cutoff = months_a[split_idx - 1]

    train_a = df_a.filter(F.col("STANDARD_YEAR_MONTH") <= F.lit(train_cutoff))
    test_a  = df_a.filter(F.col("STANDARD_YEAR_MONTH") >  F.lit(train_cutoff))

    print(f"\n[2/4] Track A 학습 (XGBRegressor, 22구, cutoff={train_cutoff})...")
    model_a = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8,
        input_cols=FEATURE_A, label_cols=[TARGET], output_cols=["PRED"],
    )
    model_a.fit(train_a)
    preds_a = model_a.predict(test_a).select(TARGET, "PRED").to_pandas()
    mape_a = _mape(preds_a[TARGET], preds_a["PRED"])
    print(f"  Track A MAPE: {mape_a:.2%}")

    # Track B: MULTI_SOURCE (3구)
    df_b = _add_features(mart.filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE")))
    months_b = sorted([r[0] for r in df_b.select("STANDARD_YEAR_MONTH").distinct().collect()])
    split_idx_b = int(len(months_b) * 0.7)
    train_cutoff_b = months_b[split_idx_b - 1]
    train_b = df_b.filter(F.col("STANDARD_YEAR_MONTH") <= F.lit(train_cutoff_b))
    test_b  = df_b.filter(F.col("STANDARD_YEAR_MONTH") >  F.lit(train_cutoff_b))

    print(f"\n[2/4] Track B 학습 (XGBRegressor, 3구, cutoff={train_cutoff_b})...")
    model_b = XGBRegressor(
        n_estimators=200, max_depth=4, learning_rate=0.05, subsample=0.8,
        input_cols=FEATURE_B, label_cols=[TARGET], output_cols=["PRED"],
    )
    model_b.fit(train_b)
    preds_b = model_b.predict(test_b).select(TARGET, "PRED").to_pandas()
    mape_b = _mape(preds_b[TARGET], preds_b["PRED"])
    print(f"  Track B MAPE: {mape_b:.2%}")

    print("\n[3/4] Snowflake Model Registry 저장 중...")
    reg = Registry(session=session, database_name="MOVING_INTEL", schema_name="ANALYTICS")

    for name, model, feat, df_train in [
        ("MOVE_DEMAND_TRACK_A", model_a, FEATURE_A, train_a),
        ("MOVE_DEMAND_TRACK_B", model_b, FEATURE_B, train_b),
    ]:
        try:
            mv = reg.get_model(name).version("v1")
            print(f"  {name} v1 이미 존재 — 덮어쓰기")
            reg.delete_model(name)
        except Exception:
            pass
        reg.log_model(
            model, model_name=name, version_name="v1",
            sample_input_data=df_train.select(feat),
        )
        print(f"  {name} v1 등록 완료")

    print("\n[4/4] PREDICTED_MOVE_DEMAND 테이블 갱신 중...")
    # 전체 데이터로 피처 계산 후 최신 월만 추출 (lag 피처가 전 기간 필요)
    all_months = sorted([r[0] for r in
        mart.select("STANDARD_YEAR_MONTH").distinct().collect()])
    latest_month = all_months[-1]

    # _add_features는 TARGET(다음달) null 제거 → 인퍼런스용은 전체 적용 후 최신월 필터
    feat_a = _add_features_no_target(
        mart.filter(F.col("DATA_TIER") == F.lit("TELECOM_ONLY"))
    ).filter(F.col("STANDARD_YEAR_MONTH") == F.lit(latest_month))

    feat_b = _add_features_no_target(
        mart.filter(F.col("DATA_TIER") == F.lit("MULTI_SOURCE"))
    ).filter(F.col("STANDARD_YEAR_MONTH") == F.lit(latest_month))

    latest_a = feat_a
    latest_b = feat_b

    pred_a = (model_a.predict(latest_a)
        .select("CITY_CODE", "CITY_KOR_NAME", "OPEN_COUNT", "CITY_MEAN_OPEN", "PRED")
        .with_column("PREDICTED_OPEN_COUNT", F.col("PRED") * F.col("CITY_MEAN_OPEN"))
    )
    pred_b = (model_b.predict(latest_b)
        .select("CITY_CODE", "CITY_KOR_NAME", "OPEN_COUNT", "CITY_MEAN_OPEN", "PRED")
        .with_column("PREDICTED_OPEN_COUNT", F.col("PRED") * F.col("CITY_MEAN_OPEN"))
    )

    all_preds = pred_a.union_all(pred_b).to_pandas()
    print(f"  예측 행: {len(all_preds)}구")
    print(all_preds[["CITY_KOR_NAME", "OPEN_COUNT", "PREDICTED_OPEN_COUNT"]].to_string())

    # PREDICTED_MOVE_DEMAND 테이블 재생성
    pred_df = session.create_dataframe(
        all_preds[["CITY_KOR_NAME", "PREDICTED_OPEN_COUNT"]].rename(
            columns={"CITY_KOR_NAME": "CITY_KOR_NAME", "PREDICTED_OPEN_COUNT": "DEMAND_SCORE"}
        ).values.tolist(),
        schema=["CITY_KOR_NAME", "DEMAND_SCORE"],
    )
    pred_df.write.mode("overwrite").save_as_table("MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND")
    print("  PREDICTED_MOVE_DEMAND 업데이트 완료")

    print(f"\n{'='*50}")
    print(f"  학습 완료!")
    print(f"  Track A MAPE: {mape_a:.2%}  (목표 <30%)")
    print(f"  Track B MAPE: {mape_b:.2%}  (목표 <25%)")
    print(f"  기준 월: {latest_month}")
    print(f"{'='*50}")

    return mape_a, mape_b


if __name__ == "__main__":
    print("Snowflake ML 이사 수요 예측 모델 학습")
    print("연결 중...")
    session = Session.builder.configs(CONNECTION).create()
    print("연결 완료")
    train_and_register(session)
    session.close()
