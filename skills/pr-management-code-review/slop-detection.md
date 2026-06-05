<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Slop detection — structural scan

This step runs immediately after Step 2 (diff and metadata fetched),
before the full line-by-line review in Step 3. It is cheap — purely
structural analysis, no LLM token budget — and it short-circuits the
review when a PR is clearly not a genuine upstream contribution.

"Slop" here means a PR whose structure demonstrates it is a **class
project, personal experiment, or low-effort AI-generated submission**
being pushed into the upstream repository. The goal is to catch
crystal-clear cases early, not to flag every imperfect PR. When in
doubt, proceed with the normal review.

---

## Signals

Signals are split into **hard** (individually strong) and **soft**
(individually weak; accumulate). All checks use data already in the
Step 2 payload — no extra `gh` calls.

### Hard signals

Each hard signal alone has a moderate probability of indicating slop;
two or more together are nearly conclusive.

| ID | Signal | How to detect |
|---|---|---|
| H1 | **New top-level directory, unrecognised** | A file path in `files[].path` starts with a directory that (a) is not present in the base ref's tree and (b) has no plausible relationship to the rest of the PR's changes. Strongest form: a new directory whose `README` or docs reference a university course, team name, instructor, or academic project. |
| H2 | **Private-fork issue reference in PR body** | The body contains an issue URL or bare `#N` reference that resolves to a fork rather than the upstream repo (pattern: `github.com/<author>/<repo-name>#\d+` where `<repo-name>` is not the upstream repo). |
| H3 | **Fork merge-commit flood** | The commit list contains 3+ commit messages matching `^Merge (pull request|branch) #\d+ from` that all share the same fork prefix and were authored within a narrow window (< 60 minutes apart). |
| H4 | **Multi-author team project** | Commits are authored by 3 or more distinct GitHub logins, yet the PR is opened by a single account — typical of a university team pushing their entire fork history. |
| H5 | **Area sprawl** | Changed files span 5 or more distinct top-level directories (or well-known project sub-areas) with no discernible semantic relationship. Count using the first two path components of each changed file. |

### Soft signals

| ID | Signal | How to detect |
|---|---|---|
| S1 | **Ticket-style PR title** | Title matches patterns like `[Ticket #N]`, `ts/ticket-\d+`, `sprint-N`, `task-\d+`, or contains a student name followed by a ticket reference. |
| S2 | **Template-only PR body** | Body contains no prose beyond the PR template boilerplate (checked: no description above the first `---`, no non-template `closes:` / `related:` references to the upstream repo). |
| S3 | **No real CI** | `statusCheckRollup` contains only external bots (e.g. Mergeable, WIP, boring-cyborg) and zero entries from the project's own CI workflows. |
| S4 | **Label sprawl** | PR carries 3+ `area:` labels spanning unrelated subsystems, suggesting the author ran an automated labeller or copied labels from multiple separate changes. |
| S5 | **Commit messages reference internal sprint/ticket tooling** | 2+ commit messages contain phrases like `sprint`, `kanban`, `jira`, `ticket #`, `story #`, or `[CSS \d+` (course codes). |

---

## Threshold for early exit

Run the check after computing which signals fire. Apply the rules below:

| Condition | Action |
|---|---|
| **2+ hard signals** | Early exit — crystal-clear slop |
| **1 hard signal + 3+ soft signals** | Early exit — crystal-clear slop |
| **1 hard signal, < 3 soft** | Note only — add `[suspicious]` chip to headline, proceed with normal review |
| **0 hard signals, any soft** | Note only — add `[suspicious]` chip if ≥ 2 soft signals, otherwise silent |

The `[suspicious]` note-only path does **not** interrupt the review
flow. It surfaces in the headline so the maintainer has the information
but is not forced to act on it before seeing the diff.

Early exit **does** interrupt the flow: Step 3 and beyond are skipped.
The maintainer chooses an action (see below) before the skill moves on.

---

## Maintainer interaction on early exit

**Propose** a slop report in place of the normal Step 3 prompt:

