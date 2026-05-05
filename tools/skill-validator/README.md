<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [skill-validator](#skill-validator)
  - [What it checks](#what-it-checks)
  - [Run](#run)
  - [Design notes](#design-notes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# skill-validator

Validate framework skill definitions — YAML frontmatter, internal
link integrity, and placeholder conventions.

## What it checks

1. **YAML frontmatter** — Every `SKILL.md` must have a valid
   frontmatter block with required keys (`name`, `description`,
   `license`).
2. **Internal link integrity** — Relative markdown links between
   skill files and docs must point to existing files and anchors.
3. **Placeholder convention** — Skill docs must use `<PROJECT>`,
   `<upstream>`, and `<tracker>` instead of hardcoded project names.

## Run

From the repo root:

```bash
uv run --project tools/skill-validator --group dev pytest
```

Or install and run as CLI:

```bash
uv run --project tools/skill-validator --group dev skill-validate
```

## Design notes

- **stdlib-only** — no external dependencies. The frontmatter parser
  is a lightweight text heuristic rather than a full YAML loader,
  because the frontmatter in skills is intentionally simple.
- **Complements `check-placeholders.sh`** — both tools share the same
  forbidden-pattern and allowlist lists. `check-placeholders.sh` runs
  as a pre-commit hook; this package runs as pytest in CI.
