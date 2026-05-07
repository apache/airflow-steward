<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Rationale

Companion to [`classify-and-act.md`](classify-and-act.md). The
decision table there is normative and short; the *why* behind
each rule lives here. Numbering tracks the decision-table rows so
maintainers can jump from a row to its reasoning in one click.

This file is **not** in the skill's hot path — Claude only loads
it when:

- a maintainer asks "why was this PR classified that way?"
- the rule's effect on a borderline PR is contested
- the table is being edited and the editor needs context

If you find yourself reading this file to *make a decision* on a
PR, the decision table in `classify-and-act.md` is missing
information — fix it there, do not re-derive from prose here.

---

## Pre-filter 5 (active maintainer conversation)

F5a (author-response cooldown) and F5b (maintainer-to-maintainer
ping) override every signal in the decision table. Two cases,
same underlying principle: do not let the triage skill talk over
a human conversation already in progress.

### F5a — 72-hour cooldown after a collaborator comment

When a maintainer just engaged with the PR, the author deserves
at least three days to read, think, and reply before the triage
skill auto-drafts or auto-comments on top of that conversation.

Why 72 hours and not 24:

- Review-style feedback takes longer to address than a flaky-CI
  nudge.
- A same-day auto-action reads as the bot talking over the
  maintainer.
