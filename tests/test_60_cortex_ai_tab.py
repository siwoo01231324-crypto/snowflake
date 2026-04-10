"""test_60_cortex_ai_tab.py — Cortex AI 분석 탭 단위 테스트 (이슈 #60)"""
import importlib
import pathlib
import sys
import types

import pytest


# ── 공통 fixture: Snowflake 의존성 mock ────────────────────────────────────

@pytest.fixture(autouse=True)
def mock_snowflake_deps(monkeypatch):
    """snowflake.snowpark, streamlit, _snowflake 를 stub으로 주입."""
    # snowflake.snowpark stub
    snowpark = types.ModuleType("snowflake.snowpark")
    snowpark.Session = object
    sys.modules.setdefault("snowflake", types.ModuleType("snowflake"))
    sys.modules["snowflake.snowpark"] = snowpark

    # streamlit stub (캐시 데코레이터 무력화)
    st_stub = types.ModuleType("streamlit")
    st_stub.cache_data = lambda **kw: (lambda f: f)
    sys.modules["streamlit"] = st_stub

    # _snowflake stub (SiS 전용 — 로컬 테스트에서는 없음)
    sys.modules.setdefault("_snowflake", types.ModuleType("_snowflake"))

    yield

    # 모듈 캐시에서 제거해 다음 테스트에 영향 없도록
    for mod in ["tabs.cortex_ai", "cortex_ai"]:
        sys.modules.pop(mod, None)


# ── 모듈 임포트 헬퍼 ──────────────────────────────────────────────────────

def _import_cortex_ai():
    """src/app/tabs/cortex_ai.py 임포트."""
    src_path = pathlib.Path(__file__).parent.parent / "src" / "app"
    tabs_path = src_path / "tabs"
    for p in [str(src_path), str(tabs_path)]:
        if p not in sys.path:
            sys.path.insert(0, p)
    # cortex 모듈도 경로에 있어야 import 성공
    return importlib.import_module("cortex_ai")


# ── TC-01: 파일 존재 확인 ────────────────────────────────────────────────

def test_cortex_ai_file_exists():
    """TC-01: src/app/tabs/cortex_ai.py 파일 존재."""
    path = (
        pathlib.Path(__file__).parent.parent
        / "src" / "app" / "tabs" / "cortex_ai.py"
    )
    assert path.exists(), f"cortex_ai.py 파일 없음: {path}"


# ── TC-02: 모듈 임포트 성공 ──────────────────────────────────────────────

def test_module_imports():
    """TC-02: cortex_ai 모듈 임포트 오류 없음."""
    mod = _import_cortex_ai()
    assert mod is not None


# ── TC-03: render_cortex_ai 함수 존재 ────────────────────────────────────

def test_render_cortex_ai_exists():
    """TC-03: render_cortex_ai(session) 함수 존재."""
    mod = _import_cortex_ai()
    assert hasattr(mod, "render_cortex_ai"), "render_cortex_ai 함수 없음"
    assert callable(mod.render_cortex_ai)


# ── TC-04: 내부 섹션 함수 존재 ───────────────────────────────────────────

@pytest.mark.parametrize("func_name", [
    "_render_insight_section",
    "_render_analyst_section",
])
def test_section_functions_exist(func_name):
    """TC-04: 2개 섹션 함수 존재 (AI 인사이트 + 자연어 질의)."""
    mod = _import_cortex_ai()
    assert hasattr(mod, func_name), f"{func_name} 함수 없음"
    assert callable(getattr(mod, func_name))


# ── TC-05: SEMANTIC_MODEL_FILE 상수 존재 ─────────────────────────────────

def test_semantic_model_file_constant():
    """TC-05: SEMANTIC_MODEL_FILE 상수 존재 및 스테이지 경로 형식."""
    mod = _import_cortex_ai()
    assert hasattr(mod, "SEMANTIC_MODEL_FILE"), "SEMANTIC_MODEL_FILE 상수 없음"
    smf = mod.SEMANTIC_MODEL_FILE
    assert smf.startswith("@"), f"SEMANTIC_MODEL_FILE이 '@'로 시작하지 않음: {smf}"
    assert smf.endswith(".yaml"), f"SEMANTIC_MODEL_FILE이 '.yaml'로 끝나지 않음: {smf}"


# ── TC-07: app.py Tab 3 연동 확인 ────────────────────────────────────────

def test_app_py_integrates_cortex_ai():
    """TC-07: app.py Tab 3에서 render_cortex_ai 임포트·호출."""
    app_path = (
        pathlib.Path(__file__).parent.parent / "src" / "app" / "app.py"
    )
    content = app_path.read_text(encoding="utf-8")
    assert "from tabs.cortex_ai import render_cortex_ai" in content, (
        "app.py에 cortex_ai import 없음"
    )
    assert "render_cortex_ai(session)" in content, (
        "app.py에 render_cortex_ai(session) 호출 없음"
    )


# ── TC-08: 불변식 — 자격증명 하드코딩 없음 ──────────────────────────────

def test_no_hardcoded_credentials():
    """TC-08: cortex_ai.py에 password/token/secret 하드코딩 없음."""
    path = (
        pathlib.Path(__file__).parent.parent
        / "src" / "app" / "tabs" / "cortex_ai.py"
    )
    text = path.read_text(encoding="utf-8").lower()
    for keyword in ("password=", "token=", "private_key=", "secret="):
        assert keyword not in text, f"cortex_ai.py에 민감 정보 포함: {keyword}"
