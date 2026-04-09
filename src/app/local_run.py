"""local_run.py — 로컬 개발용 진입점 (Python 3.14 + snowflake-connector) v3

snowflake.snowpark 없이 snowflake.connector 기반 Session 래퍼를 사용.
Snowflake 연결을 lazy하게 초기화 (첫 쿼리 시 연결).
사용: streamlit run local_run.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import snowflake.connector

# heatmap.py는 ? 플레이스홀더(qmark) 사용
snowflake.connector.paramstyle = "qmark"

_CONNECT_KWARGS = dict(
    account=os.environ["SF_ACCOUNT"],
    user=os.environ["SF_USER"],
    password=os.environ["SF_PASSWORD"],
    warehouse=os.environ.get("SF_WAREHOUSE", "MOVING_INTEL_WH"),
    database=os.environ.get("SF_DATABASE", "MOVING_INTEL"),
    schema=os.environ.get("SF_SCHEMA", "ANALYTICS"),
)

_conn = None

def _get_conn():
    global _conn
    if _conn is None:
        _conn = snowflake.connector.connect(**_CONNECT_KWARGS)
    return _conn


class _Row(dict):
    """dict처럼 동작하는 row — row['COL'] 접근 지원"""
    def __getitem__(self, key):
        return super().__getitem__(key)


class _Result:
    """sql() 반환 객체 — .to_pandas() / .collect() 구현"""
    def __init__(self, sql, params=None):
        self._sql = sql
        self._params = params or []
        self._cache = None

    def _fetch(self):
        if self._cache is None:
            cur = _get_conn().cursor(snowflake.connector.DictCursor)
            cur.execute(self._sql, self._params)
            self._cache = cur.fetchall()
            cur.close()
        return self._cache

    def to_pandas(self) -> pd.DataFrame:
        rows = self._fetch()
        return pd.DataFrame(rows) if rows else pd.DataFrame()

    def collect(self):
        return [_Row(r) for r in self._fetch()]

    @property
    def empty(self):
        return len(self._fetch()) == 0


class _Session:
    """snowflake.snowpark.Session 최소 호환 래퍼"""
    def sql(self, query: str, params=None):
        return _Result(query, params or [])


_session = _Session()

# snowflake.snowpark 스텁 (Python 3.14 환경 — snowpark 미지원)
import sys as _sys
import types as _types

if "snowflake.snowpark" not in _sys.modules:
    _sf_pkg = _sys.modules.get("snowflake") or _types.ModuleType("snowflake")
    _sp_mod = _types.ModuleType("snowflake.snowpark")
    _sp_mod.Session = type("Session", (), {})
    _sp_mod.context = _types.ModuleType("snowflake.snowpark.context")
    _sp_mod.context.get_active_session = lambda: _session
    _sf_pkg.snowpark = _sp_mod
    _sys.modules["snowflake"] = _sf_pkg
    _sys.modules["snowflake.snowpark"] = _sp_mod
    _sys.modules["snowflake.snowpark.context"] = _sp_mod.context

# ── Streamlit 앱 ─────────────────────────────────────────────
import streamlit as st
from tabs.heatmap import render_heatmap
from tabs.segment_roi import render_segment_roi

st.set_page_config(page_title="이사 수요 인텔리전스", layout="wide")
st.title("Moving Intelligence Dashboard")
st.caption("서울 25구 이사 수요 예측 · Dual-Tier 분석")

tab1, tab2, tab3 = st.tabs(["이사 수요 히트맵", "세그먼트 · ROI", "Cortex AI 분석"])

with tab1:
    render_heatmap(_session)

with tab2:
    render_segment_roi(_session)

with tab3:
    st.info("Cortex AI 분석 탭은 이슈 #27 구현 후 연동됩니다.")
