# 01 — 구현 플랜 (#43 3구 권역 프로파일 카드 데이터셋)

## AC 체크리스트

- [x] `V_DISTRICT_PROFILE_3GU` 뷰 생성 (또는 `MART_DISTRICT_PROFILE` 테이블)
- [x] 3구 각각 카드 필드 전체 채움 (NULL 금지)
- [x] `docs/presentation/01_district_profiles.md` 작성 (발표 스크립트용 서술)
- [x] TC-01~TC-04 PASS (TC-06까지 확장 — 6/6 PASS)
- [x] `sql/views/.ai.md` · `sql/test/.ai.md` · `docs/presentation/.ai.md` · `docs/.ai.md` 최신화

## 산출물 위치

| 파일 | 성격 | 비고 |
|---|---|---|
| `sql/test/test_15_district_profile.sql` | 테스트 (Red 먼저) | TC-01~TC-04 |
| `sql/views/006_district_profile_3gu.sql` | 뷰 DDL | `V_DISTRICT_PROFILE_3GU` |
| `docs/presentation/01_district_profiles.md` | 발표 스크립트용 서술 | PROFILE_TAG 근거 포함 |
| `sql/views/.ai.md` / `sql/test/.ai.md` / `docs/presentation/.ai.md` (신규) / `docs/.ai.md` | 디렉토리 안내 갱신 | 완료 조건 |

## 3구 PROFILE_TAG 초안 (수동 분류)

EXECUTION_PLAN.md line 60~64 근거 (Dual-Tier ADR 및 관찰):

| CITY_CODE | CITY_KOR_NAME | PROFILE_TAG | 근거 키워드 |
|---|---|---|---|
| 11140 | 중구 | 도심 오피스·상업 | 주거 인구 ↓, 업무·상업 활동 ↑, 단신/직장 중심 유입 |
| 11560 | 영등포구 | 금융·상업·주거 혼합 | 금융지구(여의도) + 주거 혼재, 직주근접 |
| 11650 | 서초구 | 고급 주거·학군지 | 고소득·고자산 집중, 학군 기반 가족 단위 이동 |

PROFILE_TAG는 **수동 VALUES 매핑**으로 반영(데이터로 자동 도출 금지 — 3구라 샘플이 적어 통계적 근거 부족). `district_profiles.md`에 각 태그의 관찰·문헌 근거를 명시.

## 데이터 소스 매핑 (필드별 확정) — ✅ 컬럼명 확정 (2026-04-08)

**사전 조사 완료**: `sql/views/003_sph_views.sql`·`002_richgo_views.sql`·`005_telecom_district_mapped.sql`·`pipelines/preprocessing.py` 대조 결과.

