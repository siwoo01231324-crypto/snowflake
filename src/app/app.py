"""app.py — Moving Intelligence Dashboard (이슈 #28)

3탭 구조:
  Tab 1: 이사 수요 히트맵 (heatmap.py)
  Tab 2: 세그먼트 · ROI    (이슈 #29)
  Tab 3: Cortex AI 분석   (이슈 #26/#27)
"""
import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="이사 수요 인텔리전스", layout="wide")

session = get_active_session()

st.title("Moving Intelligence Dashboard")
st.caption("서울 25구 이사 수요 예측 · Dual-Tier 분석")

tab1, tab2, tab3 = st.tabs(["이사 수요 히트맵", "세그먼트 · ROI", "Cortex AI 분석"])

with tab1:
    from tabs.heatmap import render_heatmap
    render_heatmap(session)

with tab2:
    st.info("세그먼트 · ROI 탭은 이슈 #29에서 구현됩니다.")

with tab3:
    from tabs.cortex_ai import render_cortex_ai
    render_cortex_ai(session)
