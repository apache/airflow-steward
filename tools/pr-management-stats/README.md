<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [pr-management-stats reference implementation](#pr-management-stats-reference-implementation)
  - [Layout](#layout)
  - [Invocation](#invocation)
  - [Contract for the agent](#contract-for-the-agent)
  - [Parity implementations](#parity-implementations)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# pr-management-stats reference implementation

Deterministic reference implementation of the data-fetch +
classification contract that backs the
[`pr-management-stats`](../../.claude/skills/pr-management-stats/SKILL.md) skill.

The skill's agent-emitted render is the **default** — this script
exists for two reasons:

1. **Anti-skip insurance.** Agents under context pressure can be
   tempted to omit panels from the dashboard (line charts, CODEOWNERS
   table, triager-activity table). The skill specifies all 11 panels;
   agents must render them all. This script encodes the canonical
   data-fetch shape so the agent has a single source of truth to read
   the fields from — there is no "the skill says X, the agent guessed
   Y" drift.

2. **CI-renderable artefact.** Adopters who want a daily dashboard
   rendered by CI (rather than an interactive agent session) can run
   this script on a schedule, extend it with the full render per
   [`render.md`](../../.claude/skills/pr-management-stats/render.md),
   and publish the HTML as a build artefact or gist.

## Layout

```text
tools/pr-management-stats/
├── README.md     (this file)
└── reference.py  (Python implementation: fetch + classify + emit intermediates)
```

## Invocation

```bash
python3 tools/pr-management-stats/reference.py \
    --repo <upstream> \
    --viewer <maintainer-handle> \
    --since 2026-04-12 \
    --out /tmp/dashboard.html
```

The script:

1. Fetches all open PRs with the **full engagement schema**
   (`comments`, `latestReviews`, `reviewThreads`, `timelineItems`
   with `LABELED_EVENT`/`READY_FOR_REVIEW_EVENT`/`CONVERT_TO_DRAFT_EVENT`).
2. Fetches closed/merged PRs since the cutoff.
3. Fetches `.github/CODEOWNERS` + changed-file paths for each
   currently-ready PR.
4. Classifies each PR per
   [`classify.md`](../../.claude/skills/pr-management-stats/classify.md) —
   `is_engaged` requires ANY maintainer touch (issue comment, review,
   review-thread comment, label add, draft conversion).
5. Writes a JSON sidecar with all the counts that feed the dashboard.

## Contract for the agent

When the agent invokes the skill, it MUST:

- Use the GraphQL templates from [`fetch.md`](../../.claude/skills/pr-management-stats/fetch.md) verbatim. **In particular, the open-PRs query MUST include `reviewThreads` and `latestReviews` and `timelineItems`** — without those, the `is_engaged` predicate is undercounted and untriaged numbers blow up artificially. (Earlier iterations of `fetch.md` claimed those fields were not needed for stats; that was a documentation bug and has been corrected.)
- Implement ALL 11 sections per [`render.md`](../../.claude/skills/pr-management-stats/render.md). Skipping panels (e.g. dropping the line charts, CODEOWNERS table, triager-activity table) is **not** an acceptable simplification.
- If panel data is unavailable, the panel renders a stub with a one-line explanation of WHY the data is missing — never omit a section silently.

## Parity implementations

This script is a fetch + classify reference. The full render lives
in the agent-emitted version per `render.md`. Adopters who want a
deterministic CI-runnable equivalent should extend this script with
the aggregation + HTML emission directly; we welcome PRs.

## Cross-references

- [`pr-management-stats/SKILL.md`](../../.claude/skills/pr-management-stats/SKILL.md) — skill entry point.
- [`pr-management-stats/classify.md`](../../.claude/skills/pr-management-stats/classify.md) — `is_engaged` / `is_triaged` / `is_untriaged` predicates.
- [`pr-management-stats/fetch.md`](../../.claude/skills/pr-management-stats/fetch.md) — GraphQL templates.
- [`pr-management-stats/aggregate.md`](../../.claude/skills/pr-management-stats/aggregate.md) — per-panel computations.
- [`pr-management-stats/render.md`](../../.claude/skills/pr-management-stats/render.md) — dashboard layout, recommendation rules.
- [`tools/dashboard-generator/`](../dashboard-generator/) — sibling reference implementation for `issue-reassess-stats`.
