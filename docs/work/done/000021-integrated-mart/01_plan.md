# [#21] 통합 마트 테이블 생성 — 구현 계획

> 작성: 2026-04-08 | ralplan 합의 (Planner→Architect→Critic)
> 스키마: MOVING_INTEL.ANALYTICS | 테이블: **MART_MOVE_ANALYSIS**

---

## AC 체크리스트

- [x] `MART_MOVE_ANALYSIS` 통합 마트 테이블 생성 ✅ 850 rows
- [x] Snowpark `build_integrated_mart()` 함수 구현 ✅ pipelines/preprocessing.py
- [x] 25개 구 × 월별 데이터 존재 ✅ 25구 × 34개월
- [x] 키 컬럼(CITY_CODE, STANDARD_YEAR_MONTH) NULL 0건 ✅ TC-03 PASS

---

## RALPLAN-DR

### Principles (5개)

1. **#22 호환성 최우선**: MART_MOVE_ANALYSIS는 #22(MOVE_SIGNAL_INDEX)가 참조하는 12개 필수 컬럼을 반드시 포함
2. **구(CITY_CODE) × 월 집계**: 25개 구 × 월 spine 기반. 아정당이 구 단위이므로 최소 공통 해상도
3. **데이터 현실 직시**: SPH/RICHGO = 3개 구(해커톤 샘플), 아정당 = 25개 구. DATA_TIER로 명시적 구분
4. **TDD**: 테스트 먼저 작성 → Red → Green → Refactor
5. **뷰 확장 > 원본 직참**: 기존 뷰 체계 유지, 누락 컬럼은 뷰 확장으로 해결

### Decision Drivers (3개)

1. **3개 구 vs 25개 구**: SPH/RICHGO는 3개 구(중구, 영등포구, 서초구)만 → 22개 구는 아정당(S1)만 유효
2. **INSTALL_STATE 필터 오류**: dev_spec은 `'서울특별시'`이나 실제 값은 `'서울'`
3. **YEAR_MONTH 타입 불일치**: 아정당 DATE vs SPH VARCHAR(6) → TO_CHAR 변환 필수

### Viable Options

#### Option A: 25개 구 spine + DATA_TIER (선택)

**설명**: M_SCCO_MST(25개 구) × 아정당 월 범위 CROSS JOIN으로 spine 생성. 모든 FACT를 LEFT JOIN. DATA_TIER 컬럼으로 'MULTI_SOURCE'(3구) vs 'TELECOM_ONLY'(22구) 구분.

**Pros**:
- AC TC-02 "25개 구" 충족
- 해커톤 데모에서 25개 구 히트맵 표시 가능
- #22에서 DATA_TIER 기반 차등 시그널 융합 가능
- 아정당 25개 구 데이터를 버리지 않음

**Cons**:
- 22/25 구는 SPH/RICHGO 컬럼 NULL → #22 MOVE_SIGNAL_INDEX 품질 차등
- CROSS JOIN으로 spine 생성 → 코드 복잡도 증가

#### Option B: 3개 구만 (다중소스 완전 데이터)

**설명**: SPH/RICHGO 데이터가 있는 3개 구만으로 마트 구성.

**Pros**: 모든 컬럼 non-NULL, 분석 품질 일관

**Cons**: AC TC-02 "25개 구" 실패, 해커톤 데모 범위 축소, 아정당 22개 구 데이터 유실

**기각 사유**: AC 불충족 + 해커톤 시연 범위 과소

### ADR

| 항목 | 내용 |
|------|------|
| **Decision** | Option A — 25개 구 spine + DATA_TIER + 뷰 확장 |
| **Drivers** | AC 충족, 해커톤 데모 범위, #22 호환성 |
| **Alternatives** | Option B (3구 한정) — AC 불충족으로 기각 |
| **Why chosen** | 25개 구 중 3개는 4종 시그널, 22개는 1종(아정당) → DATA_TIER로 명시적 품질 구분 |
| **Consequences** | #22에서 DATA_TIER 기반 차등 가중치 적용 필요 |
| **Follow-ups** | dev_spec "25개 구" 오기 수정, #22 이슈 body에 DATA_TIER 안내 추가 |

---

## Snowflake 실데이터 검증 결과

> Python snowflake-connector로 2026-04-08 직접 확인

