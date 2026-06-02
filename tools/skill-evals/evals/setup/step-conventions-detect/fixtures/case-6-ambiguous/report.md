Repo: github.com/example-org/migrating-project

[ -L .claude/skills ]: false — .claude/skills is a regular directory
[ -L .github/skills ]: false — .github/skills is a regular directory

ls -la .claude/skills/: (regular directory)
  setup/    (regular directory)
    SKILL.md        (regular file)
  issue-triage/
    SKILL.md        (regular file — not a symlink)

ls -la .github/skills/: (regular directory)
  pr-management-triage/
    SKILL.md        (regular file — not a symlink)
  security-issue-import/
    SKILL.md        (regular file — not a symlink)

Neither directory has symlinks linking the two. Both contain independent skill content.
No cross-directory symlinks detected.
