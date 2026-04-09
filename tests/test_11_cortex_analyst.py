"""
test_11_cortex_analyst.py — Cortex Analyst 시맨틱 모델 YAML 유효성 검증 테스트
이슈: #26
"""
import pathlib
import yaml
import pytest


YAML_PATH = pathlib.Path(__file__).parent.parent / "semantic_models" / "moving_intelligence_semantic_model.yaml"

EXPECTED_VIEW_NAMES = [
    "V_TELECOM_NEW_INSTALL",
    "V_RICHGO_MARKET_PRICE",
    "V_SPH_FLOATING_POP",
    "V_NEXTTRADE_PRICE",
]


@pytest.fixture(scope="module")
def semantic_model():
    """YAML 파일을 파싱해 반환한다."""
    with open(YAML_PATH, encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_yaml_syntax(semantic_model):
    """TC-01: YAML 파싱 에러 없음 + tables 키 존재 + 테이블 4개"""
    assert semantic_model is not None, "YAML 파싱 결과가 None"
    assert "tables" in semantic_model, "tables 키 없음"
    assert len(semantic_model["tables"]) == 4, (
        f"테이블 수 불일치: {len(semantic_model['tables'])} (기대: 4)"
    )


def test_table_names(semantic_model):
    """TC-02: base_table에 V_TELECOM_NEW_INSTALL, V_RICHGO_MARKET_PRICE, V_SPH_FLOATING_POP, V_NEXTTRADE_PRICE 포함"""
    base_tables = [t["base_table"] for t in semantic_model["tables"]]
    for view_name in EXPECTED_VIEW_NAMES:
        matched = any(view_name in bt for bt in base_tables)
        assert matched, f"base_table에 {view_name} 없음. 실제: {base_tables}"


def test_base_tables_use_analytics_schema(semantic_model):
    """TC-03: 모든 base_table이 MOVING_INTEL.ANALYTICS.V_* 뷰 참조 (Marketplace 원본 직접 참조 금지)"""
    for table in semantic_model["tables"]:
        bt = table["base_table"]
        assert bt.startswith("MOVING_INTEL.ANALYTICS.V_"), (
            f"base_table이 MOVING_INTEL.ANALYTICS.V_*가 아님: {bt}"
        )


def test_dimensions_exist(semantic_model):
    """TC-04: 모든 테이블에 dimensions 정의"""
    for table in semantic_model["tables"]:
        dims = table.get("dimensions", [])
        assert len(dims) > 0, f"테이블 {table['name']}에 dimensions 없음"


def test_measures_exist(semantic_model):
    """TC-05: 모든 테이블에 measures 정의"""
    for table in semantic_model["tables"]:
        measures = table.get("measures", [])
        assert len(measures) > 0, f"테이블 {table['name']}에 measures 없음"


def test_weekday_weekend_time_slot_in_floating_pop(semantic_model):
    """TC-06: V_SPH_FLOATING_POP 테이블에 WEEKDAY_WEEKEND, TIME_SLOT dimensions 포함"""
    floating_pop = next(
        (t for t in semantic_model["tables"] if "V_SPH_FLOATING_POP" in t["base_table"]),
        None,
    )
    assert floating_pop is not None, "V_SPH_FLOATING_POP 테이블 없음"

    dim_names = [d["name"] for d in floating_pop.get("dimensions", [])]
    assert "weekday_weekend" in dim_names, f"weekday_weekend dimension 없음. 실제: {dim_names}"
    assert "time_slot" in dim_names, f"time_slot dimension 없음. 실제: {dim_names}"


def test_verified_queries_count(semantic_model):
    """TC-07: verified_queries 3개 이상"""
    vq = semantic_model.get("verified_queries", [])
    assert len(vq) >= 3, f"verified_queries {len(vq)}개 (최소 3개 필요)"


def test_verified_queries_structure(semantic_model):
    """TC-08: 각 verified_query에 question, sql 키 존재"""
    for i, vq in enumerate(semantic_model.get("verified_queries", [])):
        assert "question" in vq, f"verified_queries[{i}]에 question 없음"
        assert "sql" in vq, f"verified_queries[{i}]에 sql 없음"
        assert vq["question"].strip(), f"verified_queries[{i}].question이 빈 문자열"
        assert vq["sql"].strip(), f"verified_queries[{i}].sql이 빈 문자열"


def test_verified_queries_use_analytics_views(semantic_model):
    """TC-09: verified_queries SQL이 MOVING_INTEL.ANALYTICS.V_* 뷰 참조"""
    for vq in semantic_model.get("verified_queries", []):
        sql = vq["sql"]
        assert "MOVING_INTEL.ANALYTICS.V_" in sql, (
            f"verified_query SQL이 MOVING_INTEL.ANALYTICS.V_* 참조 안 함: {vq['question']}"
        )


def test_no_hardcoded_credentials(semantic_model):
    """TC-10: YAML에 연결 정보(password, token, account) 하드코딩 없음 (불변식 준수)"""
    yaml_text = YAML_PATH.read_text(encoding="utf-8").lower()
    forbidden = ["password=", "token=", "private_key=", "secret="]
    for keyword in forbidden:
        assert keyword not in yaml_text, f"YAML에 민감 정보 키워드 포함: {keyword}"


def test_semantic_model_name_and_description(semantic_model):
    """TC-11: name, description 최상위 키 존재"""
    assert "name" in semantic_model, "최상위 name 키 없음"
    assert "description" in semantic_model, "최상위 description 키 없음"
    assert semantic_model["name"] == "moving_intelligence", (
        f"name 불일치: {semantic_model['name']}"
    )