| 필드 | 소스 뷰 | 집계식 요지 | 주의 |
|---|---|---|---|
| `CITY_CODE` | `V_SPH_REGION_MASTER` 또는 하드코딩 | PK | `('11140','11560','11650')` |
| `CITY_KOR_NAME` | `V_SPH_REGION_MASTER` | 한글명 | LEFT JOIN `CITY_CODE` |
| `PROFILE_TAG` | **수동 VALUES** | 문자열 | 뷰 내부 CTE `tag_map` |
| `AVG_RESIDENTIAL_POP` | `V_SPH_FLOATING_POP` | `AVG(RESIDENTIAL_POPULATION)` | ✅ `_POPULATION` 풀네임 |
| `WORKING_VISIT_RATIO` | `V_SPH_FLOATING_POP` | `AVG((WORKING_POPULATION + VISITING_POPULATION) / NULLIF(RESIDENTIAL_POPULATION, 0))` | 0 나눗셈 방지 |
| `AVG_INCOME` | `V_SPH_ASSET_INCOME` | `AVG(AVERAGE_INCOME)` | ✅ `AVERAGE_*` (이슈 body의 `AVG_INCOME` 오기) |
| `AVG_ASSET` | `V_SPH_ASSET_INCOME` | `AVG(AVERAGE_ASSET_AMOUNT)` | ✅ `AVERAGE_ASSET_AMOUNT` |
| `ELECTRONICS_FURNITURE_SHARE` | `V_SPH_CARD_SALES` | `SUM(ELECTRONICS_FURNITURE_SALES) / NULLIF(SUM(TOTAL_SALES), 0)` | ✅ 이름 일치. `CARD_TYPE`/`GENDER`/`AGE_GROUP` dimension 무시하고 SUM |
| `AVG_MEME_PRICE` | `V_RICHGO_MARKET_PRICE` | `AVG(MEME_PRICE_PER_SUPPLY_PYEONG)` | ✅ `V_BJD_DISTRICT_MAP` JOIN 필수 (CITY_CODE 없음) |
| `AVG_JEONSE_PRICE` | `V_RICHGO_MARKET_PRICE` | `AVG(JEONSE_PRICE_PER_SUPPLY_PYEONG)` | 동일 |
| `GAP_RATIO` | 파생 | `(AVG_MEME_PRICE - AVG_JEONSE_PRICE) / NULLIF(AVG_MEME_PRICE, 0)` | 0 나눗셈 방지 |
| `OPEN_COUNT_MONTHLY_AVG` | `V_TELECOM_DISTRICT_MAPPED` | `AVG(월별 OPEN_COUNT)` | 구 단위 월별 `SUM` 후 `AVG` (동일 구에 다중 행 있음) |
| `BJD_COUNT` | `V_RICHGO_MARKET_PRICE` | `COUNT(DISTINCT BJD_CODE)` | `V_BJD_DISTRICT_MAP` JOIN 후 CITY_CODE 단위 |

### 기간 컬럼 정리 (22개월 WHERE 절 타입 주의)

| 소스 뷰 | 기간 컬럼 | 타입 | WHERE 절 |
|---|---|---|---|
| `V_SPH_FLOATING_POP` | `STANDARD_YEAR_MONTH` | **VARCHAR `YYYYMM`** | `BETWEEN '202303' AND '202412'` |
| `V_SPH_CARD_SALES` | `STANDARD_YEAR_MONTH` | **VARCHAR `YYYYMM`** | `BETWEEN '202303' AND '202412'` |
| `V_SPH_ASSET_INCOME` | `STANDARD_YEAR_MONTH` | **VARCHAR `YYYYMM`** | `BETWEEN '202303' AND '202412'` |
| `V_TELECOM_DISTRICT_MAPPED` | `STANDARD_YEAR_MONTH` | **VARCHAR `YYYYMM`** | `BETWEEN '202303' AND '202412'` |
| `V_RICHGO_MARKET_PRICE` | **`YYYYMMDD`** | **DATE** | `BETWEEN DATE '2023-03-01' AND DATE '2024-12-31'` |

> **핵심 주의점 3가지**
> 1. RICHGO만 `YYYYMMDD`(DATE)·나머지는 `STANDARD_YEAR_MONTH`(VARCHAR YYYYMM). WHERE 절 타입 혼동 금지.
> 2. RICHGO는 `CITY_CODE` 없음 → `V_BJD_DISTRICT_MAP` JOIN 필수 (`preprocessing.py:88-90` 동일 패턴).
> 3. `V_SPH_CARD_SALES`·`V_SPH_ASSET_INCOME`은 CARD_TYPE/GENDER/AGE_GROUP 등 dimension으로 한 (CITY_CODE, MONTH)에 다중 행 존재 → 집계 시 `SUM`/`AVG` 필수.

## 집계 기간 — 22개월 교집합 (필수 WHERE 조건)

`EXECUTION_PLAN.md §1.1`에서 확정된 **4종 시간 교집합**은 `2023-03 ~ 2024-12` (22개월). 모든 CTE 집계에 공통 WHERE 절을 적용해야 한다. **단, 기간 컬럼 타입이 뷰별로 다르므로 타입에 맞춰 분기**:

