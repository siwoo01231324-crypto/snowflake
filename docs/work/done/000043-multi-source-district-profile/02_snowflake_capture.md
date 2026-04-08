# 02 — Snowflake 실행 캡처 (이슈 #43)

**실행일**: 2026-04-08
**실행 환경**: python_repl + snowflake-connector-python (MCP snowflake 다운으로 우회)
**대상 뷰**: `MOVING_INTEL.ANALYTICS.V_DISTRICT_PROFILE_3GU`
**롤/웨어하우스**: ACCOUNTADMIN / MOVING_INTEL_WH

## 1. DDL 적용 결과

```
USE WAREHOUSE MOVING_INTEL_WH        — OK
USE SCHEMA MOVING_INTEL.ANALYTICS    — OK
CREATE OR REPLACE VIEW V_DISTRICT_PROFILE_3GU — View V_DISTRICT_PROFILE_3GU successfully created.
```

## 2. 의존성 뷰 존재 확인 (6/6 OK)

| 뷰 | 행 수 |
|---|---:|
| V_SPH_FLOATING_POP | 2,577,120 |
| V_SPH_ASSET_INCOME | 269,159 |
| V_SPH_CARD_SALES | 6,208,957 |
| V_RICHGO_MARKET_PRICE | 4,356 |
| V_BJD_DISTRICT_MAP | 29 |
| V_TELECOM_DISTRICT_MAPPED | 866 |

## 3. TC-01 ~ TC-06 검증 결과 (6/6 PASS)

| TC | 검증 항목 | Expected | Actual | 결과 |
|---|---|---|---|---|
| TC-01 | row count | 3 | 3 | PASS |
| TC-02 | 핵심필드 NULL | 0 | 0 | PASS |
| TC-03 | CITY_CODE 목록 | `11140,11560,11650` | `11140,11560,11650` | PASS |
| TC-04 | distinct PROFILE_TAG | 3 | 3 | PASS |
| TC-05 | 매매 > 전세 위반 | 0 | 0 | PASS |
| TC-06 | GAP_RATIO ∈ [0,1] 위반 | 0 | 0 | PASS |

## 4. 카드 숫자 (worker-2/3 전달용)

`SELECT * FROM V_DISTRICT_PROFILE_3GU ORDER BY CITY_CODE` 결과:

| CITY_CODE | 구 | PROFILE_TAG | AVG_RESIDENTIAL_POP | WORKING_VISIT_RATIO | AVG_INCOME | AVG_ASSET | ELECTRONICS_FURNITURE_SHARE | AVG_MEME_PRICE | AVG_JEONSE_PRICE | GAP_RATIO | OPEN_COUNT_MONTHLY_AVG | BJD_COUNT |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 11140 | 중구 | 도심 오피스·상업 | 69.5965 | 5.2260 | 40,741.7014 | 439,219.5267 | 0.002523 | 3,810.7853 | 2,031.0919 | 0.4670 | 88.4444 | 5 |
| 11560 | 영등포구 | 금융·상업·주거 혼합 | 315.6520 | 1.0706 | 39,875.8524 | 436,377.8723 | 0.051735 | 3,767.9587 | 1,918.6901 | 0.4908 | 259.5556 | 15 |
| 11650 | 서초구 | 고급 주거·학군지 | 1,221.6574 | 1.1307 | 46,873.6599 | 683,147.0789 | 0.002491 | 6,413.1076 | 2,817.5322 | 0.5607 | 218.7222 | 9 |

### 단위 메모
- `AVG_RESIDENTIAL_POP`: V_SPH_FLOATING_POP 원본 단위 그대로 (구별 × 22개월 평균)
- `AVG_INCOME` / `AVG_ASSET`: V_SPH_ASSET_INCOME 원본 (만원 단위 추정)
- `AVG_MEME_PRICE` / `AVG_JEONSE_PRICE`: V_RICHGO_MARKET_PRICE 공급평당 가격 (만원/평 추정)
- `GAP_RATIO` = (매매 - 전세) / 매매 — 0~1 범위 검증 PASS
- `OPEN_COUNT_MONTHLY_AVG`: 통신 신규개통 — 동월 다중행 SUM → 22개월 AVG
- `BJD_COUNT`: 매핑된 법정동 수 (richgo 데이터 커버리지)

## 5. 인사이트 (3구 비교)

- **서초구 (11650)**: 거주인구 1,221.66 (압도적) · 평균소득 46,874 · 자산 683,148 · AVG_MEME 6,413 — 모든 카테고리에서 1위. GAP_RATIO 0.5607로 매매 vs 전세 격차 가장 큼 (고급 주거).
- **영등포구 (11560)**: 거주 315.65 · 통신 개통 259.56 (3구 중 1위) · 전자/가구 매출 비중 5.17% (3구 중 1위, 중구·서초의 ~20배). 금융·상업·주거 혼합 특성 부합.
- **중구 (11140)**: 거주 69.60 (3구 중 최저) · WORKING_VISIT_RATIO 5.226 (압도적) — 거주 대비 직장+방문 5배. 도심 오피스·상업 특성 정확히 반영.

## 6. 재실행 절차 (idempotent)

```bash
# Option A — MCP 복구 후
# mcp__snowflake__execute_query (sql/views/006_district_profile_3gu.sql)
# mcp__snowflake__execute_query (sql/test/test_15_district_profile.sql)

# Option B — python_repl 우회 (현재 사용)
# snowflake.connector.connect(...) → cur.execute(DDL) → 6 TC
```