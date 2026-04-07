# [#16] feat: 프로젝트 DB/스키마 생성 + 웨어하우스 검증 — 구현 계획

> 작성: 2026-04-07

---

## 완료 기준

- [x] `MOVING_INTEL` 데이터베이스 생성됨
- [x] `MOVING_INTEL.ANALYTICS` 스키마 생성됨
- [x] `MOVING_INTEL_WH` 웨어하우스 접근 확인됨

---

## 구현 계획

### Step 0: 사전 조건 확인

Snowflake MCP를 통해 환경 상태를 점검한다. 하나라도 실패하면 DDL 실행 전 원인 파악 후 사용자에게 보고.

| # | 점검 항목 | SQL | 기대 결과 |
|---|----------|-----|----------|
| P-01 | 웨어하우스 존재 확인 | `SHOW WAREHOUSES LIKE 'MOVING_INTEL_WH';` | 1행 반환, type=STANDARD, size=X-Small |
| P-02 | 현재 Role 확인 | `SELECT CURRENT_ROLE();` | ACCOUNTADMIN |
| P-03 | Marketplace DB 접근 (RICHGO) | `SHOW DATABASES LIKE '%KOREAN_POPULATION%';` | 1행 반환 |
| P-04 | Marketplace DB 접근 (SPH) | `SHOW DATABASES LIKE '%SEOUL_DISTRICTLEVEL%';` | 1행 반환 |
| P-05 | MOVING_INTEL DB 상태 확인 | `SHOW DATABASES LIKE 'MOVING_INTEL';` | 0행(미생성) 또는 1행(이미 존재 — 멱등 처리) |

> P-01~P-04가 실패하면 DDL 실행을 중단하고 사용자에게 보고한다.

---

### Step 1: DDL 스크립트 작성

**파일:** `sql/ddl/001_create_database_schema.sql`

```sql
-- ============================================================
-- 001_create_database_schema.sql
-- 프로젝트 전용 데이터베이스 및 스키마 생성
-- 이슈: #16 (feat: 프로젝트 DB/스키마 생성 + 웨어하우스 검증)
-- 멱등성: IF NOT EXISTS 사용 — 반복 실행 안전
-- ============================================================

-- Step 1: 웨어하우스 사용 선언
USE WAREHOUSE MOVING_INTEL_WH;

-- Step 2: 프로젝트 데이터베이스 생성
CREATE DATABASE IF NOT EXISTS MOVING_INTEL
  COMMENT = '무빙 인텔리전스 프로젝트 전용 데이터베이스';

-- Step 3: 분석 스키마 생성
CREATE SCHEMA IF NOT EXISTS MOVING_INTEL.ANALYTICS
  COMMENT = 'Marketplace 데이터 기반 분석 뷰/UDF 저장 스키마';
```

**파일:** `sql/test/test_01_db_schema.sql`

```sql
-- ============================================================
-- test_01_db_schema.sql
-- DB/스키마/웨어하우스 검증 쿼리 (이슈 #16 AC 검증)
-- ============================================================

-- TC-01: 데이터베이스 존재 확인
SELECT COUNT(*) AS db_exists
FROM INFORMATION_SCHEMA.DATABASES
WHERE DATABASE_NAME = 'MOVING_INTEL';
-- EXPECTED: db_exists = 1

-- TC-02: 스키마 존재 확인
SHOW SCHEMAS IN DATABASE MOVING_INTEL;
-- EXPECTED: ANALYTICS 스키마가 목록에 존재

-- TC-03: 웨어하우스 접근 확인
SELECT CURRENT_WAREHOUSE();
-- EXPECTED: MOVING_INTEL_WH

-- TC-04: 스키마 컨텍스트 전환 가능 확인
USE SCHEMA MOVING_INTEL.ANALYTICS;
SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();
-- EXPECTED: MOVING_INTEL, ANALYTICS
```

**파일:** `sql/.ai.md` — SQL 디렉토리의 목적, 구조, 역할을 기술하는 메타 문서.

---

### Step 2: SQL 실행 (Snowflake MCP)

Snowflake MCP를 통해 단계별 SQL 실행. 각 단계 결과를 확인한 뒤 다음으로 진행.

```
[Phase 0] 사전 조건 점검
  └─ P-01 ~ P-05 실행 → 모두 통과 시 Phase 1로

[Phase 1] DDL 실행
  ├─ USE WAREHOUSE MOVING_INTEL_WH;
  ├─ CREATE DATABASE IF NOT EXISTS MOVING_INTEL ...;
  └─ CREATE SCHEMA IF NOT EXISTS MOVING_INTEL.ANALYTICS ...;
```

> MCP를 통해 SQL은 **한 문장씩** 순서대로 실행한다. 세미콜론으로 구분된 다중 문장을 한 번에 보내지 않는다.

---

