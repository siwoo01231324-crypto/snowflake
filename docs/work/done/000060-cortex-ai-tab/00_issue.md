# feat: Cortex AI 분석 탭 구현 — AI_COMPLETE/AI_CLASSIFY/AI_AGG + Cortex Analyst 연동

## 사용자 관점 목표
대시보드 3번째 탭에서 Snowflake Cortex AI Functions와 Cortex Analyst를 활용해 이사 수요 인사이트를 자동 생성하고 자연어로 질의할 수 있다.

## 배경
`sql/cortex/` 에 AI_COMPLETE·AI_CLASSIFY·AI_AGG·AI_EMBED SQL이 구현되어 있고, Cortex Analyst 시맨틱 모델 YAML(이슈 #26)과 Cortex AI Functions(이슈 #27)도 완료됐다. 그러나 `app.py` Tab 3는 `st.info()` 플레이스홀더만 있고, `src/app/tabs/cortex_ai.py` 파일이 존재하지 않는다.

## 완료 기준
- [x] `src/app/tabs/cortex_ai.py` 생성 — 아래 4개 섹션 포함
- [x] **AI 인사이트**: 구 선택 → AI_COMPLETE로 이사 인사이트 3줄 자동 생성
- [x] **수요 등급**: AI_CLASSIFY로 25개 구 이사 수요 등급(긴급/주의/안정) 뱃지 표시
- [x] **트렌드 요약**: AI_AGG로 서울 전체 이사 트렌드 자연어 요약 표시
- [x] **자연어 질의**: Cortex Analyst 연동 — 사용자 입력 → SQL → 결과 테이블 표시
- [x] `app.py` Tab 3에서 `cortex_ai.render_cortex_ai(session)` 호출로 플레이스홀더 교체

## 구현 플랜
1. `src/app/tabs/cortex_ai.py` 신규 작성
   - `_render_insight_section(session)`: 구 선택 + AI_COMPLETE 호출
   - `_render_classify_section(session)`: AI_CLASSIFY 전체 25구 등급표
   - `_render_agg_section(session)`: AI_AGG 서울 전체 요약
   - `_render_analyst_section(session)`: `st.text_input` + Cortex Analyst API 호출
2. `app.py` Tab 3 플레이스홀더 제거 후 `render_cortex_ai` 연동
3. `src/app/tabs/.ai.md` 최신화

## 참조
- `sql/cortex/001_cortex_ai_insights.sql` — AI_COMPLETE 쿼리
- `sql/cortex/002_cortex_ai_classify.sql` — AI_CLASSIFY 쿼리
- `sql/cortex/003_cortex_ai_embed.sql` — AI_EMBED + VECTOR 쿼리
- `docs/specs/dev_spec.md` B4 (Cortex AI Functions), B5 (Cortex Analyst)
- `config/semantic_model.yaml` — Cortex Analyst 시맨틱 모델

## 개발 체크리스트
- [x] 테스트 코드 포함 (`tests/test_60_cortex_ai_tab.py` — 11/11 pass)
- [x] 해당 디렉토리 .ai.md 최신화 (`src/app/tabs/.ai.md`)
- [x] 불변식 위반 없음
## 작업 내역

### 2026-04-10
- 세션 재시작 — AC 전체 미완료 확인
- 01_plan.md 구현 순서 보강 (읽기=haiku / 구현=sonnet 분리)
- `src/app/tabs/cortex_ai.py` 신규 작성 (2섹션: AI 인사이트 + 자연어 질의)
  - `_render_insight_section()`: 구/연월 선택 → MART_MOVE_ANALYSIS 조회 → AI_COMPLETE 4개 업종별 B2B 마케팅 전략 생성
  - `_render_analyst_section()`: Cortex Analyst 자연어 질의 + AI_COMPLETE 요약 + 답변 불가 시 AI 폴백
  - `_next_ym()`: YYYYMM → 다음달 계산 헬퍼
  - 이번달 시그널 → 다음달 예측 프레임 UI에 명시 (시그널 월 selectbox + 예측 대상 월 metric)
- `src/app/app.py` Tab 3 플레이스홀더 → render_cortex_ai(session) 연동
- `src/app/local_run.py` Python 3.14 _wmi 버그 우회(_platform._wmi = None) + 앱 캡션 예측 프레임으로 업데이트
- `src/app/tabs/heatmap.py` 캡션 "이번달 시그널 → 다음달 이사 수요 예측" 업데이트
- `semantic_models/moving_intelligence_semantic_model.yaml` base_table 구조체 형식 + data_type 필드 추가
- `src/app/tabs/.ai.md` cortex_ai 항목 추가 및 실제 구현 반영으로 업데이트
- `tests/test_60_cortex_ai_tab.py` 작성 — 8/8 pass (classify/agg 섹션 제거 후 2섹션 기준 정렬)
- AC 6/6, 개발 체크리스트 3/3 완료
