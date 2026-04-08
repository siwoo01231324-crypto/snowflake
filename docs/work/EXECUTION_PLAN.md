# EXECUTION_PLAN — Dual-Tier Pivot

> 작성: 2026-04-08 | 해커톤 마감: 2026-04-12 (D-4) | 1인 개발
> 상태: **진행 중** (#40 Ready 대기)

---

## 0. 이 문서의 목적

아정당 25구 / SPH·RICHGO 3구 Marketplace 샘플 제약이 확정된 이후의 **전체 실행 계획**을 한 파일에 모은다. 세션 재시작 시 이 파일만 읽으면 현재 맥락·남은 작업·의존성·순서를 전부 복원할 수 있어야 한다.

세션 시작 시 읽는 순서: `CLAUDE.md` → 이 파일 → 각 이슈 본문/코멘트.

---

## 1. 배경 — 데이터 현실

### 1.1 실측 커버리지 (2026-04-08 Python snowflake-connector로 검증됨)

| 데이터셋 | 구 커버리지 | 동 커버리지 | 기간 | 근거 |
|---|---|---|---|---|
| 아정당 `V_TELECOM_NEW_INSTALL` | **25개 구 전부** | 구 단위 | 2023-03 ~ 2026-05 (39개월) | INSTALL_CITY ↔ SPH CITY_KOR_NAME 완벽 1:1 |
| SPH `V_SPH_FLOATING_POP` | **3개 구만** (11140 중 / 11560 영등포 / 11650 서초) | 동 단위 | 2021 ~ 2025 | Marketplace 샘플 |
| SPH `V_SPH_CARD_SALES` | 동일 3구 | 동 단위 | 2021 ~ 2025 | Marketplace 샘플 |
| SPH `V_SPH_ASSET_INCOME` | 동일 3구 | 동 단위 | 2021 ~ 2025 | Marketplace 샘플 |
| RICHGO `V_RICHGO_MARKET_PRICE` | 동일 3구 | 26개 동 + 3개 구 집계 (총 29 BJD) | 2012-01 ~ 2024-12 | Marketplace 샘플 |
| SPH `M_SCCO_MST` | 25구 465동 (마스터 코드북만) | 동 단위 | — | 지도 데이터 |

**4종 시간 교집합: 2023-03 ~ 2024-12 (22개월)**

### 1.2 `MART_MOVE_ANALYSIS` 현재 구조 (#21 PR #41 머지 완료)

- **850행** = 25구 × 34개월 (202307 ~ 202604, 양 끝 데이터 갭 제거)
- **`DATA_TIER` 컬럼**으로 이원화:
  - `MULTI_SOURCE` (3구): 102행 — 아정당 + SPH3종 + RICHGO 15+ 피처
  - `TELECOM_ONLY` (22구): 748행 — 아정당 OPEN/CONTRACT/PAYEND 3피처만
- 구현: `pipelines/preprocessing.py:14` `build_integrated_mart()`
- 테스트: `sql/test/test_06_integrated_mart.sql` (TC-01~TC-06 PASS)
- MULTI_SOURCE 3구: `["11140", "11560", "11650"]` — 중구 / 영등포구 / 서초구

---

## 2. Dual-Track 전략

풀 모델 25구는 **불가능**. 대신 두 트랙으로 분리:

| Track | 대상 | 피처 | 모델 후보 | 샘플수 | 발표 역할 |
|---|---|---|---|---|---|
| **A — 25구 경량** | 서울 25구 전부 | **CONTRACT_COUNT (주 선행)** + OPEN_COUNT + PAYEND_COUNT | 선형 / 이동평균 | 850 | 서울 전역 이사 시그널 히트맵 (커버리지 임팩트) |
| **B — 3구 풀** | 중·영등포·서초 | 아정당 + SPH3종 + RICHGO 15+ 피처 | Ridge / LightGBM | 54 ~ 102 | 다중 데이터 교차검증 예측 엔진 (정밀도 임팩트) |

### 2.1 발표 핵심 메시지

> "통신 신규 계약 접수(CONTRACT)는 실제 개통(OPEN)보다 평균 1개월 선행하며, 공식 전입신고(주민등록법 §16, 이사 후 14일)와 KOSIS 집계 후행 시차까지 더하면 **공식 이사 통계보다 2~4주 이상 빠른 선행 시그널**이다. 서울 25구 38개월 패널 데이터에서 r=0.895 (p<0.001, n=841) 로 실증했다. 이 구조적 사실 위에 25구 경량 + 3구 풀 Dual-Tier 프레임워크를 세워, Marketplace 데이터 확장 시 즉시 전 권역 풀 모델로 전개 가능한 **확장형 프레임워크**를 구축했다."

### 2.2 3구 권역 성격 (발표 스토리 근거)

| 구 | 성격 | 이사 수요 예상 패턴 |
|---|---|---|
| **중구** (11140) | 도심 오피스·상업 | 주거 인구 적음, 단신·직장 중심 |
| **영등포구** (11560) | 금융·상업·주거 혼합 | 직주근접, 중소가구 유입 |
| **서초구** (11650) | 고급 주거·학군지 | 가족 단위, 학군 따라 이동 |

정량 카드 + 발표 스크립트: `docs/presentation/01_district_profiles.md` (#43, `V_DISTRICT_PROFILE_3GU` 6/6 TC PASS)

### 2.3 "2-4주 선행" 검증 프레임워크 (2026-04-09 #42 신규)

발표에서 "**우리가 예측한다**"는 명제를 정당화하기 위한 증거 체계. 본 섹션은 모든 후속 이슈(#22, #23, #28)의 설계·검증 기준이 된다.

#### 2.3.1 4층 증거 체인 (이 순서대로 발표)

| 레이어 | 주장 | 근거 | 상태 |
|---|---|---|---|
| **Layer 1** (내부) | CONTRACT_COUNT 는 OPEN_COUNT 보다 1개월 선행 | 서울 25구 × 38개월 패널 r=0.895, n=841, p<0.001 / carryover 28~30% | ✅ 실증 (2026-04-09) |
| **Layer 2** (교차검증) | CONTRACT 는 KOSIS 공식 전입신고보다 k개월 선행 | KOSIS `DT_1B040A3` 교차검증 결과 | 🔄 Worker 3 진행 중 (1회 검증), 자동화는 #46 |
| **Layer 3** (법률) | 전입신고는 이사 후 14일 이내 법정 기한 → 공식 통계는 구조적 후행 | 주민등록법 §16 | ✅ 법적 근거 |
| **Layer 4** (upper bound) | 부동산 매매 계약~잔금 2~3개월 시차 → 이사 예정 상한 외곽 | 국토부 실거래가 API (백로그 #46) | ✅ 공공 데이터 |

**종합 논리**:
```
D-90~D-60 [매매 계약 체결]       ← 국토부 RTMS (upper bound, Layer 4)
D-30      [CONTRACT 접수] ⭐     ← 아정당 V05 (우리 주 선행 시그널, Layer 1)
D-14~D-7  [통신 이전신청 권장]   ← 업계 관행 (비공식)
D-day     [이사 실행 + OPEN 개통] ← 아정당 V05 후행 확인 (Layer 1)
D+1~D+14  [전입신고 법정 기한]    ← 주민등록법 §16 (Layer 3)
D+14~D+45 [KOSIS 월간 집계]       ← 공식 통계 ground truth (Layer 2)
```

"CONTRACT → KOSIS 집계" 구간은 **최소 4주 ~ 최대 10주** → **"2-4주 선행"은 보수적 하한**.

#### 2.3.2 5단계 검증 프레임 (모델 완성도 판정)

| 단계 | 방법 | 산출 | 책임 이슈 |
|---|---|---|---|
| ① Lag 증명 | CONTRACT vs KOSIS 전입 lag correlation (k=−3~+3) | k=+1 peak r | #42 §H6 (1회) / #46 (자동) |
| ② Train/Test 분리 | Walk-forward: Train 2023-03~2024-12 / Test 2025-01~2025-12 | Track A MAPE ≤ 25% / Track B MAPE ≤ 20% | #23 PREDICT_MOVE_DEMAND |
| ③ 베이스라인 대비 | Naive·이동평균·우리 모델 MAPE 비교 | 우리 > baseline Δ% | #23 |
| ④ 4종 융합 우위 | Track A vs Track B MAPE 비교 | Track B 개선 입증 | #22 MOVE_SIGNAL_INDEX + #23 |
| ⑤ Live 재현성 | Snowpark ML + SQL UDF 호출 | `PREDICT_MOVE_DEMAND('11650','202512')` 단일 호출 재현 | #23 + #28 Streamlit |

#### 2.3.3 발표 직전 필수 시연 (5분 데모 §3:00~4:00 연동)

Streamlit 대시보드 한 차트에 **3점 동시 표시**:
1. `[CONTRACT(2025-05)]` — 입력 시그널
2. `[예측 2025-06 ŷ]` — 우리 모델 출력
3. `[KOSIS 실제 2025-06 y]` — ground truth

자막: "**1개월 앞서 예측 · 공식 통계 MAPE {TBD}%**"

#### 2.3.4 관련 문서
- `.omc/research/42-lead-time-verification.md` — Worker 1 Snowflake 내부 검증 + Worker 3 KOSIS 교차검증 (§H6)
- `.omc/research/42-public-data-sources.md` — 공공 데이터 카탈로그
- `docs/presentation/00_pitch_story.md` — §4 증거 체인 + §7 검증 프레임 + §9 5분 데모 대본
- `docs/specs/dev_spec.md` — S1 선행지표 정의 (L670), MOVE_SIGNAL_INDEX 산출식 (L684)

---

## 3. 이슈 상태·의존성 (2026-04-09 기준)

### 3.1 완료 (머지됨)

| # | 제목 | 비고 |
|---|---|---|
| #17 | RICHGO 참조 뷰 3개 | V_RICHGO_MARKET_PRICE / POPULATION / YOUNG_CHILDREN |
| #18 | SPH 참조 뷰 4개 | V_SPH_FLOATING_POP / CARD_SALES / ASSET_INCOME / REGION_MASTER |
| #19 | 아정당 + NextTrade 참조 뷰 6개 | V_TELECOM_* / V_NEXTTRADE_* |
| #20 | BJD↔DISTRICT 매핑 뷰 | V_BJD_DISTRICT_MAP (동 26 + 구 3 = 29 매핑) |
| #21 | 통합 마트 | MART_MOVE_ANALYSIS (DATA_TIER 이원화) |

### 3.2 Ready — 지금 착수 가능

| # | 제목 | 의존성 | 예상 작업량 |
|---|---|---|---|
| **#40** | chore: dev_spec 오류 7건 정정 (#21에서 발견) | — | 2~3h |
| **#43** | feat: 3구 권역 프로파일 카드 데이터셋 | #21 ✅ | 3~4h |

### 3.3 Backlog — 블록됨

| # | 제목 | 블록됨 by | 블로킹 | AC 수정 필요 |
|---|---|---|---|---|
| #42 | chore: 스코프 재정의 + 발표 스토리 + 기획서 | #40 ✅ | #22, #23, #28 (S1 컬럼 CONTRACT 변경 반영 필요) | — (진행 중 2026-04-09, #46 분리) |
| #22 | feat: MOVE_SIGNAL_INDEX Dual-Tier 융합 | #40 ✅, #42 | #23, #28 | ⚠️ **S1 = CONTRACT_COUNT 재정의 반영 필요** (#42 §2.3) |
| #23 | feat: ML Dual-Track + PREDICT_MOVE_DEMAND UDF | #22 | #28 | ✅ 코멘트 #23 + ⚠️ B3-1 L1408-1410 주석 정정 반영 (#42) |
| #24 | feat: CALC_ROI UDF | #40 ✅, #42 | #29 | ✅ 코멘트 #24 |
| #25 | feat: GET_SEGMENT_PROFILE UDF | #40 ✅, #42, (#43 권장) | #29 | ✅ 코멘트 #25 |
| #26 | feat: Cortex Analyst YAML 4개 | #40 ✅, #42 | — | ✅ 코멘트 #26 |
| #27 | feat: Cortex AI Functions | — (독립) | — | — |
| #28 | feat: Streamlit 히트맵 | #22, #23, #43 ✅ | #29 | ✅ 코멘트 #28 + ⚠️ Tier 배지 + 검증 시연 차트 (#42 §2.3.3) |
| #29 | feat: Streamlit 세그먼트 + ROI | #24, #25, #28 | — | ✅ 코멘트 #29 |
| **#46** | **feat(data): 공공 데이터 통합 검증 파이프라인** | #42 | — | 신규 (2026-04-09) |

### 3.4 신규 이슈 요약

- **#42** (2026-04-08 생성, 진행 중 2026-04-09):
  - 제목: `chore: 프로젝트 스코프 재정의 + 발표 스토리 + 기획서 Dual-Tier 업데이트`
  - 포함 파일: `docs/specs/dev_spec.md` (v3.1 #42 엔트리) · `docs/presentation/00_pitch_story.md` (신규, 2026-04-09) · `docs/whitepaper/v1.0-moving-intelligence.md` (v1.2) · `docs/whitepaper/v1.1-branding-strategy.md` (v1.1.1 팩트 정정)
  - 2026-04-09 확장: "2-4주 선행" 가설 실데이터 검증 완료 (`.omc/research/42-lead-time-verification.md`), S1 선행지표 컬럼 `OPEN` → `CONTRACT` 재정의, 발표 검증 프레임워크 (§2.3) 추가
- **#43** (2026-04-08 생성, 완료 f0f6065):
  - 출력: `V_DISTRICT_PROFILE_3GU` 뷰 + `docs/presentation/01_district_profiles.md`
- **#46** (2026-04-09 생성):
  - 제목: `feat(data): 공공 데이터 통합 검증 파이프라인 (KOSIS/국토부/서울열린데이터)`
  - 목적: #42 §2.3 Layer 2 (KOSIS 교차검증) 자동화 + Layer 4 (국토부 실거래가) 연동
  - 선행: #42 머지

---

## 4. 의존성 그래프

```
[완료]
  #17 · #18 · #19 · #20 ──→ #21 (마트, Dual-Tier 이원화)
                              │
                              ▼
[Ready]                    ┌──┴──┐
  #40 (dev_spec 정정)      │     │
  #43 (권역 카드)           │     ▼
                          │   #27 (Cortex AI — 독립)
                          │
                          ▼
[Backlog / #40 블록됨]
  #42 (스코프·스토리·기획서)
    │
    ├──→ #22 (MOVE_SIGNAL_INDEX Dual-Tier)
    │      │
    │      └──→ #23 (ML Dual-Track + PREDICT UDF)
    │             │
    ├──→ #24 (CALC_ROI UDF) ───────────────────┐
    │                                          │
    ├──→ #25 (GET_SEGMENT_PROFILE UDF) ────────┤
    │     (#43 권장 선행)                       │
    │                                          │
    └──→ #26 (Cortex Analyst YAML)             │
                                               │
                                               ▼
                                        #28 (Streamlit 히트맵)
                                               │
                                               ▼
                                        #29 (Streamlit 세그먼트+ROI)
```

---

## 5. Day 0~4 실행 순서 (해커톤 마감 04-12)

### Day 0 — 2026-04-08 (오늘)
- `/si 40` — dev_spec 오류 7건 + 추가 정정 5건 (Dual-Tier 반영)
  - **Critical path의 유일한 진입점**

### Day 1 — 2026-04-09
- `/si 42` — 스코프 재정의 + pitch_story 초안 + 기획서 v1.2
  - #40 완료 직후 착수
- 병렬 가능: `/si 27` (Cortex AI Functions, 독립)
- 병렬 가능: `/si 43` (권역 카드, 독립)

### Day 2 — 2026-04-10
- `/si 22` — MOVE_SIGNAL_INDEX Dual-Tier 융합 (Critical path)
- 병렬 가능: `/si 24` — CALC_ROI UDF
- 병렬 가능: `/si 25` — GET_SEGMENT_PROFILE UDF (#43 결과 재사용)
- 병렬 가능: `/si 26` — Cortex Analyst YAML

### Day 3 — 2026-04-11
- `/si 23` — ML Dual-Track + PREDICT_MOVE_DEMAND UDF (#22 결과 필요)
- `/si 28` — Streamlit 히트맵 (#22·#23·#43 결과 필요)

### Day 4 — 2026-04-12 (마감)
- `/si 29` — Streamlit 세그먼트 + ROI 탭
- 통합 테스트 + 발표 리허설

---

## 6. 병렬 착수 가능 구간 (1인 개발 현실 고려)

1인이 동시 작업하기는 어렵지만, **중간 대기 시간 활용**은 가능:

| 시점 | 병렬 가능 이슈 | 활용 전략 |
|---|---|---|
| 지금 | **#40 / #43** | 메인은 #40, 렉 걸릴 때 #43 잠깐 |
| #40 완료 | **#42 / #27** | 메인은 #42 (critical path), #27은 ML·UDF 대기 시간 |
| #42 완료 | **#22 / #27 / #43** | #22가 critical, 나머지는 멀티태스킹 |
| #22 완료 | **#23 / #24 / #25 / #26** | #23이 critical, #24·#25·#26은 Snowflake 컴파일 대기 중 병행 |
| #23·#24·#25 완료 | #28 | Streamlit 앱 스켈레톤 — 연동 집중 |
| #28 완료 | #29 | 마지막 탭 + 리허설 |

### Critical Path
```
#40 → #42 → #22 → #23 → #28 → #29
```
**5건 순차** — 이 경로가 최소 완료 시간을 결정. 총 예상 5~6 작업일 → D-4에 빠듯.

---

## 7. 리스크 및 완화

| # | 리스크 | 영향 | 완화 |
|---|---|---|---|
| R1 | Track B 학습 샘플 54~102행 부족 → XGB 과적합 | 예측 정확도 왜곡 | Ridge / 피처 압축 / walk-forward CV |
| R2 | 1인 D-4 critical path 5건 순차 → 마감 초과 위험 | 해커톤 제출 실패 | #27·#24·#25·#26 병렬 활용, #29 최소 기능만 |
| R3 | Cursor IDE가 `.worktree/000021-integrated-mart/` 잠금 → cleanup 실패 | git 상태 노이즈 | Cursor 재시작 후 `rmdir` 재시도 |
| R4 | `.worktree/000016-db-schema/` · `000020-bjd-district-mapping/` stale | 혼란 | 동일 방법으로 정리 |
| R5 | Snowflake MCP 연결 불안정 | 개발 중 확인 지연 | `gh` + Python snowflake-connector 병행 |
| R6 | Cortex Analyst US West Oregon 리전 한정 | #26·#27 지역 이슈 없음 | 이미 계정이 Oregon — 확인됨 |
| R7 | RICHGO 2024-12 이후 데이터 없음 → 아정당 2025~2026 구간에 시세 NULL | Track B 최근 데이터 비어있음 | 학습 기간을 2023-03 ~ 2024-12로 명시 제한 |

---

## 8. 변경 이력

- **2026-04-09** #42 중간 업데이트 — "2-4주 선행" 가설 실데이터 검증 + S1 선행지표 재정의
  - 배경: #42 발표 스토리 작성 중 whitepaper v1.0의 "통신 주소변경" 근거가 Snowflake 실데이터와 불일치 발견. dev_spec L1410 "OPEN_COUNT = 이사 후 선행지표" 내부 모순. S1 컬럼을 OPEN 으로 쓰면 "선행" 주장 불가.
  - 검증: Worker 1 (scientist) Snowflake 내부 검증 → CONTRACT→OPEN k=+1 r=0.895 (n=841), carryover 28~30% (`.omc/research/42-lead-time-verification.md` §H1·§H5). Worker 2 (document-specialist) 공공 데이터 카탈로그 → KOSIS `DT_1B040A3` · 주민등록법 §16 · 국토부 실거래가 API (`.omc/research/42-public-data-sources.md`). Worker 3 (scientist) KOSIS 교차검증 §H6 진행 중.
  - 해결: §2.3 "2-4주 선행" 4층 증거 체인 + 5단계 검증 프레임워크 신규 추가. dev_spec S1 컬럼 OPEN → CONTRACT 재정의 (v3.1). whitepaper v1.0 → v1.2 팩트 정정. `docs/presentation/00_pitch_story.md` 신규 생성. 
  - 신규 이슈: **#46** (공공 데이터 통합 검증 파이프라인, 백로그)
  - 기존 이슈 영향: #22 (S1 컬럼 변경 필수 반영), #23 (B3-1 주석 정정), #28 (검증 시연 차트 추가)
- **2026-04-08** 초안 생성 — Dual-Tier 확정 직후 (#21 머지 후)
  - 배경: #21 작업 중 실데이터 검증으로 SPH/RICHGO 3구 한정 확인
  - 해결: `DATA_TIER` 컬럼 이원화 + Dual-Track 전략 수립
  - 신규 이슈: #42, #43 생성
  - 기존 이슈: #22·#23·#24·#25·#26·#28·#29에 AC 수정 권고 코멘트 추가
  - 상태 전환: #40 → Ready, #43 → Ready

---

## 9. 참조

- `CLAUDE.md` — 프로젝트 가이드
- `AGENTS.md` — 레포 목차
- `docs/specs/dev_spec.md` — 기술 명세 v3.1 (#42 변경 이력 참조)
- `docs/whitepaper/v1.0-moving-intelligence.md` — 기획서 v1.2 (#42 변경 이력 참조)
- `docs/whitepaper/v1.1-branding-strategy.md` — 브랜딩 전략 v1.1.1 (#42 팩트 정정)
- `docs/presentation/00_pitch_story.md` — 발표 스토리 종합 (#42, 2026-04-09 신규)
- `docs/presentation/01_district_profiles.md` — 3구 권역 프로파일 (#43)
- `.omc/research/42-lead-time-verification.md` — "2-4주 선행" 실데이터 검증 (#42 §H1~H6)
- `.omc/research/42-public-data-sources.md` — 공공 데이터 카탈로그 (#42)
- `docs/work/done/000021-integrated-mart/01_plan.md` — Dual-Tier 결정 ADR
- `pipelines/preprocessing.py` — `MULTI_SOURCE_CITIES` 정의 위치
- GitHub Issues: #17~#20 (done) · #21 (done) · #22~#29, #40, #42, #43 (backlog/ready)
