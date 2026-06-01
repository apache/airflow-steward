<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Candidate rules

The two-stage screen that turns the `ready for maintainer review` queue into a
ranked list of quick-merge candidates. Both stages are a **pure function** of
the data fetched in [`SKILL.md` Step 1](SKILL.md#step-1--fetch-the-ready-queue) —
no network calls, no prompts, no writes.

Reading order:

1. [Stage 1 — quality gate](#stage-1--quality-gate) — hard pass/fail. A PR that
   fails any gate is dropped and never reaches Stage 2.
2. [Stage 2 — triviality](#stage-2--triviality) — footprint + path
   allow/deny + tier assignment.
3. [Tiers](#tiers) — what Tier A and Tier B mean.
4. [Path matching](#path-matching) — how globs are evaluated, deny precedence.
5. [Drop-reason taxonomy](#drop-reason-taxonomy) — the auditable reasons a PR
   is excluded (surfaced in the [Step 4 summary](SKILL.md#step-4--session-summary)).
6. [Required fields](#required-graphql-fields) — what the batch query must
   populate.

All thresholds and path lists are read from
[`<project-config>/pr-management-quick-merge-config.md`](../../../projects/_template/pr-management-quick-merge-config.md)
at session start. The values below are the **shape**, not hard-coded constants.

---

## Stage 1 — quality gate

A PR proceeds to Stage 2 only if **every** condition holds. This mirrors the
strict reading of [`pr-management-triage`](../pr-management-triage/classify-and-act.md)
rows 19/20 plus the workflow-approval guard — a quick-merge candidate must be at
least as clean as a PR the triage skill would call `passing`.

| # | Gate | Pass condition |
|---|---|---|
| G1 | Label present | `labels` contains `ready for maintainer review` (guaranteed by the search query; re-checked defensively). |
| G2 | Real CI green | `statusCheckRollup.state == SUCCESS` **and** the [Real-CI guard](../pr-management-triage/classify-and-act.md#real-ci-guard) passes — at least one context matches a `real_ci_patterns` entry, so the SUCCESS is not coming only from `Mergeable`/`WIP`/`DCO`/`boring-cyborg`. |
| G3 | No failed/pending checks | `failed_checks` is empty **and** no context is still `QUEUED`/`IN_PROGRESS`/`PENDING`. A candidate must be *done and green*, not green-so-far. |
| G4 | No workflow approval pending | the PR's `head_sha` is **not** in the per-session `action_required` index. |
| G5 | Mergeable | `mergeable == MERGEABLE` (not `CONFLICTING`, not `UNKNOWN`) **and** `mergeStateStatus ∉ {DIRTY, BLOCKED, UNKNOWN}`. `BEHIND` is allowed (a behind-but-clean branch still merges); `UNSTABLE` is allowed only if G2/G3 already proved every *required* check green (UNSTABLE can come from a non-required check). |
| G6 | No unresolved collaborator threads | zero `reviewThreads` with `isResolved == false` whose first comment's `authorAssociation ∈ {OWNER, MEMBER, COLLABORATOR}`. Contributor-author side threads do not block (same qualifier as triage's [`unresolved_threads_only`](../pr-management-triage/classify-and-act.md#unresolved_threads_only)). |
| G7 | No outstanding changes-requested | no `latestReviews` node with `state == CHANGES_REQUESTED` that is newer than the last commit. |

**Conservative-on-uncertainty (Golden rule 4).** If `mergeable == UNKNOWN` or
`mergeStateStatus == UNKNOWN` (GitHub hasn't finished computing mergeability),
the PR **fails** G5 for this run — do not surface it. It will settle and qualify
on the next sweep. Never guess a gate green.

A PR failing any gate is dropped with the corresponding
[drop reason](#drop-reason-taxonomy) (`gate:<Gn>`) and excluded from Stage 2.

---

## Stage 2 — triviality

Of the gate-green survivors, a PR is a quick-merge candidate iff **all** hold:

### 2a. Footprint within budget

- `additions + deletions <= max_churn` (config; default `20`)
- `changed_files <= max_files` (config; default `3`)

`max_churn` counts the PR's own `additions + deletions` totals (not the diff of
the merge). Pure deletions count toward churn — a PR that deletes 40 lines is
not trivial-to-merge just because it adds nothing; deletion can be as
consequential as addition.

### 2b. Every file in the allow-list

For **every** entry in `files.nodes[].path`, the path must match at least one
glob in the active tier's allow-list (`tier_a_allow_globs`, plus
`tier_b_allow_globs` when Tier B is enabled — the default). One file that
matches no allow glob fails the PR with drop reason `path-unmatched`.

### 2c. No file in the deny-list

For **every** entry in `files.nodes[].path`, the path must match **no** glob in
`deny_globs`. One file matching a deny glob fails the PR with drop reason
`path-denied` — **even if it also matches an allow glob, and even if the PR is
one line**. Deny precedence is absolute (Golden rule 3).

A PR passing 2a–2c is a candidate; assign its [tier](#tiers).

---

## Tiers

| Tier | Meaning | Allow source | Confidence |
|---|---|---|---|
| **A** | Documentation and human-readable text only — `.rst`/`.md` docs, changelog, newsfragments, translations, the spelling wordlist. The change cannot affect runtime behaviour. | `tier_a_allow_globs` | highest — the blast radius is "wrong words on a page" |
| **B** | Low-risk code — test-only files and example/illustration code (example DAGs). No production code path changes. | `tier_b_allow_globs` | medium — still needs a read for assertion correctness, but cannot break production |

A PR is **Tier A** if every file matches a Tier A glob. It is **Tier B** if
every file matches a Tier A *or* Tier B glob and at least one matches a Tier B
glob. (A pure-docs PR is Tier A; a docs + test PR is Tier B; a test-only PR is
Tier B.) `tier:A` on the command line restricts to Tier A only.

Tiers drive **ordering and an honesty signal**, not the gate — both tiers are
surfaced by default. The maintainer reads every diff regardless; the tier tells
them how hard to look (Tier A is usually a glance; Tier B warrants reading the
assertions).

---

## Path matching

- Globs are matched against the **repo-relative POSIX path** in
  `files.nodes[].path` (e.g. `airflow-core/docs/howto/x.rst`).
- Use `**` for any-depth, `*` for single-segment. Matching is case-sensitive on
  the path, case-insensitive on the extension only where the config glob says so.
- **Deny is evaluated before allow and wins.** A path that matches both a deny
  glob and an allow glob is denied.
- A path that matches **neither** list → `path-unmatched` → PR dropped
  (Golden rule 4: unknown paths are not assumed safe).

The default globs live in the
[template config](../../../projects/_template/pr-management-quick-merge-config.md);
the shape for an Airflow-like project:

```text
tier_a_allow_globs:
  - "**/*.rst"
  - "**/*.md"
  - "**/docs/**"
  - "docs/**"
  - "**/newsfragments/**"
  - "**/changelog.rst"
  - "**/i18n/**"
  - "**/locales/**"
  - "**/*.po"
  - "spelling_wordlist.txt"

tier_b_allow_globs:
  - "**/tests/**"
  - "**/test_*.py"
  - "**/*_test.py"
  - "**/example_dags/**"

deny_globs:                 # absolute disqualifiers, even at one line
  - "**/migrations/**"
  - "**/versions/**"
  - "**/alembic*/**"
  - "pyproject.toml"
  - "**/pyproject.toml"
  - "uv.lock"
  - "setup.cfg"
  - "**/requirements*.txt"
  - ".github/**"
  - "**/Dockerfile*"
  - "scripts/ci/**"
  - "**/security/**"
  - "**/auth*/**"
  - "**/jwt*/**"
  - "airflow-core/src/airflow/jobs/**"
  - "airflow-core/src/airflow/models/**"
  - "airflow-core/src/airflow/executors/**"
  - "airflow-core/src/airflow/api_fastapi/**"
  - "airflow-core/src/airflow/serialization/**"
  - "task-sdk/src/airflow/sdk/execution_time/**"
```

The deny-list is the load-bearing safety control and is intentionally broad:
when in doubt, a maintainer adds a path to `deny_globs` rather than risk a
core/security/build path being screened as trivial. A path appearing in both an
adopter's allow and deny lists is a config smell — deny wins, and the validator
should warn.

---

## Drop-reason taxonomy

Every screened-out PR carries exactly one drop reason, surfaced in the
[Step 4 summary](SKILL.md#step-4--session-summary) so the screen is auditable:

| Reason | Meaning |
|---|---|
| `gate:G2` … `gate:G7` | failed the named quality gate (CI red, conflict, unresolved thread, …) |
| `too-large` | gate-green but `churn > max_churn` or `files > max_files` |
| `path-denied` | a changed file matched `deny_globs` (consequential area) |
| `path-unmatched` | a changed file matched no allow glob (unknown area) |

`gate:*` drops are reported as a single count (the maintainer rarely cares
*which* gate a non-ready-looking PR failed); `too-large`, `path-denied`, and
`path-unmatched` are reported with PR numbers, because those are the
"so-close" PRs a maintainer may want to glance at or hand to
`pr-management-code-review`.

---

## Required GraphQL fields

Extend the family batch query
([`pr-management-triage/fetch-and-batch.md`](../pr-management-triage/fetch-and-batch.md))
with the fields this screen needs beyond what triage already fetches:

| Stage | Required fields (delta over the triage batch query) |
|---|---|
| Stage 1 | `mergeStateStatus`; (`statusCheckRollup`, `mergeable`, `reviewThreads`, `latestReviews`, `head_sha` already present) |
| Stage 2 | `additions`, `deletions`, `files(first: 100) { nodes { path additions deletions } }` |

Everything else (label list, author association, rollup contexts, the
`action_required` index) is already fetched by the shared family machinery.
Golden rule 6 ("one query per page") still applies — the `files` connection
rides along in the same paged call.
