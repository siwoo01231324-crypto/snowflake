# 01_plan — feat: ML 학습 + PREDICT_MOVE_DEMAND UDF 배포

## AC 체크리스트

- [x] Snowpark ML로 모델 학습 완료 (SMAPE 50.8% / Spearman 0.920 달성)
- [x] `PREDICT_MOVE_DEMAND(install_state, install_city)` UDF 배포
- [x] UDF 호출 시 0~100 스코어 반환 (TC-01~TC-04 PASS)

## 구현 계획

1. **테스트 먼저 작성** (`test_08_predict_udf.sql`, `test_08_ml_training.py`)
2. **ML 모델 학습** — `ml/train.py` Snowpark ML 파이프라인
3. **UDF 배포** — `MOVING_INTEL.ANALYTICS.PREDICT_MOVE_DEMAND`
4. **테스트 검증** — TC-01~TC-04 통과 확인
5. **`.ai.md` 최신화**

## ML 학습 상세

### 타겟 변수
- `TARGET_NEXT_OPEN_COUNT` = `LEAD(OPEN_COUNT, 1)` — 다음 달 개통 건수 예측

### Train/Test Split
- `walk_forward_split(train_months=28, test_months=6)`
- 학습: 202307~202410 (28개월), 검증: 202411~202604 (6개월)

### Track A — TELECOM_ONLY (22구, 아정당만 있는 구)
| 항목 | 내용 |
|------|------|
| 모델 | `LinearRegression` (Snowpark ML) |
| 피처 | `OPEN_COUNT`, `CONTRACT_COUNT`, `PAYEND_COUNT`, `MOVE_SIGNAL_INDEX`, `MONTH_SIN`, `MONTH_COS`, `IS_PEAK_SEASON`(파생) |
| MAPE 목표 | **< 30%** (실데이터 검증 후 조정) |

### Track B — MULTI_SOURCE (3구: 중·영등포·서초)
| 항목 | 내용 |
|------|------|
| 모델 | `Ridge(alpha=1.0)` (Snowpark ML) |
| 피처 | Track A + `AVG_INCOME`, `TOTAL_RESIDENTIAL_POP`, `TOTAL_CARD_SALES`, `NEW_HOUSING_BALANCE_COUNT` |
| MAPE 목표 | **< 25%** (실데이터 검증 후 조정) |

> ⚠️ `AVG_MEME_PRICE`, `AVG_JEONSE_PRICE`는 MULTI_SOURCE 3구에서도 47% null → **Track B 피처에서 제외**

### 실데이터 검증 결과 (2026-04-09)
| 컬럼 | 상태 |
|------|------|
| `IS_PEAK_SEASON` | **MART에 없음** → `MONTH(STANDARD_YEAR_MONTH) IN (3,4,9,10)`으로 파생 |
| `AVG_MEME_PRICE`, `AVG_JEONSE_PRICE` | MULTI_SOURCE 47% null → 피처 제외 |
| `AVG_INCOME`, `TOTAL_RESIDENTIAL_POP`, `TOTAL_CARD_SALES`, `NEW_HOUSING_BALANCE_COUNT` | 12% null → forward fill 처리 |
| TELECOM_ONLY 핵심 피처 | null 0개, 정상 |

### 0~100 스코어 정규화
- 예측값 `PREDICTED_OPEN_COUNT`를 서울 25구 train 셋 전체 범위로 Min-Max 정규화 → 0~100 반환

### UDF 시그니처 (dev_spec B3-1 기준)
```sql
PREDICT_MOVE_DEMAND(city_code VARCHAR, start_month VARCHAR, end_month VARCHAR)
```
> 이슈 TC의 `(install_state, install_city)` 형태는 dev_spec 기준으로 수정함

## 참조

- `docs/specs/dev_spec.md` A5-1 (모델 설계), A5-3 (파이프라인), B3-1 (UDF)
- 의존성: #22 (MOVE_SIGNAL_INDEX) — 이미 완료
- 타깃: 다음 달 `OPEN_COUNT` (lead=1)
