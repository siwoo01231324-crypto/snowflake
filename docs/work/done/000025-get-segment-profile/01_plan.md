# 01_plan — feat: GET_SEGMENT_PROFILE UDF 구현

## AC 체크리스트

- [x] `GET_SEGMENT_PROFILE(city_code)` UDF 배포 (5자리 CITY_CODE)
- [x] 반환 JSON에 필수 키(population, income, consumption, housing) 포함
- [x] 25개 구 전체 호출 가능
- [x] MULTI_SOURCE 3구(중구 11140·영등포구 11560·서초구 11650) → 풀 프로필 4섹션 반환
- [x] TELECOM_ONLY 22구 → telecom_summary 경량 프로필만 반환

## 구현 계획

1. `sql/udf/get_segment_profile.sql` 작성 (Dual-Tier 분기 로직)
2. `sql/test/test_10_segment_udf.sql` 테스트 작성 (TC-01~04)
3. Snowflake 배포 및 25개 구 검증
