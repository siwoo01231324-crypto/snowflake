# 01 — 구현 플랜 (#40 dev_spec 오류 7건 정정)

## AC 체크리스트

- [ ] dev_spec.md 7개 오류 항목 모두 정정
- [ ] 변경 이력 섹션에 #21 발견 내용 명시 (line 번호 + 변경 전/후)
- [ ] 후속 이슈(#22~) 본문에 영향 없는지 확인 + 필요 시 동기화
- [ ] docs/specs/.ai.md 최신화

## 정정 대상 7건 요약

| # | 항목 | 위치 | 변경 전 → 변경 후 |
|---|------|------|------------------|
| 1 | INSTALL_STATE 필터 | line 629, 2292, 2550 | `'서울특별시'` → `'서울'` |
| 2 | RICHGO SD 필터 | A3-3 line 540 | `'서울특별시'` → `'서울'` |
| 3 | SPH 커버리지 | line 86, 87, 107, 820, 1165, 1193, 1523, 2342 | '25개 구 467개 동' → 마스터(M_SCCO_MST) 25개 구 / FACT 3개 구(중구·영등포구·서초구) |
| 4 | 테이블명 | A3-3 line 600 | `INTEGRATED_MART` → `MART_MOVE_ANALYSIS` |
| 5 | 조인 단위 | line 527-601 | 동(DISTRICT_CODE) → 구(CITY_CODE) |
| 6 | YEAR_MONTH 변환 | A3-3 | `TO_CHAR(YEAR_MONTH, 'YYYYMM')` 변환 로직 추가 |
| 7 | 행정동/법정동 표현 | line 87, 107 등 | '467개 동' → '467개 법정동(BJD)' 명시 |

## Dual-Tier 추가 정정 5건 (#21 머지 이후 확정 — 2026-04-08)

> **배경**: #21 작업 중 아정당 25구 / SPH·RICHGO 3구 Marketplace 샘플 제약이 Python snowflake-connector로 실증 확정됨. `MART_MOVE_ANALYSIS`가 `DATA_TIER('MULTI_SOURCE'/'TELECOM_ONLY')` 컬럼으로 이원화되어 머지됨(PR #41).
>
> **상세 컨텍스트**: `docs/work/EXECUTION_PLAN.md` (master에 hotfix `a8b104b`로 커밋됨 — 이 워크트리엔 아직 없음. 필요 시 `git fetch origin && git merge origin/master` 후 참조).

### 추가 항목 요약

| # | 섹션 | 위치 | 핵심 수정 |
|---|------|------|-----------|
| 8 | A4-1 MOVE_SIGNAL_INDEX | line 655~760 | 산출식 Tier 분기, `validate_move_signals()` MULTI_SOURCE 필터, 검증 기준 샘플수 주석 |
| 9 | A5-1 MVP 학습 계획 | line 851~867 | 단일 표 → Track A(25구 경량)·Track B(3구 풀) 두 표 분리 |
| 10 | A5-3 파이프라인 + A6 요약 | line 878~946, 957·960·962 | `train_and_deploy()` 분리, `random_split` → `walk_forward_split`, MAPE 목표 Track별 차등, A6 요약 3행 수정 |
| 11 | B3 UDF 섹션 | line 1303~1510 | B3-0 커버리지 매트릭스 신규, 각 UDF 반환에 `tier`·`confidence` 추가, B3-3 line 1491 허위 문장 수정 |
| 12 | C4 ROI 계산기 | line 2379~2466 | Tier 감지 로직, `get_apt_price_by_region()` 22구 fallback, UI Tier 배지 |

### 항목 8 — A4-1 MOVE_SIGNAL_INDEX 상세

| Line | 기존 | 수정 |
|---|---|---|
| 668~678 | 단일 산출식 `w1·S1 + w2·ΔS2 + w3·S3 + w4·ΔS4` | `CASE WHEN DATA_TIER='TELECOM_ONLY' THEN norm(OPEN_COUNT) WHEN DATA_TIER='MULTI_SOURCE' THEN w1·norm(S1)+w2·norm(ΔS2)+w3·norm(S3)+w4·norm(ΔS4) END` |
| 683 | "S1 시/군/구 단위 → S2~S4 행정동 단위이므로 집계 조인" | "S1 25구 / S2~S4 3구만 실존 → `MART_MOVE_ANALYSIS.DATA_TIER` 컬럼 기반 분기 (전처리는 #21에서 완료)" |
| 697 `validate_move_signals()` | 원본 SPH FACT 테이블 직참조 (25구 가정) | 함수 상단에 `.filter(F.col("DATA_TIER")=="MULTI_SOURCE")` 필터 또는 마트 기반 재구현 |
| 750~755 교차검증 기준표 | `r̄ > 0.35` 단일 기준 | 표 상단에 `> ⚠️ 기준: MULTI_SOURCE 3구 한정, 관측 샘플 54~102행, 통계 유의성 한계 고려` 주석 |

### 항목 9 — A5-1 Track A/B 분리 상세

기존 단일 표(line 855~865)를 **두 개의 표**로 대체:

**Track A — 25구 경량 모델**

| 항목 | 내용 |
|------|------|
| 대상 | `DATA_TIER` 무관 25구 전체 |
| 샘플 수 | 850 (25구 × 34개월) |
| 피처 | `OPEN_COUNT`, `CONTRACT_COUNT`, `PAYEND_COUNT`, `IS_PEAK_SEASON`, `MONTH_SIN`, `MONTH_COS` |
| 알고리즘 | LinearRegression 또는 지수이동평균 |
| 학습 기간 | 202307 ~ 202604 (34개월) |
| 평가 | walk-forward 최종 6개월 |
| MAPE 목표 | **< 25%** |

**Track B — MULTI_SOURCE 3구 풀 모델**

| 항목 | 내용 |
|------|------|
| 대상 | `DATA_TIER = 'MULTI_SOURCE'` (중·영등포·서초) |
| 샘플 수 | 102 (3구 × 34개월), RICHGO∩아정당 교집합 시 54 |
| 피처 | Track A + `MOVE_SIGNAL_INDEX` + `TOTAL_RESIDENTIAL_POP` + `AVG_INCOME` + `TOTAL_CARD_SALES` + `NEW_HOUSING_BALANCE_COUNT` + `AVG_MEME_PRICE` + `AVG_JEONSE_PRICE` |
| 알고리즘 | **Ridge(α=1.0)** 또는 **LightGBM(min_data_in_leaf=5)** — ⚠️ XGB 금지 (소샘플 과적합) |
| 학습 기간 | 202307 ~ 202412 (RICHGO 상한) |
| 평가 | walk-forward 최종 6개월 |
| MAPE 목표 | **< 20%** |

### 항목 10 — A5-3 파이프라인 + A6 요약 상세

**A5-3 수정 (line 878~946)**:
- **line 904**: `INTEGRATED_MART` → `MART_MOVE_ANALYSIS` (⚠️ 기존 7건 중 #4와 동일 오류의 **중복 위치**, 놓치지 말 것)
- **line 902~945** 함수 분리:
  - `train_and_deploy()` 삭제
  - 신규 `train_track_a(session)` — 위 Track A 피처 + `LinearRegression`
  - 신규 `train_track_b(session)` — 위 Track B 피처 + `Ridge(alpha=1.0)` (MULTI_SOURCE 필터)
  - 공통 헬퍼 `walk_forward_split(mart, train_months=28, test_months=6)` 신규
  - 타겟 파생: `F.lead("OPEN_COUNT", 1).over(Window.partitionBy("CITY_CODE").orderBy("STANDARD_YEAR_MONTH"))`
- **line 917** `random_split([0.8, 0.2], seed=42)` → `walk_forward_split()` (시계열에 random split 부적합)
- **line 940~943** 서비스 등록: `predict_track_a_service` / `predict_track_b_service` 두 개
- `PREDICT_MOVE_DEMAND` UDF 내부에서 `DATA_TIER` 감지 후 올바른 모델 호출

**A6 MVP vs 고도화 표 수정 (line 955~967)**:
- **line 957** `데이터 범위` 행: `서울 전체 (RICHGO 2012-2024) + SPH 25구 467동` → `Track A: 25구 × 아정당 2023-2026 (850행) / Track B: 3구(중·영등포·서초) × 아정당+SPH+RICHGO 교집합 (54~102행)`
- **line 960** `데이터 조인` 행: `RICHGO ↔ 아정당 (핵심) + SPH (보조, 서울 전체)` → `MART_MOVE_ANALYSIS DATA_TIER 컬럼 기반 Tier별 피처 선택`
- **line 966** `평가 기준` 행: `MAPE < 20%` → `Track A MAPE < 25% · Track B MAPE < 20%`

### 항목 11 — B3 UDF 커버리지 매트릭스 상세

**line 1305 직후 신규 서브섹션 `### B3-0. UDF 커버리지 매트릭스 (Dual-Tier)` 삽입**:

```markdown
### B3-0. UDF 커버리지 매트릭스 (Dual-Tier)

| UDF | MULTI_SOURCE (3구: 중·영등포·서초) | TELECOM_ONLY (22구) |
|---|---|---|
| `PREDICT_MOVE_DEMAND` | Track B 풀 피처 모델 (Ridge, 15+ 컬럼) | Track A 경량 모델 (선형, 3 컬럼) |
| `CALC_ROI` | RICHGO 평당가 + SPH 업종 분포 정밀 ROI | OPEN_COUNT × 평균 단가 근사 ROI (low confidence) |
| `GET_SEGMENT_PROFILE` | population/income/consumption/housing 4섹션 풀 프로필 | telecom_summary 경량 프로필만 |

모든 UDF는 반환에 `tier` 또는 `data_tier` 필드를 포함한다.
UDF 호출 시 내부 로직: `CITY_CODE` → `DATA_TIER` 조회 → Tier별 분기 실행.
```

**B3-1 `PREDICT_MOVE_DEMAND` 수정**:
- **line 1329** `RETURNS TABLE (...)`에 `data_tier VARCHAR`, `confidence FLOAT` 컬럼 추가
- **line 1337~1350** 내부 로직 주석 맨 앞에 `"0. CITY_CODE 기반 DATA_TIER 감지 → Track A/B 모델 선택"` 단계 추가
- 인자명 검토: `district_code` (8자리 행정동) → 실제로는 `city_code` (5자리 시군구)가 Dual-Tier와 일치 — **인자 rename 권장** (후속 이슈 영향도 검토)

**B3-2 `CALC_ROI` 수정**:
- **line 1398** `RETURNS TABLE (...)`에 `tier VARCHAR`, `confidence VARCHAR` 추가
- **line 1418~1428** 내부 로직에 Tier 분기 단계 삽입

**B3-3 `GET_SEGMENT_PROFILE` 수정**:
- **line 1491** `필터: DISTRICT_CODE = district_code (서울 25개 구 모두 가능)` → `필터: CITY_CODE = city_code. SPH FLOATING/CARD/ASSET은 3구(중·영등포·서초)만 실존이므로, 22구 요청 시 아정당 경량 프로필만 반환` ⚠️ **명백한 허위 문장이므로 반드시 수정**

### 항목 12 — C4 ROI 계산기 상세

| Line | 기존 | 수정 |
|---|---|---|
| 2383~2400 (화면 레이아웃) | 현행 레이아웃 | 결과 카드 상단에 `[🟢 MULTI_SOURCE 정밀]` 또는 `[🟡 TELECOM_ONLY 근사]` **Tier 배지** 추가 |
| 2407 (지역 선택) | `서울 25개 구 (M_SCCO_MST 기반)` | 유지 + "선택한 구의 `DATA_TIER` 조회 → 배지/문구 렌더링" 주석 |
| 2414~2443 `calculate_roi()` | 단일 로직, Tier 구분 없음 | 함수 시작에 `data_tier = query_mart_tier(city_code)` 추가 → if/else 분기 (MULTI_SOURCE는 RICHGO/SPH 기반 정밀, TELECOM_ONLY는 OPEN_COUNT 기반 근사) |
| 2445~2463 `get_apt_price_by_region()` | RICHGO 직접 쿼리, 3구 외 빈 결과 무처리 | 결과 empty 시 `{"avg_meme_price": None, "fallback": True, "note": "TELECOM_ONLY 22구 — 시세 근사 미지원"}` 반환 |
| 2466 (데이터 근거) | 기존 | Tier 경고 추가: "TELECOM_ONLY 22구는 RICHGO 시세 없음 → 전환율 벤치마크의 상한 근사만 가능, 정밀도 ↓" |

## 중복 확인 (기존 7건과의 관계)

- **항목 10 (A5-3 line 904)** `INTEGRATED_MART` 는 **기존 7건 중 #4 테이블명 오류와 동일**하나, #4는 `line 600`만 명시되어 있어 **line 904는 놓칠 수 있음**. 두 위치 모두 수정 필수.
- **항목 11 (B3-3 line 1491)** SPH 25구 가정 허위 문장은 **기존 7건 중 #3 SPH 커버리지**에 언급된 line 목록(`86, 87, 107, 820, 1165, 1193, 1523, 2342`)에 **line 1491이 누락**되어 있음 — 기존 #3 대상에 추가 편입 필요.

## 완료 기준 추가

아래 체크박스를 기존 `## 완료 조건 (Definition of Done)` 섹션에 추가:

- [ ] 항목 8 (A4-1 MOVE_SIGNAL_INDEX Tier 분기) 완료
- [ ] 항목 9 (A5-1 Track A/B 분리) 완료
- [ ] 항목 10 (A5-3 + A6 수정, line 904 `INTEGRATED_MART` 중복 포함) 완료
- [ ] 항목 11 (B3-0 매트릭스 신규 + B3-1/2/3 Tier 반영 + line 1491 허위 문장 수정) 완료
- [ ] 항목 12 (C4 ROI Tier 분기 + fallback) 완료
- [ ] dev_spec.md 변경 이력에 Dual-Tier 5건 엔트리 별도 추가

## 실행 순서

1. **사전 조사**
   - docs/specs/dev_spec.md 전체 읽고 7개 항목의 현재 line 위치 재확인 (라인 번호는 이슈 생성 시점 기준 — 변동 가능)
   - docs/work/active/000021-integrated-mart/01_plan.md 참조해서 #21 검증 근거 확인

2. **항목별 정정**
   - #1 INSTALL_STATE: `replace_all` 또는 3개 위치 개별 Edit
   - #2 RICHGO SD: 단일 Edit
   - #3 SPH 커버리지: 위치별 문맥 다르므로 개별 Edit (자동 `replace_all` 주의)
   - #4 테이블명: 단일 Edit
   - #5 조인 단위: A3-3 섹션 블록 재작성
   - #6 YEAR_MONTH 변환: A3-3 코드 블록에 변환 로직 추가
   - #7 행정동/법정동 표기: 위치별 개별 Edit

3. **변경 이력 섹션 추가**
   - dev_spec.md 최하단(또는 기존 변경 이력 위치)에 `## 변경 이력` 섹션
   - `2026-04-08 #40 (#21 검증 기반 7건 정정)` 헤더 + 각 항목의 line 번호 + 변경 전/후 기재

4. **후속 이슈 영향도 확인**
   - `gh issue view 22` (~#41) body 확인
   - MART_MOVE_ANALYSIS 컬럼, SPH 커버리지, 조인 단위 의존성 점검
   - 영향 있으면 이슈 body 업데이트 또는 코멘트

5. **docs/specs/.ai.md 최신화**
   - dev_spec.md 개정 사실 기록
   - #21 발견 → #40 정정 흐름 요약

## 리스크 / 주의점

- **라인 번호 드리프트**: 이슈 본문의 line 번호는 당시 기준. 작업 시점엔 드리프트 가능 → 키워드 기반 재탐색 필요
- **`replace_all` 오용 주의**: '서울특별시' → '서울'은 문맥에 따라 의미가 다를 수 있음 (예: 행정구역 설명 문장은 유지). 반드시 코드/쿼리/필터 문맥만 정정
- **변경 이력 누락 금지**: 정정 내용만 바꾸고 기록 없이 넘어가면 후속 혼란 발생
- **#22~#41 영향도**: 일부 이슈는 이미 closed일 수 있음 → open 이슈만 업데이트 대상

## 완료 조건 (Definition of Done)

- [ ] 7개 항목 정정 완료 (Grep으로 `'서울특별시'` 검색 시 정정 대상 0건)
- [ ] dev_spec.md 변경 이력 섹션에 #40 엔트리 추가
- [ ] 후속 이슈 영향도 분석 결과 기록 (없으면 "영향 없음" 명시)
- [ ] docs/specs/.ai.md 업데이트
- [ ] 커밋 메시지: `refactor: dev_spec 오류 7건 정정 (#21에서 발견) (#40)`
