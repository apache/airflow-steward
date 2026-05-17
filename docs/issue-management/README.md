<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Issue management skill family](#issue-management-skill-family)
  - [Family boundary](#family-boundary)
  - [Skills](#skills)
  - [Adopter contract](#adopter-contract)
  - [Status](#status)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Issue management skill family

Maintainer-facing skills for projects with a general-issue tracker
(JIRA, GitHub Issues, Bugzilla, GitLab Issues). Five skills that
cover per-issue work, pool-level sweeps, and read-only reporting:

1. **Triage** — sweep open issues in the configured candidate pool,
   classify against the project's criteria, propose a disposition
   (BUG / FEATURE-REQUEST / NEEDS-INFO / DUPLICATE / INVALID /
   ALREADY-FIXED), execute on maintainer confirmation.
2. **Reassess** — sweep a configured pool of resolved or end-of-life
   issues and re-assess each against the current upstream codebase,
   surfacing silent fixes and partial fixes.
3. **Reproducer** — for a single issue identifying a code-level bug,
   extract the reporter's example code, adapt it to run on the
   current default branch, execute via the project's runtime, and
   compose a structured verdict. Read-only on the tracker.
4. **Fix-workflow** — for a triaged issue confirmed as a bug or
   feature, draft a fix PR (code change, regression test, commit
   message, PR description). Drafts only; the human committer
   reviews and pushes.
5. **Stats** — read-only dashboard over a directory of `verdict.json`
   files produced by reassess campaigns. Surfaces health rating,
   classification distribution, partial-fix surfaces, and per-component
   breakdowns.

## Family boundary

This family sits **alongside** two related families:

- [`pr-management-*`](../pr-management/README.md) handles the
  pull-request queue (open PRs, code review, queue stats). PRs are
  not issues; the skills there operate on a different tracker
  surface and apply different criteria.
- [`security-issue-*`](../security/README.md) handles the security-
  issue tracker, with confidentiality and CVE-allocation constraints
  the general-issue family does not need. A project may use both
  families against different trackers (private security repo;
  public general-issue JIRA).

A maintainer of a project with both an issue tracker and an active
PR flow typically uses both `issue-*` and `pr-management-*` families,
configured with different trackers.

## Skills

| Skill | Mode | Purpose |
|---|---|---|
| [`issue-triage`](../../.claude/skills/issue-triage/SKILL.md) | Triage | Per-issue classification + disposition proposal |
| [`issue-reassess`](../../.claude/skills/issue-reassess/SKILL.md) | Triage | Pool-level sweep of resolved / EOL issues for re-assessment |
| [`issue-reproducer`](../../.claude/skills/issue-reproducer/SKILL.md) | — | Per-issue extraction + execution of code examples |
| [`issue-fix-workflow`](../../.claude/skills/issue-fix-workflow/SKILL.md) | Drafting | Drafts a fix PR for a triaged issue |
| [`issue-reassess-stats`](../../.claude/skills/issue-reassess-stats/SKILL.md) | — | Read-only campaign dashboard |

Reproducer and stats sit outside the MISSION mode taxonomy; they
are mechanical / read-only, not classificatory or mutating.

## Adopter contract

The skills resolve project-specific content from these files in the
adopter's `<project-config>/` directory:

| File | Used by |
|---|---|
| [`project.md`](../../projects/_template/project.md) | all `issue-*` skills (identifiers, `upstream_default_branch`) |
| [`issue-tracker-config.md`](../../projects/_template/issue-tracker-config.md) | all `issue-*` skills (URL, project key, auth, default queries) |
| [`scope-labels.md`](../../projects/_template/scope-labels.md) | `issue-triage`, `issue-reassess` (component / area routing) |
| [`release-trains.md`](../../projects/_template/release-trains.md) | `issue-triage` (`@`-mention routing) |
| [`canned-responses.md`](../../projects/_template/canned-responses.md) | `issue-triage` (NEEDS-INFO templates) |

Additional template files added by this family (forthcoming):

- `runtime-invocation.md` — how to invoke the project's runtime;
  consumed by `issue-reproducer` for executing extracted code.
- `reassess-pool-defaults.md` — pool definitions extending the
  default queries in `issue-tracker-config.md`.
- `reproducer-conventions.md` — evidence-package directory layout
  for `issue-reproducer` output.

## Status

**Experimental.** No adopter pilot has run an evaluation against
this family yet. Shape may change between framework versions.

## Cross-references

- [Top-level README — Adopting the framework](../../README.md#adopting-the-framework) — 3-step bootstrap.
- [`projects/_template/README.md`](../../projects/_template/README.md) — adopter scaffold index.
- [`docs/modes.md`](../modes.md) — MISSION mode taxonomy that the
  `mode:` frontmatter field declares against.
- [`docs/setup/agentic-overrides.md`](../setup/agentic-overrides.md) —
  the override mechanism every skill in this family supports.