```sql
-- SPH 3종 + TELECOM: VARCHAR YYYYMM
WHERE STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'

-- RICHGO: DATE
WHERE YYYYMMDD BETWEEN DATE '2023-03-01' AND DATE '2024-12-31'
```

**이유 1 — 구별 비교 공정성**: `pop_agg` / `income_agg` / `card_agg` / `richgo_agg` / `telecom_agg` 5개 CTE가 서로 다른 기간을 집계하면 3구 비교 자체가 무의미해진다. 동일 22개월로 통일해야 카드 필드 간 구별 대비가 성립.

**이유 2 — RICHGO NULL 회피 (R7)**: `EXECUTION_PLAN.md §7 R7`에 따라 `V_RICHGO_MARKET_PRICE`는 2024-12 이후 데이터 없음. WHERE 제한 없이 `AVG(MEME_PRICE_*)`를 돌리면 2025~2026 구간은 그대로 집계에 들어가지 않아 문제 없지만, `telecom_agg`는 2026-05까지 존재 → `OPEN_COUNT_MONTHLY_AVG`가 다른 구보다 긴 기간으로 평균되면 스케일이 왜곡된다. **5종 모두 동일 22개월 강제**가 핵심.

**이유 3 — TC-02 (NOT NULL) 방어**: 기간 제한이 없으면 특정 CTE가 빈 결과를 반환해 LEFT JOIN 후 NULL 발생 → TC-02 실패. 공통 WHERE가 NOT NULL 보장의 선제 조건.

**구현 체크리스트**:
- [x] 각 소스 뷰의 기간 컬럼명·타입 확인 완료 (위 "기간 컬럼 정리" 표 참조)
- [ ] `richgo_agg` 에서 `V_BJD_DISTRICT_MAP` JOIN 후 `CITY_CODE` 단위 집계 (RICHGO는 CITY_CODE 없음)
- [ ] `tag_map` CTE는 하드코딩 VALUES라 기간 조건 불필요

## 구조 선택지 비교

**옵션 A — `V_DISTRICT_PROFILE_3GU` 뷰 (권장)**
- 장점: 원본 뷰 변동 즉시 반영, 저장 비용 없음
- 단점: 호출 시마다 재집계 (Streamlit 히트맵 로드 시 latency)
- 적합: 3구 × 단일 행 → 집계 비용 미미 → **뷰로 충분**

**옵션 B — `MART_DISTRICT_PROFILE` 테이블**
- 장점: 고정값, Streamlit 응답 ↑
- 단점: 원본 변경 시 재빌드 필요, `build_district_profile()` 파이프라인 추가
- 적합: 수백~수천 행 또는 복잡 집계

**결정**: **옵션 A (뷰)** — 3행짜리 카드라 뷰로 충분. 파이프라인 추가는 YAGNI.

## 실행 순서 (TDD Red → Green → Refactor)

