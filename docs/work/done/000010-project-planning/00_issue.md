# chore: 무빙 인텔리전스 프로젝트 기획서 작성

## 목적
리서치(docs/background/ 00~14) 기반으로 현업 수준 프로젝트 기획서를 docs/whitepaper/ 하위에 작성한다.

## 배경
해커톤 리서치 단계에서 시장 조사·경쟁 분석·수익 모델·프레임워크 분석이 완료되었다. 이를 종합하여 실제 필드에서 사용되는 기법(PRD, Value Proposition Canvas, JTBD 등)으로 프로젝트 기획서를 작성한다. 브랜드 존재 이유, 타겟 고객별 문제 정의, 가치 제안, 핵심 기능 명세를 구체적으로 정리한다.

## 완료 기준
- [x] `docs/whitepaper/` 하위에 현업 수준 프로젝트 기획서 문서 작성 완료 (PRD/Value Proposition Canvas 등 실무 프레임워크 적용)
- [x] 리서치 문서(00~16)의 핵심 데이터가 기획서에 근거로 반영됨
- [x] 타겟 고객별 문제 정의, 가치 제안, 핵심 기능 목록이 구체적으로 정리됨

## 구현 플랜
1. 현업 기획서 프레임워크 리서치 (PRD, Lean Canvas, Value Proposition Canvas, Feature Spec 등)
2. `docs/whitepaper/` 하위에 기획서 문서 작성 — `docs/background/` 리서치 00~14번 전체를 근거로 활용
3. 핵심 섹션: 브랜드 미션/비전/존재 이유, 타겟 고객별 문제 정의, 가치 제안, 핵심 기능 명세, 수익 모델 & 시장 규모, GTM 전략
4. `.ai.md` 최신화

## 개발 체크리스트
- [x] 해당 디렉토리 .ai.md 최신화

## 작업 내역

### 산출물
- `docs/whitepaper/v1.0-moving-intelligence.md` — 프로젝트 기획서 (7섹션, 671줄)

### 주요 작업
1. ralplan 합의 플래닝 (Planner→Architect→Critic 2회 반복) → `01_plan.md` 구현 계획 수립
2. Team 모드 3명 병렬 집필 → 섹션 1-2(Product) / 3-4(Tech) / 5-7(Business) 분담 작성
3. 파트 파일 통합 → 누락 콘텐츠 복원 (107줄 추가) → 파트 파일 삭제
4. MVP 방향 전환: "이사 적기 분석(B2C)" → "이사 수요 예측(B2B)" — 아정당 통신 주소 변경을 선행지표로 활용, B2B 고객(통신사/가전렌탈/인테리어/이사업체)에게 예측 API 제공
5. PPT 제출 템플릿 요건 반영 (Problem Statement + Architecture + Insight 3개)
6. `docs/whitepaper/.ai.md` 최신화
