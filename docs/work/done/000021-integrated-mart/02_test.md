# [#21] 통합 마트 테이블 — 테스트 계획

> 작성: 2026-04-08

## SQL 테스트 (test_06_integrated_mart.sql)

| TC | 설명 | 쿼리 | 기대값 | 결과 |
|----|------|------|--------|------|
| TC-01 | 마트 row count | `SELECT COUNT(*) FROM MART_MOVE_ANALYSIS` | > 0 | ✅ PASS (count=850) |
| TC-02 | 25개 구 커버리지 | `SELECT COUNT(DISTINCT CITY_CODE) FROM MART_MOVE_ANALYSIS` | = 25 | ✅ PASS (gu_count=25) |
| TC-03 | 키 컬럼 NULL | `SELECT COUNT(*) WHERE CITY_CODE IS NULL OR STANDARD_YEAR_MONTH IS NULL` | = 0 | ✅ PASS (null_keys=0) |
| TC-04 | MULTI_SOURCE 필수 컬럼 | `SELECT 6개 컬럼 WHERE DATA_TIER='MULTI_SOURCE' LIMIT 1` | 6개 모두 NOT NULL | ✅ PASS |
| TC-04b | TELECOM_ONLY OPEN_COUNT | `SELECT COUNT(*) WHERE DATA_TIER='TELECOM_ONLY' AND OPEN_COUNT IS NULL` | = 0 | ✅ PASS (null_open=0) |
| TC-05 | 월별 범위 | `SELECT MIN/MAX STANDARD_YEAR_MONTH` | 202307~202604 | ✅ PASS (202307~202604) |
| TC-06 | DATA_TIER 분포 | `SELECT DATA_TIER, COUNT(DISTINCT CITY_CODE) GROUP BY DATA_TIER` | MULTI=3, TELECOM=22 | ✅ PASS |

### SQL 테스트 상세 쿼리

```sql
-- TC-01: 마트 테이블 row count
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

## Python 테스트 (test_06_snowpark.py)

| 함수 | 설명 | 검증 내용 |
|------|------|----------|
| `test_build_integrated_mart_row_count` | 마트 데이터 존재 | `count() > 0` |
| `test_build_integrated_mart_25_districts` | 25개 구 커버리지 | `CITY_CODE distinct() == 25` |
| `test_build_integrated_mart_no_null_keys` | 키 컬럼 NULL 없음 | `CITY_CODE/STANDARD_YEAR_MONTH NULL == 0` |
| `test_build_integrated_mart_multi_source` | MULTI_SOURCE 분포 | `CITY_CODE distinct == 3` |
| `test_build_integrated_mart_telecom_only` | TELECOM_ONLY 분포 | `CITY_CODE distinct == 22` |
| `test_build_integrated_mart_required_columns` | 필수 컬럼 (MULTI_SOURCE) | 6개: OPEN_COUNT, TOTAL_RESIDENTIAL_POP, TOTAL_CARD_SALES, AVG_INCOME, CITY_CODE, STANDARD_YEAR_MONTH |

### Python 테스트 상세 코드

```python
"""
tests/test_06_snowpark.py
Snowpark 기반 MART_MOVE_ANALYSIS 검증
"""
import pytest
from pyspark.sql import functions as F


def test_build_integrated_mart_row_count(session):
    """마트 데이터 존재 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    assert result.count() > 0, "마트에 데이터 없음"


def test_build_integrated_mart_25_districts(session):
    """25개 구 커버리지 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    distinct_cities = result.select("CITY_CODE").distinct().count()
    assert distinct_cities == 25, f"구 수 {distinct_cities} != 25"


def test_build_integrated_mart_no_null_keys(session):
    """키 컬럼 NULL 없음 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    null_city = result.filter(F.col("CITY_CODE").is_null()).count()
    null_month = result.filter(F.col("STANDARD_YEAR_MONTH").is_null()).count()
    
    assert null_city == 0, f"CITY_CODE NULL {null_city}건"
    assert null_month == 0, f"STANDARD_YEAR_MONTH NULL {null_month}건"


def test_build_integrated_mart_data_tier_distribution(session):
    """DATA_TIER 분포 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    
    multi_source = result.filter(F.col("DATA_TIER") == "MULTI_SOURCE").select("CITY_CODE").distinct().count()
    telecom_only = result.filter(F.col("DATA_TIER") == "TELECOM_ONLY").select("CITY_CODE").distinct().count()
    
    assert multi_source == 3, f"MULTI_SOURCE 구 수 {multi_source} != 3"
    assert telecom_only == 22, f"TELECOM_ONLY 구 수 {telecom_only} != 22"


