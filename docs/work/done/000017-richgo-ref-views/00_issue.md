# feat: RICHGO 참조 뷰 3개 생성 (아파트시세 + 인구)

## 목적
아파트 시세+인구 Marketplace 데이터를 우리 스키마(MOVING_INTEL.ANALYTICS)에서 접근 가능하게 한다.

## 완료 기준
- [x] `V_RICHGO_MARKET_PRICE` 뷰 생성 (아파트 시세)
- [x] `V_RICHGO_POPULATION` 뷰 생성 (성별/연령 인구)
- [x] `V_RICHGO_YOUNG_CHILDREN` 뷰 생성 (영유아 비율)
- [x] 각 뷰의 row count가 원본과 일치

## 테스트 코드 (TDD — 먼저 작성)

```sql
-- test_02_richgo_views.sql
-- TC-01: 시세 뷰 존재 + row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE;
-- EXPECTED: cnt = 4356

-- TC-02: 시세 뷰 필수 컬럼 확인
SELECT REGION_LEVEL, BJD_CODE, SD, SGG, EMD, YYYYMMDD,
       TOTAL_HOUSEHOLDS, MEME_PRICE_PER_SUPPLY_PYEONG, JEONSE_PRICE_PER_SUPPLY_PYEONG
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE LIMIT 1;
-- EXPECTED: 9개 컬럼 모두 존재, 에러 없음

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

## 참조
- `docs/specs/dev_spec.md` A1-2 (RICHGO 스키마), A2-3 (뷰 생성 SQL)
- 원본: `KOREAN_POPULATION__APARTMENT_MARKET_PRICE_DATA.HACKATHON_2025Q2`
- 의존성: #이슈1 (DB/스키마)

## 불변식
- 뷰는 데이터 복사 없이 원본 Marketplace DB를 직접 참조 (SELECT * FROM)
- BJD_CODE는 법정동코드 10자리, YYYYMMDD는 DATE 타입

## 작업 내역
- **2026-04-07** — 세션 시작. AC 0/4 미완료. 구현 대기 상태. 01_plan.md 구현 계획 미작성 → /plan 실행 필요.
- **2026-04-07** — team-exec: SQL 파일 3개 생성 완료 (002_richgo_views.sql, test_02_richgo_views.sql, validate_02_richgo.sql). .ai.md 3개 생성/업데이트. code-reviewer 검증 대기.
- **2026-04-07** — /ri 세션 재시작. AC 0/4 미완료. DDL·테스트·검증 SQL 파일 모두 작성 완료 (미커밋). Snowflake 실행 + TC 검증 필요.
- **2026-04-07** — /team 3 실행. DDL 정확성 검증 PASS, 인접 이슈(#16~#21) 호환성 감사 PASS, 종합 코드 리뷰 APPROVE(조건부). MAJOR 2건 수정: M1(V_RICHGO_YOUNG_FAMILY→V_RICHGO_YOUNG_CHILDREN 명칭 통일), M2(TC-02 REGION_LEVEL 컬럼 추가). Snowflake DDL 실행 + TC 검증 대기.
- **2026-04-07** — Snowflake MCP 연결 수정(uvx→npx snowflake-mcp). Python connector로 DDL 실행 완료. TC 7/7 전부 PASS (row count, 컬럼, 날짜범위 모두 일치). TC-06 주석 오타 수정(14→15개 컬럼). AC 4/4 완료. /fi 실행.
