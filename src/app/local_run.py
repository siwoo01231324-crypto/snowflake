"""local_run.py — 로컬 개발용 진입점 (Python 3.14 + snowflake-connector) v3

snowflake.snowpark 없이 snowflake.connector 기반 Session 래퍼를 사용.
Snowflake 연결을 lazy하게 초기화 (첫 쿼리 시 연결).
사용: streamlit run local_run.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

# Python 3.14 _wmi 모듈이 WMI COM 쿼리에서 무한 대기하는 버그 우회
import platform as _platform
_platform._wmi = None

# .env 파일 로드
_env_path = os.path.join(os.path.dirname(__file__), ".env")
if os.path.exists(_env_path):
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith("#") and "=" in _line:
                _k, _v = _line.split("=", 1)
                os.environ.setdefault(_k.strip(), _v.strip())

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

# _snowflake 스텁 — SiS 전용 모듈을 로컬에서 에뮬레이션
# send_snow_api_request: 기존 connector 세션 토큰으로 Cortex REST API 직접 호출
import types as _types_sf
import requests as _requests

def _send_snow_api_request(method, path, _h, _p, body, _e, timeout_ms):
    conn = _get_conn()
    token = conn._rest._token
    account = conn.account
    url = f"https://{account}.snowflakecomputing.com{path}"
    resp = _requests.request(
        method, url,
        headers={
            "Authorization": f'Snowflake Token="{token}"',
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        json=body,
        timeout=timeout_ms / 1000,
    )
    return {"status": resp.status_code, "content": resp.text}

_sf_stub = _types_sf.ModuleType("_snowflake")
_sf_stub.send_snow_api_request = _send_snow_api_request
sys.modules["_snowflake"] = _sf_stub

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
from tabs.cortex_ai import render_cortex_ai

st.set_page_config(page_title="이사 수요 인텔리전스", layout="wide")
st.title("Moving Intelligence Dashboard")
st.caption(
    "**이번 달 이사 시그널 → 다음 달 수요 예측** · "
    "통신 신규개통·계약 선행지표 기반 서울 25구 이사 수요 예측 플랫폼 · Dual-Tier 분석"
)

tab1, tab2, tab3 = st.tabs(["이사 수요 히트맵", "세그먼트 · ROI", "Cortex AI 분석"])

with tab1:
    render_heatmap(_session)

with tab2:
    render_segment_roi(_session)

with tab3:
    render_cortex_ai(_session)
