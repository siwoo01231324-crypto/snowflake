#!/bin/bash
# setup.sh — 템플릿 초기화 스크립트
# 새 프로젝트에서 1회 실행. 플레이스홀더를 실제 값으로 치환합니다.

set -e

echo "================================================"
echo "  siw-claude-template 초기화"
echo "================================================"
echo ""

# 1. 프로젝트 이름 입력
read -p "프로젝트 이름 (예: my-awesome-project): " PROJECT_NAME
if [ -z "$PROJECT_NAME" ]; then
  echo "❌ 프로젝트 이름은 필수입니다."
  exit 1
fi

# 2. 플레이스홀더 치환
echo ""
echo "📝 플레이스홀더 치환 중..."

find . -name "*.md" -not -path "./.git/*" -not -path "./node_modules/*" | while read f; do
  sed -i "s/{{PROJECT_NAME}}/$PROJECT_NAME/g" "$f"
done

echo "  ✓ CLAUDE.md, AGENTS.md, docs/ 내 {{PROJECT_NAME}} 치환 완료"

# 3. update-changelog 스코프 안내
echo ""
echo "📋 update-changelog 스코프 설정"
echo "  .claude/commands/update-changelog.md 에서 SCOPE → 경로 매핑을 직접 수정하세요."
echo "  (현재: root / src 두 가지 예시가 포함되어 있습니다)"

# 4. 불변식 설정 안내
echo ""
echo "🔒 불변식 설정"
echo "  CLAUDE.md 의 '아키텍처 불변식' 섹션을 프로젝트에 맞게 수정하세요."
echo "  scripts/check_invariants.py 에 해당 불변식 검사 로직을 작성하세요."

# 5. GitHub Project 보드 연내
echo ""
echo "📌 GitHub Project 보드 연결"
echo "  .github/workflows/project-automation.yml 에서"
echo "  PROJECT_NUMBER, OWNER, PROJECT_ID, FIELD_ID, OPTION_IDs 를 설정하세요."
echo "  자세한 방법: docs/onboarding/getting-started.md"

# 6. hooks 실행 권한
echo ""
echo "🔐 훅 실행 권한 부여..."
chmod +x .claude/hooks/secret-filter.sh 2>/dev/null || true
echo "  ✓ .claude/hooks/secret-filter.sh 실행 권한 설정 완료"

# 7. .gitkeep 삭제 안내
echo ""
echo "📁 초기 디렉토리"
echo "  docs/work/active/, docs/work/done/, docs/specs/ 에 .gitkeep 파일이 있습니다."
echo "  첫 파일 추가 후 삭제하세요."

echo ""
echo "================================================"
echo "  ✅ '$PROJECT_NAME' 초기화 완료!"
echo ""
echo "  다음 단계:"
echo "  1. docs/onboarding/getting-started.md 를 읽으세요"
echo "  2. GitHub Project 보드를 생성하고 연결하세요"
echo "  3. CLAUDE.md 불변식을 프로젝트에 맞게 수정하세요"
echo "  4. AGENTS.md 레포 구조를 실제 구조로 업데이트하세요"
echo "================================================"
