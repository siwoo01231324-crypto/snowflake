# feat: Cortex Analyst 시맨틱 모델 YAML 4개 작성

# Issue #26: feat: Cortex Analyst 시맨틱 모델 YAML 4개 작성

## 목적
"이사 많은 지역 알려줘" 같은 자연어 질의를 가능하게 하는 Cortex Analyst 시맨틱 모델을 만든다.

## 완료 기준
- [x] `moving_intelligence_semantic_model.yaml` 파일 작성
- [x] 4개 테이블 시맨틱 모델 정의 (V_TELECOM_NEW_INSTALL, V_RICHGO_MARKET_PRICE, V_SPH_FLOATING_POP, V_NEXTTRADE_PRICE)
- [ ] Cortex Analyst REST API 호출 → 자연어 응답 반환 (Snowflake 환경 배포 후 검증 예정)
- [x] verified_queries 5개 포함 (3개 이상 달성)

## 테스트 코드 (TDD — 먼저 작성)

\`\`\`python
# test_11_cortex_analyst.py
import requests

def test_yaml_syntax():
    """YAML 파싱 에러 없음 확인"""
    import yaml
    with open("semantic_models/moving_intelligence_semantic_model.yaml") as f:
        model = yaml.safe_load(f)
    assert "tables" in model, "tables 키 없음"
    assert len(model["tables"]) == 4, f"테이블 4개 필요, {len(model['tables'])}개"

def test_table_names():
    """4개 테이블 base_table 경로 확인 (#40 검증: MOVING_INTEL.ANALYTICS 뷰 레이어 통일)"""
    import yaml
    with open("semantic_models/moving_intelligence_semantic_model.yaml") as f:
        model = yaml.safe_load(f)
    table_names = [t["base_table"] for t in model["tables"]]
    # 실존하는 MOVING_INTEL.ANALYTICS 뷰 레이어 사용. Marketplace 원본 직접 참조 금지.
    assert any("V_TELECOM_NEW_INSTALL" in t for t in table_names)    # was: V05_REGIONAL_NEW_INSTALL (미존재)
    assert any("V_RICHGO_MARKET_PRICE" in t for t in table_names)    # was: REGION_APT_RICHGO_MARKET_PRICE_M_H (Marketplace 원본)
    assert any("V_SPH_FLOATING_POP" in t for t in table_names)       # was: FLOATING_POPULATION_INFO (Marketplace 원본)
    assert any("V_NEXTTRADE_PRICE" in t for t in table_names)        # was: NX_HT_ONL_MKTPR_A3 (미존재)

def test_cortex_analyst_api(session):
    """Cortex Analyst API 호출 → 응답 반환"""
    # Snowflake REST API /api/v2/cortex/analyst/message
    response = call_cortex_analyst(
        session, 
        model="moving_intelligence_semantic_model",
        question="서울에서 이사 수요가 가장 높은 구는?"
    )
    assert response is not None
    assert len(response) > 10, "응답이 너무 짧음"
\`\`\`

## 참조
- \`docs/specs/dev_spec.md\` B5 (Cortex Analyst YAML 설계)
- dimensions에 WEEKDAY_WEEKEND, TIME_SLOT 포함 (중복 집계 방지)
- Cortex Analyst는 REST API 호출 (SQL 함수 아님)
- 의존성: #17~#19 (참조 뷰 전부), #40 (실존 뷰명 동기화)

## 불변식
- YAML은 Snowflake Cortex Analyst 공식 스펙 준수
- base_table은 `MOVING_INTEL.ANALYTICS.V_*` 뷰 레이어 사용 (Marketplace 원본 테이블 직접 참조 금지)
- 실존 뷰: `V_TELECOM_NEW_INSTALL`, `V_RICHGO_MARKET_PRICE`, `V_SPH_FLOATING_POP`, `V_SPH_CARD_SALES`, `V_SPH_ASSET_INCOME`, `V_NEXTTRADE_PRICE` (#40 Snowflake 검증 결과)
- verified_queries의 SQL은 실제 뷰에서 실행 가능해야 함

## 작업 내역

### 구현 완료 (2026-04-09)

**신규 파일**
- `semantic_models/moving_intelligence_semantic_model.yaml`: Cortex Analyst 시맨틱 모델 YAML
- `tests/test_11_cortex_analyst.py`: TC-01~11 pytest 테스트

**핵심 설계 결정**
- base_table 4개: V_TELECOM_NEW_INSTALL, V_RICHGO_MARKET_PRICE, V_SPH_FLOATING_POP, V_NEXTTRADE_PRICE (모두 MOVING_INTEL.ANALYTICS.V_* 뷰 레이어)
- verified_queries 5개 작성 (이사 수요 상위 구, 아파트 시세 추이, 이사·시세 상관, 유동인구 요일/시간대, NextTrade 가격 집계)
- WEEKDAY_WEEKEND, TIME_SLOT 차원 포함 (중복 집계 방지)
- Cortex Analyst REST API 실환경 호출은 Snowflake 스테이지 업로드 후 별도 검증 예정

**TC 결과: 11/11 PASS** (pytest 로컬 검증)
- TC-01~04: YAML 파싱·구조·테이블 4개·verified_queries 5개 ✓
- TC-05~09: 각 테이블 컬럼 구조·측정값 정의 ✓
- TC-10~11: YAML 직렬화 왕복 일관성·불변식 준수 ✓
