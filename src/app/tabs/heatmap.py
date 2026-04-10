"""heatmap.py — 서울 이사 수요 히트맵 탭 (이슈 #28)"""
from __future__ import annotations

import json
import pydeck as pdk
import streamlit as st

_ALLOWED_SIGNAL_COLS: frozenset[str] = frozenset({"CONTRACT_COUNT", "OPEN_COUNT"})

_SIGNAL_OPTIONS = {
    "신규 계약 건수 (이사 1개월 전 예고)": "CONTRACT_COUNT",
    "신규 개통 건수 (이사 후 통신 재개설)": "OPEN_COUNT",
}


def _compute_color(signal: int, max_signal: int) -> list[int]:
    """신호 강도 → 파란(낮음)→빨간(높음) RGB. Python에서 미리 계산."""
    ratio = signal / max_signal if max_signal > 0 else 0
    r = int(50 + 205 * ratio)
    g = max(20, int(180 - 160 * ratio))
    b = max(20, int(220 - 200 * ratio))
    return [r, g, b, 210]


def _extract_rings(geom: dict) -> list[list]:
    gtype = geom.get("type", "")
    if gtype == "Polygon":
        return [geom["coordinates"][0]]
    if gtype == "MultiPolygon":
        return [coords[0] for coords in geom["coordinates"]]
    if gtype == "GeometryCollection":
        rings = []
        for sub in geom.get("geometries", []):
            rings.extend(_extract_rings(sub))
        return rings
    return []


def _extract_paths(geom: dict) -> list[list]:
    gtype = geom.get("type", "")
    if gtype == "LineString":
        return [geom["coordinates"]]
    if gtype == "MultiLineString":
        return geom["coordinates"]
    if gtype == "Polygon":
        return [geom["coordinates"][0]]
    if gtype == "MultiPolygon":
        return [c[0] for c in geom["coordinates"]]
    if gtype == "GeometryCollection":
        paths = []
        for sub in geom.get("geometries", []):
            paths.extend(_extract_paths(sub))
        return paths
    return []


@st.cache_data(ttl=3600)
def _load_months(_session) -> list[str]:
    """연월 목록 — 당월 포함, 최근 24개월. (#2 DATEADD 조건 제거)"""
    df = _session.sql(
        """
        SELECT DISTINCT TO_CHAR(YEAR_MONTH, 'YYYY-MM') AS YM
        FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
        WHERE YEAR_MONTH <= DATE_TRUNC('month', CURRENT_DATE())
        ORDER BY 1 DESC
        LIMIT 24
        """
    ).to_pandas()
    return df["YM"].tolist() if not df.empty else []


@st.cache_data(ttl=3600)
def _load_gu_boundaries(_session) -> list[dict]:
    """구 경계선 PathLayer 데이터 — V_SPH_REGION_MASTER 우선, 실패 시 M_SCCO_MST fallback. (#1 #6)"""

    def _parse(gu_df) -> list[dict]:
        result: list[dict] = []
        for _, row in gu_df.iterrows():
            if not row["GU_GEOJSON"]:
                continue
            try:
                geom = json.loads(row["GU_GEOJSON"])
            except (json.JSONDecodeError, TypeError):
                continue
            for path in _extract_paths(geom):
                result.append({"path": path, "gu": row["CITY_KOR_NAME"]})
        return result

    _SQL_PRIMARY = """
        SELECT CITY_KOR_NAME, CITY_CODE,
               ST_ASGEOJSON(ST_UNION_AGG(DISTRICT_GEOM)) AS GU_GEOJSON
        FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER
        WHERE PROVINCE_CODE = '11'
        GROUP BY CITY_KOR_NAME, CITY_CODE
    """
    _SQL_FALLBACK = """
        SELECT CITY_KOR_NAME, CITY_CODE,
               ST_ASGEOJSON(ST_UNION_AGG(DISTRICT_GEOM)) AS GU_GEOJSON
        FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
        WHERE PROVINCE_CODE = '11'
        GROUP BY CITY_KOR_NAME, CITY_CODE
    """

    try:
        data = _parse(_session.sql(_SQL_PRIMARY).to_pandas())
        if data:
            return data
    except Exception:
        pass

    try:
        return _parse(_session.sql(_SQL_FALLBACK).to_pandas())
    except Exception:
        return []


