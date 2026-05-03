<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — pr-management-triage comment templates](#todo-project-name--pr-management-triage-comment-templates)
  - [Project-specific URLs](#project-specific-urls)
  - [Quality-criteria marker string](#quality-criteria-marker-string)
  - [AI-attribution footer](#ai-attribution-footer)
  - [Template bodies](#template-bodies)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — pr-management-triage comment templates

This file is the **per-project comment-body library** for the
[`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md) skill. The
framework's [`comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md)
documents what each template **must** contain (the contract); this
file is where the adopter declares the project's actual wording,
URLs, and tone.

Each template body is what gets posted on a contributor PR — keep
the tone polite, link to the project's authoritative quality
criteria, and stay consistent across templates so contributors
recognise the voice across repeated triage cycles.

## Project-specific URLs

Plug these placeholders into the templates below. The framework's
[`comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md)
references each by name.

| Placeholder | Project value |
|---|---|
| `<quality_criteria_url>` | TODO: e.g. `https://github.com/apache/foo/blob/main/contributing-docs/05_pull_requests.rst#pull-request-quality-criteria` — the canonical "PR quality criteria" doc the AI footer + violations links point at. |
| `<two_stage_triage_rationale_url>` | TODO: e.g. `https://github.com/apache/foo/blob/main/contributing-docs/25_maintainer_pr_triage.md#why-the-first-pass-is-automated` — the "why is first-pass triage automated" rationale the AI footer links at. |
| `<project_display_name>` | TODO: e.g. `Apache Foo` — used in the AI footer ("an Apache Foo maintainer — a real person…"). |

## Quality-criteria marker string

The framework uses a literal string to detect already-triaged PRs
(searches the PR body and comments for it). **Do not paraphrase**:
the same exact string must appear verbatim in every triage comment
the skill posts, and the `pr-management-stats` skill uses the same marker for
"is this PR triaged" detection.

| Concept | Default value | Project value |
|---|---|---|
| Triage-marker visible link text | `Pull Request quality criteria` | TODO (default works; only override if the project's wording differs) |

## AI-attribution footer

The verbatim block appended to every contributor-facing comment
(see [`comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md#ai-attribution-footer)
for the rules — always-include, never-paraphrase, render at end of
body). Customise the **wording** for the project but keep the
**structure** (italicised meta-block, link to two-stage-triage
rationale).

```markdown
---

_Note: This comment was drafted by an AI-assisted triage tool and may contain mistakes. Once you have addressed the points above, a TODO: `<project_display_name>` maintainer — a real person — will take the next look at your PR. We use this [two-stage triage process](TODO: <two_stage_triage_rationale_url>) so that our maintainers' limited time is spent where it matters most: the conversation with you._
```

## Template bodies

The framework's [`comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md)
documents the seven template categories the skill emits:

1. `draft` — convert-to-draft body
2. `comment-only` — non-draft violations comment
3. `close` — close-with-quality-violations body
4. `review-nudge` — stale-review ping
5. `reviewer-ping` — explicit reviewer ping
6. `mark-ready-with-ping` — mark-ready handoff
7. `stale-draft-close` / `inactive-to-draft` / `stale-workflow-approval` — sweep-style bodies
8. `suspicious-changes` — first-time-contributor workflow flag (no AI footer)

For each one, see the framework file for the **structural contract**
(must-include sections, ordering, footer rules) and add the
project's actual wording below. Default airflow-flavored bodies
ship in the framework; adopters override here.

```markdown
TODO: project's draft-comment body here.

…
```

(For now the framework's defaults are airflow-shaped. Until the
follow-up PR completes the extraction, your skills will run with
the airflow-flavored content unless this file overrides specific
sections — see the open follow-up issue for the exact override
points the framework will read.)