### Step 3: 검증 쿼리 실행

| TC | SQL | 성공 기준 | AC 매핑 |
|----|-----|----------|---------|
| TC-01 | `SELECT COUNT(*) AS db_exists FROM INFORMATION_SCHEMA.DATABASES WHERE DATABASE_NAME = 'MOVING_INTEL';` | db_exists = 1 | AC-1 |
| TC-02 | `SHOW SCHEMAS IN DATABASE MOVING_INTEL;` | ANALYTICS 행 존재 | AC-2 |
| TC-03 | `SELECT CURRENT_WAREHOUSE();` | MOVING_INTEL_WH | AC-3 |
| TC-04 | `USE SCHEMA MOVING_INTEL.ANALYTICS; SELECT CURRENT_DATABASE(), CURRENT_SCHEMA();` | MOVING_INTEL, ANALYTICS | AC-1,2 보강 |
| TC-05 | `SELECT COUNT(*) FROM KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2.REGION_APT_RICHGO_MARKET_PRICE_M_H LIMIT 1;` | 1 이상 | Marketplace 크로스 접근 |
| TC-06 | `SELECT COUNT(*) FROM SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA.FLOATING_POPULATION_INFO LIMIT 1;` | 1 이상 | Marketplace 크로스 접근 |

> TC-05, TC-06은 AC 외 추가 검증이다. MOVING_INTEL.ANALYTICS 컨텍스트에서 Marketplace DB를 크로스 쿼리할 수 있는지 확인한다. 이것이 후속 이슈(뷰 생성)의 전제 조건이다.

---

### Step 4: 결과 기록

| 기록 대상 | 파일 | 내용 |
|----------|------|------|
| AC 체크 업데이트 | `docs/work/active/000016-db-schema/00_issue.md` | AC 3개 체크 표시, 작업 내역에 실행 결과 추가 |
| SQL 스크립트 | `sql/ddl/001_create_database_schema.sql` | DDL 스크립트 (파일 신규 생성) |
| 테스트 쿼리 | `sql/test/test_01_db_schema.sql` | 검증 쿼리 (파일 신규 생성) |
| 디렉토리 메타 | `sql/.ai.md` | SQL 디렉토리 설명 (파일 신규 생성) |
| 레포 구조 | `AGENTS.md` | `sql/` 디렉토리 추가 반영 |

---

## 생성/수정 파일 목록

| 파일 경로 | 역할 | 작업 |
|----------|------|------|
| `sql/.ai.md` | SQL 디렉토리 메타 문서 | 신규 생성 |
| `sql/ddl/001_create_database_schema.sql` | DB/스키마 DDL | 신규 생성 |
| `sql/test/test_01_db_schema.sql` | AC 검증 쿼리 | 신규 생성 |
| `docs/work/active/000016-db-schema/00_issue.md` | AC 체크 업데이트 | 수정 |
| `docs/work/active/000016-db-schema/01_plan.md` | 구현 계획 (이 파일) | 수정 |
| `AGENTS.md` | 레포 구조에 sql/ 추가 | 수정 |

---

## 엣지케이스 & 롤백

### 엣지케이스

| 상황 | 대응 |
|------|------|
| DB가 이미 존재 | `IF NOT EXISTS`로 멱등 처리 → 에러 없이 통과 |
| 스키마가 이미 존재 | `IF NOT EXISTS`로 멱등 처리 → 에러 없이 통과 |
| 웨어하우스 미존재 | P-01에서 감지 → DDL 실행 전 사용자에게 보고, WH 생성 필요 |
| 권한 부족 (ACCOUNTADMIN 아님) | P-02에서 감지 → `USE ROLE ACCOUNTADMIN;` 시도 또는 사용자에게 보고 |
| Marketplace DB 접근 불가 | P-03/P-04에서 감지 → 구독 상태 재확인 필요 (Snowsight에서 수동 확인) |
| MCP 연결 실패 | SQL 실행 불가 → MCP 설정 재확인 (`~/.claude/mcp.json`) |
| 네트워크 문제 | MCP 타임아웃 → 재시도, 지속 시 사용자에게 보고 |

### 롤백

실패 시 역순 삭제:

```sql
-- 롤백 Step 1: 스키마 삭제
DROP SCHEMA IF EXISTS MOVING_INTEL.ANALYTICS;

-- 롤백 Step 2: 데이터베이스 삭제
DROP DATABASE IF EXISTS MOVING_INTEL;
```

> **주의:** `DROP DATABASE`는 해당 DB 내 모든 객체를 삭제한다. 이 이슈에서는 DB/스키마 외 다른 객체가 없으므로 안전. 후속 이슈에서 뷰가 생성된 이후에는 롤백 시 주의 필요.

---

## 아키텍처 노트

### 1. 권한 모델

