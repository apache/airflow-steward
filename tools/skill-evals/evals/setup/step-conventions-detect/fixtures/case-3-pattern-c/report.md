Repo: github.com/example-org/brand-new-project

ls -la .claude/: (no such directory — .claude/ does not exist)
ls -la .github/skills/: (no such directory — .github/skills/ does not exist)

[ -L .claude/skills ]: false — path does not exist
[ -L .github/skills ]: false — path does not exist
Neither .claude/skills/ nor .github/skills/ exists.
