"""segment_roi.py — 이사 수요 × ROI 기회 분석 + 세그먼트 프로파일 탭 (이슈 #28)

핵심 인사이트:
  이사 수요(ML 예측 순위) × 마케팅 ROI → 어느 구에 광고비를 쓰면 효과적인가?

데이터 단위 정의 (Snowflake 실측 기반):
  - AVERAGE_INCOME / MEDIAN_INCOME / AVERAGE_ASSET_AMOUNT : 천원 단위 저장
  - RATE_HIGHEND : % 단위 (0~100), 직접 표시
  - MEME_PRICE_PER_SUPPLY_PYEONG / JEONSE_PRICE_PER_SUPPLY_PYEONG : 만원/평
  - GAP_RATIO : 0~1 비율 → ×100 % 표시
  - RESIDENTIAL/WORKING/VISITING_POPULATION : 세분화 셀별 평균 인원
  - card_sales : 원 단위, 분석 기간 누적 합산
"""
from __future__ import annotations
import datetime
import json
import streamlit as st
import pandas as pd
import plotly.graph_objects as go


def _to_ym_str(v) -> str:
    """YEAR_MONTH 값(datetime.date 또는 문자열)을 YYYYMM 문자열로 변환."""
    if hasattr(v, "strftime"):
        return v.strftime("%Y%m")
    return str(v)

_INDUSTRY_OPTIONS = {
    "가전·가구 (이사 직후 교체 수요)": "ELECTRONICS_FURNITURE",
    "식음료 (생활 밀착형)":            "FOOD",
    "패션·뷰티 (라이프스타일)":         "FASHION_BEAUTY",
    "홈·생활서비스 (인테리어·청소)":     "HOME_LIFE_SERVICE",
    "레저 (여가·문화)":                 "LEISURE",
}

_SEOUL_DISTRICTS = {
    "종로구": "11110", "중구": "11140", "용산구": "11170",
    "성동구": "11200", "광진구": "11215", "동대문구": "11230",
    "중랑구": "11260", "성북구": "11290", "강북구": "11305",
    "도봉구": "11320", "노원구": "11350", "은평구": "11380",
    "서대문구": "11410", "마포구": "11440", "양천구": "11470",
    "강서구": "11500", "구로구": "11530", "금천구": "11545",
    "영등포구": "11560", "동작구": "11590", "관악구": "11620",
    "서초구": "11650", "강남구": "11680", "송파구": "11710",
    "강동구": "11740",
}

_PERIOD_MONTHS = 22


@st.cache_data(ttl=3600)
def _load_ym_options(_session) -> list[str]:
    """연월 목록 — 당월 포함, 최근 24개월. (#2 #6)"""
    _current_ym = datetime.date.today().strftime("%Y%m")
    try:
        df = _session.sql(
            """SELECT DISTINCT TO_CHAR(YEAR_MONTH, 'YYYYMM') AS YM
               FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
               ORDER BY 1 DESC LIMIT 24"""
        ).to_pandas()
        raw = df["YM"].tolist() if not df.empty else ["202412"]
        return [str(v) for v in raw if str(v) <= _current_ym] or ["202412"]
    except Exception:
        return ["202504", "202503", "202502", "202501",
                "202412", "202411", "202410", "202409"]

_CVR  = {"ELECTRONICS_FURNITURE": 0.050, "FOOD": 0.040, "HOME_LIFE_SERVICE": 0.045,
          "FASHION_BEAUTY": 0.025, "LEISURE": 0.020}
_LTV  = {"ELECTRONICS_FURNITURE": 500_000, "FOOD": 200_000, "HOME_LIFE_SERVICE": 150_000,
          "FASHION_BEAUTY": 80_000, "LEISURE": 60_000}
_CPC  = 500
_FREQ = 3

# CALC_ROI UDF 동일 전환율 (calc_roi.sql 기준)
_CVR_UDF = {
    "ELECTRONICS_FURNITURE": 0.018,
    "FOOD":                  0.030,
    "FASHION_BEAUTY":        0.015,  # BEAUTY 매핑
    "HOME_LIFE_SERVICE":     0.025,  # 홈·생활서비스 상향 (이사가구 83% 홈개선 추진, PGM Solutions)
    "LEISURE":               0.015,  # SPORTS_CULTURE_LEISURE 매핑
}
_MOVE_TRIGGER = 3.0   # 이사 트리거 캠페인 승수
_BASE_CVR     = 0.01  # 기준 전환율