**결정: ACCOUNTADMIN으로 충분. 전용 Role은 이 이슈에서 생성하지 않는다.**

- 해커톤 프로젝트(1인 개발, 6일 마감)에서 RBAC를 세분화하는 것은 일론머스크 원칙 #2(불필요한 부분 삭제)에 위배된다.
- Trial 계정에서 ACCOUNTADMIN은 모든 권한을 가지므로 추가 GRANT 불필요.
- 후속에 역할 분리가 필요해지면 별도 이슈로 처리한다.

### 2. 네이밍 컨벤션

| 객체 | 이름 | 근거 |
|------|------|------|
| Database | `MOVING_INTEL` | dev_spec 전체에서 사용. 프로젝트명 약어 |
| Schema | `ANALYTICS` | dev_spec A2-3에서 모든 뷰(10개)가 `MOVING_INTEL.ANALYTICS.*`으로 정의됨 |
| Warehouse | `MOVING_INTEL_WH` | 이미 생성됨. Snowflake 관례(`_WH` 접미사) 준수 |

> 후속 이슈에서 생성할 뷰 10개, UDF 3개, 테이블 5개 모두 `MOVING_INTEL.ANALYTICS` 스키마 내에 위치한다. 이 네이밍은 dev_spec 전체와 일관성이 있다.

### 3. 디렉토리 구조

```
sql/
├── .ai.md                              ← SQL 디렉토리 목적/구조 설명
├── ddl/
│   └── 001_create_database_schema.sql  ← DDL 스크립트 (이슈 #16)
└── test/
    └── test_01_db_schema.sql           ← 검증 쿼리 (이슈 #16)
```

- `ddl/` — DDL 스크립트. 번호 prefix(`001_`, `002_`, ...)로 실행 순서 보장.
- `test/` — 검증/테스트 쿼리. `test_NN_*.sql` 패턴.
- 후속 이슈에서 `sql/views/`, `sql/udf/` 등 하위 디렉토리가 추가될 수 있다.

### 4. 멱등성

- `CREATE DATABASE IF NOT EXISTS`와 `CREATE SCHEMA IF NOT EXISTS`를 사용한다.
- 반복 실행해도 에러가 발생하지 않으며 기존 객체를 덮어쓰지 않는다.
- 이것은 MCP를 통한 수동 실행 환경에서 특히 중요하다 (실행 중 연결 끊김 후 재시도 가능).

### 5. 웨어하우스 설정

| 설정 | 값 | 적합성 |
|------|-----|--------|
| Size | X-Small | 해커톤 규모 데이터(수십만~수백만 행)에 충분. 비용 최소화 |
| Auto-suspend | 60초 | Trial $400 크레딧 절약. 유휴 시 즉시 정지 |
| Auto-resume | ON | SQL 실행 시 자동 재시작 |
| Scaling Policy | Standard (1 cluster) | 1인 개발, 동시 쿼리 없음 |

> 웨어하우스는 이미 생성되어 있으므로 이 이슈에서는 설정 변경 없이 접근 확인만 한다.

### 6. 후속 이슈 연계

이 이슈(#16)는 **모든 후속 이슈의 기반**이다.

| 후속 작업 | 의존 객체 | 확인 포인트 |
|----------|----------|------------|
| 뷰 10개 생성 (#17~) | `MOVING_INTEL.ANALYTICS` 스키마 | `USE SCHEMA MOVING_INTEL.ANALYTICS;` 정상 동작 |
| Marketplace 데이터 → 뷰 | `MOVING_INTEL_WH` + 크로스 DB 쿼리 | TC-05, TC-06으로 크로스 접근 확인 |
| Snowpark 파이프라인 | `MOVING_INTEL.ANALYTICS` 스키마 | `INTEGRATED_MART` 테이블이 이 스키마에 생성됨 |
| UDF/Cortex AI | `MOVING_INTEL.ANALYTICS` 스키마 + WH | 동일 스키마 내 배포 |

### 7. Marketplace DB 접근 검증

4종 Marketplace DB는 Snowflake 공유 데이터베이스(Shared Database)로 마운트되어 있다. `MOVING_INTEL.ANALYTICS` 컨텍스트에서 이 DB들에 크로스 쿼리가 가능한지 TC-05, TC-06으로 확인한다. RICHGO와 SPH를 대표로 검증하며, 아정당과 NextTrade는 뷰 생성 이슈에서 검증한다.

---

## 실행 요약

1. **사전 점검** (P-01~P-05) → 환경 정상 확인
2. **DDL 실행** → `sql/ddl/001_create_database_schema.sql` 내용을 MCP로 단계 실행
3. **검증** → TC-01~TC-06 실행, AC 3/3 체크
4. **파일 정리** → SQL 파일 생성, .ai.md 작성, 00_issue.md AC 업데이트
5. **커밋** → 사용자 확인 후 커밋
