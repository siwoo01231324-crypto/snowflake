# 구현 계획: BJD↔DISTRICT 매핑 뷰 생성 (#20)

> 작성일: 2026-04-07 | 마감: 2026-04-12 | 우선순위: **P0 (차단적)**

## 📌 **목적**
RICHGO(법정동코드 BJD_CODE 10자리) ↔ SPH(행정동코드 DISTRICT_CODE 8자리) 두 데이터를 동 단위로 연결하는 매핑 뷰 생성. 이후 이슈 #21~#29가 모두 이 뷰에 의존.

---

## 🚨 **임계적 선결 조건 (Blockers)**

### 1. **컬럼명 불일치 해결 완료** (T0)
- **Issue #20 AC**: `BJD_CODE_PREFIX` (STARTSWITH 방식) — dev_spec 기준 `BJD_CODE_8` + `LEFT()`로 통일
- **dev_spec.md**: `BJD_CODE_8` (LEFT 함수 방식)
- **결정**: ✅ **dev_spec 기준으로 통일** (`BJD_CODE_8` + `LEFT()`)
- **이유**: dev_spec이 전체 파이프라인의 기준 문서이며, #21~#29 이슈가 모두 dev_spec 기반. AC 테스트 SQL을 dev_spec에 맞춰 수정.

### 2. **V_SPH_REGION_MASTER 뷰 확인** (T0)
- **Issue #18 상태**: CLOSED (마크됨)
- **문제**: SQL 파일(`sql/views/003_sph_views.sql`)이 **없음**
- **필요 확인**: 뷰가 Snowflake에 이미 생성되어 있는지 여부

---

## AC 체크리스트

- [x] **T0-1**: 컬럼명 dev_spec 기준 통일 (`BJD_CODE_8` + `LEFT()` 유지)
- [x] **T0-2**: V_SPH_REGION_MASTER 뷰 존재 확인 (Python 연결로 확인 완료)
- [ ] **T1**: `sql/views/004_bjd_mapping.sql` 생성
- [ ] **T1**: `sql/test/test_05_bjd_mapping.sql` 작성
- [ ] **T1**: `sql/validation/validate_05_bjd.sql` 작성
- [ ] **T2**: 매핑 커버리지 검증 (80% 이상)
- [ ] **T2**: E2E JOIN 테스트 (RICHGO ↔ SPH)

---

## 📐 **구현 전략 (7단계)**

### **Step 1: dev_spec 기준 확정** (T0-1, 완료)

**결정**: dev_spec.md의 A1-2 SQL을 그대로 사용. 변경 없음.
```sql
LEFT(r.BJD_CODE, 8) AS BJD_CODE_8,        -- 컬럼명 유지
ON LEFT(r.BJD_CODE, 8) = m.DISTRICT_CODE   -- JOIN 로직 유지
```

**Issue #20 AC 테스트 SQL 조정**: 구현 시 `BJD_CODE_8` → `BJD_CODE_8`으로 수정하여 작성.
- TC-02: `LEFT(r.BJD_CODE, 8) = m.BJD_CODE_8` → `LEFT(r.BJD_CODE, 8) = m.BJD_CODE_8`
- TC-03: 동일 방식
- TC-04: `BJD_CODE_8` → `BJD_CODE_8`

---

### **Step 2: V_SPH_REGION_MASTER 뷰 확인** (T0-2, 10분)

**확인 작업**:
```bash
# 방법 1: Snowflake에서 직접 조회
SELECT * FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER LIMIT 1;

# 방법 2: 파일 존재 확인
ls -la sql/views/003_sph_views.sql
```

**결과 해석**:
- ✅ 뷰 존재 + 파일도 있음 → 다음 단계 진행
- ⚠️ 뷰 존재 + 파일 없음 → sql/views/003_sph_views.sql 생성 필요
- ❌ 뷰 없음 → Issue #18 재확인 필요

---

### **Step 3: sql/views/004_bjd_mapping.sql 생성** (T1, 15분)

