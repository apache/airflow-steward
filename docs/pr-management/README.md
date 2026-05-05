<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [PR management skill family](#pr-management-skill-family)
  - [Skills](#skills)
  - [Adopter contract](#adopter-contract)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# PR management skill family

Maintainer-facing PR-queue management for projects with a public
contributor PR queue. Three skills that compose into a complete
triage + review pass:

1. **Triage** — sweep open PRs, classify against the project's
   quality criteria, propose a disposition (draft / comment /
   close / rebase / rerun / mark ready / ping), execute on
   maintainer confirmation.
2. **Stats** — read-only summary tables of the open PR backlog,
   grouped by area label, so the maintainer can see where queue
   pressure is sitting before / after a triage sweep.
3. **Code review** — deep, line-aware code review one PR at a
   time. Reads the diff, applies the project's review criteria,
   drafts an `APPROVE` / `REQUEST_CHANGES` / `COMMENT` review
   with inline comments, posts on confirmation.

Why a framework skill family? These skills were originally
maintained inside one ASF project's developer-tooling repo as
`breeze pr auto-triage` and `breeze pr stats` — useful for any
ASF project with a meaningful contributor-PR queue, but locked
behind that project's local toolchain. Lifting them into the
framework lets other adopters reuse the playbook with their own
[adopter-config files](../../projects/_template/) for project-specific
knobs (committers team handle, area-label prefix, comment-template
wording, CI-check → doc-URL map, review-criteria source files).

## Skills

| Skill | Purpose |
|---|---|
| [`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md) | First-pass triage. Successor to `breeze pr auto-triage`. |
| [`pr-management-stats`](../../.claude/skills/pr-management-stats/SKILL.md) | Read-only summary tables grouped by area label. |
| [`pr-management-code-review`](../../.claude/skills/pr-management-code-review/SKILL.md) | Deep code review, one PR at a time. |

## Adopter contract

The skills resolve project-specific content from these files in
the adopter's `<project-config>/` directory:

| File | Used by |
|---|---|
| [`pr-management-config.md`](../../projects/_template/pr-management-config.md) | `pr-management-triage`, `pr-management-stats` |
| [`pr-management-triage-comment-templates.md`](../../projects/_template/pr-management-triage-comment-templates.md) | `pr-management-triage` |
| [`pr-management-triage-ci-check-map.md`](../../projects/_template/pr-management-triage-ci-check-map.md) | `pr-management-triage` |
| [`pr-management-code-review-criteria.md`](../../projects/_template/pr-management-code-review-criteria.md) | `pr-management-code-review` |

The skills read project-specific defaults from the `<project-config>/`
files above. Adopters customise by editing their copy of each
template; illustrative examples in skill prose may still use the
patterns that motivated the framework (monorepo `<area>/` layout,
`area:*` labels, etc.) — the *behaviour* is config-driven, the
*example wording* is not.

## Cross-references

- [Top-level README — Adopting the framework](../../README.md#adopting-the-framework) — 3-step bootstrap.
- [`projects/_template/README.md`](../../projects/_template/README.md) — adopter scaffold index, including the four PR-management config files.