# ── 포매팅 헬퍼 ──────────────────────────────────────────────────────────────

def _won(v) -> str:
    if v is None:
        return "—"
    try:
        f = float(v)
    except (TypeError, ValueError):
        return "—"
    if abs(f) >= 1_000_000_000_000:
        return f"{f/1_000_000_000_000:.1f}조원"
    if abs(f) >= 100_000_000:
        return f"{f/100_000_000:.1f}억원"
    if abs(f) >= 10_000:
        return f"{f/10_000:.0f}만원"
    return f"{f:,.0f}원"


def _cheon_to_won(v) -> str:
    if v is None:
        return "—"
    return _won(float(v) * 1_000)


def _pyeong_price(v) -> str:
    if v is None:
        return "—"
    return f"{float(v):,.0f}만원/평"


def _pct(v, already_pct: bool = False) -> str:
    if v is None:
        return "—"
    f = float(v)
    return f"{f:.1f}%" if already_pct else f"{f*100:.1f}%"


# ── 기회 데이터 로드 ─────────────────────────────────────────────────────────

def _load_opportunity_data(session, industry_code: str, budget: int, year_month: str) -> pd.DataFrame | None:
    """25구 이사 수요 + CALC_ROI 동일 공식(배치) → DataFrame.

    CALC_ROI UDF는 서브쿼리 제약으로 배치 호출 불가 → 동일 공식을 Python으로 재현:
      estimated_revenue = budget × 3.0 × (cvr / 0.01) × demand_weight
      demand_weight = MART_MOVE_ANALYSIS.MOVE_SIGNAL_INDEX 최근 3개월 평균
    """
    try:
        rows = session.sql(
            """
            WITH gu_rank AS (
                SELECT CITY_KOR_NAME,
                       RANK() OVER (ORDER BY DEMAND_SCORE DESC) AS ML_RANK
                FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
            ),
            gu_movers AS (
                SELECT INSTALL_CITY,
                       SUM(CONTRACT_COUNT) AS AVG_MOVERS
                FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
                WHERE TO_CHAR(YEAR_MONTH, 'YYYYMM') = ?
                  AND INSTALL_STATE = '서울'
                GROUP BY INSTALL_CITY
            ),
            gu_avg_fallback AS (
                SELECT INSTALL_CITY,
                       ROUND(AVG(CONTRACT_COUNT)) AS AVG_MOVERS
                FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
                WHERE INSTALL_STATE = '서울'
                GROUP BY INSTALL_CITY
            )
            SELECT DISTINCT
                   r.CITY_KOR_NAME,
                   r.CITY_CODE,
                   COALESCE(gr.ML_RANK, 25)                      AS ML_RANK,
                   COALESCE(gm.AVG_MOVERS, gaf.AVG_MOVERS, 500) AS AVG_MOVERS
            FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER r
            LEFT JOIN gu_rank         gr  ON r.CITY_KOR_NAME = gr.CITY_KOR_NAME
            LEFT JOIN gu_movers       gm  ON r.CITY_KOR_NAME = gm.INSTALL_CITY
            LEFT JOIN gu_avg_fallback gaf ON r.CITY_KOR_NAME = gaf.INSTALL_CITY
            WHERE r.PROVINCE_CODE = '11'
            """,
            params=[year_month],
        ).collect()
    except Exception as e:
        st.error(f"데이터 조회 오류: {e}")
        return None

    cvr = _CVR_UDF.get(industry_code, 0.010)

    # MOVE_SIGNAL_INDEX는 전국 동명 구 집계 오염 가능성 → AVG_MOVERS(V_TELECOM 서울 필터)로 정규화
    max_movers = max((float(r["AVG_MOVERS"] or 0) for r in rows), default=1) or 1

    records = []
    for r in rows:
        avg_movers    = float(r["AVG_MOVERS"] or 500)
        ml_rank       = int(r["ML_RANK"] or 25)
        demand_weight = avg_movers / max_movers  # 0~1 정규화, 서울 필터 적용된 실데이터 기준
        demand_score  = (26 - ml_rank) / 25 * 100

        # CALC_ROI 동일 공식
        est_rev = budget * _MOVE_TRIGGER * (cvr / _BASE_CVR) * demand_weight
        roi_pct = (est_rev - budget) / budget * 100 if budget else 0

        records.append({
            "구":         r["CITY_KOR_NAME"],
            "ml_rank":    ml_rank,
            "demand":     round(demand_score, 1),
            "roi_pct":    round(roi_pct, 1),
            "avg_movers": int(avg_movers),
            "est_rev":    round(est_rev),
        })

    df = pd.DataFrame(records)
    # ROI도 0~100으로 정규화해 demand/roi 균형 유지
    max_roi = df["roi_pct"].max() or 1
    df["roi_score"]   = df["roi_pct"].clip(lower=0) / max_roi * 100
    df["opportunity"] = (df["demand"] * 0.5 + df["roi_score"] * 0.5).round(1)
    return df.sort_values("opportunity", ascending=False).reset_index(drop=True)


