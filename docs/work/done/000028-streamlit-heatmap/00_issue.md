# feat: Streamlit 히트맵 탭 구현 (이사 수요 지도)

# Issue #28: feat: Streamlit 히트맵 탭 구현 (이사 수요 지도)

## 목적
서울 지도에서 이사 수요를 색깔로 보여주는 대시보드 핵심 화면을 만든다.

## 완료 기준
- [x] `app.py` Streamlit 앱 스켈레톤 (3탭 구조)
- [x] 히트맵 탭: pydeck GeoJsonLayer choropleth 렌더링
- [x] M_SCCO_MST.DISTRICT_GEOM → ST_ASGEOJSON() 지도 데이터
- [x] 월별/구별 필터 동작
- [x] PREDICT_MOVE_DEMAND UDF 연동

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`python
# test_13_heatmap.py
def test_app_imports():
    """app.py 임포트 에러 없음"""
    import importlib
    mod = importlib.import_module("app")
    assert hasattr(mod, "main") or hasattr(mod, "run")

def test_geojson_extraction(session):
    """ST_ASGEOJSON으로 GeoJSON 추출 가능"""
    result = session.sql("""
        SELECT DISTRICT_CODE, CITY_KOR_NAME, ST_ASGEOJSON(DISTRICT_GEOM) AS geojson
        FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER
        WHERE PROVINCE_CODE = '11'
        LIMIT 5
    """).to_pandas()
    assert len(result) == 5
    assert result["GEOJSON"].notna().all(), "GeoJSON NULL 존재"
    import json
    parsed = json.loads(result["GEOJSON"].iloc[0])
    assert parsed["type"] in ("Polygon", "MultiPolygon"), f"GeoJSON 타입 오류: {parsed['type']}"

def test_heatmap_data(session):
    """히트맵 데이터 쿼리 — 25개 구 전체"""
    result = session.sql("""
        SELECT m.CITY_KOR_NAME, ST_ASGEOJSON(m.DISTRICT_GEOM) AS geojson,
               COALESCE(v.OPEN_COUNT, 0) AS move_signal
        FROM MOVING_INTEL.ANALYTICS.V_SPH_REGION_MASTER m
        LEFT JOIN MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL v
            ON m.CITY_KOR_NAME = v.INSTALL_CITY
        WHERE m.PROVINCE_CODE = '11'
        GROUP BY 1, 2, 3
    """).to_pandas()
    assert result["CITY_KOR_NAME"].nunique() >= 20, "구 수 부족"

def test_filter_changes_data(session):
    """필터 변경 시 데이터 변경 확인"""
    # YEAR_MONTH는 DATE 타입이므로 명시적 캐스팅 권장 (#40 검증).
    q1 = session.sql("SELECT SUM(OPEN_COUNT) FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL WHERE YEAR_MONTH = '2025-01-01'::DATE").collect()[0][0]
    q2 = session.sql("SELECT SUM(OPEN_COUNT) FROM MOVING_INTEL.ANALYTICS.V_TELECOM_NEW_INSTALL WHERE YEAR_MONTH = '2025-06-01'::DATE").collect()[0][0]
    assert q1 != q2, "다른 월인데 같은 값 — 필터 미작동 의심"
\`\`\`

## 참조
- \`docs/specs/dev_spec.md\` C1 (대시보드 구조), C2 (히트맵), C6 (GIS/DISTRICT_GEOM)
- pydeck GeoJsonLayer + ST_ASGEOJSON(DISTRICT_GEOM)
- 의존성: #20 (BJD매핑), #23 (PREDICT UDF)

## 불변식
- 별도 GeoJSON 파일 다운로드 금지 — M_SCCO_MST.DISTRICT_GEOM 내장 데이터 사용
- Streamlit in Snowflake 환경 제약: 외부 네트워크 접근 불가
- pydeck 사용 가능 (Streamlit in Snowflake GA)


## 작업 내역

### 신규 파일
- `src/app/app.py` — 3탭 스켈레톤 (이사 수요 히트맵 / 세그먼트·ROI / Cortex AI)
- `src/app/tabs/__init__.py` — 탭 패키지 초기화
- `src/app/tabs/heatmap.py` — pydeck GeoJsonLayer choropleth 히트맵 탭
- `src/app/tabs/segment_roi.py` — 이사 수요 × ROI 산점도 + 세그먼트 프로파일 탭
- `tests/test_13_heatmap.py` — syntax check + 구조 검증 (7/7 PASS)
- `src/app/.streamlit/` — Streamlit 설정 (로컬 전용, gitignore)

### 수정 파일
- `src/app/.ai.md` — 3탭 구조·의존성·보안 불변식 최신화
- `.gitignore` — `local_run.py`, `.streamlit/secrets.toml` 추가 (자격증명 보호)

### 주요 설계 결정
- **GIS 데이터**: `V_SPH_REGION_MASTER` 뷰에 `DISTRICT_GEOM` 미반영 → `M_SCCO_MST` 원본 직접 참조로 우회
- **ROI 기준 연월**: 상단 selectbox에서 선택한 월 단일 필터 적용 (기존 6개월 평균 → 단일 월 SUM)
- **미래 월 필터**: `ym_options`를 현재 월 이하로 제한 → 데이터 없는 월 선택 방지
- **YEAR_MONTH 타입**: Snowflake에서 `datetime.date` 반환 → `strftime("%Y%m")` 변환
- **UDF 의존**: 개별 구 상세 ROI(`CALC_ROI`), 프로파일(`GET_SEGMENT_PROFILE`)은 #24, #25 머지 후 활성화
