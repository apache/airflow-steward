Repo: github.com/example-org/claude-first-project

[ -L .claude/skills ]: false — .claude/skills is a regular directory
[ -L .github/skills ]: true — .github/skills is a symlink
readlink .github/skills: ../.claude/skills
Resolved target: .claude/skills/ (within the same repo)

ls -la .claude/skills/: (directory exists, regular directory)
  setup/    (regular directory)
    SKILL.md        (regular file)
  issue-triage/
    SKILL.md
