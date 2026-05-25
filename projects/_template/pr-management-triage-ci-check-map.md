<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — pr-management-triage CI-check to doc-URL map](#todo-project-name--pr-management-triage-ci-check-to-doc-url-map)
  - [Table](#table)
  - [Notes](#notes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — pr-management-triage CI-check to doc-URL map

This file is the **CI-check categorisation table** for the
[`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md) skill's
violations comments. It holds the concrete mapping for your
adopter project.

Copy this file into your own
`<project-config>/pr-management-triage-ci-check-map.md` and
replace the `<placeholder>` URLs with your project's
documentation paths. Add or adjust rows so the patterns match
the GitHub check names your CI actually emits.

## Table

Each row maps a **GitHub check name pattern** (case-insensitive
substring match) to a **human-readable category name** the skill
prints in the violations comment, plus a **doc URL** the skill
links to.

The rows below are common starting points across Python / cloud-
native projects. Add project-specific rows above the catch-all
(`*`) row, and order more-specific patterns above broader ones —
the skill matches first-found, so a row scoped to a sub-project
must precede the generic prefix row if you want them split out
in the violations comment.

| Pattern | Category | Doc URL |
|---|---|---|
| `static checks`, `pre-commit`, `prek` | Pre-commit / static checks | `<static-checks-doc-url>` |
| `ruff` | Ruff (linting / formatting) | `<static-checks-doc-url>` |
| `mypy-` | mypy (type checking) | `<static-checks-doc-url>` |
| `unit test`, `test-` | Unit tests | `<unit-tests-doc-url>` |
| `docs`, `spellcheck-docs`, `build-docs` | Build docs | `<docs-building-doc-url>` |
| `helm` | Helm tests | `<helm-tests-doc-url>` |
| `k8s`, `kubernetes` | Kubernetes tests | `<k8s-tests-doc-url>` |
| `build ci image`, `build prod image`, `ci-image`, `prod-image` | Image build | `<image-build-doc-url>` |
| `*` (catch-all) | Other failing CI checks | `<static-checks-doc-url>` |

Add additional rows for project-specific check-name patterns
above the catch-all. For example, a project with a plugin /
extension subsystem typically wants a row matching the relevant
GitHub check names (`<your-plugin-tag>`, `<extension-name>`,
etc.) pointing at the corresponding contributing doc:

```markdown
| `<your-check-name-substring>` | <Human category> | <doc-url> |
```

## Notes

- **Order matters.** The skill matches first-found; more-specific
  patterns are listed above broader ones (e.g. `mypy-<sub-project>`
  matches the `mypy-` row, so put `<sub-project>`-scoped patterns
  above the generic `mypy-` row if you want them split out).
- **Mergeability fallback.** If the PR has `mergeable ==
  CONFLICTING`, the skill emits a separate "Merge conflicts"
  category linking to the project's git / rebase doc:

| Concept | Doc URL |
|---|---|
| Merge conflicts (rebase guide) | `<git-rebase-doc-url>` |

- **Failing-CI fallback.** If `checks_state == FAILURE` but no
  failed check names are extractable, the skill emits a generic
  "Failing CI checks" entry pointing at the same doc URL as the
  catch-all row above.