# ── 산점도 렌더링 ────────────────────────────────────────────────────────────

def _render_scatter(df: pd.DataFrame, industry_label: str, budget_만: int) -> None:
    """이사 수요 × ROI 산점도 — 핵심 인사이트 시각화."""
    top3 = set(df["구"].tolist()[:3])
    mid_demand = df["demand"].median()
    mid_roi    = df["roi_pct"].median()

    # 색상·크기
    colors = ["#e63946" if g in top3 else "#457b9d" for g in df["구"]]
    sizes  = [max(18, min(50, v / 20)) for v in df["avg_movers"]]

    hover = [
        f"<b>{row['구']}</b><br>"
        f"이사 수요 점수: {row['demand']:.0f}점 (ML 순위 {row['ml_rank']}위)<br>"
        f"추정 ROI: {row['roi_pct']:.0f}%<br>"
        f"월평균 이사: {row['avg_movers']:,}건<br>"
        f"예상 유발 매출: {_won(row['est_rev'])}<br>"
        f"<b>기회 점수: {row['opportunity']:.1f}</b>"
        for _, row in df.iterrows()
    ]

    fig = go.Figure()

    # 4분면 배경
    fig.add_shape(type="rect", x0=mid_demand, x1=105, y0=mid_roi, y1=df["roi_pct"].max()*1.15,
                  fillcolor="rgba(230,57,70,0.06)", line_width=0)
    fig.add_annotation(x=102, y=df["roi_pct"].max()*1.1, text="🎯 최우선 타겟",
                       showarrow=False, font=dict(size=11, color="#e63946"), xanchor="right")

    # 중앙선
    fig.add_shape(type="line", x0=mid_demand, x1=mid_demand,
                  y0=df["roi_pct"].min()-10, y1=df["roi_pct"].max()*1.15,
                  line=dict(color="rgba(100,100,100,0.25)", dash="dot"))
    fig.add_shape(type="line", x0=0, x1=105,
                  y0=mid_roi, y1=mid_roi,
                  line=dict(color="rgba(100,100,100,0.25)", dash="dot"))

    # 산점도
    fig.add_trace(go.Scatter(
        x=df["demand"], y=df["roi_pct"],
        mode="markers+text",
        text=df["구"],
        textposition="top center",
        textfont=dict(size=13, color="black"),
        marker=dict(color=colors, size=sizes, opacity=0.9,
                    line=dict(color="white", width=1.5)),
        hovertext=hover,
        hoverinfo="text",
    ))

    _axis_style = dict(
        title_font=dict(color="#222"),
        tickfont=dict(color="#444"),
        linecolor="#ccc",
        gridcolor="#eee",
    )
    fig.update_layout(
        title=dict(
            text=f"이사 수요 × 마케팅 ROI — <b>{industry_label}</b> · 예산 {budget_만:,}만원",
            font=dict(size=14, color="#111"),
        ),
        xaxis=dict(title="이사 수요 점수 (ML 순위 기반, 높을수록 이사 많음)", range=[0, 105],
                   **_axis_style),
        yaxis=dict(title="추정 ROI (%)", **_axis_style),
        height=480,
        margin=dict(l=40, r=20, t=60, b=40),
        plot_bgcolor="white",
        paper_bgcolor="white",
        showlegend=False,
        font=dict(color="#222"),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "🔴 상위 3구 (최우선 타겟)  🔵 나머지 구  "
        "· 점 크기 = 월평균 이사 건수  "
        "· 우상단 = 이사 수요 많고 ROI 높음 → 광고 효율 최우선 구"
    )
    st.caption(
        "ℹ️ **추정 ROI 공식**: 예산 × 3.0*(이사 트리거 효과) × (업종 전환율 ÷ 기준 1%) × 지역 이사 수요 가중치  "
        "· 수요 가중치 = 해당 구 이사 건수 ÷ 최대 구 이사 건수 (서울 25구 상대값)  "
        "· *이사가구 구매 가능성 3배 (Speedeon / Deluxe 벤치마크 기준)"
    )


