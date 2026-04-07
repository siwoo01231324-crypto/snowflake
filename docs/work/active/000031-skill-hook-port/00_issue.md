# chore: MIRAI 프로젝트에서 유용한 스킬·훅 이식

## 목적
MIRAI 프로젝트의 `.claude/skills`와 `.claude/hooks`에서 Snowflake 프로젝트에 유용한 스킬 4종과 훅 1종을 이식하여 개발 품질과 자동화를 강화한다.

## 배경
MIRAI에는 41개 스킬이 있으나, Snowflake 도메인(데이터 엔지니어링)에 맞는 범용 스킬만 선별했다. 프론트엔드/마케팅/MIRAI 전용 스킬은 제외.

## 완료 기준
- [ ] `skill-activation-prompt` 훅이 `UserPromptSubmit`에 등록되어 키워드 감지 시 스킬 자동 제안됨
- [ ] 스킬 4종이 `.claude/skills/`에 존재하고 정상 동작
  - `database-schema-design` (Snowflake SQL 문법에 맞게 커스터마이징)
  - `git-commit` (Conventional Commits 자동 분석·생성)
  - `test-driven-development` (TDD Red-Green-Refactor 강제)
  - `security-best-practices` (Snowflake RBAC/네트워크 정책 반영)
- [ ] `skill-rules.json` 생성 (Snowflake 도메인에 맞는 트리거 키워드 정의)
- [ ] 각 스킬 디렉토리에 `.ai.md` 파일 존재
- [ ] `.claude/hooks/.ai.md` 최신화

## 구현 플랜
1. `.claude/skills/` 디렉토리 생성 + `skill-rules.json` 작성
2. `skill-activation-prompt` 훅 이식 (`.sh` + `.ts`) + `settings.json`에 `UserPromptSubmit` 훅 등록
3. 스킬 4종 이식 및 커스터마이징
   - `database-schema-design` → Snowflake SQL 반영 (VARIANT, CLUSTER BY, COPY INTO 등)
   - `git-commit` → 그대로 이식
   - `test-driven-development` → 그대로 이식
   - `security-best-practices` → Snowflake 보안 맥락 반영 (RBAC, 네트워크 정책, 데이터 마스킹 등)
4. 각 스킬 디렉토리에 `.ai.md` 작성 + `.claude/hooks/.ai.md` 업데이트

## 참고
- 원본 위치: `D:\project\T아카데미\MIRAI\MIRAI\.claude\skills\`
- `secret-filter.sh`는 이미 동일하므로 제외
- 프론트엔드/마케팅 관련 스킬은 도메인 불일치로 제외

## 개발 체크리스트
- [ ] 해당 디렉토리 .ai.md 최신화


## 작업 내역

### 2026-04-07
- **세션 시작** — AC 현황 점검: 0/5 완료, 구현 대기 상태
- 작업 폴더(`00_issue.md`, `01_plan.md`) 생성 완료
- `.claude/skills/` 디렉토리 및 스킬 파일 미생성
- `skill-activation-prompt` 훅 미이식
- `skill-rules.json` 미생성

