# Plan: feat/000022 — MOVE_SIGNAL_INDEX 4종 시그널 융합 + 교차검증

## AC 체크리스트

- [ ] `MOVE_SIGNAL_INDEX` 컬럼이 통합 마트에 추가됨
- [ ] 4개 시그널 간 상관 행렬 평균 r̄ > 0.3
- [ ] 25개 구 전체에 MOVE_SIGNAL_INDEX 값 존재
- [ ] `validate_move_signals()` 교차검증 함수 구현

## 구현 계획

### 1. TDD Red (테스트 먼저)
- `tests/sql/test_07_move_signal.sql` 작성 (TC-01~TC-03)
- `tests/test_07_signal_validation.py` 작성

### 2. 피처 구현
- `features/move_signal.py`
  - `compute_move_signal_index(session)` — MULTI_SOURCE(3구): 4종 융합, TELECOM_ONLY(22구): norm(OPEN_COUNT)
  - `validate_move_signals(session)` — 상관 행렬 반환
- MART_MOVE_ANALYSIS에 MOVE_SIGNAL_INDEX 컬럼 추가

### 3. Dual-Tier 분기
- MULTI_SOURCE 3구 (중·영등포·서초): w1=0.35, w2=0.25, w3=0.25, w4=0.15
- TELECOM_ONLY 22구: norm(OPEN_COUNT) 단일 프록시

### 4. 검증
- SQL TC 실행 → Green
- Python 테스트 → avg_corr > 0.3 확인

## 참조
- `docs/specs/dev_spec.md` A4-1
- 의존성: #21 (통합 마트)
