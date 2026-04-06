# chore: 무빙 인텔리전스 dev_spec 작성 — 프로젝트 구현 설계

## 목적
whitepaper v1.0과 background 리서치(18개 문서)를 기반으로 해커톤 MVP 구현을 위한 개발 스펙(dev_spec) 문서를 작성한다.

## 배경
무빙 인텔리전스 기획서(v1.0-moving-intelligence.md)가 완성되었으나, 실제 구현을 위한 기술 설계 문서가 없다. 해커톤 마감(04-12)까지 6일이므로 구현 단위별 명확한 스펙이 필요하다.

## 완료 기준
- [x] `docs/specs/dev_spec.md`에 MVP In-Scope 5개 기능(이사 수요 예측 대시보드, 세그먼트 필터, B2B API, Snowflake 파이프라인, ROI 계산기)의 구현 설계가 포함됨
- [x] 데이터 모델(DIM_REGION, FACT_HOUSING, FACT_LIFESTYLE, FACT_MOVE_SIGNAL, FACT_MARKET) 스키마가 명세됨
- [x] 해커톤 일정(04-06~04-12)에 맞춘 일별 구현 마일스톤이 포함됨

## 구현 플랜
1. `docs/specs/` 디렉토리 생성 + `.ai.md` 작성
2. **데이터 레이어 설계**: DIM/FACT 테이블 스키마, 조인 키(행정동 코드), 4종 데이터셋 전처리 명세
3. **ML 파이프라인 설계**: 이사 수요 예측 모델(시차 상관분석, Snowpark ML), Feature Engineering 명세
4. **서빙 레이어 설계**: B2B API 엔드포인트, Cortex Analyst 시맨틱 모델(YAML), Cortex Search/Agents 설계
5. **프레젠테이션 레이어 설계**: Streamlit 대시보드(히트맵, 세그먼트 필터, ROI 계산기) 화면 설계

## 참조 문서
- `docs/whitepaper/v1.0-moving-intelligence.md` — 프로젝트 기획서
- `docs/background/` — 배경 리서치 18개 문서 (00~17)

## 개발 체크리스트
- [x] 해당 디렉토리 .ai.md 최신화


## 작업 내역

### 2026-04-06 — 세션 시작 (remind-issue)
- master rebase 완료
- AC 0/3 완료 — `docs/specs/dev_spec.md` 미작성 상태
- `01_plan.md` 구현 계획 확인됨 (5단계)
- 현재 단계: **구현 대기**

### 2026-04-06 — dev_spec 작성 완료
- Team 3명 (Data/ML, Backend/API, Frontend/Dashboard) 병렬 작성
- 섹션별 파일 3개 + 통합 `docs/specs/dev_spec.md` 생성
- AC 3/3 완료 — **완료 — /finish-issue 실행 필요**

### 2026-04-07 — 세션 시작 (remind-issue)
- AC 3/3 완료 확인 (dev_spec.md 1,846줄, 5개 기능·5개 스키마·일별 마일스톤 모두 포함)
- `.ai.md` 줄 수 1,678→1,846 최신화 완료, 개발 체크리스트 `[x]` 처리
- 미커밋 변경사항: `docs/specs/dev_spec.md`(신규), `docs/specs/.ai.md`(수정), `docs/work/active/000012-dev-spec/`(신규)
- 현재 단계: **완료 — /finish-issue 실행 필요**

### 2026-04-07 — 실데이터 스키마 검증 및 dev_spec v2 업데이트
- Snowflake MCP 연결 (snowflake-connector-python 사용)
- 4종 Marketplace DB 실 스키마 조회 완료:
  - RICHGO: 3 tables (아파트시세 4,356건, 인구 118건×2)
  - SPH: 5 tables (유동인구 257만, 카드매출 620만, 자산소득 27만, 행정구역 467건+GEOGRAPHY)
  - 아정당: 11 views (계약통계, 퍼널전환, 신규설치 등)
  - NextTrade: 7 tables (종목참조, 체결가, 시장통계 등)
- 주요 발견: SPH 서울 전체 25개 구 커버(기존 3개 구 가정 틀림), DISTRICT_GEOM(GEOGRAPHY) 존재, RICHGO 인구이동 없음, 아정당 이사추정 직접 데이터 없음
- Agent 3명 병렬로 Part A/B/C+D 전면 재작성 → 통합 (1,846줄 → 2,613줄)
- 구 스키마(REGION_CODE, DIM_REGION, FACT_*) 완전 제거, 실제 DB.SCHEMA.TABLE 참조로 교체
- `.ai.md` 줄 수 2,613으로 업데이트
- 현재 단계: **완료 — /finish-issue 실행 필요**

