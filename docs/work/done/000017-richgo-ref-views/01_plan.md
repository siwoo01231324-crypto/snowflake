# [#17] RICHGO 참조 뷰 3개 생성 — 구현 계획

> 작성: 2026-04-07 | 팀 플래닝 (explorer + architect + lead 종합)

---

## 완료 기준

- [ ] `V_RICHGO_MARKET_PRICE` 뷰 생성 (아파트 시세)
- [ ] `V_RICHGO_POPULATION` 뷰 생성 (성별/연령 인구)
- [ ] `V_RICHGO_YOUNG_CHILDREN` 뷰 생성 (영유아 비율)
- [ ] 각 뷰의 row count가 원본과 일치

---

## 구현 계획

### Phase 0: 사전 확인 (수동)

1. **Snowflake 접속 확인** — `USE WAREHOUSE MOVING_INTEL_WH;` 실행 가능 여부
2. **Marketplace 접근 확인** — #16 TC-05에서 이미 검증됨 (RICHGO 크로스 DB 접근)
3. **MOVING_INTEL.ANALYTICS 스키마 존재** — #16에서 생성 완료 (`sql/ddl/001_create_database_schema.sql`)

### Phase 1: 테스트 먼저 작성 (TDD Red)

**파일**: `sql/test/test_02_richgo_views.sql`

이슈 body에 정의된 TC-01 ~ TC-05를 SQL 파일로 작성:

```sql
-- TC-01: 시세 뷰 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE;
-- EXPECTED: cnt = 4356

-- TC-02: 시세 뷰 필수 컬럼 확인
SELECT BJD_CODE, SD, SGG, EMD, YYYYMMDD,
       MEME_PRICE_PER_SUPPLY_PYEONG, JEONSE_PRICE_PER_SUPPLY_PYEONG, TOTAL_HOUSEHOLDS
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE LIMIT 1;
-- EXPECTED: 8개 컬럼 모두 존재, 에러 없음

-- TC-03: 인구 뷰 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_RICHGO_POPULATION;
-- EXPECTED: cnt = 118

-- TC-04: 영유아 뷰 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_RICHGO_YOUNG_CHILDREN;
-- EXPECTED: cnt = 118

-- TC-05: 날짜 범위 확인
SELECT MIN(YYYYMMDD) AS min_dt, MAX(YYYYMMDD) AS max_dt
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE;
-- EXPECTED: min_dt = 2012-01-01, max_dt = 2024-12-01
```

### Phase 2: 뷰 DDL 작성 (TDD Green)

**파일**: `sql/views/002_richgo_views.sql`

