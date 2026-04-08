# feat: 3구 권역 프로파일 카드 데이터셋 생성

## 목적
MULTI_SOURCE 3개 권역(중구 11140 / 영등포구 11560 / 서초구 11650)의 '권역 카드' 데이터셋을 생성. 각 구를 어떤 성격의 권역인지 한눈에 파악할 수 있도록 인구·소비·시세·시그널 지표를 집계해 Streamlit 권역 탭과 발표 데모에서 재사용한다.

## 배경
#21에서 `DATA_TIER = 'MULTI_SOURCE'` 3구가 풀 피처를 보유. 발표·대시보드에서 "왜 이 3구인가?"를 설명하려면 각 권역의 성격을 수치로 요약한 카드가 필요하다. 서초(고급주거·학군), 영등포(금융·혼합), 중구(도심오피스·상업)는 서로 다른 이사 패턴을 보일 것으로 예상되며, 이 대비 자체가 해커톤 스토리의 핵심 소재.

## 완료 기준
- [x] `V_DISTRICT_PROFILE_3GU` 뷰 생성 (또는 `MART_DISTRICT_PROFILE` 테이블)
- [x] 3구 각각 카드 필드 전체 채움 (NULL 금지)
- [x] `docs/presentation/01_district_profiles.md` 작성 (발표 스크립트용 서술)
- [x] TC-01~TC-04 PASS (실제 TC-06까지 6/6 PASS)

## 카드 필드
| 필드 | 출처 | 집계 |
|---|---|---|
| CITY_CODE | 고정 | PK |
| CITY_KOR_NAME | 고정 | |
| PROFILE_TAG | 수동 | 도심오피스·상업 / 금융·혼합 / 고급주거·학군 |
| AVG_RESIDENTIAL_POP | V_SPH_FLOATING_POP | 12개월 평균 |
| WORKING_VISIT_RATIO | V_SPH_FLOATING_POP | (WORKING+VISITING)/RESIDENTIAL |
| AVG_INCOME | V_SPH_ASSET_INCOME | 평균 |
| AVG_ASSET | V_SPH_ASSET_INCOME | 평균 |
| ELECTRONICS_FURNITURE_SHARE | V_SPH_CARD_SALES | ELECTRONICS_FURNITURE_SALES / TOTAL_SALES |
| AVG_MEME_PRICE | V_RICHGO_MARKET_PRICE | 월별→평균 |
| AVG_JEONSE_PRICE | V_RICHGO_MARKET_PRICE | |
| GAP_RATIO | 파생 | (MEME-JEONSE)/MEME |
| OPEN_COUNT_MONTHLY_AVG | V_TELECOM_DISTRICT_MAPPED | 월평균 |
| BJD_COUNT | V_RICHGO_MARKET_PRICE | 고유 BJD 수 |

## 테스트 (TDD)
```sql
-- test_15_district_profile.sql
-- TC-01: 3구 존재
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU;
-- EXPECTED: 3

-- TC-02: 필수 필드 NOT NULL
SELECT COUNT(*) AS null_cnt FROM MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU
WHERE CITY_CODE IS NULL OR AVG_INCOME IS NULL OR AVG_MEME_PRICE IS NULL OR OPEN_COUNT_MONTHLY_AVG IS NULL;
-- EXPECTED: 0

-- TC-03: 3구 CITY_CODE 정확히 일치
SELECT CITY_CODE FROM MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU ORDER BY 1;
-- EXPECTED: 11140, 11560, 11650

-- TC-04: PROFILE_TAG 중복 없음
SELECT COUNT(DISTINCT PROFILE_TAG) AS tag_cnt FROM MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU;
-- EXPECTED: 3
```

## 구현 플랜
1. 테스트 먼저 작성 (sql/test/test_15_district_profile.sql)
2. sql/views/006_district_profile_3gu.sql 작성 — UNION ALL 3행 또는 GROUP BY 집계
3. Snowflake에서 뷰 생성 후 TC-01~TC-04 검증
4. docs/presentation/01_district_profiles.md — 각 구별 서술형 프로필 (발표 스크립트 톤)