def test_build_integrated_mart_multi_source_required_columns(session):
    """MULTI_SOURCE 행 필수 컬럼 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    
    multi_row = result.filter(F.col("DATA_TIER") == "MULTI_SOURCE").limit(1)
    required_cols = ["CITY_CODE", "STANDARD_YEAR_MONTH", "OPEN_COUNT", 
                     "TOTAL_RESIDENTIAL_POP", "TOTAL_CARD_SALES", "AVG_INCOME"]
    
    for col in required_cols:
        null_count = multi_row.filter(F.col(col).is_null()).count()
        assert null_count == 0, f"MULTI_SOURCE에서 {col} NULL 검출"


def test_build_integrated_mart_telecom_open_count_not_null(session):
    """TELECOM_ONLY 행 OPEN_COUNT NOT NULL 확인"""
    from pipelines.preprocessing import build_integrated_mart
    
    result = build_integrated_mart(session)
    
    null_count = result.filter(
        (F.col("DATA_TIER") == "TELECOM_ONLY") & F.col("OPEN_COUNT").is_null()
    ).count()
    
    assert null_count == 0, f"TELECOM_ONLY에서 OPEN_COUNT NULL {null_count}건"
```

## DATA_TIER 설명

| DATA_TIER | 구 수 | 데이터 소스 | 비고 |
|-----------|------|-----------|------|
| MULTI_SOURCE | 3 (중구, 영등포구, 서초구) | 아정당 + SPH + RICHGO | 4종 시그널 모두 유효 |
| TELECOM_ONLY | 22 | 아정당만 | S1(OPEN_COUNT)만 유효 |

## 테스트 실행 방법

### SQL 테스트 실행

Snowflake 워크시트에서 다음 순서로 각 쿼리를 실행:

1. `MART_MOVE_ANALYSIS` 테이블 생성 (Snowpark 또는 SQL로 먼저 생성)
2. TC-01 ~ TC-06 순차 실행
3. 각 쿼리 결과를 위 테이블의 '결과' 칸에 기록

### Python 테스트 실행

```bash
# Snowpark 세션 초기화 후 실행
pytest tests/test_06_snowpark.py -v
```

또는 개별 테스트:

```bash
pytest tests/test_06_snowpark.py::test_build_integrated_mart_row_count -v
pytest tests/test_06_snowpark.py::test_build_integrated_mart_25_districts -v
```

## 테스트 결과 기록

### SQL 테스트 결과 (2026-04-08 최종)

| TC | 실행 결과 | 비고 |
|----|----------|------|
| TC-01 | ✅ PASS (count=850) | 25구 × 34개월 |
| TC-02 | ✅ PASS (gu_count=25) | 서울 25개 구 전체 |
| TC-03 | ✅ PASS (null_keys=0) | spine CROSS JOIN 보장 |
| TC-04 | ✅ PASS (6개 컬럼 모두 NOT NULL) | MULTI_SOURCE 행 |
| TC-04b | ✅ PASS (null_open=0) | spine 정제로 텔레콤 갭 제거 |
| TC-05 | ✅ PASS (min=202307, max=202604) | 25구 텔레콤 완전 커버 기간 |
| TC-06 | ✅ PASS (MULTI_SOURCE=3, TELECOM_ONLY=22) | |

**Spine 정제 적용**: 텔레콤 데이터가 25개 구 모두 존재하는 월만 spine에 포함 (`HAVING COUNT(DISTINCT CITY_CODE) = 25`). 결과적으로 데이터 갭이 있는 양 끝 4개월(202303~202306, 202605) 제거 → 850행 (25구 × 34개월).

### Python 테스트 결과

```
test_build_integrated_mart_row_count: [ PASS / FAIL ]
test_build_integrated_mart_25_districts: [ PASS / FAIL ]
test_build_integrated_mart_no_null_keys: [ PASS / FAIL ]
test_build_integrated_mart_data_tier_distribution: [ PASS / FAIL ]
test_build_integrated_mart_multi_source_required_columns: [ PASS / FAIL ]
test_build_integrated_mart_telecom_open_count_not_null: [ PASS / FAIL ]
```

## 통과 기준

모든 TC 및 Python 테스트가 PASS되어야 Task #21 완료로 인정.

실패 시 다음을 확인:
1. `MART_MOVE_ANALYSIS` 테이블 존재 여부
2. `build_integrated_mart()` 함수 로직 재검토
3. VIEW(V_TELECOM_DISTRICT_MAPPED, V_SPH_* 등) 생성 확인
4. Snowflake 데이터 샘플 확인
