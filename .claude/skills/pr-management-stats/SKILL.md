---
name: pr-management-stats
description: |
  Read-only maintainer dashboard for open-PR backlog of <upstream>.
  Surfaces health rating, prioritised action recommendations, weekly
  closure velocity trends, area pressure ranking, triage-funnel
  breakdown — area-grouped tables collapsed at bottom.
when_to_use: |
  When user asks "how is the PR queue doing", "run PR stats", "what
  should I do today", "show me the trends", "where is queue pressure
  sitting", or any variation on "give me maintainer view of backlog".
  Daily health check, before/after triage sweep, planning-session
  input.
license: Apache-2.0
---

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!-- Placeholder convention:
     <repo>   → target GitHub repo, `owner/name` form (default: <upstream>)
     <viewer> → authenticated GitHub login of maintainer running skill
     Substitute before any `gh` command. -->

# pr-management-stats

Read-only. Answers "what should maintainer **do** about open-PR
backlog now". Output = **dashboard**, 5 sections:

| Section | Shows | Use |
|---|---|---|
| **Hero cards** | Health rating, total open, ready-for-review count, untriaged-non-drafts (>4w callout) | At-a-glance |
| **What needs attention** | Prioritised actions (high/med/low) + slash command | Pick next hour's work |
| **Closure velocity** | Per-week merged/closed bars, last 6w + avg/peak | Spot slowdowns / bursts |
| **Pressure by area** | `area:*` ranked by weighted untriaged-old PR count | Pick focused triage / review session |
| **Triage funnel** | Triage coverage %, author response rate %, stalest bucket, this-week velocity | Funnel health |

Original two tables (**Triaged final-state since cutoff**,
**Triaged still-open by area**) → collapsible details at bottom.

Statistical complement of [`pr-management-triage`](../pr-management-triage/SKILL.md).
Same repo, same classification, no mutations. Stats → triage →
stats sequence measures sweep effect; recommendations link back to
specific `pr-management-triage` invocations.

Detail files:

| File | Purpose |
|---|---|
| [`fetch.md`](fetch.md) | GraphQL templates: open-PR list, closed/merged-since-cutoff list. |
| [`classify.md`](classify.md) | Triage-status detection (waiting / responded / never-triaged) — reuses `Pull Request quality criteria` marker from `pr-management-triage`. Defines per-PR `pressure_weight`. |
| [`aggregate.md`](aggregate.md) | Area grouping, age buckets, totals, % rules. Weekly velocity buckets, area pressure scores, health-rating thresholds. |
| [`render.md`](render.md) | Dashboard layout (hero/actions/trends/hotspots/details), tables, colour scheme, recommendation rules. |

---

## Adopter overrides

Top of run, skill consults
[`.apache-steward-overrides/pr-management-stats.md`](../../../docs/setup/agentic-overrides.md)
in adopter repo if exists; applies agent-readable overrides. See
[`docs/setup/agentic-overrides.md`](../../../docs/setup/agentic-overrides.md)
for contract.

**Hard rule**: agents NEVER modify snapshot under
`<adopter-repo>/.apache-steward/`. Local mods → override file.
Framework changes → PR to `apache/airflow-steward`.

---

## Snapshot drift