```text
⚠  Slop detection fired for PR #<N> — <title>
   https://github.com/<upstream>/pull/<N>

Hard signals:
  [H1] New unrecognised top-level directory: `team_project/`
        → team_project/README.md mentions "CSS 566A — Software Management,
          University of Washington Bothell"
  [H3] Fork merge-commit flood: 6 "Merge pull request" commits from
        break-through-19/airflow within a 35-minute window
  [H4] Multi-author team project: 3 distinct commit authors
        (break-through-19, sanwar47, sharan-s2k) on a single-author PR
  [H5] Area sprawl: changes span go-sdk/, airflow-core/ui/,
        docs/adr/, team_project/ — no semantic relationship

Soft signals:
  [S1] Ticket-style title: "Poorani ts/ticket 36 adr document review"
  [S2] Template-only PR body (no description, private-fork issue ref only)
  [S3] No real CI (only Mergeable + WIP bots ran)
  [S4] Label sprawl: area:UI + area:task-sdk + area:go-sdk

This PR shows crystal-clear structural signals of a team class project
or personal experiment being submitted to the upstream repository. Full
line-by-line review is not warranted until these signals are resolved.

Action?
  [C]omment  — post a contribution-guidelines warning on the PR
  [X]        — close PR, lock conversation, show report-to-GitHub link
  [R]eview   — proceed with full review anyway (e.g. to extract
               the legitimate commits from the noise)
  [S]kip     — skip this PR this session
  [Q]uit     — end the session
```

Wait for explicit input before taking any action. The maintainer may
want to pick multiple actions sequentially (e.g. `[C]` then `[X]`).
If they do, execute in order and confirm before each write.

---

## Action: [C] — post contribution-guidelines warning

Draft and confirm a PR comment using the template below, then post:

```bash
gh pr comment <N> --repo <repo> --body "$(cat <<'BODY'
[comment body here — see template]
BODY
)"
```

### Warning comment template

```markdown
Thank you for your interest in Apache <PROJECT>. Unfortunately this PR
cannot be accepted in its current form.

**Structural issues detected:**

[List each fired signal as a plain-English sentence. Example:]

- The `team_project/` directory appears to be a student class project
  unrelated to Apache <PROJECT>.
- The PR bundles several independent changes with no shared purpose.
- The PR description does not explain what problem the changes solve
  or reference an upstream issue.

**What to do instead:**

1. Remove any files that are not genuine upstream contributions.
2. Split the remaining changes into separate, focused PRs — one PR
   per logical change.
3. Each PR should include a clear description of the problem it
   solves and a reference to the relevant upstream issue (or a
   justification if no issue exists).
4. Please read the [contribution guidelines](<contributing-docs-url>)
   before opening a new PR.

We welcome genuine contributions and are happy to help if you have
questions about the process.
```

The `<contributing-docs-url>` is the adopter's contributing guide, read
from `<project-config>/project.md → contributing_docs_url`. If not set,
link to the repo's `CONTRIBUTING.md`.

Substitute `<PROJECT>` with the project name from
`<project-config>/project.md → project_name`.

After the comment is posted, return to the action menu to allow a
follow-up `[X]` close if the maintainer wants to.

---

## Action: [X] — close, lock, and prompt to report

**Propose** the sequence of operations, then **confirm** before executing:

> *About to: close PR #N, lock the conversation (reason: spam), and
> show you the report link. Confirm? `[Y]es` / `[N]o`.*

On confirm, execute in order:

```bash
# 1. Close the PR
gh pr close <N> --repo <repo>

# 2. Lock the conversation
gh api --method PUT "repos/<owner>/<repo>/issues/<N>/lock" \
  --field lock_reason=spam
```

Then surface the report link (cannot be automated — GitHub does not
expose a report API):

```text
To report this PR to GitHub:
  1. Open: https://github.com/<upstream>/pull/<N>
  2. Click the "…" menu (top-right of the PR header).
  3. Select "Report content".
  4. Choose the appropriate reason (e.g. "Spam or misleading").
```

Note in the session summary that this PR was closed and locked, with
the timestamp and the maintainer's stated reason.

---

## [R] — review anyway

Proceed with Step 3 as normal. Add a `[slop-signals present]` note
to the session summary so the maintainer can reference which signals
were detected even if they chose not to act on them.

Use this path when the PR contains a mix of legitimate and illegitimate
changes and the maintainer wants to isolate the legitimate commits
for a cherry-pick or to direct the author to split the PR correctly.

---

## In the session summary

For each PR that triggered early exit, record:

- Fired signals (hard + soft, by ID)
- Action taken: `comment` / `close+lock` / `review-anyway` / `skip`
- For `close+lock`: timestamp and whether the maintainer reported to GitHub

This gives the maintainer an audit trail without requiring them to
remember which PRs they handled as slop.

---

## False-positive calibration

The threshold is deliberately conservative. A PR that looks suspicious
but doesn't cross the 2-hard-signal or 1-hard-3-soft threshold proceeds
with the normal review. The `[suspicious]` chip in the headline is the
only signal — no interruption, no menu.

When the maintainer says `[R]eview anyway` after an early exit, that
choice is noted and the full review runs normally. The slop detection
does not influence the findings or disposition of the subsequent
review.

Do not raise slop signals as findings inside the normal review. If the
maintainer chose `[R]eview anyway`, they made a deliberate choice. The
normal review covers the code; the slop detection covered the
structural envelope.
