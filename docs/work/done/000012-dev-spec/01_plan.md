# 작업 계획 — #12 dev_spec 작성

## 완료 기준 (AC)

- [ ] `docs/specs/dev_spec.md`에 MVP In-Scope 5개 기능(이사 수요 예측 대시보드, 세그먼트 필터, B2B API, Snowflake 파이프라인, ROI 계산기)의 구현 설계가 포함됨
- [ ] 데이터 모델(DIM_REGION, FACT_HOUSING, FACT_LIFESTYLE, FACT_MOVE_SIGNAL, FACT_MARKET) 스키마가 명세됨
- [ ] 해커톤 일정(04-06~04-12)에 맞춘 일별 구현 마일스톤이 포함됨

## 구현 순서

1. `docs/specs/` 디렉토리 생성 + `.ai.md` 작성
2. 데이터 레이어 설계: DIM/FACT 테이블 스키마, 조인 키(행정동 코드), 4종 데이터셋 전처리 명세
3. ML 파이프라인 설계: 이사 수요 예측 모델(시차 상관분석, Snowpark ML), Feature Engineering 명세
4. 서빙 레이어 설계: B2B API 엔드포인트, Cortex Analyst 시맨틱 모델(YAML), Cortex Search/Agents 설계
5. 프레젠테이션 레이어 설계: Streamlit 대시보드(히트맵, 세그먼트 필터, ROI 계산기) 화면 설계