# ── 메인 렌더링 ──────────────────────────────────────────────────────────────

def render_segment_roi(session) -> None:
    st.header("마케팅 기회 분석 — 이사 수요 × ROI")
    st.caption(
        "XGBoost ML이 예측한 **이사 수요**와 업종별 **마케팅 ROI**를 결합해 "
        "광고비를 어느 구에 쓰면 가장 효과적인지 찾아드립니다."
    )

    # ── 상단 필터: 기준 연월 + 업종 + 예산 ──────────────────────────────────
    ym_options = _load_ym_options(session)

    col_ym, col_ind, col_bud = st.columns([2, 3, 2])
    with col_ym:
        global_ym = st.selectbox(
            "기준 연월",
            ym_options,
            help="이사 건수 및 ROI 계산 기준 월",
        )
    with col_ind:
        industry_label = st.selectbox("광고 업종", list(_INDUSTRY_OPTIONS.keys()))
        industry_code  = _INDUSTRY_OPTIONS[industry_label]
    with col_bud:
        budget_만 = st.number_input(
            "마케팅 예산 (만원)", min_value=10, max_value=5000, value=200, step=10
        )
        budget = int(budget_만 * 10_000)

    # ── 핵심 인사이트: 기회 산점도 (즉시 표시) ───────────────────────────────
    opp_df = _load_opportunity_data(session, industry_code, budget, global_ym)
    if opp_df is None or opp_df.empty:
        st.warning("데이터를 불러올 수 없습니다.")
        return

    _render_scatter(opp_df, industry_label, budget_만)

    # Top 3 콜아웃
    top3_rows = opp_df.head(3)
    cols_top = st.columns(3)
    for i, (_, row) in enumerate(top3_rows.iterrows()):
        with cols_top[i]:
            st.metric(
                f"{'🥇' if i==0 else '🥈' if i==1 else '🥉'} {row['구']}",
                f"ROI {row['roi_pct']:.0f}%",
                f"수요 {row['ml_rank']}위 · 기회 {row['opportunity']:.0f}점",
            )

    st.divider()

    # ── 전체 순위 테이블 (접기) ───────────────────────────────────────────────
    with st.expander("25구 전체 기회 순위 보기"):
        display = opp_df[["구", "ml_rank", "avg_movers", "roi_pct", "opportunity"]].copy()
        display.columns = ["구", "이사 수요 순위", "월평균 이사 (건)", "추정 ROI (%)", "기회 점수"]
        display["이사 수요 순위"] = display["이사 수요 순위"].apply(lambda x: f"{x}위")
        display.index = range(1, len(display) + 1)
        html = display.to_html(border=0, classes="roi-rank-table")
        st.markdown(
            f"""<style>
.roi-rank-table {{ border-collapse:collapse; width:100%; font-size:14px; }}
.roi-rank-table th, .roi-rank-table td {{ color:#000 !important; background:#fff !important;
    padding:6px 10px; border-bottom:1px solid #ddd; text-align:right; }}
.roi-rank-table th {{ background:#f5f5f5 !important; font-weight:600; }}
.roi-rank-table td:first-child, .roi-rank-table th:first-child {{ text-align:left; }}
</style><div style="overflow-x:auto">{html}</div>""",
            unsafe_allow_html=True,
        )

    st.divider()

    # ── 하단: 개별 구 상세 분석 ──────────────────────────────────────────────
    st.subheader("개별 구 상세 분석")

    # ML 순위 로드 (구 선택기 레이블용)
    _rank_map: dict[str, int] = dict(zip(opp_df["구"], opp_df["ml_rank"]))

    def _gu_label(name: str) -> str:
        rank = _rank_map.get(name)
        return f"{name} (수요 {rank}위)" if rank else name

    _district_labels = {_gu_label(k): k for k in _SEOUL_DISTRICTS.keys()}

    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        default_idx = 0
        if "heatmap_selected_gu" in st.session_state:
            gu = st.session_state.pop("heatmap_selected_gu")
            labels = list(_district_labels.keys())
            matched = [i for i, lbl in enumerate(labels) if gu in lbl]
            if matched:
                default_idx = matched[0]
        selected_label = st.selectbox(
            "분석할 구 선택",
            list(_district_labels.keys()),
            index=default_idx,
            help="이사 수요 순위는 XGBoost ML 모델 기준",
        )
        selected_name = _district_labels[selected_label]
        city_code = _SEOUL_DISTRICTS[selected_name]

    with col2:
        selected_ym = global_ym
        st.write("")
        st.caption(f"기준 연월: **{global_ym[:4]}.{global_ym[4:]}** (상단에서 변경)")

    with col3:
        st.write("")
        st.write("")
        run = st.button("상세 분석 실행", type="primary", use_container_width=True)

    if not run:
        st.info("구와 기준 연월을 선택한 뒤 '상세 분석 실행'을 누르세요.")
        return

    st.divider()
    col_roi, col_profile = st.columns([1, 2])

    # ── ROI 계산 ─────────────────────────────────────────────────────────────
    with col_roi:
        st.subheader(f"마케팅 ROI — {selected_name}")
        try:
            rows = session.sql(
                "SELECT MOVING_INTEL.ANALYTICS.CALC_ROI(?, ?, ?) AS ROI",
                params=[city_code, budget, industry_code],
            ).collect()
            roi = None
            if rows:
                raw = rows[0]["ROI"]
                roi = json.loads(raw) if isinstance(raw, str) else raw

            if not roi or roi.get("data_tier") == "NO_DATA":
                st.warning("해당 지역 ROI 데이터 없음")
            else:
                tier = roi.get("data_tier", "")
                tier_badge = "🟢 통합 데이터" if tier == "MULTI_SOURCE" else "🟡 통신 데이터"
                st.caption(f"데이터 등급: {tier_badge}")

                # overview와 동일한 공식 값 사용 (일관성 유지)
                gu_row = opp_df[opp_df["구"] == selected_name]
                if not gu_row.empty:
                    _roi_pct = float(gu_row.iloc[0]["roi_pct"])
                    _est_rev = float(gu_row.iloc[0]["est_rev"])
                else:
                    _roi_pct = float(roi.get("roi_pct") or 0)
                    _est_rev = float(roi.get("estimated_revenue") or 0)
                st.metric("추정 ROI", f"{_roi_pct:.1f}%")
                st.metric("예상 광고 유발 매출", _won(_est_rev))
                movers = roi.get("movers_reached")
                if movers is not None:
                    st.metric("도달 이사가구", f"{int(float(movers)):,}가구")
                convs = roi.get("conversions")
                if convs is not None:
                    st.metric("예상 전환 건수", f"{float(convs):.1f}건")
                avg_price = roi.get("avg_price_pyeong")
                if avg_price is not None:
                    st.metric("지역 평균 평당 매매가", _pyeong_price(avg_price))
                st.caption(
                    "추정 ROI = 예산 × 3.0 × (업종전환율÷1%) × 지역수요지수  "
                    "· 이사 트리거 효과 3배: Speedeon/Deluxe 벤치마크"
                )
                st.caption(
                    f"예산 {budget_만:,}만원 · CPC 500원 · "
                    "업종 전환율·LTV 적용 · 이사 수요 상한 반영"
                )
        except Exception as e:
            st.error(f"ROI 계산 오류: {e}")

    # ── 세그먼트 프로파일 ─────────────────────────────────────────────────────
    with col_profile:
        st.subheader(f"지역 프로파일 — {selected_name}")
        try:
            rows = session.sql(
                "SELECT MOVING_INTEL.ANALYTICS.GET_SEGMENT_PROFILE(?, ?) AS PROFILE",
                params=[city_code, selected_ym],
            ).collect()
            profile = None
            if rows:
                raw = rows[0]["PROFILE"]
                profile = json.loads(raw) if isinstance(raw, str) else raw

            if not profile:
                st.warning("프로파일 데이터 없음")
                return

            tier = profile.get("data_tier", "")
            if tier == "MULTI_SOURCE":
                tab_pop, tab_inc, tab_con, tab_hou = st.tabs(
                    ["인구 유동", "소득·자산", "카드 소비", "주거 시장"]
                )
                with tab_pop:
                    pop = profile.get("population", {})
                    st.caption("세분화 측정 단위(행정동×시간대×성별×연령) 기준 셀평균 인구")
                    c1, c2, c3 = st.columns(3)
                    c1.metric("거주인구 지수", f"{float(pop.get('avg_residential', 0)):.1f}")
                    c2.metric("직장인구 지수", f"{float(pop.get('avg_working', 0)):.1f}")
                    c3.metric("방문인구 지수", f"{float(pop.get('avg_visiting', 0)):.1f}")
                    st.info("수치가 높을수록 해당 유형 인구 밀도가 높은 지역입니다.")

                with tab_inc:
                    inc = profile.get("income", {})
                    st.caption("소득·자산은 천원 단위 원시 데이터 기준 연간 추정값")
                    c1, c2 = st.columns(2)
                    c1.metric("평균 연소득", _cheon_to_won(inc.get("avg_income")))
                    c2.metric("중간 연소득", _cheon_to_won(inc.get("median_income")))
                    c1.metric("평균 자산",   _cheon_to_won(inc.get("avg_asset")))
                    rate = inc.get("rate_highend")
                    c2.metric("고소득층 비율", _pct(rate, already_pct=True))

                with tab_con:
                    con = profile.get("consumption", {})
                    ym_display = profile.get("year_month", selected_ym)
                    st.caption(f"{ym_display[:4]}.{ym_display[4:]} 당월 카드매출 기준")
                    total = con.get("total_sales")
                    if total:
                        st.metric("전체 합산", _won(total))
                    items = [
                        ("식음료",    con.get("food_sales")),
                        ("카페",      con.get("coffee_sales")),
                        ("뷰티",      con.get("beauty_sales")),
                        ("의료",      con.get("medical_sales")),
                        ("홈·생활",   con.get("home_life_sales")),
                        ("가전·가구", con.get("electronics_furniture_sales")),
                    ]
                    cols = st.columns(2)
                    for i, (label, val) in enumerate(items):
                        cols[i % 2].metric(label, _won(val))

                with tab_hou:
                    hou = profile.get("housing", {})
                    st.caption("RICHGO 아파트 시세 기준 · 만원/평 단위")
                    c1, c2 = st.columns(2)
                    c1.metric("평균 매매가",  _pyeong_price(hou.get("avg_meme_price_per_pyeong")))
                    c2.metric("평균 전세가",  _pyeong_price(hou.get("avg_jeonse_price_per_pyeong")))
                    gap = hou.get("gap_ratio")
                    if gap is not None:
                        st.metric(
                            "갭 비율 ((매매-전세)/매매)",
                            _pct(gap, already_pct=False),
                            help="수치가 낮을수록 전세가율이 높아 갭투자 위험 낮음",
                        )
            else:
                st.caption("🟡 통신 데이터만 제공되는 지역")
                tel = profile.get("telecom_summary", {})
                contract = float(tel.get("monthly_contract", 0))
                move_in  = float(tel.get("monthly_open", 0))
                move_out = float(tel.get("monthly_payend", 0))
                net      = move_in - move_out
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("신규 통신 계약", f"{contract:,.0f}건")
                c2.metric("이사 유입",      f"{move_in:,.0f}건")
                c3.metric("이사 유출",      f"{move_out:,.0f}건")
                c4.metric("순 유입",        f"{net:+,.0f}건")
                st.info(
                    "📌 중구·영등포구·서초구는 소득·소비·주거 데이터까지 포함된 "
                    "**통합 데이터** 분석이 가능합니다."
                )
        except Exception as e:
            st.error(f"프로파일 조회 오류: {e}")
