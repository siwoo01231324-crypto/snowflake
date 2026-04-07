# feat: SPH 참조 뷰 4개 생성 (유동인구/카드매출/자산소득/행정구역)

## 목적
유동인구/카드매출/자산소득/행정구역(지도 경계) 데이터를 우리 스키마에서 접근 가능하게 한다.

## 완료 기준
- [ ] `V_SPH_FLOATING_POP` 뷰 생성
- [ ] `V_SPH_CARD_SALES` 뷰 생성
- [ ] `V_SPH_ASSET_INCOME` 뷰 생성
- [ ] `V_SPH_REGION_MASTER` 뷰 생성 (M_SCCO_MST, DISTRICT_GEOM 포함)
- [ ] 서울 25개 구, 467개 동 전체 커버 확인

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`sql
-- test_03_sph_views.sql
-- TC-01: 유동인구 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP;
-- EXPECTED: cnt = 2577120

-- TC-02: 카드매출 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_CARD_SALES;
-- EXPECTED: cnt = 6208957

-- TC-03: 자산소득 row count
SELECT COUNT(*) AS cnt FROM MOVING_INTEL.ANALYTICS.V_SPH_ASSET_INCOME;
-- EXPECTED: cnt = 269159

-- TC-04: 행정구역 마스터 — 25개 구 확인
SELECT COUNT(DISTINCT CITY_CODE) AS gu_count, COUNT(*) AS dong_count 
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER;
-- EXPECTED: gu_count = 25, dong_count = 467

-- TC-05: DISTRICT_GEOM NOT NULL 확인
SELECT COUNT(*) AS null_geom 
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER 
WHERE DISTRICT_GEOM IS NULL;
-- EXPECTED: null_geom = 0

-- TC-06: GeoJSON 추출 가능 확인
SELECT ST_ASGEOJSON(DISTRICT_GEOM) AS geojson 
FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER LIMIT 1;
-- EXPECTED: 유효한 GeoJSON 문자열 반환

-- TC-07: 날짜 범위 확인
SELECT MIN(STANDARD_YEAR_MONTH) AS min_ym, MAX(STANDARD_YEAR_MONTH) AS max_ym 
FROM MOVING_INTEL.ANALYTICS.V_SPH_FLOATING_POP;
-- EXPECTED: min_ym = '202101', max_ym = '202512'
\`\`\`

## 참조
- `docs/specs/dev_spec.md` A1-3~A1-5 (SPH 스키마), A2-3 (뷰 생성 SQL)
- 원본: `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA`
- 의존성: #이슈1 (DB/스키마)

## 불변식
- SPH는 서울 전체 25개 구 467개 동 커버 ("3개 구" 아님)
- 조인 키: PROVINCE_CODE(2) + CITY_CODE(5) + DISTRICT_CODE(8)
- DISTRICT_GEOM은 GEOGRAPHY 타입 — 별도 GeoJSON 파일 불필요
## 작업 내역
- [x] sql/test/test_03_sph_views.sql 생성 (TC-01~TC-07)
- [x] sql/views/003_sph_views.sql 생성 (V_SPH_FLOATING_POP, V_SPH_CARD_SALES, V_SPH_ASSET_INCOME, V_SPH_REGION_MASTER)
- [x] sql/views/.ai.md 생성
- [x] sql/test/.ai.md 최신화
- [x] sql/.ai.md 최신화
