# chore: dev_spec 오류 7건 정정 (#21에서 발견)

**Issue**: #40
**URL**: https://github.com/siwoo01231324-crypto/snowflake/issues/40
**State**: OPEN
**Labels**: backlog

## 목적
이슈 #21 통합 마트 작업 중 Snowflake 실데이터 검증으로 발견된 dev_spec.md의 오류 7건을 정정한다.

## 배경
#21에서 Python snowflake-connector로 직접 Snowflake에 접속하여 실데이터를 검증하는 과정에서, dev_spec.md가 Marketplace 데이터의 실제 상태와 다른 부분 7건을 발견했다. 일부는 #20에서 우회 처리되었으나 dev_spec 원본이 여전히 오류 상태이며, 후속 이슈(#22~)에 그대로 영향을 줄 수 있어 일괄 정정이 필요하다.

## 발견된 오류

### 1. INSTALL_STATE 필터 오류 (line 629, 2292, 2550)
- dev_spec: `WHERE INSTALL_STATE = '서울특별시'`
- 실제: `'서울'` (짧은 형태)
- 영향: V_TELECOM_DISTRICT_MAPPED 매핑 0건 발생

### 2. RICHGO SD 필터 오류 (A3-3, line 540)
- dev_spec: `F.col('SD') == '서울특별시'`
- 실제: `'서울'`
- #20에서 V_RICHGO_MARKET_PRICE 뷰로 우회했으나 dev_spec 원본 코드는 여전히 오류 상태

### 3. SPH 데이터 커버리지 오기 (line 86, 87, 107, 820, 1165, 1193, 1523, 2342)
- dev_spec: 'SPH M_SCCO_MST 기반, 서울 25개 구 467개 동'
- 실제: M_SCCO_MST(마스터)만 25개 구. FACT 테이블(FLOATING_POPULATION_INFO, CARD_SALES_INFO, ASSET_INCOME_INFO)은 **3개 구만** (중구/영등포구/서초구) — 해커톤 Marketplace 샘플 한정
- 영향: '25개 구' 가정으로 후속 이슈 설계 시 데이터 갭 발생

### 4. 테이블명 불일치 (A3-3, line 600)
- dev_spec: `INTEGRATED_MART`
- 이슈 #21 AC: `MART_MOVE_ANALYSIS`
- #22가 `MART_MOVE_ANALYSIS`를 참조하므로 `MART_MOVE_ANALYSIS`가 표준

### 5. A3-3 조인 단위 오류 (line 527-601)
- dev_spec: 동(DISTRICT_CODE) 단위 조인
- 실제 필요: 구(CITY_CODE) 단위 (아정당이 시군구 단위이므로 최소 공통 해상도)

### 6. YEAR_MONTH 타입 변환 누락 (A3-3)
- 아정당 `YEAR_MONTH` = DATE 타입 (예: 2023-03-01)
- SPH `STANDARD_YEAR_MONTH` = VARCHAR(6) (예: 202303)
- dev_spec 코드에 `TO_CHAR(YEAR_MONTH, 'YYYYMM')` 변환 로직 없음

### 7. '행정동' vs '법정동' 표현 오류 (line 87, 107 등)
- dev_spec: 'M_SCCO_MST 467개 동' (행정동으로 암시)
- 실제: 467개는 **법정동(BJD)** 기준. DISTRICT_CODE 8자리는 법정동 코드 (예: 중구 74개 법정동 = 무교동, 명동1가, 명동2가...)
- 일반인이 생각하는 행정동(약 425개)과 다름

