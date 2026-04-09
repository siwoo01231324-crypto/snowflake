# 01_plan — feat: CALC_ROI UDF 구현

## AC 체크리스트

- [x] `CALC_ROI(city_code, budget, industry)` UDF 배포
- [x] 샘플 입력 → 기대 범위 내 ROI 반환
- [x] RICHGO 시세 데이터 연동 확인

## 구현 계획

1. `sql/udf/calc_roi.sql` 작성 (RICHGO 시세 + SPH CARD_SALES 연동)
2. `sql/test/test_09_roi_udf.sql` 테스트 작성 (TC-01~04)
3. Snowflake 배포 및 검증
