# feat: Streamlit 대시보드 디버깅 6종

## 사용자 관점 목표
히트맵·ROI 탭의 시각적 오류, 데이터 이상, 성능 문제를 일괄 해결하여 신뢰할 수 있는 대시보드를 제공한다.

## 배경
로컬 실행 중 발견된 6가지 버그/개선사항 (src/app/tabs/heatmap.py, segment_roi.py)

## 완료 기준
- [x] **#1 히트맵 윤곽선** — `_load_gu_boundaries` 캐싱 함수 + M_SCCO_MST fallback 추가
- [x] **#2 기준 연월 확장** — `DATE_TRUNC('month', CURRENT_DATE())` 기준으로 당월 포함, 미래 제외
- [x] **#3 중구 급등 원인** — `INSTALL_STATE='서울'` 필터 누락이 원인 (전국 중구 6개 합산) → 양 쿼리에 필터 추가
- [x] **#4 ROI 동일값** — `gu_avg_fallback` CTE 추가 + `INSTALL_STATE='서울'` 필터로 동일값 해소
- [x] **#5 ROI 표 글자색** — `st.markdown` CSS `td { color: #000 !important; }` 주입
- [x] **#6 로딩 성능** — `@st.cache_data(ttl=3600)` — `_load_months`, `_load_gu_boundaries`, `_load_ym_options` 3개 함수 캐싱

## 구현 플랜
1. `heatmap.py`: PathLayer except 블록 디버깅, 당월 필터 제거, 중구 데이터 집계 조사
2. `segment_roi.py`: `_load_opportunity_data` JOIN 로직 수정, 당월 필터 제거, 글자색 CSS 고정, 캐싱 적용
3. Snowflake에서 중구·ROI raw 쿼리로 원인 확인 후 수정

## 개발 체크리스트
- [ ] 테스트 코드 포함
- [ ] 해당 디렉토리 .ai.md 최신화
- [ ] 불변식 위반 없음

## 작업 내역

### 2026-04-10
- 세션 시작, AC 전체 미완료 확인 (0/6)
- Python으로 Snowflake 직접 조회 → 중구 급등 원인: 전국 중구 6개(인천·부산·울산·대전·대구·서울) 합산 집계
- heatmap.py 리팩터: `_extract_rings`·`_extract_paths` 모듈 상위 이동, `_load_months`·`_load_gu_boundaries` @cache_data 함수 추출
  - `DATE_TRUNC('month', CURRENT_DATE())` 기준으로 당월 포함·미래 제외 (#2)
  - `INSTALL_STATE='서울'` 필터 추가 (#3)
  - M_SCCO_MST fallback 추가 (#1)
- segment_roi.py: `_load_ym_options` @cache_data 함수 추출 (#6), `gu_avg_fallback` CTE + `INSTALL_STATE='서울'` 필터 (#3 #4), CSS 글자색 (#5)
- 검증: 연월 목록 2026-04 포함 확인, 서울 중구 402건(기존 2,062건) 확인
- AC 6/6 완료

### 2026-04-10 (추가 개선)
- **중구 MOVE_SIGNAL_INDEX 이상 수정**: MART_MOVE_ANALYSIS의 MOVE_SIGNAL_INDEX가 중구(0.45)에서 비정상적으로 높음 → V_TELECOM 서울 필터 기반 avg_movers / max_movers 로 demand_weight 교체 (중구 0.45→0.23)
- **demand_signal CTE 제거**: MART_MOVE_ANALYSIS 조인 불필요해져 쿼리 단순화
- **ROI 일관성 수정**: 개별 구 상세 분석의 roi_pct·est_rev를 opp_df에서 참조 → overview 산점도와 동일한 값 표시
- **통신 전용 지역 지표 개선**: 신규계약/신규개통/해지 → 신규 통신 계약/이사 유입/이사 유출/순 유입 4개 컬럼으로 인사이트 강화
- **산점도 축 텍스트 가시성 수정**: 다크테마 색상(밝은 회색)이 흰 배경에서 보이지 않던 문제 → 어두운 색(#111~#444)으로 교체