| 항목 | 결과 |
|------|------|
| SPH FLOATING_POP CITY_CODE | 3개 (11140=중구, 11560=영등포구, 11650=서초구) |
| SPH CARD_SALES CITY_CODE | 3개 (동일) |
| SPH ASSET_INCOME CITY_CODE | 3개 (동일) |
| RICHGO BJD_CODE→CITY_CODE | 3개 (동일, 29개 BJD) |
| M_SCCO_MST | 25개 구, 467개 동 |
| 아정당 INSTALL_STATE | **'서울'** (NOT '서울특별시') |
| 아정당 INSTALL_CITY | **25개 구** (SPH CITY_KOR_NAME과 완벽 1:1 매핑) |
| 아정당 YEAR_MONTH | **DATE** 타입 (2023-03-01 ~ 2026-05-01) |
| SPH STANDARD_YEAR_MONTH | **VARCHAR(6)** (202101 ~ 202512) |
| RICHGO YYYYMMDD | DATE (2012-01-01 ~ 2024-12-01) |
| CARD_SALES_INFO.ELECTRONICS_FURNITURE_SALES | **존재** ✓ (NUMBER(38,0)) |
| ASSET_INCOME_INFO.NEW_HOUSING_BALANCE_COUNT | **존재** ✓ (NUMBER(38,0)) |
| V_TELECOM_DISTRICT_MAPPED | **미생성** (이번 이슈에서 생성) |
| 시간 교집합 (4종 전체) | 2023-03 ~ 2024-12 (22개월) |
| 시간 범위 (아정당 기준 spine) | 2023-03 ~ 2026-05 (39개월) |

---

## 구현 계획

### Step 1: 테스트 코드 작성 (TDD Red)

**파일**: `sql/test/test_06_integrated_mart.sql` (신규)

```sql
-- TC-01: 마트 테이블 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS;
-- EXPECTED: cnt > 0

-- TC-02: 25개 구 전체 커버
SELECT COUNT(DISTINCT CITY_CODE) AS gu_count FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS;
-- EXPECTED: gu_count = 25

-- TC-03: 키 컬럼 NULL 확인
SELECT COUNT(*) AS null_keys FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
WHERE CITY_CODE IS NULL OR STANDARD_YEAR_MONTH IS NULL;
-- EXPECTED: null_keys = 0

-- TC-04: 필수 컬럼 존재 (MULTI_SOURCE 행에서)
SELECT CITY_CODE, STANDARD_YEAR_MONTH, OPEN_COUNT,
       TOTAL_RESIDENTIAL_POP, TOTAL_CARD_SALES, AVG_INCOME
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
WHERE DATA_TIER = 'MULTI_SOURCE' LIMIT 1;
-- EXPECTED: 6개 컬럼 모두 존재, NOT NULL

-- TC-04b: TELECOM_ONLY 행에서 OPEN_COUNT NOT NULL
SELECT COUNT(*) AS null_open FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
WHERE DATA_TIER = 'TELECOM_ONLY' AND OPEN_COUNT IS NULL;
-- EXPECTED: null_open = 0 (아정당 데이터 범위 내)

-- TC-05: 월별 데이터 범위 (아정당 spine 기준)
SELECT MIN(STANDARD_YEAR_MONTH) AS min_ym, MAX(STANDARD_YEAR_MONTH) AS max_ym
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS;
-- EXPECTED: min_ym = '202303', max_ym = '202605'

-- TC-06: DATA_TIER 분포
SELECT DATA_TIER, COUNT(DISTINCT CITY_CODE) AS gu_count
FROM MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS
GROUP BY DATA_TIER;
-- EXPECTED: MULTI_SOURCE = 3, TELECOM_ONLY = 22
```

**파일**: `tests/test_06_snowpark.py` (신규)

```python
def test_build_integrated_mart(session):
    from pipelines.preprocessing import build_integrated_mart
    result = build_integrated_mart(session)
    assert result.count() > 0, "마트에 데이터 없음"
    assert result.select("CITY_CODE").distinct().count() == 25, "25개 구 미달"
    null_count = result.filter(F.col("CITY_CODE").is_null()).count()
    assert null_count == 0, f"CITY_CODE NULL {null_count}건"
    # DATA_TIER 분포
    multi = result.filter(F.col("DATA_TIER") == "MULTI_SOURCE").select("CITY_CODE").distinct().count()
    assert multi == 3, f"MULTI_SOURCE 구 수 {multi} != 3"
```

**검증**: Snowflake에서 TC-01 실행 → 테이블 미존재로 실패(Red) 확인

---

### Step 2: 뷰 보강

#### 2a. V_SPH_CARD_SALES 확장 — ELECTRONICS_FURNITURE_SALES 추가

