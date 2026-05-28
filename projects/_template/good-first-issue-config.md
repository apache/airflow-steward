<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — good-first-issue authoring configuration](#todo-project-name--good-first-issue-authoring-configuration)
  - [Identifiers](#identifiers)
  - [Getting-started links](#getting-started-links)
  - [Out-of-scope topics](#out-of-scope-topics)
  - [AI-attribution footer](#ai-attribution-footer)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — good-first-issue authoring configuration

This file configures the
[`good-first-issue-author`](../../.claude/skills/good-first-issue-author/SKILL.md)
skill (Mentoring, `experimental`). Copy it into your own
`<project-config>/good-first-issue-config.md` and replace every
`<placeholder>` with your project's value. If a required key is missing,
the skill aborts and points back here rather than guessing.

## Identifiers

| Key | Value | Notes |
|---|---|---|
| `good_first_issue_label` | `good first issue` | The label proposed on the drafted issue. The skill proposes it; a maintainer applies it on confirmation. |
| `max_effort_hours` | `4` | Upper bound on the estimated effort a good first issue may carry. A candidate that clearly exceeds it is `scope-too-large`. |

## Getting-started links

Links the drafted issue points a newcomer at, by trigger. The skill links
these rather than paraphrasing them. Replace the example URLs with the
equivalent docs in your project; drop a row that does not apply.

| Trigger | Link | One-line label |
|---|---|---|
| Contributing guide | `<contributing-doc-url>` | How to contribute |
| Local setup | `<local-setup-doc-url>` | Set up a local dev environment |
| Opening a PR | `<pr-opening-doc-url>` | How to open a pull request |

## Out-of-scope topics

The skill always declines (decision `unsuitable`) when a candidate touches
one of these. Adjust for your project; the defaults below are typical of
an Apache project.

- Security-sensitive work (vulnerabilities, CVE-adjacent, embargoed)
- Deprecation or removal timing (which release drops X)
- Licensing questions (compatibility, header policy)
- Architectural taste on a project-specific subsystem

## AI-attribution footer

Appended verbatim to every drafted issue body, disclosing AI authorship.

```markdown
---

_This issue was drafted with the help of an AI-assisted tool and reviewed by a <PROJECT> maintainer before posting. If anything here is unclear or looks wrong, say so on the issue: a real person is reading._
```

Replace `<PROJECT>` with the project's display name (read from
[`<project-config>/project.md`](project.md)).
