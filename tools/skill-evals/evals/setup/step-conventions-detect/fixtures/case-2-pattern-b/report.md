Repo: github.com/example-org/my-project

ls -la .claude/skills/: (directory exists, regular directory)
  setup/    (regular directory)
    SKILL.md        (regular file)
  security-issue-import  →  ../../.github/skills/security-issue-import/  (symlink resolving into .github/skills/)
  pr-management-triage   →  ../../.github/skills/pr-management-triage/   (symlink resolving into .github/skills/)

ls -la .github/skills/: (directory exists, regular directory)
  security-issue-import/
    SKILL.md
  pr-management-triage/
    SKILL.md

[ -L .claude/skills ]: false — .claude/skills is a regular directory
[ -L .github/skills ]: false — .github/skills is a regular directory
At least one entry in .claude/skills/ is a symlink resolving into .github/skills/.
