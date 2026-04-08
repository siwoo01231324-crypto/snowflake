# snowflake — Claude Code 가이드

> 세션 시작 시 이 파일을 먼저 읽는다. 지도(map)다. 백과사전이 아니다.

## 시작 전 필수 확인 순서
1. `gh issue list --assignee @me` — 내 담당 이슈 확인
2. `docs/work/EXECUTION_PLAN.md` — **현재 실행 계획·의존성 그래프·Day별 순서** (Dual-Tier Pivot 진행 중)
3. `AGENTS.md` — 레포 전체 목차·불변식·규칙
4. 작업 대상 디렉토리의 `.ai.md` — 목적·구조·역할
5. `docs/work/active/` — 현재 진행 중인 작업 내역 (있는 경우)

## 아키텍처 불변식 (위반 시 CI 차단)

> ⚠️ 프로젝트에 맞게 직접 정의하세요. `scripts/check_invariants.py` 와 연동됩니다.

```
1. Snowflake 연결 정보(account, password, token)를 소스코드에 하드코딩 금지
   - UDF/UDTF → Snowflake SECRET 객체 사용
   - Streamlit → st.connection() + secrets.toml (gitignore 대상)
   - Python 스크립트 → 환경변수 또는 ~/.snowflake/connections.toml
2. 실데이터 샘플을 코드·주석·커밋 메시지에 포함 금지
   - 테스트에는 기대값(row count, 컬럼 존재 여부)만 기재
   - 개인정보(이름, 전화번호, 주소) 절대 커밋 금지
3. API 키·토큰이 git history에 유입되면 즉시 키 폐기 + 재발급
   - secret-filter hook이 탐지하지만, 방어선은 커밋 전 확인이 우선
```

## 레포 규칙
```
1. 5MB 초과 파일 커밋 시 컨펌 필요
2. *.pdf, *.csv, *.pkl, *.parquet 커밋 금지 (.gitignore 적용)
3. 모든 디렉토리에 .ai.md 포함 — 목적·구조·역할 기술
4. 작업 전 해당 디렉토리의 .ai.md 확인
5. 작업 완료 후 .ai.md 최신화 필수 (생략 시 작업 미완료)
6. AGENTS.md는 간결한 레포 목차(디렉토리 트리 + 핵심 링크)로만 유지한다
   - 상세 스펙/설계/마일스톤은 docs/specs/ 또는 .ai.md에 기술
   - dev_spec, 기획서 등의 내용을 AGENTS.md에 복사·요약하지 않는다
   - 서브에이전트가 AGENTS.md를 편집할 때도 이 규칙을 적용한다
```

## 작업 흐름
1. 해당 디렉토리 `.ai.md` 읽기
2. GitHub Issue body에서 AC 확인 (`docs/specs/`는 기획/기술 설계 문서)
3. 테스트 먼저 작성 → Red → Green → Refactor
4. **완료 후 `.ai.md` 최신화 — 필수, 생략 시 작업 미완료로 간주**
5. 실패 시 → "레포에 무엇이 없었나?" 진단 → 문서 업데이트

## 핵심 문서 위치
- 기능 명세 + AC → `docs/specs/`
- 온보딩·워크플로우 → `docs/onboarding/`
- 작업 내역 → `docs/work/active/` · `docs/work/done/`

## 조사·리서치 규칙
- 서베이·리서치 등 조사 작업은 팩트에 근거한 내용만 작성한다
- 조사 결과 문서 하단에는 반드시 출처를 명시한다

## 행동 규칙
- `git commit` 전에 항상 사용자에게 먼저 확인한다 ("커밋할까?" 등으로 물어보고 승인 후 실행)
- `git push` 전에 항상 사용자에게 먼저 확인한다 ("푸시할까?" 등으로 물어보고 승인 후 실행)