def render_heatmap(session) -> None:
    st.header("서울 이사 수요 히트맵")
    st.caption(
        "서울 25개 구의 월별 이사 이동 강도를 지도로 시각화합니다. "
        "**색이 붉을수록** 이사 활동이 많은 지역입니다. 지도 위에 마우스를 올리면 상세 정보를 볼 수 있습니다."
    )

    # ── 필터 ────────────────────────────────────────────────────────────────
    col1, col2 = st.columns([2, 1])

    with col1:
        ym_list = _load_months(session)
        selected_month = st.selectbox("기준 연월", ym_list)

    with col2:
        signal_label = st.radio(
            "이사 시그널 유형",
            list(_SIGNAL_OPTIONS.keys()),
            index=0,
        )
        signal_col = _SIGNAL_OPTIONS[signal_label]
        if signal_col not in _ALLOWED_SIGNAL_COLS:
            st.error(f"잘못된 시그널 컬럼: {signal_col}")
            return

    if not selected_month:
        st.warning("조회 가능한 데이터가 없습니다.")
        return

    # ── 데이터 로드 ──────────────────────────────────────────────────────────
    # 행정동(DISTRICT) 단위 폴리곤 전체 로드 (467개) + 구 단위 통신 신호 JOIN
    # 동 경계선을 제거해 구 단위처럼 보이도록 렌더링
    query = f"""
        SELECT
            m.CITY_KOR_NAME,
            m.CITY_CODE,
            ST_ASGEOJSON(m.DISTRICT_GEOM)               AS GEOJSON,
            COALESCE(t.{signal_col}, 0)                  AS MOVE_SIGNAL,
            COALESCE(p.DEMAND_RANK, 0)                   AS ML_RANK,
            CASE
                WHEN m.CITY_CODE IN ('11140','11560','11650')
                THEN 'MULTI_SOURCE'
                ELSE 'TELECOM_ONLY'
            END                                           AS DATA_TIER
        FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
        LEFT JOIN (
            SELECT INSTALL_CITY,
                   MAX({signal_col}) AS {signal_col}
            FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
            WHERE TO_CHAR(YEAR_MONTH, 'YYYY-MM') = ?
              AND INSTALL_STATE = '서울'
            GROUP BY INSTALL_CITY
        ) t ON m.CITY_KOR_NAME = t.INSTALL_CITY
        LEFT JOIN (
            SELECT CITY_KOR_NAME,
                   RANK() OVER (ORDER BY DEMAND_SCORE DESC) AS DEMAND_RANK
            FROM MOVING_INTEL.ANALYTICS.PREDICTED_MOVE_DEMAND
        ) p ON m.CITY_KOR_NAME = p.CITY_KOR_NAME
        WHERE m.PROVINCE_CODE = '11'
    """
    df = session.sql(query, params=[selected_month]).to_pandas()

    if df.empty:
        st.warning("선택한 연월에 데이터가 없습니다.")
        return

    # ── 폴리곤 데이터 조립 ───────────────────────────────────────────────────
    polygon_data: list[dict] = []
    for _, row in df.iterrows():
        if not row["GEOJSON"]:
            continue
        try:
            geom = json.loads(row["GEOJSON"])
        except (json.JSONDecodeError, TypeError):
            continue

        signal = int(row["MOVE_SIGNAL"])
        ml_rank = int(row["ML_RANK"]) if row["ML_RANK"] else 0
        tier_label = "통합 데이터" if row["DATA_TIER"] == "MULTI_SOURCE" else "통신 데이터"

        for ring in _extract_rings(geom):
            polygon_data.append({
                "polygon":    ring,
                "gu":         row["CITY_KOR_NAME"],
                "dong":       row.get("DISTRICT_KOR_NAME", ""),
                "signal":     signal,
                "ml_rank":    ml_rank,
                "tier":       tier_label,
            })

    if not polygon_data:
        st.warning("지도 데이터를 불러올 수 없습니다.")
        return

    max_signal = max(d["signal"] for d in polygon_data) or 1
    for d in polygon_data:
        d["fill_color"] = _compute_color(d["signal"], max_signal)

    # ── 구 경계선 데이터 로드 (캐싱) ─────────────────────────────────────────
    boundary_data = _load_gu_boundaries(session)

    # ── pydeck PolygonLayer ─────────────────────────────────────────────────
    # stroked=False → 행정동 경계선 숨김 → 같은 구는 하나의 덩어리처럼 보임
    fill_layer = pdk.Layer(
        "PolygonLayer",
        data=polygon_data,
        get_polygon="polygon",
        get_fill_color="fill_color",
        pickable=True,
        auto_highlight=True,
        filled=True,
        stroked=False,
        extruded=False,
    )

    # ── PathLayer: 구 경계선 ────────────────────────────────────────────────
    border_layer = pdk.Layer(
        "PathLayer",
        data=boundary_data,
        get_path="path",
        get_color=[255, 255, 255, 180],
        get_width=40,               # 지도 단위(미터 환산)
        width_min_pixels=1,
        width_max_pixels=2,
        pickable=False,
        joint_rounded=True,
        cap_rounded=True,
    )

    view_state = pdk.ViewState(
        latitude=37.5510,
        longitude=126.9882,
        zoom=10.5,
        pitch=0,
    )

    st.pydeck_chart(
        pdk.Deck(
            layers=[fill_layer, border_layer],
            initial_view_state=view_state,
            map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
            tooltip={
                "html": (
                    "<b style='font-size:14px'>{gu}</b> "
                    "<span style='font-size:12px;color:#aaa'>· {dong}</span><br>"
                    "이번달 이사 시그널: <b>{signal}건</b><br>"
                    "이사 수요 순위: <b style='color:#f5a623'>{ml_rank}위</b> / 25구 "
                    "<span style='font-size:11px;color:#aaa'>(XGBoost ML)</span><br>"
                    "데이터 등급: {tier}"
                ),
                "style": {
                    "backgroundColor": "#2b2b2b",
                    "color": "white",
                    "padding": "8px",
                    "borderRadius": "4px",
                },
            },
        )
    )

    # ── 색상 범례 ────────────────────────────────────────────────────────────
    # 구 단위 유니크 시그널로 범례 계산
    district_signals = sorted(
        df.groupby("CITY_CODE")["MOVE_SIGNAL"].first().tolist()
    )
    if district_signals:
        p33 = district_signals[len(district_signals) // 3]
        p67 = district_signals[2 * len(district_signals) // 3]
        max_sig = district_signals[-1]
        st.markdown(
            f"""<div style="display:flex;gap:24px;margin:6px 0;font-size:13px">
<span>🔵 <b>낮음</b> (0~{p33:,}건)</span>
<span>🟡 <b>중간</b> ({p33+1:,}~{p67:,}건)</span>
<span>🔴 <b>높음</b> ({p67+1:,}~{max_sig:,}건)</span>
</div>""",
            unsafe_allow_html=True,
        )

    with st.expander("데이터 신뢰 등급 안내"):
        st.markdown(
            """
| 등급 | 해당 구 | 사용 데이터 |
|------|---------|------------|
| **통합 데이터** | 중구·영등포구·서초구 | 통신 + 유동인구 + 소득 + 카드소비 + 아파트시세 |
| **통신 데이터** | 22개 구 | 통신 신규계약·개통 건수 |

**시그널 해석**
- **신규 계약**: 이사 1개월 전 예고 지표 (새 주소지 통신 계약)
- **신규 개통**: 이사 완료 확인 지표 (실제 이사 후 개통)
            """
        )

    with st.expander("구별 이사 시그널 순위"):
        district_df = (
            df.groupby(["CITY_KOR_NAME", "CITY_CODE", "DATA_TIER"])["MOVE_SIGNAL"]
            .first()
            .reset_index()
        )
        ml_rank_map = df.groupby("CITY_KOR_NAME")["ML_RANK"].first()
        district_df["ML_RANK"] = district_df["CITY_KOR_NAME"].map(ml_rank_map).fillna(0).astype(int)
        display_df = district_df[["CITY_KOR_NAME", "MOVE_SIGNAL", "ML_RANK", "DATA_TIER"]].copy()
        display_df.columns = ["구", "이사 시그널 (건)", "ML 수요 순위", "데이터 등급"]
        display_df["데이터 등급"] = display_df["데이터 등급"].map(
            {"MULTI_SOURCE": "통합", "TELECOM_ONLY": "통신"}
        )
        display_df = display_df.sort_values("ML 수요 순위", ascending=True).reset_index(drop=True)
        display_df.index += 1
        st.dataframe(display_df, use_container_width=True)
        st.caption("💡 **세그먼트·ROI 탭**에서 관심 구를 선택하면 소득·소비 프로파일과 마케팅 ROI를 확인할 수 있습니다.")