**파일**: `sql/views/003_sph_views.sql` (수정)

V_SPH_CARD_SALES에 `ELECTRONICS_FURNITURE_SALES` 컬럼 추가.

#### 2b. V_SPH_ASSET_INCOME 확장 — NEW_HOUSING_BALANCE_COUNT 추가

**파일**: `sql/views/003_sph_views.sql` (수정)

V_SPH_ASSET_INCOME에 `NEW_HOUSING_BALANCE_COUNT` 컬럼 추가.

#### 2c. V_TELECOM_DISTRICT_MAPPED 신규 생성

**파일**: `sql/views/005_telecom_district_mapped.sql` (신규)

핵심 수정사항 (dev_spec A3-4 대비):
- `WHERE t.INSTALL_STATE = '서울'` (NOT '서울특별시')
- `TO_CHAR(t.YEAR_MONTH, 'YYYYMM') AS STANDARD_YEAR_MONTH` 추가 (DATE→VARCHAR 변환)

```sql
CREATE OR REPLACE VIEW MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED AS
SELECT
    t.YEAR_MONTH,
    TO_CHAR(t.YEAR_MONTH, 'YYYYMM') AS STANDARD_YEAR_MONTH,
    t.INSTALL_STATE,
    t.INSTALL_CITY,
    t.CONTRACT_COUNT,
    t.OPEN_COUNT,
    t.PAYEND_COUNT,
    t.AVG_NET_SALES,
    m.CITY_CODE,
    m.PROVINCE_CODE
FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL t
LEFT JOIN (
    SELECT DISTINCT PROVINCE_CODE, CITY_CODE, CITY_KOR_NAME
    FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST
) m ON t.INSTALL_CITY = m.CITY_KOR_NAME
WHERE t.INSTALL_STATE = '서울';
```

**검증**: 생성 후 `SELECT COUNT(*), COUNT(DISTINCT CITY_CODE) FROM V_TELECOM_DISTRICT_MAPPED` → 25개 구 확인

---

### Step 3: Snowpark build_integrated_mart() 구현

**파일**: `pipelines/__init__.py` (신규), `pipelines/preprocessing.py` (신규)

#### 핵심 로직

