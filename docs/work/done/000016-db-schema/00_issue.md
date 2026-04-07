# feat: 프로젝트 DB/스키마 생성 + 웨어하우스 검증

## 목적
Snowflake에 프로젝트 전용 데이터베이스(MOVING_INTEL)와 스키마(ANALYTICS)를 만든다.

## 완료 기준
- [x] `MOVING_INTEL` 데이터베이스 생성됨
- [x] `MOVING_INTEL.ANALYTICS` 스키마 생성됨
- [x] `MOVING_INTEL_WH` 웨어하우스 접근 확인됨

## 테스트 코드 (TDD — 먼저 작성)

```sql
-- test_01_db_schema.sql
-- TC-01: 데이터베이스 존재 확인
SELECT COUNT(*) AS db_exists 
FROM INFORMATION_SCHEMA.DATABASES 
WHERE DATABASE_NAME = 'MOVING_INTEL';
-- EXPECTED: db_exists = 1

-- TC-02: 스키마 존재 확인
SHOW SCHEMAS IN DATABASE MOVING_INTEL;
-- EXPECTED: ANALYTICS 스키마 존재

-- TC-03: 웨어하우스 접근 확인
SELECT CURRENT_WAREHOUSE();
-- EXPECTED: MOVING_INTEL_WH
```

## 참조
- `docs/specs/dev_spec.md` A2 섹션 (Marketplace 연동)
- 의존성: 없음 (첫 번째 이슈)

## 불변식
- MOVING_INTEL.ANALYTICS 스키마는 모든 후속 이슈의 기반
- 웨어하우스는 X-Small, auto-suspend 60초

## 작업 내역
- 2026-04-07: 세션 시작. AC 0/3 완료. 구현 대기 상태. 01_plan.md 구현 계획 본문 미작성.
- 2026-04-07: US-001 완료 — SQL 디렉토리 구조 및 DDL/테스트 스크립트 생성
- 2026-04-07: US-002~US-004 완료 — DDL 실행 및 AC/Marketplace 검증 완료. 결과:
  - TC-01: MOVING_INTEL DB 존재 확인 ✅ (1 row)
  - TC-02: ANALYTICS 스키마 존재 확인 ✅ (schemas: ANALYTICS, INFORMATION_SCHEMA, PUBLIC)
  - TC-03: CURRENT_WAREHOUSE() = MOVING_INTEL_WH ✅
  - TC-04: USE SCHEMA MOVING_INTEL.ANALYTICS → DB=MOVING_INTEL, SCHEMA=ANALYTICS ✅
  - TC-05: RICHGO Marketplace 크로스 쿼리 ✅ (4,356 rows)
  - TC-06: SPH Floating Population 크로스 쿼리 ✅ (2,577,120 rows)
- 2026-04-07: AC 3/3 완료. US-005 문서 업데이트 완료.