Top of run, skill compares gitignored
`.apache-steward.local.lock` (per-machine fetch) against committed
`.apache-steward.lock` (project pin). Mismatch → surface gap +
propose [`/setup-steward upgrade`](../setup-steward/upgrade.md).
Non-blocking — user may defer. See
[`docs/setup/install-recipes.md` § Subsequent runs and drift detection](../../../docs/setup/install-recipes.md#subsequent-runs-and-drift-detection).

Drift severity:

- **method/URL differ** → ✗ full re-install.
- **ref differs** (project bumped tag, or `git-branch` local
  behind upstream tip) → ⚠ sync.
- **`svn-zip` SHA-512 mismatches committed anchor** → ✗
  security-flagged; investigate before upgrade.

---

## Adopter config

Reads same area-label prefix + triage-marker string from
[`pr-management-triage` adopter config](../pr-management-triage/SKILL.md#adopter-configuration):

- [`<project-config>/pr-management-config.md → area_label_prefix`](../../../projects/_template/pr-management-config.md) — drives area grouping in both stats tables.
- [`<project-config>/pr-management-triage-comment-templates.md → Triage-marker visible link text`](../../../projects/_template/pr-management-triage-comment-templates.md) — literal string classifying PR as triaged. **Both `pr-management-triage` and `pr-management-stats` must agree** on this string. Default: `Pull Request quality criteria`.

No `pr-management-stats`-specific config — read-only, inherits
from `pr-management-triage` contract.

---

## Golden rules

**1 — no mutations, ever.** Read-only. No comments, labels,
close, rebase, approve. Maintainer asks for stats + action →
decline mutation, redirect to `pr-management-triage`.

**2 — reuse pr-management-triage triage-detection.** "Triaged"
+ "responded" counts depend on same `Pull Request quality
criteria` marker + same collaborator set
(`OWNER`/`MEMBER`/`COLLABORATOR`) driving triage-marker rows in
`pr-management-triage/classify-and-act.md` (rows 3–4 —
`already_triaged`). No second definition. Both skills agree on
"is this PR triaged".

**3 — one GraphQL call per batch, not per PR.** Same as
`pr-management-triage/fetch-and-batch.md`. One aliased query →
open-PR list per page; closed/merged fetch paginated by GitHub
search cursor. Never `gh pr view` per PR.

**4 — legend with every render.** Tables dense (15+ cols on
still-open table). Print short legend after tables: `Contrib.`
= non-collaborator; `Responded` = author replied after triage
comment; `Drafted by triager` = PR converted to draft by viewer;
etc. Hero cards + recommendations self-explanatory — no legend
there. Legend covers collapsed "Detailed tables".

**5 — state input scope up front.** Before render, one line:
repo name, total open PR count, closed-since cutoff date, viewer
login. Numbers need context.

**6 — recommendations deterministic, not opinions.** Every
action in "What needs attention" panel comes from fixed rule in
[`render.md#recommendation-rules`](render.md). Never editorialise
("queue is doing well", "you should focus on X"). Surface rule
trigger + suggested next-step command. Maintainer reads trigger,
decides. New rules → edit rules table, no free-text in renderer.

**7 — actions link to other skills, never mutate.** Every
recommendation `action` = exact slash-command maintainer pastes
to do the work. Almost always `/pr-management-triage`,
`/maintainer-review`, or focused variant with label/PR-number
filter. Stats skill = pure-read (Rule 1). Dashboard makes
downstream skills *one paste away*.

---

## Inputs

Optional selectors:

| Selector | Resolves to |
|---|---|
| *(no args)* | default — all open PRs on `<upstream>`, closed/merged since configured cutoff |
| `repo:<owner>/<name>` | override target repo |
| `since:YYYY-MM-DD` | override closed-since cutoff (default: 6 weeks ago) |
| `clear-cache` | invalidate scratch cache before fetch |

No per-PR drill-in — aggregate-only.

---

## Step 0 — Pre-flight

1. `gh auth status` succeeds; capture viewer login (needed for
   triage-marker check, step 2).
2. One GraphQL query asking both `viewer { login }` +
   `repository(owner, name) { name }` → confirms repo
   reachable. `viewerPermission` NOT required (no mutations) —
   skip write-check `pr-management-triage` does.
3. Read/init scratch cache at
   `/tmp/pr-management-stats-cache-<repo-slug>.json` (see
   [`aggregate.md#cache`](aggregate.md)). Stores viewer login +
   `pr_number → (head_sha, triage_status)` map → re-run in same
   session skips per-PR enrichment.

Step 1 fail → **stop**. Steps 2/3 degrade with warnings.

---

## Step 1 — Fetch open PRs

Query template: [`fetch.md#open-prs`](fetch.md). Every open PR
with fields needed for classification: labels, `isDraft`,
`authorAssociation`, `createdAt`, last commit `committedDate`,
last 10 comments for triage-marker scan.

Paginate until `pageInfo.hasNextPage == false`. Batch 50 safe
(open-PR selection lighter than `pr-management-triage`'s — no
`statusCheckRollup`, no `reviewThreads`, no `latestReviews`).
300-PR backlog → 6 GraphQL calls.

---

## Step 2 — Classify triage status per PR

Per open PR, determine:

- `is_triaged_waiting` — viewer's (or any collaborator's)
  comment contains `Pull Request quality criteria` marker;
  comment post-dates PR's last commit; author has NOT commented
  after.
- `is_triaged_responded` — same marker; author HAS commented
  after.
- `is_drafted_by_triager` — PR converted to draft by viewer at
  or after triage comment (`ConvertToDraftEvent` timeline,
  optional — see [`classify.md#drafted-by-triager`](classify.md)
  for cheaper heuristic).
- `last_author_interaction_at` — most recent
  `commit.committedDate` OR author comment `createdAt`,
  whichever later.

Cache per `(pr_number, head_sha)` → subsequent run skips scan.

---

## Step 3 — Fetch closed/merged triaged PRs since cutoff

Second table = separate search. Closed or merged PRs whose
comment history contains triage marker since configured cutoff.
Template: [`fetch.md#closed-merged-triaged`](fetch.md).

Cutoff default `today - 6 weeks`. Configurable: "how did last
week's sweep do" → `since:today-7d`; monthly report →
`since:today-30d`.

---

## Step 4 — Aggregate by area

Group each PR by every `area:*` label it carries. PR with
`area:UI` + `area:scheduler` → both groups. PR with no
`area:*` → pseudo-area `(no area)`.

Per area, counters in [`aggregate.md#counters`](aggregate.md):
total, drafts, non-drafts, contributors, triaged-waiting,
triaged-responded, ready-for-review, drafted-by-triager + age-
bucket histograms.

`TOTAL` row: each PR counted exactly once (NOT sum of per-area
counters — multi-`area:*` PRs would double-count).

---

## Step 5a — Health rating + action recommendations

Pure fn of classified open-PR set. No network.

1. Apply **health rating** thresholds from
   [`aggregate.md#health-rating`](aggregate.md): each fired
   threshold = "issue point". Total points → `✅ Healthy` /
   `⚠️ Needs attention` / `🔥 Action needed`.
2. Walk **recommendation rules** from
   [`render.md#recommendation-rules`](render.md) in declared
   order. Each fired rule → entry with `priority`, `icon`,
   `title`, `detail`, `action` (exact slash command), count.
3. Recommendation list → "What needs attention" panel. Zero
   rules fire → surface explicit "no urgent actions detected"
   panel; never empty.

---

## Step 5b — Weekly velocity buckets

Pure fn of closed/merged-since-cutoff PR set.

Last 6 weeks (rolling, anchored on fetch-start `<now>`): bucket
PRs by `closedAt`; count `merged` + `closed` separately. Also
count triaged-then-merged / triaged-then-closed /
triaged-then-responded subsets → trend mini-stats below
velocity bars.

See [`aggregate.md#weekly-velocity`](aggregate.md) for exact
bucket boundaries + avg/peak summary computation.

---

## Step 5c — Opened-vs-closed weekly buckets

Pure fn of *both* open-PR set (Step 1) + closed/merged-since-
cutoff PR set (Step 3). Every PR's `createdAt` checked against
each weekly window regardless of current state.

Same six rolling weekly windows, compute:

- `opened` — PR `createdAt` in window
- `closed_total` — PR closed/merged in window (reuses Step 5b
  velocity buckets)
- `net_delta = opened - closed_total`

Per-week numbers → "Opened vs closed momentum" line chart +
two-line "Net delta" summary. See
[`aggregate.md#opened-vs-closed-weekly-buckets`](aggregate.md).

---

## Step 5d — Ready-for-review trend by top areas

Needs one extra fetch
([`fetch.md#ready-label-timeline`](fetch.md)): per currently-
`ready for maintainer review` PR, timestamp of most recent
`LabeledEvent` adding that label. Aliased GraphQL, ~30 PRs/call.

Per top-pressure area (top 5 by Step 5f score, filtered to
areas with ≥3 currently-ready PRs), 6-bucket cumulative count:
`ready_count[a][w] = count of currently-ready PRs in area a
where labeled_at <= w.end`.

Feeds "Ready-for-review trend" multi-line chart. See
[`aggregate.md#ready-for-review-trend-by-top-areas`](aggregate.md).

---

## Step 5e — Closed-by-triage-reason buckets

Pure fn of closed/merged-since-cutoff PR set (Step 3) — reuses
per-PR `is_triaged` / `responded_before_close` / `merged` flags.

Per weekly bucket, classify each closed PR into exactly one of
four categories: `merged`, `closed-after-responded`,
`closed-after-triage-no-response`, `closed-no-triage`. Sum per
category per week.

Feeds "Closed-by-triage-reason per week" stacked bar chart. See
[`aggregate.md#closed-by-triage-reason-per-week`](aggregate.md)
for category definitions, colour map, summary line.

---

## Step 5f — Area pressure scores

Pure fn of classified open-PR set.

Per area, **pressure score** = weighted sum of urgent PR
conditions. Weights in
[`aggregate.md#pressure-score`](aggregate.md):

- untriaged non-draft, >4w → 5 pts
- untriaged non-draft, 1–4w → 3 pts
- untriaged non-draft, <1w → 1 pt
- triaged-waiting, >7d → 2 pts (author abandoned, sweep
  candidate)
- ready-for-review (label present) → 1 pt (queue waiting on
  maintainer review)
- everything else → 0 pts (drafts maintainer ignores until
  author engages)

Sort areas by score desc; render top 8 (filter areas with <3
contributor PRs as noise) in "Pressure by area" panel.

---

## Step 6 — Render dashboard

Layout: [`render.md#dashboard-layout`](render.md):

1. **Context line** — repo, open count, cutoff, viewer,
   timestamp.
2. **Hero cards (4)** — health rating, total open, ready
   count, untriaged-non-draft count.
3. **What needs attention** — recommendation list from Step 5a.
4. **Closure velocity** — weekly bar chart from Step 5b.
5. **Opened vs closed momentum** — line chart from Step 5c.
6. **Ready-for-review trend** — multi-line chart from Step 5d
   (top areas).
7. **Closed by triage reason** — stacked-bar chart from Step
   5e.
8. **Pressure by area** — top areas from Step 5f.
9. **Triage funnel** — coverage %, response rate %, stalest
   bucket, this-week velocity.
10. **Detailed tables** (collapsed by default):
    1. **Triaged PRs — Final State since `<cutoff>`** — one
       row per area where `Triaged Total > 0`.
    2. **Triaged PRs — Still Open** — one row per area where
       `Total > 0`, plus `TOTAL` row.
11. **Legend** — verbose explanation of every colour, column
    abbreviation, computed metric.

Dashboard = **HTML by default** → colour-coded hero cards,
action priority bars, velocity bars render correctly. Markdown
fallback (+ Rich terminal-tables variant for detailed-tables
section only) when maintainer passes `markdown` or
`tables-only`. See [`render.md`](render.md) for full layout,
colour scheme, recommendation rule definitions.

---

## Skill does NOT do

- **No mutations.** Rule 1.
- **No per-PR drill-in.** Aggregate-only. Per-PR inspection →
  `pr-management-triage pr:<N>` or browser.
- **No author-level stats.** Group by area label, not author
  login. Stats-by-author = separate scope.
- **No PR *quality* scoring.** CI pass/fail, diff size,
  review-thread counts → omitted. Belong in per-PR
  `pr-management-triage` view.
- **No long-term historical trends.** Closure-velocity covers
  last 6 weeks from closed-since-cutoff fetch (one snapshot at
  fetch time). No persistent time-series. Month-over-month →
  maintainer's job; re-run with different `since:`.
- **No automatic actions from recommendations.** Every "What
  needs attention" entry = *suggestion* with slash-command
  maintainer pastes. Stats skill never invokes another skill,
  never adds labels, never closes PRs.

---

## Budget discipline

Typical session against `<upstream>`:

- 1 pre-flight query (viewer + repo)
- ~6 paginated GraphQL calls for ~300 open PRs (50/page)
- ~2 paginated calls for closed/merged-since-cutoff (typically
  20–80 PRs/week of cutoff)
- No per-PR REST calls — comment scan for triage markers from
  `comments(last: 10)` subfield in open-PR query

Total: ~10 GraphQL calls regardless of repo size. <5% of
hourly budget.
