<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — pr-management-triage configuration](#todo-project-name--pr-management-triage-configuration)
  - [Identifiers](#identifiers)
  - [Project-specific labels](#project-specific-labels)
  - [Grace windows](#grace-windows)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — pr-management-triage configuration

This file is the **per-project configuration** for the
[`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md) skill. The
framework's skill code reads it to learn project-specific
identifiers (committers team, area-label conventions, project-
specific labels) without baking any one project's flavor into the
framework.

Grep for `TODO` to see every field still to fill in:

```bash
grep -n TODO <project-config>/pr-management-config.md
```

## Identifiers

| Key | Value | Used by |
|---|---|---|
| `committers_team` | TODO: e.g. `apache/foo-committers` | `classify-and-act.md` row F5b — team-mention detection. Used to recognise PR comments that `@`-mention the project's committers as a maintainer-to-maintainer ping. |
| `area_label_prefix` | TODO: e.g. `area:` (default) | `classify-and-act.md`, `pr-management-stats` — area-label grouping. Set to whatever prefix the project uses on its area/scope labels. |

## Project-specific labels

Labels the skill applies or watches for. Each row maps a generic
**framework concept** to whatever label string the adopter uses.
If the project doesn't have a given concept, leave the value blank
and the skill will skip that row of decision-table actions.

| Concept | Label | Notes |
|---|---|---|
| `ready_for_maintainer_review` | TODO: e.g. `ready for maintainer review` | Applied by the `mark-ready` action; used by `pr-management-code-review` as a default selector. |
| `quality_violations_close` | TODO: e.g. `quality violations - closed` | Applied when a PR is closed for failing the project's PR quality criteria after multiple opportunities to fix. |
| `suspicious_changes` | TODO: e.g. `suspicious changes` | Applied to first-time-contributor workflow approvals where the diff looks suspicious (binary blobs, unrelated CI changes, etc.). |
| `work_in_progress` | TODO: e.g. `WIP` (or blank if the project doesn't use a WIP label) | Trips the skill's "leave alone" decision for in-progress PRs. |

## Grace windows

Tunable thresholds. Defaults are reasonable starting points for
projects with airflow-shaped contributor traffic; raise them for
slower-moving projects.

| Concept | Default | Project value |
|---|---|---|
| Stale-draft close threshold | 30 days | TODO |
| Inactive-open → draft threshold | 14 days | TODO |
| Stale-review-ping cooldown | 7 days | TODO |
| Stale-workflow-approval threshold | 7 days | TODO |
