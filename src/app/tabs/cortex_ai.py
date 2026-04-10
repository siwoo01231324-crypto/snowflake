"""cortex_ai.py — Cortex AI 분석 탭 (이슈 #60)

2개 섹션:
  1. AI 인사이트: 구 선택 → AI_COMPLETE 4개 업종별 B2B 마케팅 전략 자동 생성
  2. 자연어 질의: Cortex Analyst 연동 + AI_COMPLETE 요약
"""
from __future__ import annotations

import json
import streamlit as st
from snowflake.snowpark import Session

# Cortex Analyst 시맨틱 모델 스테이지 경로
# 배포 시 semantic_models/moving_intelligence_semantic_model.yaml 을
# MOVING_INTEL.ANALYTICS.CORTEX_STAGE 스테이지에 업로드 후 이 경로를 지정한다.
SEMANTIC_MODEL_FILE = (
    "@MOVING_INTEL.ANALYTICS.CORTEX_STAGE/moving_intelligence_semantic_model.yaml"
)


def _next_ym(yyyymm: str) -> str:
    """YYYYMM 문자열에서 다음 달 YYYYMM을 반환한다."""
    y, m = int(yyyymm[:4]), int(yyyymm[4:])
    m += 1
    if m > 12:
        y += 1
        m = 1
    return f"{y}{m:02d}"


def _clean_ai_text(text: str) -> str:
    """AI_COMPLETE 응답의 이스케이프 시퀀스를 실제 문자로 변환."""
    # 리터럴 \n → 실제 줄바꿈
    text = text.replace("\\n", "\n")
    # 리터럴 \t → 실제 탭
    text = text.replace("\\t", "\t")
    # 앞뒤 따옴표 제거 (AI가 전체를 따옴표로 감싸는 경우)
    text = text.strip().strip('"')
    # ~ 를 이스케이프 — 마크다운 취소선(~~)으로 오파싱 방지
    text = text.replace("~", "\\~")
    return text


@st.cache_data(ttl=3600)
def _load_district_options(_session) -> list[tuple[str, str]]:
    """구 목록 (code, name) — MART_MOVE_ANALYSIS 기준"""
    rows = _session.sql(
        """
        SELECT DISTINCT CITY_CODE, CITY_KOR_NAME
        FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
        WHERE CITY_CODE IS NOT NULL
        ORDER BY CITY_KOR_NAME
        """
    ).collect()
    return [(r["CITY_CODE"], r["CITY_KOR_NAME"]) for r in rows]


@st.cache_data(ttl=3600)
def _load_year_months(_session) -> list[str]:
    """연월 목록 (YYYYMM) — 최근 24개월"""
    rows = _session.sql(
        """
        SELECT DISTINCT STANDARD_YEAR_MONTH AS YM
        FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
        ORDER BY YM DESC
        LIMIT 24
        """
    ).collect()
    return [r["YM"] for r in rows]