- The 24-hour window in [grace
  periods](classify-and-act.md#grace-periods) is for *CI*
  failures the author may not have noticed yet — different
  failure mode, different patience budget.

Cost asymmetry: a missed auto-action on one of these PRs is one
extra day of queue presence. An auto-action that talks over a
maintainer is a contributor reading the project as chaotic. Prefer
the former.

### F5b — maintainer-to-maintainer ping unanswered

When a maintainer pings other maintainers (e.g.
*"@ash @kaxil could you weigh in on the API shape?"*), the PR is
waiting on **maintainer input**, not on author work.
Auto-drafting it with a "the author should work on comments"
message is wrong on two counts:

- The contributor isn't the bottleneck — the maintainer review
  / conversation is.
- It de-focuses the thread away from the maintainer-to-
  maintainer discussion the original commenter was trying to
  start.

Skip silently until one of the pinged collaborators responds, at
which point F5a's 72-hour window starts ticking from that reply.

Team mentions (`@<upstream>-committers`) are conservatively
treated as F5b matches — we cannot cheaply expand team membership
in the batch query, and the false-positive cost (skipping a PR
that should have been actioned) is much lower than the false-
negative cost (talking over a real maintainer call-out).

---

## Pre-filter 6 (maintainer co-drafted)

F6 covers a different shape of "do not talk over a maintainer"
than F5a/F5b: a draft PR that a maintainer (other than the
viewer running the skill) has already substantively engaged
with — typically by leaving a review with `CHANGES_REQUESTED`,
posting a substantive comment outlining what is wrong, or both —
and where the author has not yet responded with a new commit.

The motivating cases are PRs the maintainer would already
demote-and-comment on by hand and which the classifier, running
later, would propose the same `draft` action for a second time.
A few historical examples on `<upstream>` (each manually skipped
to avoid a duplicate proposal):

- `potiuk-drafted` `<upstream>#58149`
- `vargacypher-drafted` `<upstream>#63260`
- `bugraoz93-drafted` `<upstream>#64906`

In each case the classifier wanted to emit a `deterministic_flag
→ draft` proposal whose substance a different maintainer had
already covered on the draft. F5a does not cover this: F5a
expires after 72 hours and only fires when the **most recent**
comment is by a collaborator. F5b does not cover this either:
the maintainer engagement here is directed at the author, not at
other maintainers. F6 closes the gap.

### Empirical check against the motivating examples

Snapshotting the three PRs at the time of the issue (`<now>` =
2026-05-07):

| PR | Last author commit | Qualifying maintainer engagement after that anchor | F6 fires (viewer = potiuk)? |
|---|---|---|---|
| `<upstream>#63260` | 2026-03-22 (vargacypher) | `kaxil` comment 2026-04-15, body length 80 chars | yes — comment branch |
| `<upstream>#64906` | 2026-04-11 (stephen-bracken) | `bugraoz93` comment 2026-04-20, body length 102 chars | yes — comment branch |
| `<upstream>#58149` | 2026-01-23 (Philip Abernethy) | only `potiuk`'s own triage / closure comments | **no** — viewer-self engagement is excluded |

`#58149` is therefore not addressed by F6 as written. It is a
related-but-distinct concern: the viewer's *own* prior
engagement on a draft is conceptually
[`already_triaged`](classify-and-act.md#decision-table)
territory (rows 3–5), and the duplicate-proposal symptom there
is "viewer left a free-form drafting comment that doesn't carry
the triage marker, so rows 3–5 don't recognise it." Closing
that gap belongs in the marker-detection logic of rows 3–5 (or
in the stale-sweep duplicate-suppression), not in F6 — F6's
contract is "do not talk over a *different* maintainer." The
issue tracking the marker-detection extension is
[#79's first follow-up bullet](https://github.com/apache/airflow-steward/issues/79).

### Why drafts only, not ready-for-review

The F6 signal is "a maintainer is co-drafting this PR" — a
collaborative state that only exists while the PR is `isDraft ==
true`. Once a PR is promoted to ready-for-review the surrounding
semantics flip: F4 already exempts ready PRs without regression,
and a regression on a ready PR is exactly the moment we *want*
the classifier to surface a signal to the maintainer queue, not
suppress it. Limiting F6 to drafts keeps that signal path
intact.

### Why "after the last author commit", not a wall-clock TTL

A wall-clock expiry (e.g. "ignore engagements older than 30
days") would re-introduce the same duplicate-proposal problem
F6 is meant to avoid: an old draft that a maintainer engaged
with months ago, which the author has not pushed to since, is
still in the same conversational state — re-proposing `draft`
on it adds nothing. The right invalidation signal is **author
activity**, not time: when the author pushes a new commit, the
maintainer's prior critique may or may not be addressed and the
classifier should re-evaluate. Anchoring F6 at
`commits(last:1).committedDate` matches F5a's anchor and lets
the eventual-resurfacing job stay where it belongs — the stale-
sweep flow in [`stale-sweeps.md`](stale-sweeps.md), which acts
on a different action (`stale_draft` → close), not on a
duplicate `draft` proposal.

### Why ≥ 80 chars on comments

The threshold filters out emoji reactions, `+1`, `lgtm`, and
single-sentence acknowledgements while letting through the
typical maintainer critique ("Two things — the migration here
needs a downgrade path, and the new helper duplicates X in
`utils.py`. Converting to draft until those are addressed.").
80 is empirical, not load-bearing; tune with feedback if real
PRs slip through. Reviews are not gated on length because a
review submission is itself a stronger commitment than a free-
form comment — a maintainer who clicks through the review UI
to attach `CHANGES_REQUESTED` has already engaged substantively
even if the body is terse.

### What F6 does not yet cover

Two further signals would strengthen F6 but require new fields
in the batch query:

- A maintainer pushing commits to the author's branch (not
  currently exposed — `commits(last:1)` returns committed-by
  data but not the GitHub login of the pusher in a form the
  query consumes).
- A `convert_to_draft` timeline event authored by a maintainer
  (would require pulling `timelineItems(itemTypes:
  [CONVERT_TO_DRAFT_EVENT])`).

Both are tracked as follow-ups; neither blocks the MVP because
the historical examples that motivated F6 all surface via the
review-or-comment signals F6 already inspects.

---

## Row 1 — `pending_workflow_approval`

Single most sensitive category in the skill. Approving a workflow
lets a first-time contributor's code run inside the project's CI with
its secret material. The diff-review and flag-suspicious protocol
is in [`workflow-approval.md`](workflow-approval.md).

The REST `action_required` index is the **primary** signal, not a
fallback. Empirically (2026-04, `<upstream>`), 17 first-time-
contributor PRs in a single sweep reported
`statusCheckRollup.state == SUCCESS` while every real CI workflow
was held in `action_required`. Trusting the rollup classified all
17 as `passing` and would have applied `mark-ready` to PRs whose
real CI never ran. Golden rule 1b in [`SKILL.md`](SKILL.md)
captures this as a mandatory invariant.

---

## Row 2 — `stale_copilot_review`

Copilot-review comments are work items queued against the
author. Even when individual Copilot suggestions turn out to be
wrong, the author is still responsible for replying — accept,
reject with a one-line explanation, or fix. When Copilot comments
sit unresolved for a week the PR has stalled — author is either
unaware of the feedback or assuming someone else will triage it.

`draft` is the softer equivalent of the stale-draft sweep: it
unblocks the maintainer review queue while preserving the
conversation for when the author returns. The dedicated
"Unaddressed Copilot review" violation is rendered by
[`comment-templates.md`](comment-templates.md).

Why 7 days, not 24h / 96h:

- Review feedback takes longer to address than a CI-flake nudge.
- A same-week nudge would be noisy.
- The threshold matches the patience budget for any unresolved
  reviewer thread, just with the Copilot-specific message body.

Why row 2 and not later: Copilot signal is more specific than the
generic `unresolved review thread` row. A PR with both signals
should get the Copilot-specific message because it points the
author at the actual unresolved thread URL — listing both
violations in one comment is fine, but the action and template
are picked from row 2.

---

## Rows 3–5 — `already_triaged`

Two sub-states matter:

- **waiting** — no author comment after the triage comment.
  Quiet `skip`; nothing to do.
- **responded** — author commented, possibly with a question
  that needs a maintainer answer. Quiet `skip` here too; we do
  not auto-suggest a reply because the author's response might
  not be a fix push.

The 7-day cutoff into `stale_draft` (row 5) is what stops
forever-waiting PRs from sitting in the queue. After 7 days with
no author reply on a draft, the close-with-stale-notice sweep
takes over.

The triage-comment marker — the literal string
`Pull Request quality criteria` — is what makes this row
detectable from a single comment scan. Do not paraphrase the
marker in [`comment-templates.md`](comment-templates.md); it is
load-bearing.

---

## Row 6 — viewer is the PR author

Triaging your own PR from this skill is unintended. Mutation APIs
will work but the skill's signal is calibrated for outside
contributors — applying it to your own PR risks self-drafting.
Skip with a one-line note and let the maintainer use the action
verbs directly.

---

## Row 7 — too fresh

A PR created in the last 30 minutes hasn't had time for CI to
finish. Flagging it on checks that simply haven't run yet would
read as the bot pouncing on new contributors. Skip with a
"too fresh" note.

---

## Rows 8–17 — `deterministic_flag` ladder

These rows turn the 7-way sub-condition that the old
`suggested-actions.md` had under `deterministic_flag` into an
ordered ladder. The ordering is the rule — read top-to-bottom,
first match wins. A few notes:

### Row 8 — author has > 3 flagged PRs (page-scoped)

When the same author has more than 3 flagged PRs visible on the
current page, suggest closing rather than drafting each one.
Queue pressure from a single contributor with many low-quality
PRs is a different signal than a single broken PR — the
proportionate response is "talk to them, close the bulk", not
"draft them all and triple the comment volume".

Page-scoped to keep the math cheap and the false-positive surface
small. A contributor with three flagged PRs across many pages
won't trip this row.

### Row 9 — `CONFLICTING` always means draft, never rebase

GitHub's `update-branch` endpoint side-merges `<base>` into the
PR head and refuses on conflicts. Empirically every rebase
attempt on a `CONFLICTING` PR has returned "Cannot update PR
branch due to conflicts" and wasted a round-trip. Routing
straight to `draft` with the merge-conflicts violation points
the author at the local-rebase instructions in their comment
body. Action-side guard: see the `rebase` recipe in
[`actions.md`](actions.md).

### Rows 10–13 — CI-failure shape decides the action

The shape of the failures determines the action:

- All failures match systemic main-branch failures → `rerun`.
  Their PR is not the cause; the rerun is the right move.
- Some failures match → `rerun`. Same logic, lower confidence.
- All failures are static checks → `comment`. These are
  deterministic; rerunning won't help. Author needs to fix and
  push. No reason to draft when a comment closes the loop in
  one round-trip.
- Otherwise (≤ 2 failures, no conflict, branch up-to-date) →
  `rerun`. Most "two-failure" cases on a clean PR are flakes.

### Rows 14, 15 — `mark-ready-with-ping` vs `ping`

Both fire when the only signal is unresolved review threads.
Difference is what we believe about the threads:

- `ping` is the safe default — threads are unresolved, may not
  yet be addressed, nudge the author to fix or explain.
- `mark-ready-with-ping` is the optimistic path — threads are
  unresolved but the author has already engaged (post-review
  commit, or in-thread reply, *and* the latest commit post-dates
  the most recent unresolved thread). The PR is plausibly ready
  for the maintainer to take another look; we promote it with
  the `ready for maintainer review` label *and* ping the
  reviewer to confirm and resolve their threads.

The `unresolved_threads_only_likely_addressed` heuristic is conservative on
purpose. False-negative degrades to plain `ping` (cheap). False-
positive would advance a PR that isn't actually ready, which is
the worse failure mode. The maintainer still confirms; the
posted comment explicitly invites the reviewer to push back if a
thread is not actually addressed, so a heuristic false-positive
self-corrects on the next round-trip rather than silently landing
the PR.

### Row 16 — no real CI ran, mergeable

The PR is mergeable but `statusCheckRollup.contexts` has no real
CI checks (only bot/labeler noise). Two reasons this can happen:

- A first-time contributor PR whose real CI is held in
  `action_required` — but row 1 should have caught that. If we
  reach row 16, the author isn't first-time and the REST index
  was empty.
- A workflow path-filter excluded all the workflows for this
  PR's diff. Rare but real on `<upstream>` for diffs that
  only touch docs or configs.

`rebase` re-triggers the whole CI matrix. If the path-filter
explanation is the right one, the rerun is harmless and the PR
will fall through to row 20 next time.

### Row 17 — fallback `draft`

Anything left with `has_deterministic_signal` and no other rule
matched. This is the catch-all that prevents a "no proposal"
outcome on a flagged PR. Deliberately conservative — we'd rather
nudge the author too gently than miss queue pressure.

---

## Row 18 — `stale_review`

Author pushed commits after a `CHANGES_REQUESTED` review but
neither the author nor the reviewer pinged. The author is
ostensibly waiting on a re-review but never nudged. The `ping`
action posts the nudge for them with the relevant reviewer(s)
`@`-mentioned.

Default the body to pinging the *author*, not the reviewer. Only
flip to the reviewer-re-review variant after
[`comment-templates.md#review-nudge`](comment-templates.md#review-nudge)
confirms the feedback has been addressed in a post-review commit
or resolved in-thread. A bare "nudge reviewer" default is the
wrong call when the author hasn't done the work yet.

---

## Rows 19, 20 — `passing`

Row 19 (`skip`) exists for the case where a previous run already
applied the `ready for maintainer review` label. The skill has
nothing more to do; the review skill owns the PR now.

Row 20 (`mark-ready`) is the happy path — green CI, no
conflicts, no threads. Real-CI guard fires before either row to
prevent the SUCCESS-with-only-bot-checks false positive.

---

## `unresolved_threads_only_likely_addressed` heuristic detail

The fields the heuristic touches:

- `reviewThreads.nodes.comments(first: 5).nodes` — needs more
  than the first comment per thread to detect post-first-comment
  author replies. The choice of `first: 5` (vs. `first: 1`) is
  documented in
  [`fetch-and-batch.md`](fetch-and-batch.md); 5 is the smallest
  window that catches the typical "reviewer comment → author
  reply" exchange without blowing GraphQL complexity.
- `commits(last: 1).committedDate` — for the post-thread-push
  fallback when there's no in-thread author reply.

The heuristic is opt-in to the optimistic path. The alternative
is dropping every "unresolved threads only" PR back to plain
`ping` forever, which adds maintainer-review-queue latency for
PRs that are actually ready.

---

## Draft vs comment vs ping

All three actions can land violations text on the same PR. The
difference is how they shape the maintainer's queue and the
author's expectations:

- `draft` flips the PR out of the review queue. Says "stop
  requesting review, fix these first, mark ready yourself".
  Right when maintainer review time would be wasted (CI red,
  conflicts, multiple threads, etc.).
- `comment` keeps the PR in the queue. Says "here are the
  issues, continue working, we'll re-look once addressed". Right
  for narrow deterministic issues (static-check failures) the
  author can resolve in one push.
- `ping` is the lightest touch. Says "two specific people, look
  here". Right when the contributor is clearly still iterating
  and dropping back to draft would be discourteous — a full
  violations-list comment would be overkill for "your reviewer
  hasn't seen your latest push yet".

Collaborator-authored PRs (when `authors:collaborators` is
active) always default to `comment` — never `draft`. Collaborators
don't need gentle routing and converting a colleague's PR to
draft is an overreach.

---

## Group-level overrides

The interaction loop lets the maintainer override the suggested
action for an entire group (e.g. "these 5 PRs suggested `draft`
but I want to `comment` them instead — the author is actively
fixing"). Mechanics:
[`interaction-loop.md#group-action-override`](interaction-loop.md#group-action-override).
Classification stays the same; only the action switches.

Class overrides are **out of scope**. The maintainer cannot tell
the skill "pretend this PR is `passing`" — they would use
`mark-ready` directly on the PR instead, which is a per-PR
decision the skill never tries to second-guess.

---

## Refuse-to-suggest cases

Rows 6, 7, and 22 in the decision table cover the refuse-to-
suggest cases. The intent of each:

- Row 6 (viewer is the PR author) — see [Row 6](#row-6--viewer-is-the-pr-author).
- Row 7 (too fresh) — see [Row 7](#row-7--too-fresh).
- Row 22 (data inconsistency) — when the PR's data looks
  inconsistent (rollup says SUCCESS but `failed_checks` is non-
  empty, or similar), surface the inconsistency to the
  maintainer with a one-line note and skip. Data anomalies
  usually mean GitHub hasn't fully settled the rollup yet; a
  refresh on the next page typically clears it. Do not guess.

---

## Reason strings — tone and discipline

The reason goes in front of a maintainer who is already
frustrated; do not add to the frustration. Concrete rules:

- Lead with the signal that fired the rule (failing-check
  category, reviewer login, age, flagged-PR count).
- End with the proposal verb (suggest rerun / draft / close /
  comment / ping / mark-ready).
- No editorialising, no scare quotes, no emoji, no LLM-generated
  prose.

The full surface area is the templates in
[`classify-and-act.md#reason-template-rules`](classify-and-act.md#reason-template-rules).
Anything beyond that is drift.