> 넘버링: `001_` = DB/스키마(#16), `002_` = RICHGO 뷰(#17), `003_` = SPH 뷰(#18) ...

```sql
-- ============================================================
-- 002_richgo_views.sql
-- RICHGO Marketplace 데이터 참조 뷰 3개 생성
-- 이슈: #17 (feat: RICHGO 참조 뷰 3개 생성)
-- 의존성: #16 (MOVING_INTEL.ANALYTICS 스키마)
-- 멱등성: CREATE OR REPLACE — 반복 실행 안전
-- ============================================================

USE WAREHOUSE MOVING_INTEL_WH;
USE SCHEMA MOVING_INTEL.ANALYTICS;

-- 1) V_RICHGO_MARKET_PRICE — 아파트 시세 (2012-01 ~ 2024-12, 4356건)
CREATE OR REPLACE VIEW V_RICHGO_MARKET_PRICE AS
SELECT
    REGION_LEVEL,
    BJD_CODE,       -- 법정동코드 10자리 (후속 #20 V_BJD_DISTRICT_MAP에서 매핑 키)
    SD,             -- 시/도
    SGG,            -- 시/군/구
    EMD,            -- 읍/면/동
    YYYYMMDD,       -- DATE 타입, 월별 집계 기준일
    TOTAL_HOUSEHOLDS,
    MEME_PRICE_PER_SUPPLY_PYEONG,
    JEONSE_PRICE_PER_SUPPLY_PYEONG
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H;

-- 2) V_RICHGO_POPULATION — 인구 성별/연령 (2025-01, 118건)
CREATE OR REPLACE VIEW V_RICHGO_POPULATION AS
SELECT
    BJD_CODE,
    SD, SGG, EMD,
    YYYYMMDD,
    TOTAL, MALE, FEMALE,
    AGE_UNDER20, AGE_20S, AGE_30S, AGE_40S, AGE_50S, AGE_60S, AGE_OVER70
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_GENDER_AGE_M_H;

-- 3) V_RICHGO_YOUNG_CHILDREN — 영유아/가임여성 비율 (2025-01, 118건)
--    dev_spec 기준 명칭 확정
CREATE OR REPLACE VIEW V_RICHGO_YOUNG_CHILDREN AS
SELECT
    BJD_CODE,
    SD, SGG, EMD,
    YYYYMMDD,
    AGE_UNDER5,
    FEMALE_20TO40,
    AGE_UNDER5_PER_FEMALE_20TO40
FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_MOIS_POPULATION_AGE_UNDER5_PER_FEMALE_20TO40_M_H;
```

### Phase 3: Snowflake 실행 + 검증 (TDD Verify)

1. Snowflake MCP 또는 웹 콘솔에서 `002_richgo_views.sql` 실행
2. `test_02_richgo_views.sql`의 TC-01 ~ TC-05 순서대로 실행
3. 결과를 `00_issue.md` 작업 내역에 기록

### Phase 4: 데이터 검증 쿼리 추가

**파일**: `sql/validation/validate_02_richgo.sql`

```sql
-- RICHGO 3개 뷰 데이터 정합성 검증
SELECT 'V_RICHGO_MARKET_PRICE' AS view_name, COUNT(*) AS row_cnt,
       MIN(YYYYMMDD) AS min_date, MAX(YYYYMMDD) AS max_date
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE
UNION ALL
SELECT 'V_RICHGO_POPULATION', COUNT(*), MIN(YYYYMMDD), MAX(YYYYMMDD)
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_POPULATION
UNION ALL
SELECT 'V_RICHGO_YOUNG_CHILDREN', COUNT(*), MIN(YYYYMMDD), MAX(YYYYMMDD)
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_YOUNG_CHILDREN;
```

### Phase 5: .ai.md 최신화 + 정리

1. `sql/views/.ai.md` 생성 — 뷰 목록, 의존성, 실행 순서 기술
2. `sql/test/.ai.md` 업데이트 — test_02 추가 반영
3. `00_issue.md` AC 체크리스트 업데이트

---

## 파일 변경 목록

| 동작 | 파일 경로 | 설명 |
|------|----------|------|
| CREATE | `sql/views/002_richgo_views.sql` | RICHGO 뷰 3개 DDL |
| CREATE | `sql/test/test_02_richgo_views.sql` | AC 검증 테스트 쿼리 |
| CREATE | `sql/validation/validate_02_richgo.sql` | 데이터 정합성 검증 쿼리 |
| CREATE | `sql/views/.ai.md` | views 디렉토리 문서 |
| UPDATE | `sql/test/.ai.md` | test_02 추가 반영 (없으면 생성) |
| UPDATE | `docs/work/active/000017-richgo-ref-views/00_issue.md` | AC 체크 + 작업 내역 |

---

## 이전 이슈 연동 (#16)

| 항목 | 상태 |
|------|------|
| `MOVING_INTEL` DB 존재 | ✅ #16에서 생성 (`sql/ddl/001_create_database_schema.sql`) |
| `MOVING_INTEL.ANALYTICS` 스키마 존재 | ✅ #16에서 생성 |
| `MOVING_INTEL_WH` 웨어하우스 접근 | ✅ #16 TC-03에서 검증 |
| Marketplace 크로스 DB 접근 | ✅ #16 TC-05에서 RICHGO 접근 검증 |

---

## 후속 이슈 호환성

| 후속 이슈 | 의존하는 #17 산출물 | 호환성 검증 |
|----------|-------------------|------------|
| **#18** SPH 뷰 4개 | 없음 (독립적) | ✅ 파일 넘버링 `003_` 예약 |
| **#19** 아정당+NextTrade 뷰 | 없음 (독립적) | ✅ 파일 넘버링 `004_` 예약 |
| **#20** BJD↔DISTRICT 매핑 뷰 | `V_RICHGO_MARKET_PRICE.BJD_CODE` | ✅ BJD_CODE(10자리) 컬럼명 유지, LEFT(BJD_CODE,8)로 DISTRICT_CODE 매핑 |
| **#21** 통합 마트 | `V_RICHGO_MARKET_PRICE` 직접 참조 | ✅ dev_spec A3의 `session.table("MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE")` 호환 |

---

## 위험 요소 + 완화

| 위험 | 영향 | 완화 |
|------|------|------|
| **명칭 불일치**: 이슈 AC에 `V_RICHGO_YOUNG_FAMILY`로 오기 | 후속 이슈에서 잘못된 이름 참조 | dev_spec 기준 `V_RICHGO_YOUNG_CHILDREN` 확정. 이슈 body는 참고만 |
| row count가 실데이터와 다를 수 있음 | TC 실패 | Marketplace 데이터 업데이트 시 count 변동 가능. 검증 후 TC 기대값 수정 |
| Marketplace 구독 만료 | 뷰 쿼리 실패 | Marketplace 구독 상태 사전 확인 (현재 4종 구독 완료 확인됨) |

---

## 실행 순서 요약

```
1. sql/test/test_02_richgo_views.sql 작성 (TDD Red)
2. sql/views/002_richgo_views.sql 작성
3. Snowflake에서 002_richgo_views.sql 실행
4. test_02_richgo_views.sql로 AC 검증 (TDD Green)
5. sql/validation/validate_02_richgo.sql 작성 + 실행
6. .ai.md 최신화
7. 00_issue.md AC 체크 + 작업 내역 기록
8. dev_spec.md에서 V_RICHGO_YOUNG_CHILDREN → V_RICHGO_YOUNG_CHILDREN 수정
```

---

## 결정 사항 (확정)

1. **뷰 이름**: `V_RICHGO_YOUNG_CHILDREN` (dev_spec 기준 통일) — 모든 작업은 dev_spec 기준으로 실행
2. **row count 기대값**: dev_spec 명시값 그대로 사용 (4356/118)