def _render_insight_section(session: Session, year_months: list[str]) -> None:
    st.subheader("AI 인사이트")
    st.caption(
        "이번 달 이사 시그널을 분석해 **다음 달 수요를 예측**하고, 4개 업종별 B2B 마케팅 전략을 자동 생성합니다."
    )

    districts = _load_district_options(session)
    if not districts:
        st.warning("구 데이터를 불러올 수 없습니다.")
        return

    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        selected_name = st.selectbox(
            "구 선택",
            [name for _, name in districts],
            key="insight_district",
        )
    with col2:
        selected_ym = st.selectbox("시그널 월 (이번 달)", year_months[:2], key="insight_ym")
    with col3:
        next_ym = _next_ym(selected_ym)
        st.metric("예측 대상 월 (다음 달)", next_ym, help="시그널 월 기준 다음 달 이사 수요를 예측합니다")

    city_code = next((c for c, n in districts if n == selected_name), None)
    if city_code is None:
        return

    if st.button("인사이트 생성", key="btn_insight"):
        with st.spinner("데이터 조회 중…"):
            try:
                # 1단계: 데이터 조회 — YOY_PCT는 LAG으로 직접 계산
                rows = session.sql("""
                    WITH base AS (
                        SELECT CITY_CODE, CITY_KOR_NAME, DATA_TIER, STANDARD_YEAR_MONTH,
                               OPEN_COUNT, AVG_MEME_PRICE,
                               ELECTRONICS_FURNITURE_SALES, TOTAL_RESIDENTIAL_POP,
                               LAG(OPEN_COUNT) OVER (
                                   PARTITION BY CITY_CODE ORDER BY STANDARD_YEAR_MONTH
                               ) AS PREV_OPEN_COUNT
                        FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
                        WHERE CITY_CODE = ?
                    )
                    SELECT *,
                        ROUND(
                            (OPEN_COUNT - PREV_OPEN_COUNT)
                            / NULLIF(PREV_OPEN_COUNT, 0) * 100, 1
                        ) AS YOY_PCT
                    FROM base
                    WHERE STANDARD_YEAR_MONTH = ?
                """, params=[city_code, selected_ym]).collect()
            except Exception as e:
                st.error(f"조회 실패: {e}")
                return

        if not rows:
            st.warning("데이터 없음")
            return
        r = rows[0]

        with st.spinner("서울 평균 집계 중…"):
            try:
                # 2단계: 이사 강도 판단 (서울 평균 대비)
                avg_rows = session.sql("""
                    SELECT AVG(OPEN_COUNT) AS avg_open
                    FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
                    WHERE STANDARD_YEAR_MONTH = ?
                """, params=[selected_ym]).collect()
            except Exception as e:
                st.error(f"평균 조회 실패: {e}")
                return

        avg_open = float(avg_rows[0]["AVG_OPEN"]) if avg_rows and avg_rows[0]["AVG_OPEN"] else 0
        open_count = r["OPEN_COUNT"] or 0
        strength = "강함" if open_count >= avg_open else "약함"

        # 3단계: AI_COMPLETE 직접 호출 — 4개 업종별 B2B 전략
        tier_label = "정밀 Tier (4종 시그널)" if r["DATA_TIER"] == "MULTI_SOURCE" else "근사 Tier (통신 단일)"
        yoy_str = f"{r['YOY_PCT']:+.1f}%" if r["YOY_PCT"] is not None else "N/A"
        price_str = f"{int(r['AVG_MEME_PRICE']):,}원/평" if r["AVG_MEME_PRICE"] else "N/A"
        sales_str = f"{int(r['ELECTRONICS_FURNITURE_SALES']):,}원" if r.get("ELECTRONICS_FURNITURE_SALES") else "N/A"
        pop_str = f"{int(r['TOTAL_RESIDENTIAL_POP']):,}명" if r.get("TOTAL_RESIDENTIAL_POP") else "N/A"

        next_ym = _next_ym(selected_ym)
        prompt = f"""당신은 이사 수요 데이터 기반 B2B 마케팅 전문 컨설턴트입니다.
서울 25개 구의 이사 선행 시그널(이번 달)을 분석하여 다음 달 이사 수요를 예측하고, 기업 영업팀에게 선제적 마케팅 전략을 제시합니다.

## 예측 대상: 서울 {r['CITY_KOR_NAME']} — {next_ym} 이사 수요 예측
(시그널 기준 월: {selected_ym})

**{selected_ym} 이사 선행 시그널**
- 신규 통신 개통(이사 프록시): {open_count}건
- 전월 대비 변화: {yoy_str}
- 서울 25구 평균 대비: **{strength}** ({open_count}건 vs 평균 {avg_open:.0f}건)
- 데이터 신뢰도: {tier_label}

**부동산·생활 데이터**
- 평당 아파트 매매가: {price_str}
- 가전/가구 카드매출: {sales_str}
- 상주 인구: {pop_str}

---

{selected_ym} 시그널을 바탕으로 **{next_ym}(다음 달) 이사 수요**를 예측하고, 아래 4개 업종에 대한 **선제적 B2B 마케팅 전략**을 **마크다운 형식**으로 작성하세요.
이사 수요가 '{strength}' 지역임을 반영하여 {'적극적인 공세 전략' if strength == '강함' else '효율 중심의 선택적 전략'}을 제시하세요.

각 업종은 다음 구조로 작성하세요:
### [번호]. [업종명]
**전략 방향**: (한 줄 핵심 전략)
- 타겟 고객: 구체적인 세그먼트
- 추천 액션: {next_ym} 이사 시즌 전 실행 가능한 캠페인/채널/시점
- 예상 효과: 수치 기반 기대 효과

업종 목록:
1. 가구/가전 렌탈 (이케아·롯데렌탈·SK매직 등)
2. 통신 서비스 (SKT·KT·LG U+)
3. 인테리어/리모델링 (오늘의집·현대리바트 등)
4. 이사업체/입주청소업체

마지막에 **종합 의견** 섹션을 추가하여 {next_ym} 대비 이 구에 가장 효과적인 업종 우선순위를 제시하세요."""

        with st.spinner("AI_COMPLETE 호출 중…"):
            try:
                result_rows = session.sql(
                    "SELECT AI_COMPLETE('claude-4-sonnet', ?) AS insight",
                    params=[prompt]
                ).collect()
                insight_text = result_rows[0]["INSIGHT"] if result_rows else "AI 응답 없음"
            except Exception as e:
                st.error(f"AI_COMPLETE 호출 실패: {e}")
                return

        st.markdown(f"**{r['CITY_KOR_NAME']}** · 시그널 {selected_ym} → **예측 {next_ym}** · `{tier_label}`")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("신규개통 건수", f"{open_count:,}건", delta=yoy_str)
        with col2:
            st.metric("서울 평균 대비", strength, delta=f"평균 {avg_open:.0f}건")

        st.markdown("---")
        st.markdown("#### B2B 마케팅 인사이트")
        with st.container(border=True):
            st.markdown(_clean_ai_text(insight_text))


