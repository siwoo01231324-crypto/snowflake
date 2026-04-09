# 01_plan.md — Issue #28: Streamlit 히트맵 탭 구현

## 목표
서울 25구 이사 수요를 pydeck GeoJsonLayer choropleth으로 시각화하는 Streamlit 앱 구현.

## 구현 범위
1. `src/app/app.py` — 3탭 스켈레톤 (히트맵 / 세그먼트 / Cortex AI)
2. `src/app/tabs/__init__.py` — 패키지 초기화
3. `src/app/tabs/heatmap.py` — 히트맵 탭 렌더러
4. `tests/test_13_heatmap.py` — TDD 테스트 (syntax check + 구조 검증)
5. `src/app/.ai.md` 최신화

## 설계 결정
- **데이터**: `V_SPH_REGION_MASTER.DISTRICT_GEOM` → `ST_ASGEOJSON()` (별도 GeoJSON 파일 금지)
- **렌더링**: pydeck `GeoJsonLayer` (Streamlit in Snowflake GA)
- **연결**: `get_active_session()` (Streamlit in Snowflake 내장 세션)
- **필터**: 연월(selectbox) + 시그널 유형(CONTRACT_COUNT / OPEN_COUNT)
- **UDF 연동**: `PREDICT_MOVE_DEMAND(city_code, YYYYMM)` 버튼 실행
- **Dual-Tier 배지**: MULTI_SOURCE(중구·영등포구·서초구) vs TELECOM_ONLY(22구) 범례

## 불변식
- Snowflake 연결 정보 하드코딩 금지 → get_active_session() 사용
- 실데이터 샘플 코드 포함 금지
- 외부 네트워크 접근 금지 (Streamlit in Snowflake 환경)
- f-string SQL 금지 → params 바인딩 사용 (단, 컬럼명은 allowlist 검증 후 포맷팅)

## 실행 순서
1. [x] 컨텍스트 파악 (00_issue.md, .ai.md, cortex.py)
2. [x] 01_plan.md 작성
3. [x] TDD 테스트 작성 (test_13_heatmap.py)
4. [x] app.py, tabs/__init__.py, tabs/heatmap.py 구현
5. [x] 테스트 실행 (syntax check) — 7/7 PASS
6. [x] local_run.py 로컬 개발 진입점 구현 (snowflake.connector 기반 Session 래퍼)
7. [x] segment_roi.py 구현 — 이사 수요 × ROI 산점도 + 세그먼트 프로파일 탭
8. [x] 로컬 실행 버그 수정 (2026-04-09)
9. [x] .ai.md 최신화

## Snowflake 실측 결과 (2026-04-09)

| 검증 항목 | 결과 |
|-----------|------|
| app.py 존재 | PASS |
| heatmap.py 존재 | PASS |
| tabs/__init__.py 존재 | PASS |
| tests/test_13_heatmap.py 존재 | PASS |
| ST_ASGEOJSON(DISTRICT_GEOM) 실행 (3행, NULL없음) | PASS |
| V_SPH_REGION_MASTER 서울 25구 확인 | PASS (count=25) |
| V_TELECOM_DISTRICT_MAPPED 월별 필터 (202412) | PASS (1 row) |
| PREDICT_MOVE_DEMAND UDF 존재 | PASS |

## 로컬 실행 버그 수정 내역 (2026-04-09)

### heatmap.py
- `V_SPH_REGION_MASTER`에 `DISTRICT_KOR_NAME`, `DISTRICT_GEOM` 컬럼 미존재 확인
  - `DISTRICT_KOR_NAME` SELECT에서 제거 (툴팁 dong 필드 `row.get()` fallback 처리)
  - `FROM` 절을 `V_SPH_REGION_MASTER` → `M_SCCO_MST` (원본 마켓플레이스 테이블) 직접 참조로 변경
  - **원인**: 뷰가 DISTRICT_GEOM 없이 배포됐거나 VIEW DDL이 실제 Snowflake에 미반영된 상태

### segment_roi.py
- **기준 연월 선택기 상단 이동**: 업종·예산 필터보다 앞에 3열 배치 (기준연월 | 업종 | 예산)
- **단일 월 필터 적용**: `AVG(6개월)` → `SUM(선택월)` + `TO_CHAR(YEAR_MONTH, 'YYYYMM') = ?`
- **미래 월 필터**: `ym_options`를 현재 월(YYYYMM ≤ 오늘) 이하로 제한 → 데이터 없는 미래 월 선택 방지
- **datetime.date 타입 처리**: Snowflake에서 YEAR_MONTH가 `datetime.date` 반환 → `strftime("%Y%m")` 변환
- **하단 개별 구 분석**: 기준연월 중복 선택기 제거, 상단 `global_ym` 공유
- **UDF 의존**: 개별 구 상세 ROI(`CALC_ROI`) 및 프로파일(`GET_SEGMENT_PROFILE`)은 이슈 #24, #25 머지 후 활성화
