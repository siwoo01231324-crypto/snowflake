# 01_plan — feat: Cortex Analyst 시맨틱 모델 YAML 4개 작성

## AC 체크리스트

- [x] `moving_intelligence_semantic_model.yaml` 파일 작성
- [x] 4개 테이블 시맨틱 모델 정의 (V_TELECOM_NEW_INSTALL, V_RICHGO_MARKET_PRICE, V_SPH_FLOATING_POP, V_NEXTTRADE_PRICE)
- [ ] Cortex Analyst REST API 호출 → 자연어 응답 반환
- [x] verified_queries 3개 이상 포함 (5개 작성)

## 구현 계획

1. `semantic_models/moving_intelligence_semantic_model.yaml` 작성
2. `test_11_cortex_analyst.py` 테스트 작성
3. YAML 문법 검증 + Cortex Analyst API 호출 검증
