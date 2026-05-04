---
name: security-issue-invalidate
description: |
  Close an `<tracker>` tracking issue as invalid: apply the
  `invalid` label, remove the scope label, post a short closing
  comment, archive the item from the project board, and — for
  trackers imported from `<security-list>` — draft a
  polite-but-firm reply to the reporter on the original Gmail
  thread explaining the team's reasoning (extracted from the
  tracker's discussion). For trackers opened via
  `security-issue-import-from-pr`, the email-draft step is skipped
  per the *no outreach to the PR author* rule of that skill.
when_to_use: |
  Invoke when a security team member says "close NN as invalid",
  "invalidate NN", "mark NN invalid", "NN is not a security
  issue" — typically after a Step 5 consensus-invalid decision
  in the issue's discussion. Not appropriate when the team has
  not yet reached consensus, when a CVE has already been allocated
  (a separate Vulnogram REJECT flow is required first), or when
  the advisory has already shipped (closing as invalid then is a
  retraction with public consequences and needs explicit team
  escalation).
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory
     <tracker>        → value of `tracker_repo:` in <project-config>/project.md
                       (example: airflow-s/airflow-s for the Apache Airflow security team)
     <upstream>       → value of `upstream_repo:` in <project-config>/project.md
                       (example: apache/airflow)
     Before running any bash command below, substitute these with the
     concrete values from the adopting project's <project-config>/project.md. -->

# security-issue-invalidate

