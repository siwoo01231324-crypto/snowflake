# 작업 계획 — #58 Streamlit 대시보드 디버깅 6종

## AC 체크리스트

- [ ] **#1 히트맵 윤곽선** — 25개 구 경계선이 흰색으로 항상 표시됨 (`border_layer` PathLayer 또는 fallback 보장)
- [ ] **#2 기준 연월 확장** — 히트맵·ROI 탭 연월 목록에 2026-04(당월) 포함 (`DATEADD -1month` 조건 제거)
- [ ] **#3 중구 급등 원인** — 중구가 여러 달에 걸쳐 비정상 급등하는 원인 파악 및 수정
- [ ] **#4 ROI 동일값** — 상위 3구가 모두 동일 ROI 표시되는 문제 해결
- [ ] **#5 ROI 표 글자색** — ROI 분석 전체 순위 표의 텍스트를 검정(#000)으로 고정
- [ ] **#6 로딩 성능** — `@st.cache_data` 적용으로 정적 데이터 캐싱

## 파일 대상

- `src/app/tabs/heatmap.py`
- `src/app/tabs/segment_roi.py`

## 작업 순서

1. #2 기준 연월 확장 (heatmap.py L37, segment_roi.py L248) — 단순 조건 제거
2. #1 히트맵 윤곽선 — PathLayer except 블록 디버깅
3. #3 중구 급등 — Snowflake raw 쿼리로 원인 파악
4. #4 ROI 동일값 — `_load_opportunity_data` JOIN 로직 수정
5. #5 ROI 글자색 — CSS 스타일 적용
6. #6 로딩 성능 — `@st.cache_data` 적용
