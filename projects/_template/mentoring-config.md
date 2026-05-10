<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Apache Airflow — mentoring (Mentoring) configuration](#apache-airflow--mentoring-mentoring-configuration)
  - [Identifiers](#identifiers)
  - [Convention pointers](#convention-pointers)
  - [Out-of-scope topics](#out-of-scope-topics)
  - [AI-attribution footer](#ai-attribution-footer)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Apache Airflow — mentoring (Mentoring) configuration

**This file is a placeholder ahead of the Mentoring skill landing.**
The skill does not exist yet (Mentoring is proposed per
[`docs/modes.md`](../../docs/modes.md#mentoring)).
The keys below match the
[Mentoring spec](../../docs/mentoring/spec.md#adopter-contract)
and are the values the future skill will read. New adopters
should copy this file into their own
`<project-config>/mentoring-config.md` and replace every
Airflow-specific value with their project's equivalents.

## Identifiers

| Key | Value |
|---|---|
| `mentoring_invocation_command` | `/pr-management-mentor` |
| `maintainer_team_handle` | `@apache/airflow-committers` |
| `max_agent_turns` | `2` |

## Convention pointers

Triggers that the future skill will detect, mapped to the docs
link the comment should reference instead of paraphrasing.

| Trigger | Link | One-line label |
|---|---|---|
| Missing version on bug report | https://airflow.apache.org/docs/apache-airflow/stable/start.html | "How to find your Airflow version" |
| Missing repro | https://github.com/apache/airflow/blob/main/contributing-docs/03_contributors_quick_start.rst | "Contributors quick start" |
| First-time contributor PR setup | https://github.com/apache/airflow/blob/main/contributing-docs/05_pull_requests.rst | "How to open a PR" |

## Out-of-scope topics

The skill always hands off to a human when the thread touches:

- Security-sensitive design (CVE-adjacent, embargoed work)
- Deprecation timing (which release will drop X)
- License questions (compatibility, header policy)
- Provider-specific architectural taste

## AI-attribution footer

```markdown
---

_Note: This comment was drafted by an AI-assisted mentoring tool and may contain mistakes. Once you have addressed the points above, an Apache Airflow maintainer — a real person — will take the next look. We use this [two-stage process](https://github.com/apache/airflow/blob/main/PROCESS.md) so that our maintainers' limited time is spent where it matters most: the conversation with you._
```

Replace the two-stage-process URL with the project's documented
mentoring/triage policy. Replace `Apache Airflow` with the
project name.