This skill is the **terminal-disposition apply step** for the
`invalid` close on an `<tracker>` tracker. It does not host the
discussion that decides invalidity — that happens at Step 5 of the
[handling process](../../../README.md#step-5--validity-decision)
in the tracker's comments. Once the team has reached a
consensus-invalid decision, this skill applies it: labels the
tracker `invalid`, posts a short public-facing closing comment,
closes the tracker, archives the project-board item, and (for
`security@`-imported trackers) drafts a reply to the reporter
explaining why.

It is the symmetric counterpart of
[`security-cve-allocate`](../security-cve-allocate/SKILL.md) (apply step for the
*valid → CVE* path). Both skills assume the validity decision has
already been reached; they wire that decision into the tracker
state in one pass.

**Golden rule — never sends email.** Any reply to the reporter is
created as a Gmail draft on the original inbound thread. The
triager reviews the draft in Gmail before sending. The skill must
not call `send` on any drafting backend.

**Golden rule — public-facing comment is brief.** The closing
comment posted on the public-by-collaborator-access tracker is
short and process-shaped (*"closing as invalid per team consensus
in this thread"*); the team's full reasoning lives in the
discussion comments and the rollup. The detailed reasoning belongs
in the email draft to the reporter (where it actually serves a
purpose), not in a closing comment that re-packages the same
material.

**Golden rule — no outreach to PR-imported tracker authors.** When
the tracker came in via
[`security-issue-import-from-pr`](../security-issue-import-from-pr/SKILL.md)
(detected by the `N/A — opened from public PR …` sentinel in the
*Security mailing list thread* body field), there is no reporter
to notify — the PR author is not the CVE reporter and the public
PR stays unaware of the CVE process per that skill's policy. Skip
the email-draft step entirely; do not comment on the public PR;
do not reach out to the PR author through any channel.

---

## Adopter overrides

Before running the default behaviour documented
below, this skill consults
[`.apache-steward-overrides/security-issue-invalidate.md`](../../../docs/setup/agentic-overrides.md)
in the adopter repo if it exists, and applies any
agent-readable overrides it finds. See
[`docs/setup/agentic-overrides.md`](../../../docs/setup/agentic-overrides.md)
for the contract — what overrides may contain, hard
rules, the reconciliation flow on framework upgrade,
upstreaming guidance.

**Hard rule**: agents NEVER modify the snapshot under
`<adopter-repo>/.apache-steward/`. Local modifications
go in the override file. Framework changes go via PR
to `apache/airflow-steward`.

---

## Snapshot drift

Also at the top of every run, this skill compares the
gitignored `.apache-steward.local.lock` (per-machine
fetch) against the committed `.apache-steward.lock`
(the project pin). On mismatch the skill surfaces the
gap and proposes
[`/setup-steward upgrade`](../setup-steward/upgrade.md).
The proposal is non-blocking — the user may defer if
they want to run with the local snapshot for now. See
[`docs/setup/install-recipes.md` § Subsequent runs and drift detection](../../../docs/setup/install-recipes.md#subsequent-runs-and-drift-detection)
for the full flow.

Drift severity:

- **method or URL differ** → ✗ full re-install needed.
- **ref differs** (project bumped tag, or `git-branch`
  local is behind upstream tip) → ⚠ sync needed.
- **`svn-zip` SHA-512 mismatches the committed
  anchor** → ✗ security-flagged; investigate before
  upgrading.

---
## Prerequisites

Before running, the skill needs:

- **`gh` CLI authenticated** with collaborator access to
  `<tracker>` and access to the project-board mutations
  (`addProjectV2ItemById`, `updateProjectV2ItemFieldValue`,
  `archiveProjectV2Item`). The skill calls `gh issue view`,
  `gh issue edit`, `gh issue comment`, `gh issue close`, and
  `gh api graphql`.
- **Gmail MCP connected** (only required when the tracker is
  `security@`-imported and a draft reply is to be created).
  Without Gmail, the skill can still close the tracker — but it
  surfaces the missing draft as a follow-up the user must do
  manually before the close is fully complete.

See [Prerequisites for running the agent skills](../../../README.md#prerequisites-for-running-the-agent-skills)
in `README.md` for overall setup and the
[`claude_ai_mcp` (default) vs `oauth_curl` (opt-in) backend rule](../../../tools/gmail/draft-backends.md#how-the-skills-pick-a-backend)
for the Gmail draft path.

---

## Step 0 — Pre-flight check

Before any work, verify:

1. **`gh` is authenticated and has access.** Run
   `gh api repos/<tracker> --jq .name`; on 401 / 403 / 404, stop
   and tell the user to log in or get added.
2. **The tracker number is parseable.** Accept any of:

   | User input | Resolved tracker |
   |---|---|
   | `240` | `<tracker>#240` |
   | `<tracker>#240` | `<tracker>#240` (require repo == `<tracker>`) |
   | `https://github.com/<tracker>/issues/240` | `<tracker>#240` |

3. **Hard-stop blockers** (apply *before* doing any other work):

   | Detected state | Stop reason |
   |---|---|
   | `cve allocated` label set, or *CVE tool link* body field populated with a CVE-ID URL | Closing as invalid requires the CVE record to be marked **REJECTED** in Vulnogram first. That is a separate flow (PMC-gated, similar to allocation). Stop and surface the URL of the *CVE tool link* alongside a one-line ask: *"This tracker has CVE `<CVE-ID>` allocated. Reject the CVE in Vulnogram first, then re-invoke this skill."* |
   | `fix released`, `announced - emails sent`, or `announced` label set | The advisory has already shipped (or is mid-flight). Closing as invalid retroactively is a retraction with public consequences. Stop and surface a one-line ask: *"This tracker is past `pr merged` (label: `<label>`). Closing as invalid here would retract a published advisory; escalate to the team before re-invoking."* |
   | Tracker is already `closed` | No-op; surface the existing close reason and stop. |

   Both hard stops are deliberate — the skill must not paper over
   a CVE-allocation or a published-advisory state by silently
   labelling and closing.
4. **Privacy-LLM contract.** This skill drafts a closing reply
   on the inbound `<security-list>` Gmail thread, so it reads
   the original report's body to mine the team's reasoning
   (Step 3) and assembles an outbound draft (Step 6). Before
   either, load `<project-config>/privacy-llm.md` and verify
   the pre-flight items in
   [`tools/privacy-llm/wiring.md`](../../../tools/privacy-llm/wiring.md#step-0--pre-flight).
   The Step 3 read follows the
   [redact-after-fetch protocol](../../../tools/privacy-llm/wiring.md#redact-after-fetch-protocol);
   the Step 6 draft follows the
   [reveal-before-send protocol](../../../tools/privacy-llm/wiring.md#reveal-before-send-protocol)
   when (and only when) the closing reply references a
   third-party identifier.

If `gh` fails or any hard stop fires, do **not** proceed. A
privacy-llm pre-flight failure is also a hard stop.

---

## Step 1 — Fetch tracker state

Pull everything the rest of the skill needs in one `gh issue view`:

```bash
gh issue view <N> --repo <tracker> --json \
    number,title,body,labels,state,milestone,assignees,comments,url \
  > /tmp/invalidate-<N>.json
```

Record into the observed-state bag:

- `tracker.number`, `tracker.url`, `tracker.title`, `tracker.state`
  (must be `OPEN` to proceed).
- `tracker.labels[].name` — used to detect hard-stop conditions
  (Step 0) and to decide which scope label to remove (Step 5a).
- `tracker.body` — parsed for the *Security mailing list thread*,
  *PR with the fix*, *CVE tool link*, *Reporter credited as*, and
  *Affected versions* fields.
- `tracker.comments[]` — mined for the team's invalidity reasoning
  (Step 3).
- `tracker.milestone.title` — informational only; stays as-is.
- `tracker.assignees[].login` — informational only; stays as-is.

Re-check the hard stops from Step 0 against the freshly-fetched
labels and body fields, in case the user invoked from stale state.

---

## Step 2 — Detect import path

The tracker's import path drives whether an email draft is part of
the close. Read the *Security mailing list thread* body field:

| Body field shape | Import path | Email-draft step |
|---|---|---|
| Real `lists.apache.org` URL or any URL | `security@`-imported (public-archive case) | Draft on the original Gmail thread; locate via the rollup-comment `threadId` reference. |
| `No public archive URL — tracked privately on Gmail thread <threadId>` (sentinel from [`security-issue-import`](../security-issue-import/SKILL.md) Step 7) | `security@`-imported (Gmail-only case) | Draft on the named `<threadId>`. |
| `N/A — opened from public PR <upstream>#<N>; no security@ thread` (sentinel from [`security-issue-import-from-pr`](../security-issue-import-from-pr/SKILL.md)) | PR-imported | **Skip** the email-draft step. No reporter exists to notify. |
| Empty / `_No response_` / unrecognised | Indeterminate | Surface to the user; ask whether the tracker has a Gmail thread the skill should reply on, or whether the close is silent (no email). |

For `security@`-imported trackers, locate the Gmail `threadId`:

1. Read the rollup comment on the tracker (the first
   `<details>` block with the `<tracker> status rollup v1`
   marker). Look for `threadId` references in the *Provenance:*
   line of the import entry.
2. If the rollup is missing or thin, fall back to a Gmail subject
   search: `mcp__claude_ai_Gmail__search_threads` with the
   tracker title (or a distinctive phrase from the body). One
   match → use it; multiple → surface to user.
3. Capture `tracker.threadId`, `tracker.reporterEmail` (the
   `From:` of the inbound root message), and
   `tracker.reporterName` (used to address the reply).

---

## Step 3 — Mine invalidity reasoning from the discussion

The team's reasoning is the load-bearing input for the email
draft. Extract verbatim quotes the user can confirm before any
draft is written.

Scan `tracker.comments[]` for posts that argue **why** the report
is not a security issue. Strong signals:

- Citations of the
  [the project's security model](<security-model-url>)
  (full URL, anchor links, paraphrases).
- Phrases like *"this is by design"*, *"out of scope"*,
  *"documented behavior"*, *"requires X privileges already"*,
  *"not a CVE"*, *"not CVE worthy"*, *"won't fix"*, *"working as
  intended"*.
- Pointers to existing CVEs that already addressed the broader
  class (e.g. *"already covered by CVE-2023-37379"*).
- Pointers to a documented mitigation the reporter missed
  (config flag, RBAC role, security-policy section).
- Counter-examples or PoC failures from team members trying to
  reproduce.

Surface the **3–5 most-load-bearing quotes** verbatim, each with
the comment author's handle and a clickable comment URL. Do not
paraphrase — the user should be able to copy a quote into the
email draft if it fits.

If no clear reasoning is present in the comments (e.g. the team
discussed in chat and only landed a one-line *"closing as invalid"*
on the tracker), surface this gap to the user with:

> The tracker has no detailed reasoning in its public comments.
> The email draft will need a reason to communicate to the
> reporter. Options: (a) supply a one-paragraph reason inline
> (`--reason "<text>"`), (b) point me to a chat transcript /
> private GHSA comment to extract from, or (c) close silently
> with no reply (only appropriate when the tracker is
> `security@`-imported but the reporter is unreachable — flag
> this in the rollup so the gap is visible).

---

## Step 4 — Match a canned-response template

The email draft is built canned-response-spine + augmentation,
same pattern as
[`security-issue-import` Step 5](../security-issue-import/SKILL.md).
Read [`<project-config>/canned-responses.md`](../../../<project-config>/canned-responses.md)
and pick the section that best matches the invalidity reasoning
mined in Step 3:

| Reasoning shape | Canned section |
|---|---|
| Generic *"after review, not CVE-worthy"* with case-specific reasoning | *Negative Assessment response* (the `HERE DETAILED EXPLANATION FOLLOWS` placeholder is filled with the augmentation). |
| Dag-author-provided input is the attack vector | *When someone claims Dag author-provided "user input" is dangerous*. |
| DoS / RCE / arbitrary read via Connection configuration | *DoS/RCE/Arbitrary read via Provider's Connection configuration*. |
| Self-XSS by an authenticated user | *Immediate response for self-XSS issues triggered by Authenticated users*. |
| DoS triggered by an authenticated user (no privilege escalation) | *DoS issues triggered by Authenticated users*. |
| Parameter injection to operator/hook called by the dag author | *Parameter injection to operator or hook*. |
| Automated-scanner output without human-verified PoC | *Automated scanning results*. |
| Image / video reproducer instead of a written report | *When someone submits a media report* (or *Or an alternative response*). |

If multiple canned sections apply, pick the most-specific one and
note the others to the user; if none fits, default to *Negative
Assessment response* with the team's reasoning filling the
placeholder.

The skill must not invent a canned response or paraphrase one
into the file. If the adopting project lacks a fitting template,
surface the gap to the user — adding a canned response is a
separate `canned-responses.md` PR, not part of this run.

---

## Step 5 — Build the proposal

Surface every change to the user before any write.

### 5a — Labels

- **Add:** `invalid`.
- **Remove:** `needs triage` (if set), the scope label
  (`airflow` / `providers` / `chart`), and `pr created` /
  `pr merged` (if set — the public PR stays open as the
  contributor's normal-process work, but the tracker no longer
  treats it as the security fix).

The `security issue` label **stays** — it pins the tracker to
the security project board's filter and keeps the tracker
findable in future searches for invalid-class history.

### 5b — Closing comment on the tracker

Brief, process-shaped. Examples:

```markdown
Closing as `invalid` per team consensus in [this discussion](#issuecomment-<id>).

Reasoning summary in the [status rollup](#issuecomment-<rollup-id>); a draft reply to the reporter is in Gmail awaiting review.
```

For PR-imported trackers, replace *"a draft reply to the reporter
is in Gmail awaiting review"* with *"no reporter notification
(PR-imported tracker — see the import-from-pr skill's
[Reporter credit policy](https://github.com/<tracker>/blob/<tracker-default-branch>/.claude/skills/security-issue-import-from-pr/SKILL.md#reporter-credit-policy-for-public-pr-imports))"*.

The comment links must resolve once the rollup entry from Step 5e
has been posted (capture its URL and substitute before posting
this closing comment, or post the rollup first and use its ID
here).

### 5c — Project-board archive

Locate the project-board item ID:

```bash
gh api graphql -f query='
  query($pid:ID!,$nid:ID!) {
    node(id:$pid) {
      ... on ProjectV2 {
        items(first: 100) {
          nodes { id content { ... on Issue { number id } } }
        }
      }
    }
  }' \
  -F pid=PVT_kwDOCAwKzs4BUzbt \
  -F nid=<tracker-node-id> \
  --jq '.data.node.items.nodes[] | select(.content.number == <N>) | .id'
```

Then archive:

```bash
gh api graphql -f query='
  mutation($pid:ID!,$iid:ID!) {
    archiveProjectV2Item(input: { projectId: $pid, itemId: $iid }) {
      item { id isArchived }
    }
  }' \
  -F pid=PVT_kwDOCAwKzs4BUzbt \
  -F iid=<item-id>
```

`archiveProjectV2Item` (not `deleteProjectV2Item`) — archiving
preserves the item's history in the board's archived view; the
team can still find old invalid trackers via the *Archived items*
filter when they need precedent for a similar future close.
Deletion would lose that history.

If the tracker is not on the board (no rows returned by the
introspection query), skip the archive step and note in the
rollup that the item was already absent from the board (an
`Auto-add` workflow gap or a manual prior removal — surface as
informational, not a blocker).

### 5d — Email draft (security@-imported only)

Skip this entire substep when the import path detected in Step 2
is *PR-imported*.

For `security@`-imported trackers:

1. **Recipients:**
   - `toRecipients`: `tracker.reporterEmail` (the `From:` of
     the inbound root message). If the import was via the
     ASF-security relay path (the `From:` is a `@apache.org`
     forwarder, not the external reporter), reply to the
     forwarder per the *ASF-security relay* convention in
     [`security-issue-import` Step 7](../security-issue-import/SKILL.md).
   - `ccRecipients`: always includes `<security-list>`
     (`<security-list>` for the adopting project) —
     value comes from
     [`<project-config>/project.md`](../../../<project-config>/project.md#gmail-and-ponymail).
2. **Subject:** `Re: <root subject>`. Never invent a fresh
   subject — the reply lands on the inbound thread via
   thread attachment (`replyToMessageId` for `claude_ai_mcp`,
   `--thread-id` for `oauth_curl`).
3. **Body:**
   - Spine: the canned section picked in Step 4, verbatim.
   - Augmentation: a clearly-marked block filling the
     `HERE DETAILED EXPLANATION FOLLOWS` placeholder (or
     equivalent) with the case-specific reasoning gathered in
     Step 3. Use the same `> **[Inline addition for this
     report]**` block convention as
     [`security-issue-import` Step 5](../security-issue-import/SKILL.md)
     — the user must be able to delete the augmentation
     cleanly without leaving a grammatical orphan.
   - **No mention of `<tracker>`.** The tracker repo is
     private; the reporter has no access; references would
     leak. Cite the public Security Model and any public CVEs
     instead.
   - **Polite-but-firm.** Per
     [`AGENTS.md`](../../../AGENTS.md#tone-and-register), state
     the team's position once, clearly, with reasoning. Do not
     re-open the discussion with phrases like *"happy to
     discuss further"* — close the loop.
4. **Backend selection:** use the project's configured
   drafting backend per
   [`tools/gmail/draft-backends.md`](../../../tools/gmail/draft-backends.md#how-the-skills-pick-a-backend).
   Default is `claude_ai_mcp` with `replyToMessageId` thread
   attachment; the opt-in `oauth_curl` backend is used when
   `tools.gmail.draft_backend: oauth_curl` is set and
   credentials are on disk (default path
   `~/.config/apache-steward/gmail-oauth.json`).
5. **Existing-draft check.** Before drafting, scan the inbound
   thread for an existing pending draft per the
   [*Detecting drafts that already exist on a thread*](../../../tools/gmail/draft-backends.md#detecting-drafts-that-already-exist-on-a-thread)
   recipe — both `mcp__claude_ai_Gmail__list_drafts` and
   `mcp__claude_ai_Gmail__get_thread`. If a pending draft
   already exists, surface it instead of silently shadowing.

### 5e — Status-rollup entry

Append a new `<details>` block to the existing rollup comment
(per
[`tools/github/status-rollup.md`](../../../tools/github/status-rollup.md)
upsert recipe). Shape:

```markdown
<details><summary><YYYY-MM-DD> · @<author-handle> · Closed as invalid</summary>

**Closed as `invalid` on <YYYY-MM-DD>** (decided in [comment](#issuecomment-<id>)).

**Reasoning** (verbatim from the team's discussion, capped at ~5 quotes):

- @<author>: > <quote 1> ([source](#issuecomment-<id>))
- @<author>: > <quote 2> ([source](#issuecomment-<id>))
- ...

**Canned response selected:** *<canned section name>* in [`canned-responses.md`](https://github.com/<tracker>/blob/<tracker-default-branch>/<project-config>/canned-responses.md#<anchor>).

**Reporter notification:** <one of:>
- **`security@`-imported:** Gmail draft `<draftId>` created on thread `<threadId>` — awaiting user review.
- **PR-imported:** none (no reporter; per [Reporter credit policy](https://github.com/<tracker>/blob/<tracker-default-branch>/.claude/skills/security-issue-import-from-pr/SKILL.md#reporter-credit-policy-for-public-pr-imports)).
- **Indeterminate import path:** none (flag from Step 2 surfaced; user explicitly chose silent close).

**Project board:** archived (item `<item-id>`).

**Next:** none — terminal disposition.

</details>
```

Zero-whitespace rules from
[`status-rollup.md`](../../../tools/github/status-rollup.md#the-rollup-comment-shape)
apply. The reasoning quotes section is trimmed to ~5 entries
even when more material exists in the discussion — the rollup is
a navigation aid, not an archive.

### 5f — Confirmation forms

Surface the full proposal — labels, closing comment, archive
target, email draft (when applicable, fully rendered), rollup
entry — and ask:

- `go` / `proceed` / `yes` — apply as proposed.
- `email: <freeform>` — replace the email-draft body with the
  user's text (skill still wraps with subject + recipients;
  user is overriding only the body).
- `canned: <section name>` — re-pick the canned response and
  re-augment.
- `silent` — for an `security@`-imported tracker, deliberately
  skip the email draft and note in the rollup why (e.g. the
  reporter is unreachable, GHSA closed, etc.).
- `cancel` / `none` — bail; nothing applied.

The user must confirm explicitly. Unlike `security-issue-import`,
this skill does **not** default to apply — the close is a
terminal disposition and the email draft is a public message
attributed to the security team. One round of confirmation is
the right trade.

---

## Step 6 — Apply

Sequenced. Each substep depends on the previous one.

### 6a — Post the rollup entry first

Posting the rollup before the closing comment lets the closing
comment link to the rollup's permalink. Append to the existing
rollup comment via the upsert recipe in
[`status-rollup.md`](../../../tools/github/status-rollup.md):

```bash
EXISTING=$(gh api repos/<tracker>/issues/comments/<rollup-comment-id> --jq .body)
cat > /tmp/invalidate-<N>-rollup.md <<EOF
${EXISTING}

<new <details> block from Step 5e>
EOF
gh api -X PATCH repos/<tracker>/issues/comments/<rollup-comment-id> \
  -F body=@/tmp/invalidate-<N>-rollup.md \
  --jq .html_url
```

If no rollup comment exists (very old trackers predating the
rollup convention), create one fresh with just the new entry —
same as the *create* branch of the upsert recipe.

Capture the rollup permalink for use in the closing comment.

### 6b — Post the closing comment

```bash
gh issue comment <N> --repo <tracker> --body-file /tmp/invalidate-<N>-close.md
```

Body is the Step 5b shape with comment IDs substituted.

### 6c — Apply labels

```bash
gh issue edit <N> --repo <tracker> \
  --add-label 'invalid' \
  --remove-label '<scope-label>' \
  --remove-label 'needs triage' \
  --remove-label 'pr created' \
  --remove-label 'pr merged'
```

`gh issue edit` ignores `--remove-label` for labels that aren't
set, so listing all candidates is safe and idempotent.

### 6d — Close the tracker

```bash
gh issue close <N> --repo <tracker> --reason 'not planned'
```

`not planned` is the right close reason — `completed` would
imply the issue was resolved, which is misleading for an
invalid disposition.

### 6e — Archive the project-board item

Run the introspection query + `archiveProjectV2Item` mutation
from Step 5c. Capture the returned `isArchived: true` and
record in the rollup if it differs from expected.

### 6f — Create the Gmail draft (security@-imported only)

Skip if PR-imported or the user chose `silent`.

Use the backend chosen in Step 5d:

- **`claude_ai_mcp`:** call `mcp__claude_ai_Gmail__get_thread`
  on `<tracker.threadId>` with `messageFormat: MINIMAL`, take
  the chronologically-last message's `id`, and call
  `mcp__claude_ai_Gmail__create_draft` with `to=<reporterEmail>`,
  `cc=<security-list>`, `subject='Re: <root subject>'`,
  `body=<file>`, and `replyToMessageId=<that message id>`. The
  draft lands attached to the inbound thread.
- **`oauth_curl`:** call the `oauth_curl drafts:create` script
  per [`draft-backends.md`](../../../tools/gmail/draft-backends.md)
  with `threadId=<tracker.threadId>`, `to=<reporterEmail>`,
  `cc=<security-list>`, `subject='Re: <root subject>'`,
  `body=<file>`. The draft lands attached to the inbound thread.

Capture the returned `draftId`. Update the rollup entry's
*Reporter notification* line with the actual draft ID
(re-PATCH the rollup comment if the draft ID was a placeholder
when 6a ran).

### 6g — Cleanup

Delete `/tmp/invalidate-<N>-*.md`.

---

## Step 7 — Recap and hand-off

Print a one-screen recap:

- Tracker number, clickable URL, new state (`closed - not planned`).
- Labels applied / removed.
- Rollup entry permalink.
- Closing comment permalink.
- Project board status (`archived` or `not on board`).
- Gmail draft ID + Gmail web URL (security@-imported only) — or
  the explicit *no draft* explanation (PR-imported or silent
  close).

Hand-off line:

> Terminal disposition. No further skill runs are expected on
> `<tracker>#<N>`. If the team later changes its mind, re-open
> the tracker manually and re-run the discussion at Step 5;
> there is no `un-invalidate` skill (and there should not be —
> reversing an invalid close is a deliberate team action that
> deserves a fresh discussion).

---

## What this skill does **not** do

- **Does not host the validity discussion.** The decision is the
  team's, made in the tracker comments. The skill only applies
  the decision once it has been reached.
- **Does not mark the CVE record REJECTED in Vulnogram.** When
  a CVE has been allocated, that is a separate flow gated on
  the Step 0 hard-stop. Once the CVE is REJECTED, the user
  re-invokes this skill.
- **Does not delete the tracker, its comments, or its history.**
  The audit trail (who decided what and when) is the project's
  long-term record of how the security team handles invalid
  reports — that material stays. Only the project-board item is
  archived (which preserves it in the *Archived* view).
- **Does not send email.** Drafts only.
- **Does not comment on the public PR** when the tracker is
  PR-imported.

---

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Step 0 hard stop fires (`cve allocated`) | The tracker has a CVE; closing as invalid here would orphan a CVE record | Reject the CVE in Vulnogram first, then re-invoke. The CVE-tool URL is in the *CVE tool link* body field. |
| Step 0 hard stop fires (`fix released` / `announced`) | The advisory has already shipped | Escalate to the team — closing as invalid here is a public retraction, not a routine close. |
| `archiveProjectV2Item` returns `not found` for the item | Project-board item ID has changed (rare; usually because the item was manually moved) | Re-run the introspection query. If the tracker is genuinely not on the board, skip 6e and note in the rollup. |
| Gmail draft creation fails with `oauth_curl` 401 | OAuth token expired | Re-run the credential refresh per [`tools/gmail/oauth-draft/README.md`](../../../tools/gmail/oauth-draft/README.md); fall back to `claude_ai_mcp` if oauth refresh is impractical. |
| The tracker title contains characters that break heredoc / shell quoting | Title with `'` or backticks | Use `--body-file` paths everywhere (already the convention); never inline issue titles into shell strings. |
| Rollup comment not found (very old tracker, pre-convention) | Rollup didn't exist yet | Create one fresh with just the close entry (per the *create* branch of the upsert recipe). |
| The tracker is `security@`-imported but the inbound thread can't be located in Gmail | Thread was archived / Gmail account changed / threadId is stale | Surface to the user; offer the `silent` confirmation form — the close still happens, the rollup notes the missing reply. |

---

## Examples

### Example 1 — `security@`-imported, dag-author-input class

```text
invalidate 244
```

Tracker `<tracker>#244` (*DAG author RCE on webserver via
unrestricted import_string() in BaseSerialization.deserialize()*),
import path: `security@`-imported. Step 3 mines five comments
arguing the dag author is already trusted (with quotes from
@potiuk and @ephraimbuddy). Canned: *When someone claims Dag
author-provided "user input" is dangerous*. Email draft created
on thread `<threadId>` with the canned spine + augmentation
quoting the team's specific reasoning. Tracker closed as
`not planned`, `invalid` label applied, scope label removed,
project board item archived. Rollup entry posted with five
verbatim quotes and the draft ID. Hand-off: terminal.

### Example 2 — PR-imported, no email

```text
invalidate 355
```

Tracker `#355` (the public-PR-imported tracker from the test of
`security-issue-import-from-pr` against PR 65703). Suppose the
team later decides the report is not CVE-worthy on its own
merits. Step 2 detects the `N/A — opened from public PR` sentinel;
the email-draft step is skipped. Closing comment notes *"no
reporter notification (PR-imported tracker)"*. Rollup entry
records the `silent` notification path with a link to the
*Reporter credit policy* explaining why. Tracker closed,
archived. PR `<upstream>#65703` is **not** commented on —
the public PR stays unaware of the CVE process per the
import-from-pr skill's golden rules.

### Example 3 — Hard stop: CVE already allocated

```text
invalidate 257
```

Step 0 sees `cve allocated` label and *CVE tool link* populated
with `https://cveprocess.apache.org/.../CVE-2026-XXXXX`. The
skill stops:

> Tracker `#257` has CVE `CVE-2026-XXXXX` allocated.
> Closing as invalid here would orphan a public CVE record.
> Reject the CVE in Vulnogram first
> (https://cveprocess.apache.org/.../CVE-2026-XXXXX), then
> re-invoke `invalidate 257`.

No labels touched, no comments posted, no archive performed.