## 참조
- `pipelines/preprocessing.py:10` MULTI_SOURCE_CITIES
- `sql/views/003_sph_views.sql`, `sql/views/002_richgo_views.sql`, `sql/views/005_telecom_district_mapped.sql`
- 의존성: #21 ✅ (마트), #22 권장 (OPEN_COUNT_MONTHLY_AVG 계산에 마트 사용 시)
- 활용처: #28 히트맵 3구 상세 카드, #29 세그먼트 탭

## 불변식
- PROFILE_TAG는 수동 분류 (문헌 근거 또는 관찰 근거 명시)
- 3구 이외 확장 금지 (TELECOM_ONLY는 이 카드의 scope 아님)

## 개발 체크리스트
- [x] sql/views/.ai.md · sql/test/.ai.md · docs/presentation/.ai.md (신규) · docs/.ai.md 최신화

---

## 작업 내역

<!-- 세션마다 /ri 또는 /fi 호출 시 여기에 현황 스냅샷이 추가된다 -->

### 2026-04-08 — 워크트리 생성 (/si 43)
- 브랜치: `feat/000043-multi-source-district-profile`
- 베이스: master @ `a8b104b` (hotfix: EXECUTION_PLAN.md Dual-Tier 실행 계획)
- 병렬 컨텍스트: #40 (`.worktree/000040-devspec-fix`)이 동시 진행 중 — critical path의 dev_spec 정정 이슈
- 의존성 상태: #21 ✅ (PR #41 머지) → `MART_MOVE_ANALYSIS` 이원화 완료, 3구 풀 피처 확보됨
- 상태: 구현 대기

### 2026-04-08 — 세션 재개 현황 (/ri)
- AC 진행: 0/4 (미착수)
  - [ ] `V_DISTRICT_PROFILE_3GU` 뷰 — `sql/views/006_*` 미존재
  - [ ] 3구 카드 필드 채움 — 상기 뷰 미생성
  - [ ] `docs/presentation/01_district_profiles.md` — 미작성
  - [ ] TC-01~TC-04 — `sql/test/test_15_*` 미존재
- 브랜치 커밋: 베이스 `a8b104b`에서 전진 없음 (0 commit)
- 미커밋: `docs/work/active/000043-*/` 워크폴더만 untracked
- 플랜: `01_plan.md` 작성 완료 (TDD Red→Green→Refactor 6단계)
- 다음 액션: **1. 사전 조사** (소스 뷰 실컬럼명 확인) → **2. 테스트 Red 작성** (test_15)
- 현재 단계: **구현 대기**

### 2026-04-08 — AC 경로 변경: district_profiles.md → `docs/presentation/01_*`
- 사용자 결정: 발표 스크립트 산출물을 `docs/specs/` 대신 신규 디렉토리 `docs/presentation/`에 수용
- AC 문구 수정: `docs/specs/district_profiles.md` → `docs/presentation/01_district_profiles.md`
- 개발 체크리스트: `docs/specs/.ai.md` 항목 삭제, `docs/presentation/.ai.md` (신규) + `docs/.ai.md` (presentation 행 추가) 2건으로 교체
- 01_plan.md 동기화 완료 (AC 체크리스트·산출물 표·실행 순서 4·5단계·커밋 포함 파일·완료 조건 전부 반영)
- **미완료**: 실제 `docs/presentation/` 디렉토리·파일 생성은 TDD 4단계(뷰 Green 이후)에서 진행. 지금 작성해도 카드 숫자를 인용할 수 없어 뼈대만 남음.