### 1. 사전 조사 — ✅ 완료 (2026-04-08)
- [x] `pipelines/preprocessing.py:10` `MULTI_SOURCE_CITIES = ['11140','11560','11650']` 확인
- [x] `sql/views/003_sph_views.sql` 대조 — `STANDARD_YEAR_MONTH` / `RESIDENTIAL_POPULATION` / `AVERAGE_INCOME` / `AVERAGE_ASSET_AMOUNT` / `ELECTRONICS_FURNITURE_SALES` / `TOTAL_SALES` 확정
- [x] `sql/views/002_richgo_views.sql` 대조 — `YYYYMMDD` (DATE) / `BJD_CODE` / `MEME_PRICE_PER_SUPPLY_PYEONG` / `JEONSE_PRICE_PER_SUPPLY_PYEONG` 확정, **CITY_CODE 없음 → V_BJD_DISTRICT_MAP JOIN 필수**
- [x] `sql/views/005_telecom_district_mapped.sql` 대조 — `STANDARD_YEAR_MONTH` / `CITY_CODE` / `OPEN_COUNT` 확정
- [x] `pipelines/preprocessing.py:81-92` RICHGO BJD→CITY JOIN 패턴 확인 (#43도 동일 패턴 재사용)
- [ ] Snowflake MCP `describe_table` 실시간 재확인 — **생략 가능** (sql/views/*.sql이 진리원본, #18·#19에서 검증 완료)
- [ ] `sql/views/.ai.md` 읽기 → 다음 단계 Green 때 확인

### 2. 테스트 먼저 (Red) (20분)
- `sql/test/test_15_district_profile.sql` 작성
- 이슈 body의 TC-01~TC-04 그대로 + TC-05 추가 제안:
  - **TC-05**: `AVG_MEME_PRICE > AVG_JEONSE_PRICE` (모든 3구 상식 검증)
  - **TC-06**: `GAP_RATIO BETWEEN 0 AND 1` (합리성 확인)
- Snowflake 실행 → 4~6건 모두 FAIL(뷰 없음) 확인 → Red 달성

### 3. 뷰 구현 (Green) (1~2h)
- `sql/views/006_district_profile_3gu.sql` 작성
- 구조 스케치:
  ```sql
  CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU AS
  WITH tag_map AS (
    SELECT '11140' AS CITY_CODE, '중구'   AS CITY_KOR_NAME, '도심 오피스·상업' AS PROFILE_TAG UNION ALL
    SELECT '11560',              '영등포구',               '금융·상업·주거 혼합' UNION ALL
    SELECT '11650',              '서초구',                 '고급 주거·학군지'
  ),
  -- 공통 3구 필터: CITY_CODE IN ('11140','11560','11650')
  -- 공통 기간: STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412' (VARCHAR)
  --          또는 YYYYMMDD BETWEEN DATE '2023-03-01' AND DATE '2024-12-31' (RICHGO만 DATE)
  pop_agg AS (
    SELECT CITY_CODE,
           AVG(RESIDENTIAL_POPULATION) AS AVG_RESIDENTIAL_POP,
           AVG((WORKING_POPULATION + VISITING_POPULATION) / NULLIF(RESIDENTIAL_POPULATION, 0)) AS WORKING_VISIT_RATIO
    FROM V_SPH_FLOATING_POP
    WHERE CITY_CODE IN ('11140','11560','11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
  ),
  income_agg AS (
    SELECT CITY_CODE,
           AVG(AVERAGE_INCOME)       AS AVG_INCOME,
           AVG(AVERAGE_ASSET_AMOUNT) AS AVG_ASSET
    FROM V_SPH_ASSET_INCOME
    WHERE CITY_CODE IN ('11140','11560','11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
  ),
  card_agg AS (
    SELECT CITY_CODE,
           SUM(ELECTRONICS_FURNITURE_SALES) / NULLIF(SUM(TOTAL_SALES), 0) AS ELECTRONICS_FURNITURE_SHARE
    FROM V_SPH_CARD_SALES
    WHERE CITY_CODE IN ('11140','11560','11650')
      AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
    GROUP BY CITY_CODE
  ),
  richgo_agg AS (
    SELECT b.CITY_CODE,
           AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG)   AS AVG_MEME_PRICE,
           AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG) AS AVG_JEONSE_PRICE,
           COUNT(DISTINCT r.BJD_CODE)            AS BJD_COUNT
    FROM V_RICHGO_MARKET_PRICE r
    JOIN V_BJD_DISTRICT_MAP    b ON r.BJD_CODE = b.BJD_CODE
    WHERE b.CITY_CODE IN ('11140','11560','11650')
      AND r.YYYYMMDD BETWEEN DATE '2023-03-01' AND DATE '2024-12-31'
    GROUP BY b.CITY_CODE
  ),
  telecom_agg AS (
    -- 동일 (CITY_CODE, STANDARD_YEAR_MONTH)에 다중 행(INSTALL_CITY 다름) 가능 → 월 SUM 후 구 AVG
    SELECT CITY_CODE,
           AVG(monthly_open) AS OPEN_COUNT_MONTHLY_AVG
    FROM (
      SELECT CITY_CODE, STANDARD_YEAR_MONTH, SUM(OPEN_COUNT) AS monthly_open
      FROM V_TELECOM_DISTRICT_MAPPED
      WHERE CITY_CODE IN ('11140','11560','11650')
        AND STANDARD_YEAR_MONTH BETWEEN '202303' AND '202412'
      GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    )
    GROUP BY CITY_CODE
  )
  SELECT t.CITY_CODE, t.CITY_KOR_NAME, t.PROFILE_TAG,
         p.AVG_RESIDENTIAL_POP, p.WORKING_VISIT_RATIO,
         i.AVG_INCOME, i.AVG_ASSET,
         c.ELECTRONICS_FURNITURE_SHARE,
         r.AVG_MEME_PRICE, r.AVG_JEONSE_PRICE,
         (r.AVG_MEME_PRICE - r.AVG_JEONSE_PRICE) / NULLIF(r.AVG_MEME_PRICE, 0) AS GAP_RATIO,
         tl.OPEN_COUNT_MONTHLY_AVG,
         r.BJD_COUNT
    FROM tag_map t
    LEFT JOIN pop_agg     p  USING (CITY_CODE)
    LEFT JOIN income_agg  i  USING (CITY_CODE)
    LEFT JOIN card_agg    c  USING (CITY_CODE)
    LEFT JOIN richgo_agg  r  USING (CITY_CODE)
    LEFT JOIN telecom_agg tl USING (CITY_CODE);
  ```
- Snowflake에서 뷰 생성 → `SELECT *` → 3행 조회 확인
- TC-01~TC-06 전부 PASS 될 때까지 수정

### 4. 발표 스크립트 작성 (1h)
- `docs/presentation/01_district_profiles.md` 작성, 구조:
  - 개요 (왜 이 3구인가 — Dual-Tier Marketplace 샘플 제약)
  - **중구** — 도심 오피스·상업: 카드 필드 값 인용 + 관찰 서술 (주거 인구 vs 유동 인구 대비)
  - **영등포구** — 금융·상업·주거 혼합: 여의도 금융지구 + 주거 혼재 근거
  - **서초구** — 고급 주거·학군지: 소득·자산·시세 상위 근거, 학군지 문헌
  - 각 구별 "이사 수요 예상 패턴" 한 문장 (발표 hook)
  - 출처 섹션: EXECUTION_PLAN.md · #21 검증 결과 · 뷰 숫자
- **팩트만 기재** (CLAUDE.md 조사·리서치 규칙)

### 5. `.ai.md` 최신화 (15분)
- `sql/views/.ai.md` → 006 뷰 항목 추가 (목적·의존 뷰·PK)
- `sql/test/.ai.md` → test_15 항목 추가
- `docs/presentation/.ai.md` **신규 생성** → 디렉토리 목적·구조·역할 정의 (발표 스크립트·Q&A 근거 자료 저장소), `01_district_profiles.md` 항목 기술
- `docs/.ai.md` → 구조 표에 `presentation/` 행 추가 (역할: "발표 스크립트·데모 근거")

### 6. 커밋 (사용자 확인 후)
- 커밋 메시지: `feat: 3구 권역 프로파일 카드 데이터셋 (#43)`
- 포함: `sql/views/006_*.sql`, `sql/test/test_15_*.sql`, `docs/presentation/01_district_profiles.md`, `docs/presentation/.ai.md` (신규), `docs/.ai.md`, `sql/views/.ai.md`, `sql/test/.ai.md`
- **커밋 전 사용자에게 컨펌 질문** (`CLAUDE.md` 행동 규칙)

## 병렬 컨텍스트 (#40과의 관계)

- **#40** (`.worktree/000040-devspec-fix`) — `docs/specs/dev_spec.md` 대규모 정정 진행 중 (critical path)
- **#43은 독립 진행 가능**:
  - 수정 파일 겹치지 않음 (#43은 전부 신규 파일, #40은 dev_spec.md 수정)
  - 의존성: #43은 #21만 필요 → ✅ 완료
  - 예외: `docs/specs/.ai.md` 1개만 양쪽이 추가 수정 → 머지 시 충돌 가능성 낮음
- 활용처: #28 히트맵 3구 상세 카드·#29 세그먼트 탭이 이 뷰를 재사용 → #43 일찍 끝낼수록 후속 unblock

## 리스크 / 주의점

- **컬럼명 가정 오류**: 이슈 body의 컬럼명은 기획 단계 추정. Snowflake 실제 컬럼명과 다를 수 있으므로 `describe_table` 또는 `sql/views/*.sql`에서 확정 후 진행
- **기간 불일치로 인한 구별 비교 왜곡 (R7 연계)**: `EXECUTION_PLAN.md §1.1` 4종 교집합 `2023-03 ~ 2024-12`(22개월) 외 범위를 섞으면 카드 지표 스케일이 구별로 달라져 비교 무의미. 5개 집계 CTE 전체 공통 WHERE 필수 (위 "집계 기간" 섹션 참조)
- **NULL 발생 시나리오**: `V_RICHGO_MARKET_PRICE`는 2024-12 이후 데이터 없음 → WHERE 기간 제한 안 하면 최근 구간에 NULL 섞임. 공통 WHERE로 선제 차단
- **PROFILE_TAG 수동 분류의 주관성**: 근거를 `district_profiles.md`에 반드시 명시 (발표 Q&A 대비). 1차 근거는 `EXECUTION_PLAN.md §2.2` line 60~64
- **뷰 재빌드**: `CREATE OR REPLACE` 사용 시 기존 consumer 없음 확인 (현재 #28·#29가 아직 착수 전이라 안전)
- **커밋 전 항상 확인**: `git commit` / `git push` 전 반드시 사용자 컨펌 (CLAUDE.md)

## 완료 조건 (Definition of Done)

- [x] `sql/test/test_15_district_profile.sql` TC-01~TC-06 전부 PASS
- [x] `V_DISTRICT_PROFILE_3GU` 3행 NULL 없음 (PROFILE_TAG 제외 모든 수치 필드 NOT NULL)
- [x] `docs/presentation/01_district_profiles.md` 3구 서술 + 출처 섹션 작성
- [x] `sql/views/.ai.md` · `sql/test/.ai.md` · `docs/presentation/.ai.md` · `docs/.ai.md` 업데이트
- [ ] 커밋 메시지: `feat: 3구 권역 프로파일 카드 데이터셋 (#43)` — **사용자 컨펌 대기**

## 참조

- `pipelines/preprocessing.py:10` — `MULTI_SOURCE_CITIES = ["11140", "11560", "11650"]`
- `sql/views/003_sph_views.sql` — SPH 3종 뷰
- `sql/views/002_richgo_views.sql` — `V_RICHGO_MARKET_PRICE`
- `sql/views/005_telecom_district_mapped.sql` — `V_TELECOM_DISTRICT_MAPPED`
- `docs/work/EXECUTION_PLAN.md` — Day 1 병렬 계획 line 157, 병렬 매트릭스 line 181
- `docs/work/done/000021-integrated-mart/01_plan.md` — Dual-Tier ADR 원본
- 연관 이슈: **#21 ✅** (마트), **#22 권장** (OPEN_COUNT 계산에 마트 사용 시), **#28·#29** (활용처), **#25** (권장 선행)