```python
def build_integrated_mart(session: Session) -> DataFrame:
    """
    25개 구 × 월 spine 기반 통합 마트 생성.
    DATA_TIER: 'MULTI_SOURCE' (3구) / 'TELECOM_ONLY' (22구)
    """

    # 1. Spine: 25개 구 × 아정당 월 범위
    district_spine = session.sql("""
        SELECT DISTINCT CITY_CODE, CITY_KOR_NAME, PROVINCE_CODE
        FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER
    """)

    month_spine = session.sql("""
        SELECT DISTINCT TO_CHAR(YEAR_MONTH, 'YYYYMM') AS STANDARD_YEAR_MONTH
        FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL
        WHERE INSTALL_STATE = '서울'
    """)

    spine = district_spine.cross_join(month_spine)

    # 2. 아정당 (25개 구) — CITY_CODE + STANDARD_YEAR_MONTH
    telecom = session.sql("""
        SELECT CITY_CODE, STANDARD_YEAR_MONTH,
               SUM(OPEN_COUNT) AS OPEN_COUNT,
               SUM(CONTRACT_COUNT) AS CONTRACT_COUNT,
               SUM(PAYEND_COUNT) AS PAYEND_COUNT
        FROM MOVING_INTEL.ANALYTICS.V_TELECOM_DISTRICT_MAPPED
        GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    """)

    # 3. SPH 유동인구 (3개 구) — 동→구 집계
    sph_pop = session.sql("""
        SELECT CITY_CODE, STANDARD_YEAR_MONTH,
               SUM(RESIDENTIAL_POPULATION) AS TOTAL_RESIDENTIAL_POP,
               SUM(WORKING_POPULATION) AS TOTAL_WORKING_POP,
               SUM(VISITING_POPULATION) AS TOTAL_VISITING_POP
        FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP
        GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    """)

    # 4. SPH 카드매출 (3개 구) — 동→구 집계
    sph_card = session.sql("""
        SELECT CITY_CODE, STANDARD_YEAR_MONTH,
               SUM(TOTAL_SALES) AS TOTAL_CARD_SALES,
               SUM(ELECTRONICS_FURNITURE_SALES) AS ELECTRONICS_FURNITURE_SALES
        FROM MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES
        GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    """)

    # 5. SPH 자산소득 (3개 구) — 동→구 집계
    sph_income = session.sql("""
        SELECT CITY_CODE, STANDARD_YEAR_MONTH,
               AVG(AVERAGE_INCOME) AS AVG_INCOME,
               AVG(AVERAGE_ASSET_AMOUNT) AS AVG_ASSET,
               SUM(NEW_HOUSING_BALANCE_COUNT) AS NEW_HOUSING_BALANCE_COUNT
        FROM MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME
        GROUP BY CITY_CODE, STANDARD_YEAR_MONTH
    """)

    # 6. RICHGO 시세 (3개 구) — BJD→구 집계, DATE→YYYYMM 변환
    richgo = session.sql("""
        SELECT b.CITY_CODE,
               TO_CHAR(r.YYYYMMDD, 'YYYYMM') AS STANDARD_YEAR_MONTH,
               AVG(r.MEME_PRICE_PER_SUPPLY_PYEONG) AS AVG_MEME_PRICE,
               AVG(r.JEONSE_PRICE_PER_SUPPLY_PYEONG) AS AVG_JEONSE_PRICE,
               SUM(r.TOTAL_HOUSEHOLDS) AS TOTAL_HOUSEHOLDS
        FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
        JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP b
            ON r.BJD_CODE = b.BJD_CODE
        GROUP BY b.CITY_CODE, TO_CHAR(r.YYYYMMDD, 'YYYYMM')
    """)

    # 7. LEFT JOIN 조립
    mart = (
        spine
        .join(telecom, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_pop, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_card, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(sph_income, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
        .join(richgo, ["CITY_CODE", "STANDARD_YEAR_MONTH"], "left")
    )

    # 8. DATA_TIER 컬럼 추가
    multi_source_cities = ["11140", "11560", "11650"]  # 중구, 영등포구, 서초구
    mart = mart.with_column(
        "DATA_TIER",
        F.when(F.col("CITY_CODE").isin(multi_source_cities), F.lit("MULTI_SOURCE"))
         .otherwise(F.lit("TELECOM_ONLY"))
    )

    # 9. 저장
    mart.write.save_as_table(
        "MOVING_INTEL.ANALYTICS.MART_MOVE_ANALYSIS",
        mode="overwrite"
    )
    return mart
```

#### 최종 컬럼 목록 (12 + α)

| # | 컬럼 | 타입 | 출처 | 25구 유효 | #22 용도 |
|---|------|------|------|----------|---------|
| 1 | CITY_CODE | VARCHAR(5) | spine (PK) | ✓ | PK |
| 2 | STANDARD_YEAR_MONTH | VARCHAR(6) | spine (PK) | ✓ | PK |
| 3 | CITY_KOR_NAME | VARCHAR(50) | spine | ✓ | 표시 |
| 4 | PROVINCE_CODE | VARCHAR(2) | spine | ✓ | |
| 5 | OPEN_COUNT | NUMBER | 아정당 | ✓ | S1 |
| 6 | CONTRACT_COUNT | NUMBER | 아정당 | ✓ | |
| 7 | PAYEND_COUNT | NUMBER | 아정당 | ✓ | |
| 8 | TOTAL_RESIDENTIAL_POP | NUMBER | SPH 유동인구 | 3구만 | S2 Δ |
| 9 | TOTAL_WORKING_POP | NUMBER | SPH 유동인구 | 3구만 | |
| 10 | TOTAL_VISITING_POP | NUMBER | SPH 유동인구 | 3구만 | |
| 11 | TOTAL_CARD_SALES | NUMBER | SPH 카드매출 | 3구만 | TC-04 |
| 12 | ELECTRONICS_FURNITURE_SALES | NUMBER | SPH 카드매출 | 3구만 | S4 Δ |
| 13 | AVG_INCOME | NUMBER | SPH 자산소득 | 3구만 | TC-04 |
| 14 | AVG_ASSET | NUMBER | SPH 자산소득 | 3구만 | |
| 15 | NEW_HOUSING_BALANCE_COUNT | NUMBER | SPH 자산소득 | 3구만 | S3 |
| 16 | AVG_MEME_PRICE | NUMBER | RICHGO 시세 | 3구만 | |
| 17 | AVG_JEONSE_PRICE | NUMBER | RICHGO 시세 | 3구만 | |
| 18 | TOTAL_HOUSEHOLDS | NUMBER | RICHGO | 3구만 | |
| 19 | DATA_TIER | VARCHAR | 파생 | ✓ | 차등 가중치 |

