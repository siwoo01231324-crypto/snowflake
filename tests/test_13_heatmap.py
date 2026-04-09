"""test_13_heatmap.py — Issue #28 TDD: 히트맵 탭 구조 검증 (Snowflake 연결 없이)"""
import os
import sys


def _worktree_root() -> str:
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def test_app_imports():
    """app.py 임포트 에러 없음 (syntax check)"""
    app_path = os.path.join(_worktree_root(), "src", "app", "app.py")
    assert os.path.exists(app_path), "app.py 파일 없음"
    with open(app_path, encoding="utf-8") as f:
        source = f.read()
    compile(source, app_path, "exec")  # syntax check only


def test_heatmap_tab_exists():
    """히트맵 탭 모듈 존재 및 syntax 정상"""
    tab_path = os.path.join(_worktree_root(), "src", "app", "tabs", "heatmap.py")
    assert os.path.exists(tab_path), "heatmap.py 탭 모듈 없음"
    with open(tab_path, encoding="utf-8") as f:
        source = f.read()
    compile(source, tab_path, "exec")


def test_geojson_query_present():
    """히트맵 탭에 ST_ASGEOJSON / DISTRICT_GEOM 쿼리 포함"""
    tab_path = os.path.join(_worktree_root(), "src", "app", "tabs", "heatmap.py")
    with open(tab_path, encoding="utf-8") as f:
        source = f.read()
    assert "ST_ASGEOJSON" in source or "DISTRICT_GEOM" in source, "GeoJSON 쿼리 없음"


def test_pydeck_usage():
    """pydeck 사용 확인"""
    tab_path = os.path.join(_worktree_root(), "src", "app", "tabs", "heatmap.py")
    with open(tab_path, encoding="utf-8") as f:
        source = f.read()
    assert "pydeck" in source or "pdk" in source, "pydeck 미사용"


def test_render_heatmap_function_exists():
    """render_heatmap 함수 정의 확인"""
    tab_path = os.path.join(_worktree_root(), "src", "app", "tabs", "heatmap.py")
    with open(tab_path, encoding="utf-8") as f:
        source = f.read()
    assert "def render_heatmap" in source, "render_heatmap 함수 없음"


def test_tabs_package_exists():
    """tabs 패키지 __init__.py 존재"""
    init_path = os.path.join(_worktree_root(), "src", "app", "tabs", "__init__.py")
    assert os.path.exists(init_path), "tabs/__init__.py 없음"


def test_no_hardcoded_credentials():
    """연결 정보 하드코딩 금지 확인"""
    for rel in ["src/app/app.py", "src/app/tabs/heatmap.py"]:
        path = os.path.join(_worktree_root(), rel)
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            source = f.read()
        for forbidden in ("account=", "password=", "private_key="):
            assert forbidden not in source, f"{rel}에 인증 정보 하드코딩 감지: {forbidden}"
