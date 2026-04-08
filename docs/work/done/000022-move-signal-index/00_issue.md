# feat: MOVE_SIGNAL_INDEX 4종 시그널 융합 + 교차검증

# Issue #22: feat: MOVE_SIGNAL_INDEX 4종 시그널 융합 + 교차검증

## 목적
4개 이사 시그널(통신설치/거주인구Δ/신규대출/가전소비Δ)을 융합해서 "이 지역에 이사가 많다" 점수를 만든다.

## 완료 기준
- [x] `MOVE_SIGNAL_INDEX` 컬럼이 통합 마트에 추가됨
- [x] 시그널 교차검증 완료 — S3(주담대) r(S1↔S3)=-0.215로 제외, 3종 융합으로 전환 (dev_spec 규칙 적용)
- [x] 25개 구 전체에 MOVE_SIGNAL_INDEX 값 존재 (null_idx=0, gu_count=25)
- [x] `validate_move_signals()` 교차검증 함수 구현

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`sql
-- test_07_move_signal.sql
-- ⚠️ MOVE_SIGNAL_INDEX 컬럼은 이 이슈에서 MART_MOVE_ANALYSIS에 신규 추가됨.
-- TDD Red 시작이 정상 (이슈 진행 전에는 컬럼 미존재로 TC-01 실패).
-- #40 검증 결과: MART_MOVE_ANALYSIS 19컬럼 중 MOVE_SIGNAL_INDEX 미존재 확인.
-- 이슈 완료 후 Green 전환 (컬럼 추가 + NOT NULL 채움) 되어야 함.
-- 또한 dev_spec A4-1 Dual-Tier 분기: TELECOM_ONLY 22구는 norm(OPEN_COUNT) 단일 시그널 / MULTI_SOURCE 3구는 4종 융합.

-- TC-01: MOVE_SIGNAL_INDEX 컬럼 존재 + NOT NULL
SELECT COUNT(*) AS null_idx FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
WHERE MOVE_SIGNAL_INDEX IS NULL;
-- EXPECTED: null_idx = 0

-- TC-02: 값 범위 확인 (0~1 정규화)
SELECT MIN(MOVE_SIGNAL_INDEX) AS min_val, MAX(MOVE_SIGNAL_INDEX) AS max_val
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS;
-- EXPECTED: min_val >= 0, max_val <= 1

-- TC-03: 25개 구 전체 커버
SELECT COUNT(DISTINCT CITY_CODE) AS gu_count 
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
WHERE MOVE_SIGNAL_INDEX IS NOT NULL;
-- EXPECTED: gu_count = 25
\`\`\`

\`\`\`python
# test_07_signal_validation.py
def test_signal_correlation(session):
    from features.move_signal import validate_move_signals
    corr_matrix = validate_move_signals(session)
    # 4개 시그널 간 평균 상관계수
    avg_corr = corr_matrix.values[np.triu_indices(4, k=1)].mean()
    assert avg_corr > 0.3, f"시그널 평균 상관 {avg_corr:.3f} < 0.3 — 프록시 전략 재검토 필요"

def test_signal_coverage(session):
    from features.move_signal import compute_move_signal_index
    result = compute_move_signal_index(session)
    assert result.filter(F.col("MOVE_SIGNAL_INDEX").is_null()).count() == 0
    assert result.select("CITY_CODE").distinct().count() == 25
\`\`\`

## 참조
- `docs/specs/dev_spec.md` A4-1 (MOVE_SIGNAL_INDEX 산출식 + 교차검증)
- S1=OPEN_COUNT, S2=ΔRESIDENTIAL_POP, S3=NEW_HOUSING_BALANCE, S4=ΔELECTRONICS_FURNITURE_SALES
- 의존성: #21 (통합 마트)

## 불변식
- 4종 시그널 융합 — MULTI_SOURCE 3구(중·영등포·서초) 한정. TELECOM_ONLY 22구는 단일 프록시(norm(OPEN_COUNT))로 fallback.
- 가중치 초기값 (MULTI_SOURCE만 적용): w1=0.35, w2=0.25, w3=0.25, w4=0.15
- 상관 r̄ < 0.3이면 프록시 전략 자체를 재검토 (MULTI_SOURCE 3구 샘플 54~102행 통계 한계 고려)
- dev_spec A4-1 Dual-Tier 산출식 분기 준수 (#40 검증 반영)

## 작업 내역

### 2026-04-09
- 세션 시작, AC 0/4 미완료, 구현 대기 상태
- 01_plan.md 구현 계획 확인 완료
- 구현 완료:
  - `features/__init__.py`, `features/.ai.md` 생성
  - `features/move_signal.py` — compute_move_signal_index(), update_mart_with_signal_index(), validate_move_signals()
  - `tests/test_07_signal_validation.py` — TC-04~TC-07
  - `sql/test/test_07_move_signal.sql` — TC-01~TC-04
  - `sql/ddl/002_add_move_signal_index.sql` — ALTER TABLE 마이그레이션
- S1=CONTRACT_COUNT (OPEN_COUNT 아님, dev_spec A4-1 반영)
- CARRYOVER_RATIO 추가 (#23 ML 피처용)
- Snowflake 실데이터 TC 검증 완료:
  - TC-01 null_idx=0 PASS / TC-02 범위 0~1 PASS / TC-03 25구 PASS / TC-04 분포 PASS
  - 상관 검증: r(S1↔S3)=-0.215 → S3 제외, 3종 융합(w1=0.45,w2=0.35,w4=0.20)으로 변경
  - dev_spec A4-1 가중치 업데이트 완료