**파일 구조**:
```sql
-- ============================================================
-- 004_bjd_mapping.sql
-- BJD_CODE(법정동코드) ↔ DISTRICT_CODE(행정동코드) 매핑 뷰
-- 이슈: #20
-- 의존성: #17 (V_RICHGO_MARKET_PRICE), #18 (V_SPH_REGION_MASTER)
-- 멱등성: CREATE OR REPLACE
-- ============================================================

USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

CREATE OR REPLACE VIEW V_BJD_DISTRICT_MAP
  COMMENT = 'RICHGO BJD_CODE ↔ SPH DISTRICT_CODE 매핑 뷰'
AS
SELECT
    m.PROVINCE_CODE,
    m.CITY_CODE,
    m.DISTRICT_CODE,
    m.DISTRICT_KOR_NAME,
    m.CITY_KOR_NAME,
    LEFT(r.BJD_CODE, 8) AS BJD_CODE_8,  -- 8자리 접두사
    r.BJD_CODE,                               -- 10자리 전체
    r.EMD AS RICHGO_EMD_NAME
FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.M_SCCO_MST m
JOIN (
    SELECT DISTINCT BJD_CODE, EMD
    FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE
    WHERE SD = '서울특별시'
) r 
ON LEFT(r.BJD_CODE, 8) = m.DISTRICT_CODE;
```

**주의점**:
- RICHGO에서 '서울특별시' 데이터만 필터 (SPH는 서울만 범위)
- DISTINCT BJD_CODE를 서브쿼리로 중복 제거
- ON 절: `LEFT(r.BJD_CODE, 8) = m.DISTRICT_CODE` (dev_spec 기준)

---

### **Step 4: sql/test/test_05_bjd_mapping.sql 작성** (T1, 20분)

