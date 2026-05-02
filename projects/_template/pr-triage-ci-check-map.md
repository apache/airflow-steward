<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — pr-triage CI-check to doc-URL map](#todo-project-name--pr-triage-ci-check-to-doc-url-map)
  - [Table](#table)
  - [Notes](#notes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — pr-triage CI-check to doc-URL map

This file is the **CI-check categorisation table** for the
[`pr-triage`](../../.claude/skills/pr-triage/SKILL.md) skill's
violations comments. When a PR has failing CI checks, the skill
groups the failures by category (static checks, tests, image
builds, etc.) and links each category to the project's
documentation for that area.

The framework reads this table at session start; without it, the
skill falls back to a generic "see CI for details" link.

## Table

Each row maps a **GitHub check name pattern** (case-insensitive
substring match) to a **human-readable category name** the skill
prints in the violations comment, plus a **doc URL** the skill
links to.

| Pattern | Category | Doc URL |
|---|---|---|
| TODO: e.g. `static checks` | TODO: e.g. `Pre-commit / static checks` | TODO: e.g. `https://github.com/apache/foo/blob/main/contributing-docs/08_static_code_checks.rst` |
| TODO: e.g. `ruff` | Ruff (linting / formatting) | TODO |
| TODO: e.g. `mypy-` | mypy (type checking) | TODO |
| TODO: e.g. `unit test`, `test-` | Unit tests | TODO |
| TODO: e.g. `docs`, `spellcheck-docs`, `build-docs` | Build docs | TODO |
| TODO: e.g. `helm` | Helm tests | TODO (skip if not applicable) |
| TODO: e.g. `k8s`, `kubernetes` | Kubernetes tests | TODO (skip if not applicable) |
| TODO: e.g. `build ci image`, `build prod image`, `ci-image`, `prod-image` | Image build | TODO (skip if not applicable) |
| TODO: e.g. `provider` | Provider tests | TODO (skip if not applicable) |
| `*` (catch-all) | `Other failing CI checks` | TODO: catch-all link to the project's static-checks or contributing doc |

## Notes

- **Order matters.** The skill matches first-found; put more-
  specific patterns above broader ones (e.g. `mypy-airflow-core`
  before bare `mypy`).
- **Mergeability fallback.** If the PR has `mergeable ==
  CONFLICTING`, the skill emits a separate "Merge conflicts"
  category linking to the project's git/rebase doc — declare
  that link here too:

| Concept | Doc URL |
|---|---|
| Merge conflicts (rebase guide) | TODO: e.g. `https://github.com/apache/foo/blob/main/contributing-docs/10_working_with_git.rst` |

- **Failing-CI fallback.** If `checks_state == FAILURE` but no
  failed check names are extractable, the skill emits a generic
  "Failing CI checks" entry pointing at the same doc URL as the
  catch-all row above.