---

### Step 4: Snowflake 실행 + 테스트 Green 검증

1. Step 2 뷰 SQL 실행 (003_sph_views.sql + 005_telecom_district_mapped.sql)
2. `build_integrated_mart(session)` 실행
3. TC-01~TC-06 순차 검증
4. 실패 시 → Step 3 수정 → 재실행

---

### Step 5: .ai.md 최신화 + #22 호환성 확인

1. `sql/views/.ai.md` — V_TELECOM_DISTRICT_MAPPED 추가, SPH 뷰 확장 반영
2. `pipelines/.ai.md` — 디렉토리 생성, preprocessing.py 역할 기술
3. `00_issue.md` AC 체크 + 작업 내역 업데이트

#### #22 호환성 체크리스트

| 컬럼 | 존재 | #22 용도 | 비고 |
|------|------|---------|------|
| CITY_CODE | ✓ | PK | spine 보장 |
| STANDARD_YEAR_MONTH | ✓ | PK | spine 보장 |
| OPEN_COUNT | ✓ | S1 | 25개 구 |
| TOTAL_RESIDENTIAL_POP | ✓ | S2 Δ | 3개 구만 non-NULL |
| NEW_HOUSING_BALANCE_COUNT | ✓ | S3 | 3개 구만 non-NULL |
| ELECTRONICS_FURNITURE_SALES | ✓ | S4 Δ | 3개 구만 non-NULL |
| DATA_TIER | ✓ | 차등 가중치 | MULTI_SOURCE / TELECOM_ONLY |

**#22 설계 참고**: TELECOM_ONLY 행(22개 구)에서 S2/S3/S4 = NULL → #22에서 처리 방안:
- (a) MOVE_SIGNAL_INDEX = norm(OPEN_COUNT) (w1=1.0으로 재조정)
- (b) NULL → 0 처리 후 가중치 유지
- (c) INDEX = NULL로 두고 Streamlit에서 처리
→ 이 결정은 #22 scope. 마트는 DATA_TIER로 구분만 제공.

---

## dev_spec 오류 정정 목록

| 위치 | 오류 | 수정 |
|------|------|------|
| A3-4 line 629 | `WHERE t.INSTALL_STATE = '서울특별시'` | `WHERE t.INSTALL_STATE = '서울'` |
| A3-3 line 540 | `F.col("SD") == "서울특별시"` | `F.col("SD") == "서울"` |
| A3-3 line 600 | `INTEGRATED_MART` | `MART_MOVE_ANALYSIS` |
| 여러 곳 | "SPH 25개 구 467동" (FACT 테이블) | "SPH M_SCCO_MST 25개 구(마스터), FACT는 3개 구" |

> dev_spec 수정은 이번 이슈 scope 밖. 별도 chore 이슈로 분리 권장.

---

## 변경 파일 요약

| 파일 | 작업 | Step |
|------|------|------|
| `sql/test/test_06_integrated_mart.sql` | 신규 | 1 |
| `tests/test_06_snowpark.py` | 신규 | 1 |
| `sql/views/003_sph_views.sql` | 수정 (컬럼 추가) | 2 |
| `sql/views/005_telecom_district_mapped.sql` | 신규 | 2 |
| `pipelines/__init__.py` | 신규 | 3 |
| `pipelines/preprocessing.py` | 신규 | 3 |
| `pipelines/.ai.md` | 신규 | 5 |
| `sql/views/.ai.md` | 수정 | 5 |
| `docs/work/active/000021-integrated-mart/00_issue.md` | 수정 | 5 |

---

## Guardrails

### Must Have
- 테이블명 **MART_MOVE_ANALYSIS** (NOT INTEGRATED_MART)
- 구(CITY_CODE) 단위 집계 (NOT 동 단위)
- 25개 구 × 월 spine (CROSS JOIN)
- DATA_TIER 컬럼 ('MULTI_SOURCE' / 'TELECOM_ONLY')
- INSTALL_STATE = **'서울'** (NOT '서울특별시')
- YEAR_MONTH → TO_CHAR(,'YYYYMM') 변환
- 12개 필수 컬럼 전부 포함
- TC-01~TC-06 전부 PASS

### Must NOT Have
- 실데이터 샘플을 코드/주석/커밋에 포함
- Snowflake 연결 정보 하드코딩
- 동 단위 조인 (SPH 3구만이므로 구 단위 필수)
- dev_spec 코드 그대로 복사 (4건 오류 있음)
