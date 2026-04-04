---
description: PR 머지 확인 후 워크트리와 로컬 브랜치를 정리한다. 사용법: /cleanup-issue [이슈번호|짧은이름]
---

## 인수 형식 (유연하게 지원)

`$ARGUMENTS`는 다음 형식 중 하나거나 생략 가능하다:

| 형식 | 예시 | 동작 |
|------|------|------|
| **생략** | (없음) | 전체 워크트리 스캔 → 머지된 이슈 자동 감지 후 일괄 정리 |
| 이슈번호만 | `15` | `git worktree list`에서 번호로 매칭 |
| 6자리 패딩+짧은이름 | `000015-my-feature` | 직접 워크트리 경로 구성 |
| 짧은이름만 | `my-feature` | `git worktree list`에서 이름으로 매칭 |

## 실행 순서

### 1. 워크트리·이슈번호 확정

**인수 없는 경우 — 자동 일괄 정리 모드:**

```
git worktree list
```

`.worktree/` 하위 항목을 모두 수집한다. 각 항목에서:
1. 이름 패턴 `{PADDED}-{짧은이름}`에서 이슈번호 추출
2. `gh issue view {번호} --json state` 로 상태 확인
3. CLOSED 상태인 것만 정리 대상으로 분류

정리 대상 목록을 출력하고 확인을 받는다. 확인 후 각 항목에 대해 2~6단계 실행.

### 2. 서버 프로세스 종료

워크트리 경로 기준으로 실행 중인 dev 서버 프로세스를 찾아 종료한다.

### 3. 이슈 상태 확인 (단일 정리 모드)

```
gh issue view {이슈번호} --json state,title
```

이슈가 OPEN 상태이면 경고 출력 후 사용자 확인.

### 4. Worktree 삭제

```
git worktree remove --force {WORKTREE}
```

### 5. 로컬 브랜치 삭제

```
git branch -D {브랜치명}
```

### 6. 리모트 브랜치 삭제

```
git push origin --delete {브랜치명}
```

### 7. 최종 상태 확인

```
git worktree list
```
