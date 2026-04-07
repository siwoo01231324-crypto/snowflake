# 구현 계획: MIRAI 스킬·훅 이식

## 완료 기준 체크리스트

- [ ] `skill-activation-prompt` 훅이 `UserPromptSubmit`에 등록되어 키워드 감지 시 스킬 자동 제안됨
- [ ] 스킬 4종이 `.claude/skills/`에 존재하고 정상 동작
  - `database-schema-design` (Snowflake SQL 문법에 맞게 커스터마이징)
  - `git-commit` (Conventional Commits 자동 분석·생성)
  - `test-driven-development` (TDD Red-Green-Refactor 강제)
  - `security-best-practices` (Snowflake RBAC/네트워크 정책 반영)
- [ ] `skill-rules.json` 생성 (Snowflake 도메인에 맞는 트리거 키워드 정의)
- [ ] 각 스킬 디렉토리에 `.ai.md` 파일 존재
- [ ] `.claude/hooks/.ai.md` 최신화

## 구현 단계

### Phase 1: 기반 구조
1. `.claude/skills/` 디렉토리 생성
2. `skill-rules.json` 작성 (Snowflake 도메인 키워드)
3. `skill-activation-prompt.sh` + `skill-activation-prompt.ts` 이식
4. `settings.json`에 `UserPromptSubmit` 훅 등록

### Phase 2: 스킬 이식
5. `git-commit` 스킬 이식 (그대로)
6. `test-driven-development` 스킬 이식 (그대로)
7. `database-schema-design` 스킬 이식 + Snowflake SQL 커스터마이징
8. `security-best-practices` 스킬 이식 + Snowflake 보안 맥락 반영

### Phase 3: 문서화
9. 각 스킬 디렉토리 `.ai.md` 작성
10. `.claude/hooks/.ai.md` 업데이트
11. `.claude/skills/.ai.md` 작성