**파일 구조** (Issue #20 AC 기반):
```sql
-- ============================================================
-- test_05_bjd_mapping.sql
-- V_BJD_DISTRICT_MAP AC 검증 (이슈 #20)
-- ============================================================

-- TC-01: 매핑 뷰 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP;
-- EXPECTED: cnt > 0

-- TC-02: 매핑 커버리지 확인
SELECT 
    COUNT(DISTINCT r.BJD_CODE) AS total_bjd,
    COUNT(DISTINCT m.BJD_CODE) AS mapped_bjd,
    ROUND(COUNT(DISTINCT m.BJD_CODE) / COUNT(DISTINCT r.BJD_CODE) * 100, 1) AS coverage_pct
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
LEFT JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m ON LEFT(r.BJD_CODE, 8) = m.BJD_CODE_8;
-- EXPECTED: coverage_pct >= 80

-- TC-03: JOIN 결과 확인 (RICHGO 시세 + SPH 행정구역)
SELECT r.SGG, r.EMD, r.MEME_PRICE_PER_SUPPLY_PYEONG, s.CITY_KOR_NAME
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m ON LEFT(r.BJD_CODE, 8) = m.BJD_CODE_8
JOIN MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER s ON m.CITY_CODE = s.CITY_CODE
LIMIT 5;
-- EXPECTED: 4개 컬럼 모두 값 존재, NULL 없음

-- TC-04: 매핑 키 유니크 확인
SELECT BJD_CODE_8, COUNT(*) AS cnt 
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP 
GROUP BY 1 HAVING cnt > 1;
-- EXPECTED: 0 rows (중복 없음)
```

**검증 방식**:
- TC-01: 뷰 생성 여부
- TC-02: 커버리지 >= 80% (AC 요구사항)
- TC-03: 다운스트림 JOIN 동작 확인
- TC-04: 중복 행 없음 (데이터 정합성)

---

### **Step 5: sql/validation/validate_05_bjd.sql 작성** (T1, 10분)

**파일 구조**:
```sql
-- ============================================================
-- validate_05_bjd.sql
-- V_BJD_DISTRICT_MAP 데이터 정합성 검증
-- ============================================================

-- 1. 기본 통계
SELECT 
    'V_BJD_DISTRICT_MAP' AS view_name,
    COUNT(*) AS row_cnt,
    COUNT(DISTINCT BJD_CODE_8) AS distinct_prefix,
    COUNT(DISTINCT BJD_CODE) AS distinct_bjd_code,
    COUNT(DISTINCT DISTRICT_CODE) AS distinct_district
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP;

-- 2. 커버리지 상세 분석
SELECT 
    m.CITY_KOR_NAME,
    COUNT(DISTINCT m.BJD_CODE) AS bjd_count,
    COUNT(DISTINCT m.DISTRICT_CODE) AS district_count,
    ROUND(COUNT(DISTINCT m.BJD_CODE) / COUNT(DISTINCT m.DISTRICT_CODE), 2) AS bjd_per_district
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m
GROUP BY m.CITY_KOR_NAME
ORDER BY bjd_count DESC;

-- 3. 누락 BJD_CODE 확인 (서울 내 미매핑)
SELECT COUNT(DISTINCT r.BJD_CODE) AS unmapped_bjd
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
WHERE r.SD = '서울특별시'
  AND NOT EXISTS (
    SELECT 1 FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m 
    WHERE LEFT(r.BJD_CODE, 8) = m.BJD_CODE_8
  );
-- EXPECTED: 0 또는 매우 적은 수 (커버리지 > 80%)
```

---

### **Step 6: Snowflake에서 실행 및 검증** (T2, 20분)

**실행 순서**:
1. `sql/views/004_bjd_mapping.sql` 실행 → V_BJD_DISTRICT_MAP 생성
2. `sql/test/test_05_bjd_mapping.sql` 실행 → 4개 TC 통과 확인
3. `sql/validation/validate_05_bjd.sql` 실행 → 통계 및 커버리지 분석

**예상 결과**:
```
TC-01: cnt > 0              ✅
TC-02: coverage_pct >= 80   ✅ (예상 >= 95%)
TC-03: 5개 행 모두 NULL 없음  ✅
TC-04: 0 rows              ✅
```

---

### **Step 7: 01_plan.md + 00_issue.md 최신화** (T2, 10분)

**업데이트 내용**:
1. AC 체크리스트 완료 체크
2. 작업 내역 기록 (2026-04-07)
3. 다음 단계 링크: Issue #21 (FACT_HOUSING_PRICE 통합)

---

## 📊 **의존성 맵**

```
Issue #20: V_BJD_DISTRICT_MAP (현재)
  ├─ Issue #21: FACT_HOUSING_PRICE (RICHGO 시세 통합 마트)
  ├─ Issue #22: MOVE_SIGNAL_INDEX (매핑을 통한 조인)
  ├─ Issue #23: ML 학습 + PREDICT_MOVE_DEMAND UDF
  ├─ Issue #24: CALC_ROI UDF
  ├─ Issue #25: GET_SEGMENT_PROFILE UDF
  ├─ Issue #26: Cortex Analyst 시맨틱 모델 (4개)
  ├─ Issue #27: Cortex AI Functions 구현
  ├─ Issue #28: Streamlit 히트맵 탭 (의존)
  └─ Issue #29: Streamlit 필터 + ROI 계산기 탭 (의존)
```

**임계 경로**: Issue #20 → #21 → #22 → #23 (ML 파이프라인)

**현재 상태**: 🔴 **BLOCKED** (컬럼명 불일치)

---

## ⏱️ **예상 소요 시간**

| Step | 작업 | 예상 시간 | 누적 |
|------|------|---------|------|
| 1 | dev_spec.md 수정 | 5분 | 5분 |
| 2 | V_SPH_REGION_MASTER 확인 | 10분 | 15분 |
| 3 | 매핑 뷰 생성 SQL | 15분 | 30분 |
| 4 | 테스트 쿼리 작성 | 20분 | 50분 |
| 5 | 검증 쿼리 작성 | 10분 | 60분 |
| 6 | Snowflake 실행 + 검증 | 20분 | 80분 |
| 7 | 문서 최신화 | 10분 | 90분 |
| **Total** | | **~90분 (1.5시간)** | |

---

## 🎯 **성공 기준**

- ✅ Issue #20 AC 3개 모두 통과
- ✅ 매핑 커버리지 >= 80%
- ✅ E2E RICHGO ↔ SPH JOIN 정상 동작
- ✅ 문서 최신화 (01_plan.md, 00_issue.md)
- ✅ 다음 이슈(#21) 구현 차단 제거
