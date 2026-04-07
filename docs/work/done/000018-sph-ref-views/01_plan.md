# 구현 계획: SPH 참조 뷰 4개 생성

## AC 체크리스트
- [x] V_SPH_FLOATING_POP 뷰 생성
- [x] V_SPH_CARD_SALES 뷰 생성
- [x] V_SPH_ASSET_INCOME 뷰 생성
- [x] V_SPH_REGION_MASTER 뷰 생성 (M_SCCO_MST, DISTRICT_GEOM 포함)
- [ ] 서울 25개 구, 467개 동 전체 커버 확인 → Snowflake 실행 후 검증 필요

## 구현 계획
1. TDD Red: `sql/test/test_03_sph_views.sql` 작성 (TC-01~TC-07)
2. TDD Green: `sql/views/003_sph_views.sql` 작성 (4개 뷰)
3. `.ai.md` 최신화 (sql/, sql/views/, sql/test/)
4. Snowflake에서 테스트 실행 → Red→Green 확인
5. 커밋

## 작업 내역

### 2026-04-07

#### 1. TDD Red — 테스트 쿼리 작성
- 파일: `sql/test/test_03_sph_views.sql`
- TC-01: V_SPH_FLOATING_POP row count = 2,577,120
- TC-02: V_SPH_CARD_SALES row count = 6,208,957
- TC-03: V_SPH_ASSET_INCOME row count = 269,159
- TC-04: V_SPH_REGION_MASTER 25개 구, 467개 동
- TC-05: DISTRICT_GEOM NOT NULL 확인
- TC-06: ST_ASGEOJSON() GeoJSON 추출 가능 확인
- TC-07: STANDARD_YEAR_MONTH 날짜 범위 (202101~202512)

#### 2. TDD Green — 뷰 SQL 작성
- 파일: `sql/views/003_sph_views.sql`
- 원본 DB: `SEOUL_DISTRICTLEVEL_DATA_FLOATING_POPULATION_CONSUMPTION_AND_ASSETS.GRANDATA`
- 기존 패턴 참조: `002_richgo_views.sql` (#17)

| 뷰 이름 | 원본 테이블 | 주요 컬럼 | 건수 |
|---------|------------|----------|------|
| V_SPH_FLOATING_POP | FLOATING_POPULATION_INFO | PROVINCE/CITY/DISTRICT_CODE, STANDARD_YEAR_MONTH, RESIDENTIAL/WORKING/VISITING_POPULATION | 2,577,120 |
| V_SPH_CARD_SALES | CARD_SALES_INFO | 위 + CARD_TYPE, LIFESTYLE, 업종별 매출 19개 중 6개 + TOTAL | 6,208,957 |
| V_SPH_ASSET_INCOME | ASSET_INCOME_INFO | 위 + AVERAGE/MEDIAN_INCOME, AVERAGE_ASSET_AMOUNT, 주택보유 | 269,159 |
| V_SPH_REGION_MASTER | M_SCCO_MST | PROVINCE/CITY/DISTRICT_CODE, *_KOR_NAME, *_ENG_NAME, DISTRICT_GEOM(GEOGRAPHY) | 467 |

- 모든 뷰: `CREATE OR REPLACE VIEW` + `COMMENT` — 멱등성 보장
- 컨텍스트 설정: `USE WAREHOUSE MOVING_INTEL_WH; USE SCHEMA MOVING_INTEL.ANALYTICS;`

#### 3. .ai.md 최신화
- `sql/.ai.md` — views/ 디렉토리 설명 추가
- `sql/views/.ai.md` — 신규 생성 (003_sph_views.sql 항목, 불변식)
- `sql/test/.ai.md` — test_03_sph_views.sql 항목 추가

#### 4. 미완료 항목
- [ ] Snowflake 실행: `003_sph_views.sql` → `test_03_sph_views.sql` 순서로 실행하여 Red→Green 확인
- [ ] 25개 구 467개 동 커버리지 실데이터 검증