def _render_analyst_section(session: Session) -> None:
    st.subheader("자연어 질의 (Cortex Analyst)")
    st.caption(
        "이사 수요·아파트 시세·유동인구 등을 자연어로 질문하면 SQL을 자동 생성해 AI 요약과 함께 결과를 반환합니다."
    )

    with st.expander("질문 예시"):
        st.markdown(
            "- 서울에서 이사 수요가 가장 높은 구는?\n"
            "- 강남구 아파트 평균 시세는?\n"
            "- 서초구 월별 이사 수요 추이 (최근 12개월)\n"
            "- 영등포구 유동인구 시간대별 현황은?"
        )

    question = st.text_input(
        "질문 입력", placeholder="예: 서울에서 이사 수요가 가장 높은 구는?"
    )

    if st.button("질의 실행", key="btn_analyst") and question.strip():
        with st.spinner("Cortex Analyst 처리 중…"):
            try:
                import _snowflake  # Streamlit in Snowflake 전용

                # 한국어 답변 고정 지시 포함
                kr_question = question + "\n\n반드시 한국어로만 답변하세요."
                response_raw = _snowflake.send_snow_api_request(
                    "POST",
                    "/api/v2/cortex/analyst/message",
                    {},
                    {},
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": [{"type": "text", "text": kr_question}],
                            }
                        ],
                        "semantic_model_file": SEMANTIC_MODEL_FILE,
                    },
                    {},
                    30000,
                )
            except Exception as e:
                st.error(f"Cortex Analyst 호출 실패: {e}")
                return

        status_code = response_raw.get("status", 200)
        if status_code != 200:
            st.error(
                f"API 오류 (HTTP {status_code}): {response_raw.get('content', '')}"
            )
            return

        try:
            content = json.loads(response_raw.get("content", "{}"))
        except (json.JSONDecodeError, TypeError):
            st.error("응답 파싱 실패")
            return

        sql_text: str | None = None
        explanation: str | None = None
        for msg in content.get("message", {}).get("content", []):
            if msg.get("type") == "sql":
                sql_text = msg.get("statement", "")
            elif msg.get("type") == "text":
                explanation = msg.get("text", "")

        # SQL 없이 explanation만 온 경우 = Cortex Analyst가 답변 불가 → AI_COMPLETE 폴백
        _ANALYST_FAIL_PATTERNS = (
            "i apologize", "i'm sorry", "i am sorry",
            "multiple tables", "no relationship", "not able", "cannot",
            "does not define", "unable to",
        )
        analyst_failed = (
            not sql_text
            and explanation
            and any(p in explanation.lower() for p in _ANALYST_FAIL_PATTERNS)
        )

        if analyst_failed:
            st.info("현재 데이터로는 정확한 수치 조회가 어렵습니다. AI가 플랫폼 데이터 맥락을 기반으로 직접 답변합니다.")
            with st.spinner("AI 답변 생성 중…"):
                fallback_prompt = f"""당신은 서울 25개 구 이사 수요 인텔리전스 플랫폼의 수석 데이터 분석가입니다.
보유 데이터: 통신 신규개통(이사 프록시), 아파트 매매가/전세가, SPH 유동인구(중구·영등포·서초), 주식 시세.

사용자 질문: {question}

이 플랫폼의 데이터 맥락을 바탕으로 마크다운 형식의 한국어 답변을 작성하세요.
정확한 수치가 없는 경우에는 일반적인 인사이트와 권장 분석 방향을 제시하세요.

### 답변
### 추천 분석 방향
(더 정확한 답변을 위해 어떤 데이터를 조회하면 좋은지 제안)"""
                try:
                    fb_rows = session.sql(
                        "SELECT AI_COMPLETE('claude-4-sonnet', ?) AS answer",
                        params=[fallback_prompt]
                    ).collect()
                    fb_text = fb_rows[0]["ANSWER"] if fb_rows else None
                except Exception as e:
                    fb_text = None
                    st.error(f"AI 폴백 실패: {e}")
            if fb_text:
                st.markdown("#### AI 답변")
                with st.container(border=True):
                    st.markdown(_clean_ai_text(fb_text))
            return

        if explanation and not analyst_failed:
            st.caption(explanation)

        if sql_text:
            with st.spinner("SQL 실행 중…"):
                try:
                    result_df = session.sql(sql_text).to_pandas()
                except Exception as e:
                    st.error(f"SQL 실행 실패: {e}")
                    return

            if result_df.empty:
                st.warning("조회 결과가 없습니다.")
                return

            # AI 요약 생성
            with st.spinner("AI 요약 생성 중…"):
                # DataFrame을 텍스트로 변환 (최대 30행)
                sample = result_df.head(30).to_string(index=False)
                summary_prompt = f"""당신은 이사 수요 인텔리전스 플랫폼의 수석 데이터 분석가입니다.
B2B 고객(가구·통신·인테리어·이사업체 영업팀)이 이사 수요 데이터를 활용해 의사결정을 내릴 수 있도록 명확하고 실용적인 분석을 제공합니다.

## 사용자 질문
{question}

## 쿼리 결과 데이터
{sample}

---

위 데이터를 분석하여 **마크다운 형식**으로 답변을 작성하세요.

다음 구조를 따르세요:
### 핵심 답변
(질문에 대한 직접적인 답변 2~3문장, 핵심 수치 포함)

### 데이터 해석
- 주목할 패턴이나 트렌드
- 이상치나 특이사항 (있는 경우)

### 비즈니스 시사점
(B2B 이사 수요 플랫폼 맥락에서 실용적 인사이트 1~2개)

답변은 간결하고 수치 기반으로 작성하세요."""

                try:
                    summary_rows = session.sql(
                        "SELECT AI_COMPLETE('claude-4-sonnet', ?) AS summary",
                        params=[summary_prompt]
                    ).collect()
                    summary_text = summary_rows[0]["SUMMARY"] if summary_rows else None
                except Exception:
                    summary_text = None

            if summary_text:
                st.markdown("#### AI 분석 결과")
                with st.container(border=True):
                    st.markdown(_clean_ai_text(summary_text))

            with st.expander(f"원본 데이터 ({len(result_df):,}행)"):
                st.dataframe(result_df, use_container_width=True)

            with st.expander("생성된 SQL"):
                st.code(sql_text, language="sql")

        elif not explanation:
            st.warning(
                "Cortex Analyst가 응답을 생성하지 못했습니다. 질문을 바꿔보세요."
            )


def render_cortex_ai(session: Session) -> None:
    """Tab 3 진입점 — 2개 섹션 렌더링"""
    st.header("Cortex AI 분석")
    st.caption(
        "Snowflake Cortex AI Functions(AI_COMPLETE)와 "
        "Cortex Analyst로 이사 수요 인사이트를 자동 생성합니다."
    )

    year_months = _load_year_months(session)
    if not year_months:
        st.error("연월 데이터를 불러올 수 없습니다. Snowflake 연결 상태를 확인하세요.")
        return

    tab_insight, tab_analyst = st.tabs(["AI 인사이트", "자연어 질의"])
    with tab_insight:
        _render_insight_section(session, year_months)
    with tab_analyst:
        _render_analyst_section(session)
