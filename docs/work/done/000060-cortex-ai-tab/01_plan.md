# 작업 계획 — #60 Cortex AI 분석 탭 구현

## AC 체크리스트
- [ ] `src/app/tabs/cortex_ai.py` 생성 — 아래 4개 섹션 포함
- [ ] **AI 인사이트**: 구 선택 → AI_COMPLETE로 이사 인사이트 3줄 자동 생성
- [ ] **수요 등급**: AI_CLASSIFY로 25개 구 이사 수요 등급(긴급/주의/안정) 뱃지 표시
- [ ] **트렌드 요약**: AI_AGG로 서울 전체 이사 트렌드 자연어 요약 표시
- [ ] **자연어 질의**: Cortex Analyst 연동 — 사용자 입력 → SQL → 결과 테이블 표시
- [ ] `app.py` Tab 3에서 `cortex_ai.render_cortex_ai(session)` 호출로 플레이스홀더 교체

## 개발 체크리스트
- [ ] 테스트 코드 포함
- [ ] 해당 디렉토리 .ai.md 최신화
- [ ] 불변식 위반 없음

## 구현 순서

### 읽기 단계 (haiku)
1. `sql/cortex/001_cortex_ai_insights.sql` 읽기 → AI_COMPLETE 호출 패턴 파악
2. `sql/cortex/002_cortex_ai_classify.sql` 읽기 → AI_CLASSIFY 패턴 파악
3. `sql/cortex/003_cortex_ai_agg.sql` 또는 관련 SQL 읽기 → AI_AGG 패턴 파악
4. `src/app/app.py` 읽기 → Tab 3 플레이스홀더 위치 파악
5. `src/app/tabs/heatmap.py` 읽기 → 탭 구조 패턴 참고
6. `config/semantic_model.yaml` 읽기 → Cortex Analyst 시맨틱 모델 확인

### 구현 단계 (sonnet)
7. `src/app/tabs/cortex_ai.py` 신규 작성
   - `_render_insight_section(session)`: 구 선택 selectbox + AI_COMPLETE 호출 → 3줄 인사이트
   - `_render_classify_section(session)`: AI_CLASSIFY 25구 등급(긴급/주의/안정) 뱃지 테이블
   - `_render_agg_section(session)`: AI_AGG 서울 전체 트렌드 자연어 요약
   - `_render_analyst_section(session)`: st.text_input + Cortex Analyst REST API → SQL + 결과 테이블
   - `render_cortex_ai(session)`: 4섹션 조합 진입점
8. `src/app/app.py` Tab 3 플레이스홀더 → `render_cortex_ai(session)` 교체
9. `src/app/tabs/.ai.md` 최신화