## 완료 기준
- [x] dev_spec.md 7개 오류 항목 모두 정정 (+ Dual-Tier 5건 + 잔여 8건 = 총 20건+)
- [x] 변경 이력 섹션에 #21 발견 내용 명시 (line 번호 + 변경 전/후) — `## 변경 이력` 섹션 신설
- [x] 후속 이슈(#22~) 본문에 영향 없는지 확인 + 필요 시 동기화 — 7개 이슈 body + 코멘트 동기화 완료

## 구현 플랜
1. dev_spec.md를 1회 전체 읽고 7개 항목의 정확한 line 위치 재확인
2. 항목별 Edit (특히 #3 SPH 커버리지는 여러 line에 분산 — replace_all 또는 개별 Edit)
3. dev_spec.md 변경 이력 섹션(또는 신규 섹션)에 #21 발견 내용 정리
4. #22 이슈 body에서 영향받는 부분 확인 (MART_MOVE_ANALYSIS 컬럼 의존성)
5. docs/specs/.ai.md 업데이트

## 참조
- 이슈 #21 (통합 마트 테이블 생성) — 발견 출처
- 이슈 #20 (BJD 매핑) — 항목 #2 우회 사례
- docs/work/active/000021-integrated-mart/01_plan.md — 상세 분석

## 불변식
- dev_spec은 Snowflake 실데이터로 검증된 사실만 기재
- 차원 테이블(M_SCCO_MST)과 사실 테이블(FACT_*)의 커버리지를 명확히 구분
- 코드 체계 표현 시 '행정동/법정동' 명시

## 개발 체크리스트
- [x] docs/specs/.ai.md 최신화 (v3 엔트리 + #40 흐름 요약)

## 작업 내역

### 2026-04-08 — /ri 세션 시작 스냅샷

- 브랜치: `refactor/000040-devspec-fix` (워크트리: `.worktree/000040-devspec-fix/`)
- 미커밋 변경: 없음 (워크폴더 추적 외)
- dev_spec.md 현재 상태: **정정 0건** — 7건 + Dual-Tier 5건 모두 미착수
  - `'서울특별시'` 잔존 8곳 (정정 대상: line 540, 629, 2292, 2550 / 유지: line 1177·1185 JSON 예시, 1721·1754 컬럼 description)
  - `INTEGRATED_MART` 잔존 4곳 (line 600, 882, 904, 976) — 01_plan.md 항목 #4·#10 모두 포함
  - `25개 구 467개 동` 잔존 다수 (line 86, 107, 236, 820, 1157, 1165, 1193, 1491, 1523, 1779, 2100, 2325, 2340, 2342, 2407, 2520, 2606, 2624, 2626, 2714, 2718, 2841)
  - 변경 이력 섹션: #20 엔트리만 존재(line 132~136), #40 엔트리 없음
- docs/specs/.ai.md: 13줄, dev_spec 줄 수가 옛 값(2,711줄)으로 표기 — 갱신 필요
- 01_plan.md: 12개 항목(7+5) 상세 플랜 완비, 그대로 실행 가능
- 다음 단계: **구현 대기** — 항목별 정정 → 변경 이력 추가 → .ai.md 갱신 순서로 진입

### 2026-04-08 — /finish-issue 완료 스냅샷

**팀 운영**: 3-worker team (`fix-devspec-040`)
- `ground-truth` (Snowflake 검증 + PR #41 코드 분석 + 후속 이슈 호환성 → `.omc/research/snowflake-ground-truth.md` 333줄 9 섹션)
- `editor-early` (dev_spec line 1~1300 편집, Phase A-G)
- `editor-late` (dev_spec line 1301~끝 편집, Phase H-K)
- Lead: 변경 이력 + .ai.md v3 + 잔여 정정 + backlog 이슈 7개 동기화 + 검증 + 커밋 분리

**정정 결과 (20건+)**:
1~5 기본 7건 (#1~#7): 필터값, 테이블명, SPH Dual-Tier 롤백, A3-3 조인 단위, YEAR_MONTH 변환, 행정동→법정동, 이력 보존
6~10 Dual-Tier 5건 (#8~#12): A4-1 CASE 분기, A5-1 Track A/B 분리, A5-3 walk_forward_split + train_track_a/b, B3-0 신규 매트릭스 + B3-1 city_code rename + B3-2/3 tier/confidence, C4 ROI Tier 분기 + fallback
11~20 잔여 8건: A6 표 행, C3 세그먼트, C7 발표 스크립트, A8 디렉토리 매핑, 출처 섹션 등

**dev_spec.md 변경**: 2,850 → 2,997 lines (+147), 299 insertions / 154 deletions
**docs/specs/.ai.md**: v3 엔트리 추가

**Backlog 이슈 동기화 (7건)**:
- #22: TC 주석 + 불변식 Tier 명시
- #23: `'서울특별시'` → `'서울'` 3곳
- #25: `district_code` → `city_code` rename, TC `'11680'` → `'11140'`, AC Dual-Tier
- #26: `V05_*` / `NX_*` → 실존 뷰명 통일 + 불변식 강화
- #28: `YEAR_MONTH` DATE 캐스팅
- #29: TC `'11680'` → `'11140'`, TELECOM_ONLY fallback TC 추가
- #42: `465동` → `467개 법정동(BJD)`

**검증 통과** (본문 잔존 0건, 변경 이력/JSON 예시/Cortex YAML/의도적 금지 명시만 허용):
- `'서울특별시'`, `INTEGRATED_MART`, `25개 구 467개 동`, `25개 구 모두 가능`, `train_and_deploy`, `XGBRegressor` (정정 대상)

**커밋 2개 on `refactor/000040-devspec-fix`**:
- `ef80455` chore(work): #40 작업 내역 + 구현 플랜 기록 (#40)
- `c3ebf5d` refactor(devspec): Snowflake 실데이터 검증 기반 dev_spec 12건+α 정정 + Dual-Tier 반영 (#40)

**PR**: [siwoo01231324-crypto/snowflake#44](https://github.com/siwoo01231324-crypto/snowflake/pull/44)

**Team 정리**: 3 워커 shutdown_response → TeamDelete 성공 → state_clear 완료
