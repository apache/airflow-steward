<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Apache Airflow — pr-management-code-review criteria](#apache-airflow--pr-management-code-review-criteria)
  - [Repo-wide source files](#repo-wide-source-files)
  - [Per-area source files](#per-area-source-files)
  - [Security-model calibration](#security-model-calibration)
  - [Backports / version-specific PRs](#backports--version-specific-prs)
  - [Section anchors](#section-anchors)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Apache Airflow — pr-management-code-review criteria

This file is the **navigation map** for the Apache Airflow
project's review criteria — the source files the
[`pr-management-code-review`](../../.claude/skills/pr-management-code-review/SKILL.md)
skill reads when forming its findings.  New adopters should copy
this file into their own
`<project-config>/pr-management-code-review-criteria.md` and
replace every Airflow-specific path with their project's
equivalents.

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
| `.github/instructions/code-review.instructions.md` | The rule set every Apache Airflow PR is reviewed against (architecture / DB / quality / testing / API / UI / generated files / AI-generated-code signals / quality signals). | |
| `AGENTS.md` | Repo-wide AI/agent instructions (architecture boundaries, security model, coding standards, testing standards, commits & PR conventions). | |

## Per-area source files

Files that apply only when the PR touches a specific subtree.
The skill auto-discovers any `AGENTS.md` under the touched paths
via `git ls-files`, but rows listed here are **always** loaded
even if the PR doesn't directly touch the area.

| File | When it applies | Notes |
|---|---|---|
| `registry/AGENTS.md` | PR touches `registry/` | Registry-tree-specific rules. |
| `dev/AGENTS.md` | PR touches `dev/` | `dev/` scripts conventions. |
| `dev/ide_setup/AGENTS.md` | PR touches `dev/ide_setup/` | IDE bootstrap conventions. |
| `providers/AGENTS.md` | PR touches `providers/<name>/` | Provider-tree boundary, compat-layer, and provider-yaml expectations. |
| `providers/elasticsearch/AGENTS.md` | PR touches `providers/elasticsearch/` | Elasticsearch-specific rules. |
| `providers/opensearch/AGENTS.md` | PR touches `providers/opensearch/` | OpenSearch-specific rules. |

## Security-model calibration

A short doc the skill consults before flagging anything that
looks security-flavoured. Used to distinguish (a) actual
vulnerabilities, (b) known-but-documented limitations, (c)
deployment-hardening opportunities.

| File | Used by |
|---|---|
| `airflow-core/docs/security/security_model.rst` | The `Security model — calibration` section of the skill's review-flow.md |

## Backports / version-specific PRs

Pattern the skill uses to detect that a PR is a backport vs. a
main-branch change. Backports get a lighter-touch review focused
on diff parity and cherry-pick conflicts.

| Concept | Pattern | Notes |
|---|---|---|
| Backport branch pattern | `v\d+-\d+-test` | Regex matched against the PR's base branch name (e.g. `v3-0-test`). |

## Section anchors

For projects whose review docs are structured around named
sections, list the section anchor URLs the framework expects.
These are used when the skill links out per-finding.

| Section | Anchor URL |
|---|---|
| Architecture boundaries | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#architecture-boundaries` |
| Database / query correctness | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#database-and-query-correctness` |
| Code quality | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#code-quality-rules` |
| License headers | `https://www.apache.org/legal/src-headers.html` |
| Testing | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#testing-requirements` |
| API correctness | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#api-correctness` |
| UI (React/TypeScript) | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#ui-code-reacttypescript` |
| Generated files | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#generated-files` |
| AI-generated code signals | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#ai-generated-code-signals` |
| Quality signals to check | `https://github.com/apache/airflow/blob/main/.github/instructions/code-review.instructions.md#quality-signals-to-check` |
| Commits and PRs (newsfragments, commit messages, tracking issues) | `https://github.com/apache/airflow/blob/main/AGENTS.md#commits-and-prs` |
| Security model | `https://github.com/apache/airflow/blob/main/AGENTS.md#security-model` |
| Third-party license compliance | `https://www.apache.org/legal/resolved.html` |
| Applying the Apache licence | `https://www.apache.org/legal/apply-license.html` |