### 2026-04-08 — 구현·검증·문서화 전부 완료 (MCP snowflake 우회)
- **MCP 다운 우회**: `mcp__snowflake__*` 응답 불가 → main Claude가 `python_repl` + `snowflake-connector-python`으로 직접 연결
  - 의존성 6개 뷰 존재 확인: V_SPH_FLOATING_POP(2.5M) · V_SPH_ASSET_INCOME(269K) · V_SPH_CARD_SALES(6.2M) · V_RICHGO_MARKET_PRICE(4356) · V_BJD_DISTRICT_MAP(29) · V_TELECOM_DISTRICT_MAPPED(866)
  - DDL 적용: `View V_DISTRICT_PROFILE_3GU successfully created.` (CREATE OR REPLACE, idempotent)
- **TC-01 ~ TC-06 전부 PASS** (6/6)
  - TC-01 row=3 / TC-02 null=0 / TC-03 city='11140,11560,11650' / TC-04 distinct_tag=3 / TC-05 매매>전세 위반=0 / TC-06 GAP_RATIO∈[0,1] 위반=0
- **카드 숫자 캡처**: `02_snowflake_capture.md` 신규 — DDL 적용 결과 + 의존성 + 6 TC + `SELECT *` 결과 + 단위 메모 + 재실행 절차
- **발표 스크립트 작성**: `docs/presentation/01_district_profiles.md` 신규 (오프닝/3구 카드+관찰+이사 가설/요약 카드/Q&A 5개/출처 11개)
- **신규 디렉토리**: `docs/presentation/` + `docs/presentation/.ai.md` 생성
- **.ai.md 갱신**: `docs/.ai.md` (presentation 행 추가) · `sql/views/.ai.md` (006 행 추가) · `sql/test/.ai.md` (test_15 행 추가)
- **AC 진행: 5/5 (모두 완료)**, 미커밋 상태 — 사용자 컨펌 후 `feat: 3구 권역 프로파일 카드 데이터셋 (#43)` 커밋 진행 예정
- **인사이트 3줄 요약** (발표 hook):
  - 서초구: 거주 1,221.66 / 평균자산 683,148 / 매매가 6,413 — 모든 카테고리 1위 ("사는 곳")
  - 영등포구: 가전·가구 매출 5.17% (3구 평균 0.25%의 ~20배) + 통신 신규개통 259.56/월 (3구 최다) ("이사 직후 소비하는 곳")
  - 중구: 거주 69.60 (최저) · WORKING_VISIT_RATIO 5.226 (압도적) ("일하는 곳")

### 2026-04-08 — 사전 조사 완료 + 01_plan 컬럼명 확정
- EXECUTION_PLAN.md 읽기 반영 → 01_plan.md에 "집계 기간 22개월" 섹션, 리스크 R7 연계, PROFILE_TAG 근거 위치 보강
- 소스 뷰 4개 실컬럼명 확정 (sql/views/*.sql + pipelines/preprocessing.py 대조):
  - **이슈 body 오기 3건 수정**: `AVG_INCOME`→`AVERAGE_INCOME`, `AVG_ASSET_AMOUNT`→`AVERAGE_ASSET_AMOUNT`, `RESIDENTIAL_POP`→`RESIDENTIAL_POPULATION` (WORKING/VISITING 동일)
  - **기간 컬럼**: SPH 3종 + TELECOM은 `STANDARD_YEAR_MONTH` (VARCHAR YYYYMM), RICHGO만 `YYYYMMDD` (DATE) — WHERE 타입 분기 필요
  - **RICHGO CITY_CODE 없음** → `V_BJD_DISTRICT_MAP` JOIN 패턴 확정 (preprocessing.py:88-90 재사용)
  - **TELECOM**: (CITY_CODE, MONTH)에 다중 행 가능 → 월 SUM 후 구 AVG 2단 집계
- 01_plan.md 구현 스케치 SQL을 실컬럼명 기반 풀 코드로 재작성 (pop/income/card/richgo/telecom 5개 CTE)
- 다음 액션: **2. 테스트 Red 작성** — `sql/test/test_15_district_profile.sql` (TC-01~TC-06)
- 현재 단계: **구현 대기** (사전 조사 단계만 완료, 여전히 #43 scope 1/6 진행)
