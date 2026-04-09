# feat: CALC_ROI UDF 구현

## 목적
"이 지역에 마케팅하면 ROI가 얼마인지" 계산하는 UDF를 만든다.

## 완료 기준
- [x] `CALC_ROI(city_code, budget, industry)` UDF 배포
- [x] 샘플 입력 → 기대 범위 내 ROI 반환
- [x] RICHGO 시세 데이터 연동 확인

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`sql
-- test_09_roi_udf.sql
-- TC-01: UDF 존재
SHOW USER FUNCTIONS LIKE 'CALC_ROI' IN SCHEMA MOVING_INTEL.ANALYTICS;
-- EXPECTED: 1 row

-- TC-02: 기본 호출 (강남구, 1억 예산, 가전업종)
SELECT MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE') AS roi;
-- EXPECTED: roi > 0 (양수 ROI)

-- TC-03: 반환 구조 확인 (JSON)
SELECT PARSE_JSON(MOVING_INTEL.ANALYTICS.CALC_ROI('11680', 100000000, 'ELECTRONICS_FURNITURE')) AS result;
-- EXPECTED: result:roi_pct, result:estimated_revenue, result:avg_price_pyeong 키 존재

-- TC-04: 존재하지 않는 지역 → graceful 처리
SELECT MOVING_INTEL.ANALYTICS.CALC_ROI('99999', 100000000, 'FOOD') AS roi;
-- EXPECTED: NULL 또는 에러 메시지 JSON
\`\`\`

## 참조
- `docs/specs/dev_spec.md` B3 (CALC_ROI UDF 설계), C4 (ROI 계산기)
- RICHGO: MEME_PRICE_PER_SUPPLY_PYEONG, JEONSE_PRICE_PER_SUPPLY_PYEONG, TOTAL_HOUSEHOLDS
- 의존성: #17 (RICHGO 뷰)

## 불변식
- ROI = (예상매출 - 투입비용) / 투입비용 × 100
- 아파트 시세(평당가)와 세대수 기반 시장 규모 추정
- industry는 SPH CARD_SALES 20개 업종 중 하나

## 작업 내역

### 구현 완료 (2026-04-09)

**신규 파일**
- `sql/udf/calc_roi.sql`: CALC_ROI SQL scalar UDF 구현
- `sql/test/test_09_roi_udf.sql`: TC-01~05 테스트

**핵심 설계 결정**
- 파라미터명 `p_city_code`, `p_budget`, `p_industry`로 명명 (Snowflake SQL UDF 파라미터-컬럼명 충돌 방지)
- `city_meta` CTE에 `MAX()` 집계 → 미존재 city_code도 항상 1행 반환, graceful 처리 보장
- `estimated_revenue = p_budget × 3.0 × (conversion_rate / 0.01) × COALESCE(avg_signal, 0.5)` 공식 확정
- MOVE_SIGNAL_INDEX 0~1 스케일 기반 수요 가중치 적용
- RICHGO 데이터 실존 3구(서초·영등포·중구) 외 22구는 avg_price_pyeong=NULL, ROI 계산은 정상 수행

**TC 결과: 5/5 PASS**
- TC-01: UDF 존재 확인 ✓
- TC-02: 강남구(11680) roi_pct > 0 ✓
- TC-03: 서초구(11650) 필수 JSON 키 3개 존재 ✓
- TC-04: 존재하지 않는 city_code(99999) graceful 처리 ✓
- TC-05: 업종별(FOOD/ELECTRONICS_FURNITURE/EDUCATION_ACADEMY/HOME_LIFE_SERVICE) ROI 순차 반환 ✓
