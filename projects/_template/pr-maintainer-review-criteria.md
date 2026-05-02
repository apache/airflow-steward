<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — pr-maintainer-review criteria](#todo-project-name--pr-maintainer-review-criteria)
  - [Repo-wide source files](#repo-wide-source-files)
  - [Per-area source files](#per-area-source-files)
  - [Security-model calibration](#security-model-calibration)
  - [Backports / version-specific PRs](#backports--version-specific-prs)
  - [Section anchors](#section-anchors)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — pr-maintainer-review criteria

This file is the **navigation map** for the project's review
criteria — the source files the
[`pr-maintainer-review`](../../.claude/skills/pr-maintainer-review/SKILL.md)
skill reads when forming its findings. The framework does not
restate the rules; this file points at them.

The skill's review pass reads each source file at session start
(and re-reads per-area files as PRs route into different trees)
and quotes the **source rule verbatim** in any finding it raises.
If the file is missing or unreadable, the skill warns and falls
back to a smaller default rule set.

## Repo-wide source files

These apply to every PR regardless of which subtree it touches.
At least one entry is required.

| File | What it covers | Notes |
|---|---|---|
| TODO: e.g. `.github/instructions/code-review.instructions.md` | TODO: rule set every PR is reviewed against (architecture / DB / quality / testing / API / UI / generated files / AI-generated-code signals / quality signals) | |
| TODO: e.g. `AGENTS.md` | TODO: repo-wide AI/agent instructions (architecture boundaries, security model, coding standards, testing standards, commits & PR conventions) | |

## Per-area source files

Files that apply only when the PR touches a specific subtree.
The skill auto-discovers any `AGENTS.md` (or project-equivalent
filename) under the touched paths via `git ls-files`, but rows
listed here are **always** loaded even if the PR doesn't directly
touch the area — useful for files referenced by name throughout
the repo-wide rules.

| File | When it applies | Notes |
|---|---|---|
| TODO: e.g. `providers/AGENTS.md` | TODO: PR touches `providers/<name>/` | |
| TODO: e.g. `providers/elasticsearch/AGENTS.md` | TODO: PR touches `providers/elasticsearch/` | |

## Security-model calibration

A short doc the skill consults before flagging anything that
looks security-flavoured. Used to distinguish (a) actual
vulnerabilities, (b) known-but-documented limitations, (c)
deployment-hardening opportunities.

| File | Used by |
|---|---|
| TODO: e.g. `airflow-core/docs/security/security_model.rst` | The `Security model — calibration` section of the skill's review-flow.md |

## Backports / version-specific PRs

Pattern the skill uses to detect that a PR is a backport vs. a
main-branch change. Backports get a lighter-touch review focused
on diff parity and cherry-pick conflicts.

| Concept | Pattern | Notes |
|---|---|---|
| Backport branch pattern | TODO: e.g. `vX-Y-test` | Regex matched against the PR's base branch name. Skip if the project doesn't ship backport PRs. |

## Section anchors

For projects whose review docs are structured around named
sections (and where the skill should link out per-finding), list
the section anchor URLs the framework expects.

| Section | Anchor URL |
|---|---|
| Architecture boundaries | TODO |
| Database / query correctness | TODO |
| Code quality | TODO |
| Testing | TODO |
| API correctness | TODO |
| UI (React/TypeScript) | TODO (skip if no UI) |
| Generated files | TODO |
| AI-generated code signals | TODO |
| Quality signals to check | TODO |
| Commits and PRs (newsfragments, commit messages, tracking issues) | TODO |
| Security model | TODO |

(If the project's review-criteria doc isn't structured this way,
this section is optional — the skill will still load the source
files and quote rules verbatim, just without per-section deep
links.)
