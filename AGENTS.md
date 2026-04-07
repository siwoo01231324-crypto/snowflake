# snowflake AGENTS.md

> 이 파일은 레포 전체의 목차다. 백과사전이 아니다.
> 규칙·불변식은 `CLAUDE.md` 참조. 각 디렉토리 상세는 해당 `.ai.md` 참조.

---

## 레포 구조

```
snowflake/
├── AGENTS.md               ← 지금 이 파일 (목차)
├── CLAUDE.md               ← 불변식·규칙·작업 흐름
├── README.md               ← 프로젝트 소개
├── setup.sh                ← 템플릿 초기화 스크립트 (1회 실행)
├── .github/
│   └── workflows/          GitHub Actions (project-automation.yml)
├── .claude/
│   ├── agents/             커스텀 에이전트 정의
│   ├── commands/           슬래시 커맨드 (bi, si, fi, ci 등)
│   └── hooks/              Git 훅 스크립트
├── sql/                    ← Snowflake SQL 스크립트
│   ├── ddl/                DB·스키마·테이블 생성 DDL (A2-3)
│   ├── views/              Marketplace 연동 뷰 10개 (A2-3)
│   ├── udf/                UDF·UDTF 정의 3개 (B3)
│   ├── cortex/             Cortex AI Functions SQL (B4)
│   ├── validation/         데이터 검증 쿼리
│   └── test/               AC 검증 테스트 쿼리
├── src/                    ← Python 소스 코드
│   ├── pipeline/           Snowpark 전처리 파이프라인 (A3)
│   ├── features/           Feature Engineering (A4)
│   ├── ml/                 ML 모델 학습·배포 (A5)
│   └── app/                Streamlit 대시보드 (C1~C6)
│       ├── app.py          앱 진입점
│       ├── tabs/           탭별 모듈 (히트맵, 세그먼트, ROI, AI)
│       ├── components/     재사용 컴포넌트 (지도, 필터)
│       └── utils/          유틸리티 (세션, 상수)
├── config/                 ← 설정 파일
│   └── semantic_model.yaml Cortex Analyst 시맨틱 모델 (B5)
├── tests/                  ← Python 테스트
├── docs/                   ← 프로젝트 문서 (SOT)
│   ├── specs/              기능 명세 + AC (dev_spec.md)
│   ├── background/         배경 리서치 18건
│   ├── whitepaper/         백서
│   ├── onboarding/         환경 설정·기여 가이드
│   └── work/               이슈별 작업 내역
│       ├── active/         진행 중인 작업
│       └── done/           완료된 작업
└── scripts/                ← 유틸리티 스크립트
    ├── check_invariants.py 아키텍처 불변식 검증
    └── check_forbidden_files.py 금지 파일 검사
```

---

## 핵심 문서 링크

- 기능 명세 + AC → `docs/specs/`
- 작업 내역 → `docs/work/active/`
- 온보딩 → `docs/onboarding/getting-started.md`

