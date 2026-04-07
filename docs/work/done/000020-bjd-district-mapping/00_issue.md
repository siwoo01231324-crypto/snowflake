# feat: BJD↔DISTRICT 매핑 뷰 생성

## 목적
RICHGO(법정동코드 BJD_CODE)와 SPH(행정동코드 DISTRICT_CODE) 두 데이터를 연결하는 다리를 놓는다.

## 완료 기준
- [x] `V_BJD_DISTRICT_MAP` 매핑 뷰 생성
- [x] RICHGO BJD_CODE → SPH CITY_CODE 매핑 커버리지 80% 이상 (100% — 동 26개 + 구 fallback 3개 = 29/29)
- [x] 매핑 뷰를 통한 RICHGO↔SPH JOIN 테스트 통과

## 테스트 코드 (TDD — 먼저 작성)

```sql
-- test_05_bjd_mapping.sql
-- TC-01: 매핑 뷰 존재
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP;
-- EXPECTED: cnt > 0

-- TC-02: 매핑 커버리지 확인 (RICHGO BJD_CODE 중 매핑 성공 비율)
SELECT 
    COUNT(DISTINCT r.BJD_CODE) AS total_bjd,
    COUNT(DISTINCT m.BJD_CODE) AS mapped_bjd,
    ROUND(COUNT(DISTINCT m.BJD_CODE) / COUNT(DISTINCT r.BJD_CODE) * 100, 1) AS coverage_pct
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
LEFT JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m ON STARTSWITH(r.BJD_CODE, m.BJD_CODE_PREFIX);
-- EXPECTED: coverage_pct >= 80

-- TC-03: JOIN 결과 확인 (RICHGO 시세 + SPH 행정구역)
SELECT r.SGG, r.EMD, r.MEME_PRICE_PER_SUPPLY_PYEONG, s.CITY_KOR_NAME
FROM MOVING_INTEL.ANALYTICS.V_RICHGO_MARKET_PRICE r
JOIN MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP m ON STARTSWITH(r.BJD_CODE, m.BJD_CODE_PREFIX)
JOIN MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER s ON m.CITY_CODE = s.CITY_CODE
LIMIT 5;
-- EXPECTED: 4개 컬럼 모두 값 존재, NULL 없음

-- TC-04: 매핑 키 유니크 확인
SELECT BJD_CODE_PREFIX, COUNT(*) AS cnt 
FROM MOVING_INTEL.ANALYTICS.V_BJD_DISTRICT_MAP 
GROUP BY 1 HAVING cnt > 1;
-- EXPECTED: 0 rows (중복 없음)
```

## 참조
- `docs/specs/dev_spec.md` A1-1 (조인 전략), A2-3 (V_BJD_DISTRICT_MAP SQL)
- RICHGO BJD_CODE(10자리) ↔ SPH DISTRICT_CODE(8자리) 매핑
- 의존성: #17 (RICHGO 뷰), #18 (SPH 뷰)

## 불변식
- BJD_CODE(법정동코드)와 DISTRICT_CODE(행정동코드)는 체계가 다름 — 접두사 매핑 or SGG 텍스트 매핑
- 매핑 실패 시 해당 지역 데이터 JOIN 불가 → 커버리지 80% 이상 필수

## 작업 내역

### 2026-04-07
- `/remind-issue` 실행 — AC 0/3 완료, 구현 대기 상태
- work 폴더(00_issue.md, 01_plan.md) 생성됨
- Snowflake MCP 연결 실패로 뷰 존재 여부 미확인
- 다음 단계: Snowflake 연결 복구 후 `/plan` 실행 → 구현 시작
- `sql/views/004_bjd_mapping.sql` 생성 (worker-1)
- `sql/test/test_05_bjd_mapping.sql`, `sql/validation/validate_05_bjd.sql` 생성 (worker-2)
- `V_BJD_DISTRICT_MAP` 뷰 Snowflake에 생성 완료 (worker-3)
  - SD 필터 버그 수정: `'서울특별시'` → `'서울'`
  - TC-01~TC-04 전부 PASS
  - 커버리지 89.7% (동 단위 26/29)
  - 구 단위 fallback 추가 (UNION ALL) → 100% 커버리지 달성 (29/29)
  - MATCH_LEVEL 컬럼 추가: DONG(동 단위) / GU(구 단위 fallback)
  - dev_spec A1-2 변경 이력 및 SQL 업데이트 완료
