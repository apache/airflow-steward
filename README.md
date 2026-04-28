<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Overview](#overview)
- [Who this guide is for](#who-this-guide-is-for)
- [Prerequisites for running the agent skills](#prerequisites-for-running-the-agent-skills)
  - [1. An agent that speaks the `SKILL.md` convention](#1-an-agent-that-speaks-the-skillmd-convention)
  - [2. Email connection (Gmail MCP, today)](#2-email-connection-gmail-mcp-today)
  - [3. GitHub connection (GitHub MCP / `gh` CLI)](#3-github-connection-github-mcp--gh-cli)
  - [4. PMC membership (only for CVE allocation)](#4-pmc-membership-only-for-cve-allocation)
  - [5. Browser (for the human-click steps)](#5-browser-for-the-human-click-steps)
  - [6. Local `<upstream>` clone (only for `fix-security-issue`)](#6-local-upstream-clone-only-for-fix-security-issue)
  - [7. `uv` (for `generate-cve-json`)](#7-uv-for-generate-cve-json)
- [Shared conventions](#shared-conventions)
  - [Keeping the reporter informed](#keeping-the-reporter-informed)
  - [Recording status transitions on the tracker](#recording-status-transitions-on-the-tracker)
  - [Confidentiality](#confidentiality)
- [For issue triagers — Steps 1–6](#for-issue-triagers--steps-16)
  - [Daily triage loop](#daily-triage-loop)
  - [Assessing a report](#assessing-a-report)
  - [Allocating the CVE](#allocating-the-cve)
  - [Tools you use most](#tools-you-use-most)
- [For remediation developers — Steps 7–11](#for-remediation-developers--steps-711)
  - [Picking up a tracker](#picking-up-a-tracker)
  - [Attempting an automated fix](#attempting-an-automated-fix)
  - [Opening the public fix PR manually](#opening-the-public-fix-pr-manually)
  - [Private-PR fallback](#private-pr-fallback)
  - [Handoff to the release manager](#handoff-to-the-release-manager)
  - [Tools you use most](#tools-you-use-most-1)
- [For release managers — Steps 12–15](#for-release-managers--steps-1215)
  - [Handoff from the remediation developer](#handoff-from-the-remediation-developer)
  - [Sending the advisory](#sending-the-advisory)
  - [Capturing the public archive URL](#capturing-the-public-archive-url)
  - [Publishing the CVE and closing the issue](#publishing-the-cve-and-closing-the-issue)
  - [Post-release credit corrections](#post-release-credit-corrections)
  - [Tools you use most](#tools-you-use-most-2)
- [Process reference: the 16 steps](#process-reference-the-16-steps)
  - [Step 1 — Report arrives on security@](#step-1--report-arrives-on-security)
  - [Step 2 — Import the report](#step-2--import-the-report)
  - [Step 3 — Discuss CVE-worthiness](#step-3--discuss-cve-worthiness)
  - [Step 4 — Escalate stalled discussions](#step-4--escalate-stalled-discussions)
  - [Step 5 — Land the valid/invalid consensus](#step-5--land-the-validinvalid-consensus)
  - [Step 6 — Allocate the CVE](#step-6--allocate-the-cve)
  - [Step 7 — Self-assign and implement the fix](#step-7--self-assign-and-implement-the-fix)
  - [Step 8 — Open a public PR (straightforward cases)](#step-8--open-a-public-pr-straightforward-cases)
  - [Step 9 — Open a private PR (exceptional cases)](#step-9--open-a-private-pr-exceptional-cases)
  - [Step 10 — Link the PR and apply `pr created`](#step-10--link-the-pr-and-apply-pr-created)
  - [Step 11 — PR merged](#step-11--pr-merged)
  - [Step 12 — Fix released](#step-12--fix-released)
  - [Step 13 — Send the advisory](#step-13--send-the-advisory)
  - [Step 14 — Capture the public advisory URL](#step-14--capture-the-public-advisory-url)
  - [Step 15 — Publish the CVE record and close the issue](#step-15--publish-the-cve-record-and-close-the-issue)
  - [Step 16 — Credit corrections](#step-16--credit-corrections)
- [Label lifecycle](#label-lifecycle)
  - [State diagram](#state-diagram)
  - [Label reference](#label-reference)
- [Current projects](#current-projects)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

## Overview

This repository (`apache/airflow-steward`, future-renamed to
`apache/steward`) hosts a reusable, project-agnostic framework for
running an ASF project's security-issue handling process. The
lifecycle and conventions below are framework-level; everything
project-specific (identity, repositories, mailing lists, canned
responses, release trains, security model, scope labels, milestone
formats, title-normalisation rules, fix-workflow specifics) is
declared in the **adopting project's** `<project-config>/`
directory — i.e. the `.apache-steward/` directory the adopting
project keeps at the root of its tracker repository. The framework
itself is pulled into the adopter's tracker as a git submodule at
`.apache-steward/apache-steward/`.

A new project adopts the framework by:

1. Cloning this repository as a submodule of its tracker repo at
   `.apache-steward/apache-steward/`.
2. Copying the [`projects/_template/`](projects/_template/)
   scaffold into the tracker's `.apache-steward/` directory and
   filling in the project's identity, mailing lists, scope labels,
   release-train roster, security model, and canned responses.
3. Symlinking `.claude/skills/` in the tracker repo to the
   submodule's `.claude/skills/` so Claude Code (or another
   `SKILL.md`-aware agent) loads the framework's skills against the
   adopter's project configuration.

The private `<tracker>` repository is the adopting project's security
team's shared tracker. Only members of the security team have access.
Issues are created from reports raised on the project's security
mailing list (see `<project-config>/project.md → Mailing lists`)
and copied into `<tracker>` by security-team members — the GitHub
author of a tracker is therefore **not always the reporter**, and
the real reporter is whoever sent the original email.

Every tracker flows through two channels at the same time:

- the original security-list mail thread, where the reporter is
  kept informed at every status transition;
- a comment on the tracking issue, so the rest of the security team and the
  release manager can follow along without reconstructing state from labels
  and timestamps.

The rest of this document is organised by audience. Pick the role that matches
what you are about to do, read its section, and jump into the
[process reference](#process-reference-the-16-steps) when you need the
step-level detail.

## Who this guide is for

Three roles share the handling process. Any security-team member can take on
any of them for a given issue, and in practice people rotate — but at any
moment a given tracking issue has exactly one person who owns the next move.

Pick whichever applies to you now:

- **I am new to the security team, or I mostly just want to comment on
  issues.** Read [Shared conventions](#shared-conventions) below. The
  adopting project's security-issues board (for Airflow:
  <https://github.com/orgs/airflow-s/projects/2>; in general, see
  `<project-config>/project.md → GitHub project board`) is the main
  view. You do not need an agent for commenting.
- **I am a rotational triager** — running `import new reports` and
  `sync all` a few times a week. Jump to
  [For issue triagers — Steps 1–6](#for-issue-triagers--steps-16).
- **I picked up a tracker and am about to open a fix PR.** Jump to
  [For remediation developers — Steps 7–11](#for-remediation-developers--steps-711).
- **I am the release manager for a cut containing a security fix.** Jump to
  [For release managers — Steps 12–15](#for-release-managers--steps-1215).
- **I am looking up a specific step or label.** Go straight to
  [Process reference](#process-reference-the-16-steps) or
  [Label lifecycle](#label-lifecycle).

## Prerequisites for running the agent skills

If you only plan to **comment on issues** from the board, skip this
section — a browser and your `<tracker>` collaborator access are
enough.

If you plan to **run any of the agent skills** (`import`, `sync`,
`allocate-cve`, `fix`, `generate-cve-json`, `deduplicate`) — typically
as a rotational triager, remediation developer, or release manager —
check the following setup **before** invoking a skill. Each skill also
runs a short Step 0 pre-flight against the same list and stops with a
clear message if something is missing, so you do not discover a
missing piece half-way through a workflow.

### 1. An agent that speaks the `SKILL.md` convention

[Claude Code](https://www.anthropic.com/claude-code) is the reference
implementation the skills are written against. Any agent that reads
the `.claude/skills/*/SKILL.md` files and follows their step-by-step
instructions should work; there is no hard dependency on Claude Code
specifically.

### 2. Email connection (Gmail MCP, today)

The import, sync, and allocate-cve skills **read the security-list
mail thread** associated with each tracker and draft replies on that
thread. Today this goes through the
[Claude Gmail MCP](https://docs.anthropic.com/en/docs/build-with-claude/mcp)
connected to the personal Gmail account of a security-team member
who is subscribed to the adopting project's security list (see
`<project-config>/project.md → Mailing lists`). That is enough
access for the skills to see inbound reports and create drafts on
the right threads.

There is an ASF-wide alternative on the horizon:
[`rbowen/ponymail-mcp`](https://github.com/rbowen/ponymail-mcp) (by
Rich Bowen, former ASF board director and ComDev lead) now supports
OAuth authentication and can read private ASF lists. Once ASF OAuth
is wired in, individual triagers should be able to run the skills
without connecting their personal Gmail — authenticating directly
against ASF credentials (and, eventually, the ASF's new MFA) will be
sufficient. Until then, Gmail MCP is the way.

**Without this connection:** `import-security-issue` cannot find new
reports, `sync-security-issue` cannot reconcile status with the mail
thread, and no skill can draft replies to reporters. The skills will
refuse to start and tell you to configure the MCP first.

### 3. GitHub connection (GitHub MCP / `gh` CLI)

Every skill reads and writes `<tracker>` issues. Claude Code ships
with the GitHub MCP by default, and the skills also use the `gh`
CLI directly for some calls. What the skills need:

- Authenticated `gh auth status` on the shell the agent runs in.
- Collaborator access (any permission level) on `<tracker>` — the
  security-team roster is maintained per-project; for the active
  project see
  [`<project-config>/release-trains.md`](<project-config>/release-trains.md#security-team-roster).
- For `fix-security-issue`: a fork of `<upstream>` on your GitHub
  account (the skill pushes a branch there before opening the PR
  via `gh pr create --web`).

### 4. PMC membership (only for CVE allocation)

The adopting project's CVE-tool allocation form is **PMC-gated** on
the server side — only the project's PMC members can submit a CVE
allocation. Non-PMC triagers can still run `allocate-cve`; the
skill detects this up front (it asks *"are you a PMC member of
`<PROJECT>`?"*) and produces a relay message for a PMC member to
click through instead. For Airflow the concrete tool is ASF's
Vulnogram at <https://cveprocess.apache.org/allocatecve>; see
[`<project-config>/project.md → CVE tooling`](<project-config>/project.md#cve-tooling).

The same PMC gate applies to ponymail URL lookups on private ASF
lists; until `ponymail-mcp` is wired in with ASF OAuth, only PMC
members can see private-list archives directly.

### 5. Browser (for the human-click steps)

Several parts of the process involve a form a human has to fill in
and click — the CVE-tool allocation form, the CVE record `#source`
paste, the `gh pr create --web` compose view. The skills prepare
the URL and the exact text to paste and hand it off to the browser;
they do not try to automate those clicks.

### 6. Local `<upstream>` clone (only for `fix-security-issue`)

The fix skill writes the change in your local clone, runs local
checks and tests, pushes a branch to your fork, and opens a PR via
`gh pr create --web`. You need:

- a clean clone of `<upstream>` reachable from the agent's working
  directory — the path comes from `config/user.md →
  environment.upstream_clone`, set interactively the first time
  you run the skill;
- the adopting project's dev toolchain installed per its contributing
  docs — for Airflow see
  [`<project-config>/fix-workflow.md → Toolchain`](<project-config>/fix-workflow.md#toolchain);
- a remote named for your GitHub fork that `gh pr create` can push
  to.

### 7. `uv` (for `generate-cve-json`)

The `generate-cve-json` script is a small `uv`-managed Python
project. Install `uv` once
(<https://github.com/astral-sh/uv>); the script bootstraps the
rest.

## Shared conventions

These conventions bind every role. If you are unsure whether a rule applies to
you, it does.

### Keeping the reporter informed

The security team commits to keeping the original reporter informed about the
state of their report **at every status transition**, on the original mail
thread (not on the GitHub-notifications mirror thread). A short status update
should be sent to the reporter whenever any of the following happens:

* the report has been acknowledged or assessed (valid / invalid);
* a CVE has been allocated;
* a fix PR has been opened;
* a fix PR has been **merged**;
* the issue has been scheduled for a specific release (milestone set);
* the release has shipped and the public advisory has been sent;
* the CVE record has been published on cve.org (completes the disclosure);
* any credits or fields visible in the eventual public advisory have changed.

Each status update should plainly state what has changed, link to the relevant
artifact (PR URL, CVE ID, advisory link), and state what comes next. If the
reporter has not yet replied with their preferred credit, ask the
credit-preference question — but **do not re-ask it if it has already been
asked** on the same thread and is still awaiting a reply. Pinging the reporter
twice about the same open question is rude and gets us blocklisted; default to
the reporter's full name from the original email if they do not respond
before publication.

Reusable wording for the common cases lives in
[`<project-config>/canned-responses.md`](<project-config>/canned-responses.md) — consult it before drafting a
reply from scratch.

### Recording status transitions on the tracker

**Every status transition must also be recorded as a comment on the GitHub
issue in `<tracker>`**, not only sent by email. The two channels
serve different audiences: the email keeps the reporter informed; the issue
comment keeps the rest of the security team and the release manager informed
without forcing them to reconstruct the state from labels and timestamps. The
comment should briefly state what changed, link to the artifact (PR URL, CVE
ID, advisory link), and indicate whether the reporter has been notified.

### Confidentiality

Confidentiality of the private tracker (`<tracker>` for the
adopting project) is both a **lifecycle rule** and a **writing rule**:
every transition you record on a tracker, every status comment, every
email draft has to respect it. The full rule set — forbidden surfaces,
allowed surfaces, scrubbing guidance, the exception buckets for private
`security@` / `private@` threads and in-repo `gh issue comment` calls —
lives in
[`AGENTS.md` — Confidentiality of the tracker repository](AGENTS.md#confidentiality-of-the-tracker-repository).
Read it before editing anything that might be seen outside the team.

## For issue triagers — Steps 1–6

You own the tracker from an inbound report on `<security-list>`
through to a CVE allocated, a scope label applied, and the issue ready for a
remediation developer to pick up. Step 6 (the CVE allocation itself) is
PMC-gated: **only the adopting project's PMC members can submit the
CVE-tool allocation form**. If you are not on the PMC you relay a
pre-drafted request to a PMC
member — either way you are the one who lands the resulting CVE ID back into
the tracker.

### Daily triage loop

A typical triage sweep runs three skills in order:

1. **`import new reports`** —
   [`import-security-issue`](.claude/skills/import-security-issue/SKILL.md)
   scans `<security-list>` for threads not yet imported,
   classifies each candidate (real report vs. automated-scan / consolidated /
   media / spam), and proposes a tracker per valid report plus a
   receipt-of-confirmation Gmail draft. See
   [Step 2](#step-2--import-the-report).
2. **`sync all`** —
   [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md)
   reconciles every open tracker against its mail thread, the fix PR, the
   release train, and the users@ archive. Proposes label / milestone /
   assignee / body changes in one pass.
3. **`allocate CVE for issue #N`** —
   [`allocate-cve`](.claude/skills/allocate-cve/SKILL.md) when a report has
   been assessed as valid. See [Step 6](#step-6--allocate-the-cve).

Nothing is applied without an explicit confirmation — each skill is a
proposal engine, not an auto-pilot.

### Assessing a report

For each `needs triage` tracker, drive the validity assessment in comments,
pulling at least one other security-team member into the discussion. Use the
canned-response templates from [`<project-config>/canned-responses.md`](<project-config>/canned-responses.md)
for negative assessments so the tone stays polite-but-firm.

When the report is confirmed valid, apply exactly one scope label (`airflow`
/ `providers` / `chart`). If a report affects more than one scope, split into
per-scope trackers before allocation — the `sync-security-issue` skill
surfaces this as a blocker. See
[Step 5](#step-5--land-the-validinvalid-consensus).

If discussion stalls for about 30 days, escalate to a broader audience per
[Step 4](#step-4--escalate-stalled-discussions).

### Allocating the CVE

Use [`allocate-cve`](.claude/skills/allocate-cve/SKILL.md). The skill asks up
front whether you are on the PMC; if not, it reshapes the recipe into an
``@``-mention relay message you forward to a PMC member on the tracker or on
the `<security-list>` thread. Once the allocated `CVE-YYYY-NNNNN`
is pasted back, the skill wires it into the tracker in one pass (the *CVE
tool link* body field, the `cve allocated` label, a status-change comment, a
refreshed CVE-JSON attachment) and hands off to `sync-security-issue` to
reconcile the rest of the tracker. See [Step 6](#step-6--allocate-the-cve)
for the full detail.

### Tools you use most

- [`import-security-issue`](.claude/skills/import-security-issue/SKILL.md) —
  *"import new reports"* at the start of each triage sweep. The entry point
  into the process for `<security-list>` reports.
- [`import-security-issue-from-pr`](.claude/skills/import-security-issue-from-pr/SKILL.md) —
  *"import a tracker from PR <N>"* when a security-relevant fix landed
  publicly without going through `<security-list>` and the team has agreed
  it warrants a CVE. Lands directly in the `Assessed` column.
- [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md) —
  *"sync <issue-ref>"* or *"sync all"*. Surfaces stalled issues, missing
  fields, credit replies, and scope-split requirements in one combined
  proposal.
- [`allocate-cve`](.claude/skills/allocate-cve/SKILL.md) — *"allocate a CVE
  for <issue-ref>"*.
- [`generate-cve-json`](tools/vulnogram/generate-cve-json/SKILL.md) — to
  refresh the paste-ready JSON embedded in the issue body on demand.
- [`deduplicate-security-issue`](.claude/skills/deduplicate-security-issue/SKILL.md) —
  when two trackers describe the same root-cause bug discovered
  independently.
- [`invalidate-security-issue`](.claude/skills/invalidate-security-issue/SKILL.md) —
  *"close NN as invalid"* once Step 5 lands a consensus-invalid
  decision. Applies the `invalid` label, archives the project-board
  item, and (for `<security-list>`-imported trackers) drafts a reply
  to the reporter explaining the reasoning.

## For remediation developers — Steps 7–11

You own the tracker from a CVE allocated to a merged public fix PR in
`<upstream>` (including the `pr merged` hand-off where the tracker sits
waiting for the release train to ship). The role name matches the
`remediation developer` credit you receive in the published CVE record (see
`credits[]` with `type: "remediation developer"` in the generated CVE JSON).

### Picking up a tracker

Pick a tracker that has a scope label, `cve allocated`, and clear consensus
on the fix shape. Self-assign yourself on GitHub so the board reflects
ownership. See [Step 7](#step-7--self-assign-and-implement-the-fix).

### Attempting an automated fix

Before writing the fix by hand, consider letting the
[`fix-security-issue`](.claude/skills/fix-security-issue/SKILL.md) skill try
it first. Invoked as *"try to fix issue #N"* (or *"draft a PR for #N"*), the
skill:

- runs `sync-security-issue` first to make sure the tracker's state is
  current;
- reads the full tracker discussion and the linked `security@` mail
  thread and decides whether the issue is *easily fixable* — clear
  consensus on the fix shape, small scope, known location in
  `<upstream>`. If it is not, the skill stops and tells you what
  more the tracker needs before it is safe to attempt;
- if it is, proposes an implementation plan (which file(s) to touch,
  what to change, what tests to add) and **waits for your explicit
  confirmation** before making any edits;
- writes the change in your local `<upstream>` clone, runs the
  local static checks and tests, and iterates on failures;
- opens the public PR from your fork via `gh pr create --web` with a
  scrubbed title and body — every public surface (commit message,
  branch name, PR title, PR body, newsfragment) is grep-checked for
  `CVE-`, `airflow-s`, `vulnerability`, *"security fix"* and similar
  leakage before being written or pushed;
- updates the `<tracker>` tracking issue with the new PR
  link and applies the `pr created` label, handing back off to
  `sync-security-issue`.

The skill refuses to proceed in cases where a human decision still
needs to happen: reports that are still being assessed, reports not
yet classified as valid vulnerabilities, and changes that require the
private-PR fallback in
[Step 9](#step-9--open-a-private-pr-exceptional-cases). If it refuses,
fall back to the manual flow below.

Even when the skill succeeds end-to-end, you remain the PR's author
and reviewer-facing contact on the public `<upstream>` PR. Stay
on the PR through review and merge.

### Opening the public fix PR manually

If you are writing the fix by hand, write the code change in your local
`<upstream>` clone, run the local checks and tests, and open the PR
via `gh pr create --web`. The PR description **must not** reveal the CVE,
the security nature of the change, or link back to `<tracker>` —
see [Step 8](#step-8--open-a-public-pr-straightforward-cases) and the
confidentiality rules in
[`AGENTS.md`](AGENTS.md#confidentiality-of-the-tracker-repository).

Request a `backport-to-v3-2-test` (or equivalent) label on the public PR
when the fix should ship on a patch train.

### Private-PR fallback

In exceptional cases — highly critical fixes, or code that needs private
review — open the PR against the `main` branch of `<tracker>`
instead of `<upstream>`. CI does not run there, so run static checks and
tests manually before asking for review. Once approved, re-open the PR in
`<upstream>` by pushing the branch public. See
[Step 9](#step-9--open-a-private-pr-exceptional-cases).

### Handoff to the release manager

Once the `<upstream>` PR merges, `sync-security-issue` moves the tracker
from `pr created` to `pr merged` and sets the milestone of the release the
fix will ship in. The tracker then waits for the release train. When the
release ships, sync swaps `pr merged` → `fix released` and the tracker
becomes the release manager's responsibility. See
[Step 11](#step-11--pr-merged) and [Step 12](#step-12--fix-released).

### Tools you use most

- [`fix-security-issue`](.claude/skills/fix-security-issue/SKILL.md) —
  *"try to fix issue #N"*. Proposes a plan, writes the code, runs local
  tests, and opens a `--web` PR with a scrubbed title/body. See
  [Attempting an automated fix](#attempting-an-automated-fix) above for
  the full flow and the cases where the skill refuses to proceed.
- [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md) — to
  keep the tracker's labels, milestone, and assignee aligned with the PR
  state as it moves through review and merge.

## For release managers — Steps 12–15

You own the tracker from the moment the fix actually ships (`fix released`)
to a closed tracking issue with a PUBLISHED CVE record. The hand-off from
the remediation developer is automatic: `sync-security-issue` detects the
milestone version on PyPI / the Helm registry, swaps `pr merged` →
`fix released`, and assigns the advisory-send to you.

### Handoff from the remediation developer

Watch your `fix released` queue on the board. Until the `pr merged` →
`fix released` swap fires, the tracker is still the remediation developer's
(Step 11 territory). Once it fires, it is yours. See
[Step 12](#step-12--fix-released).

### Sending the advisory

Review the attached CVE JSON on the tracker, fill any missing body fields
(CWE, severity, affected versions), and send the advisory emails to
`<announce-list>` / `<users-list>` from the ASF CVE tool.
Add `announced - emails sent` and remove `fix released`. **Do not close the
issue yet** — see [Step 13](#step-13--send-the-advisory).

### Capturing the public archive URL

This is a handoff the sync skill handles for you: once the advisory has
been archived on the users@ list, the next `sync-security-issue` run finds
the URL, populates the *Public advisory URL* body field, regenerates the
CVE JSON attachment, and moves the label to `announced`. See
[Step 14](#step-14--capture-the-public-advisory-url).

### Publishing the CVE and closing the issue

For every `announced` issue: open Vulnogram at
`https://cveprocess.apache.org/cve5/<CVE-ID>#source`, paste the latest
attached CVE JSON, save, and move the record from REVIEW to PUBLIC.
Then close the issue (do not update any labels). This is the terminal
step of the lifecycle. See
[Step 15](#step-15--publish-the-cve-record-and-close-the-issue).

An issue that sits on `announced` for more than a day or two
is a signal to ping the RM.

### Post-release credit corrections

If credits need correction after announcement, respond to the announcement
emails with the missing credits, update the ASF CVE tool, and ask the ASF
security team to push the information to `cve.org`. See
[Step 16](#step-16--credit-corrections).

### Tools you use most

- [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md) —
  *"sync announced"* at the start of each release window, to
  see the `announced` backlog needing a Vulnogram push. Also
  *"sync CVE-YYYY-NNNN"* to drill into one specific CVE before sending the
  advisory.
- [`generate-cve-json`](tools/vulnogram/generate-cve-json/SKILL.md) — to
  regenerate the attachment on demand when a body field changes after the
  URL has been captured.

## Process reference: the 16 steps

This is the authoritative step-by-step description of the lifecycle. Each
role section above points into specific steps. If something in the role
sections conflicts with what is here, the reference wins.

### Step 1 — Report arrives on security@

The reporter reports the issue to the adopting project's
`<security-list>` or to `security@apache.org` (in the latter case,
the security team of the Apache Software Foundation will forward the
issue to the project's security mailing list).

### Step 2 — Import the report

**Import the report into `<tracker>` as a tracking issue.** The
[`import-security-issue`](.claude/skills/import-security-issue/SKILL.md)
skill is the on-ramp of the process: it scans `<security-list>`
for threads that have not yet been imported, classifies each candidate
(real report vs. automated-scan / consolidated / media / spam), extracts
the issue-template fields from the root message, and proposes one tracker
per valid report plus a receipt-of-confirmation Gmail draft for each.
Nothing is applied without explicit user confirmation. A security team
member runs the skill (*"import new reports"*) as the first action of a
triage sweep; the newly-created issue lands with the `needs triage` label
set automatically by the issue template, and the draft reply is ready in
Gmail for the triager to review and send.

If the report is "obviously invalid" (we've seen such issues before and
triaged or responded to them) — for example an automated-scanner dump or a
consolidated multi-issue report — the skill proposes the matching canned
response from [`<project-config>/canned-responses.md`](<project-config>/canned-responses.md) as a Gmail draft
and does **not** create a tracker, so the invalid class never enters the
board.

The tracker still has no scope label at this point — that is applied at
Step 5 when validity is confirmed.

**Alternate entry point — found in a public PR.** Occasionally a
security-relevant fix lands as a public PR on `<upstream>` without ever
going through `<security-list>` (a contributor opens a routine-looking
fix that the security team later realises warrants a CVE). For that
case, use
[`import-security-issue-from-pr`](.claude/skills/import-security-issue-from-pr/SKILL.md)
instead of `import-security-issue`. The skill takes a PR URL/number,
detects scope from the changed file paths, and creates the tracker
directly in the **`Assessed`** column with the scope label applied —
the deliberate import implies the security team has already
informally concluded the report is a security issue, so the
validity-discussion gate at Step 5 is skipped and the tracker is
ready for `allocate-cve` immediately. There is no reporter to ack on
this path, so no Gmail draft is created. Only use this skill when the
security relevance is already agreed; for genuinely-uncertain reports,
discuss in security team chat first and then either route through
`security@` if a reporter is involved, or open a `Needs triage`
tracker manually.

### Step 3 — Discuss CVE-worthiness

In the issue, we discuss and agree on whether it is worth having a CVE for
it.

### Step 4 — Escalate stalled discussions

If the discussion stalls and we cannot make a decision in about 30 days,
escalate to a broader audience. Escalation runs in **two phases** —
phase 1 is a short call for ideas; phase 2, if phase 1 stays silent for
another ~7 days, is an AI-generated design-space analysis intended to
unstick the discussion by surfacing concrete options. **Both phases are
proposals that the triager driving the escalation reviews before
posting** — the agent never posts to the tracker, the
`<private-list>` thread, the `<security-list>` thread, or the reporter
without an explicit "go" from the triager.

Audiences (same for both phases):

* `<private-list>`
* `security@apache.org`
* the reporter(s) who raised the issue, asking them for their opinion and
  additional context

#### Phase 1 — short call for ideas (no AI analysis)

The first escalation message is **deliberately short**. It states the
report exists, that internal discussion has stalled for ~30 days, asks
the wider audience for input, and links the tracker URL as a stable
identifier — fine on either private or public audiences per the
[three-layer confidentiality rule](AGENTS.md#confidentiality-of-the-tracker-repository)
(URLs are public-safe; tracker contents and security framing stay
embargoed). It does **not** include a design-space analysis or
proposed fixes — that is phase 2's job. The point of phase 1 is to give domain experts who haven't seen
the report a chance to weigh in with their own ideas, without being
anchored to a pre-baked solution.

Phase-1 message shape (3-4 short paragraphs):

1. One sentence: tracker `<tracker>#NNN`, CVE `CVE-…`, one-line
   description.
2. One sentence: discussion has been stalled for `<N>` days, last
   substantive comment was `<date>` by `<who>`.
3. One sentence: we are asking for input on the design / fix-direction;
   any thoughts welcome.
4. The relevant links (tracker URL on private audiences only; GHSA URL
   if applicable; reporter thread ID).

The triager drafts this with the agent assistance, the agent presents
the draft as a proposal for review (Gmail draft + status-rollup
preview), and only after the triager confirms does the agent send /
post.

#### Phase 2 — AI-generated design-space analysis

When phase 1 has been out for **another ~7 days** with no substantive
response (silence, "+1 looks bad" without a fix proposal, or
acknowledgement-without-engagement), the agent prepares a deeper
analysis to unstick the design question. The shape:

1. **Lead with an AI-generated disclaimer** — the analysis was drafted
   by an AI agent, the triager reviewed it before posting, and errors
   are possible. Invite reviewers to push back on anything that smells
   wrong.
2. **Methodology for tagging** — explain how the people pinged were
   selected. Standard methodology: cross-reference of (a) top
   committers since `<date>` on the affected files (commit-frequency
   via `git log`), (b) the `<tracker>` collaborator list
   (`gh api repos/<tracker>/collaborators`), and (c)
   participants already engaged on the thread.
3. **TL;DR** — one paragraph with the recommended short-term + long-term
   fix combo.
4. **Why the obvious fix is insufficient** — if the discussion already
   surfaced a "just do X" suggestion that the agent thinks is partial,
   explain the gap concretely (with a code example showing the
   bypass). This is the most load-bearing part of the analysis — it
   converts a stalled "should we do X?" into a concrete "X alone
   doesn't close case Y, here is the alternative".
5. **Design-space options** — labelled A, B, C, etc. Each option has:
   *what it does* (concrete code sketch where useful), *what it
   closes*, *what it does not close*, *risk* (deployment-compat
   concerns, migration cost, etc.).
6. **Open design questions** — the 3-5 blockers that need a human
   decision before any of the options can ship. These are the things
   the agent cannot decide on its own (which option to take, how to
   handle migration, whether to deviate from a project convention).
7. **Tag people inline + at the bottom** with `@`-mentions per the
   methodology above.

The agent presents the full draft as a proposal — the entire comment
body, plus the list of `@`-handles it intends to mention with the
selection rationale. **The triager reviews and approves the draft
before the agent posts it** to the tracker. The same applies for any
parallel `<private-list>` mail draft that mirrors the analysis to
the PMC audience.

If the triager edits the draft, the agent applies the edits and
re-presents for confirmation. The agent does not "iterate to
quality" on its own — every visible change to the analysis goes
through the triager.

#### Recording the escalation on the tracker

Both phases land as rollup entries on the tracker (per
[`tools/github/status-rollup.md`](tools/github/status-rollup.md)),
tagged with the action label `Sync (Step 4 escalation)` so the audit
trail shows where in the timeline each phase was sent. The phase-1
entry records the message that went out and the silence-period clock
start; the phase-2 entry records the AI-analysis comment + the list
of people pinged + the 7-day post-phase-1 silence that triggered
phase 2.

#### Why phases

Posting an AI-generated analysis as the *first* escalation step
short-circuits the two best outcomes phase 1 is designed to produce:

- **A domain expert proposing a fix the agent didn't think of.** Phase
  1 leaves space for ideas the agent's literature is unaware of —
  particularly for cross-cutting architectural patterns that are
  obvious to someone with deep area knowledge but not visible from
  the file diff. The AI analysis tends to converge on
  reporter-suggested options + standard hardening patterns; it
  *will* miss novel approaches.
- **An expert flagging that the report is invalid / out of scope.**
  Sometimes the right answer is "this is documented behaviour" or
  "this duplicates `airflow-s#XYZ` from 2 years ago"; an AI analysis
  that already proposes a fix anchors the discussion towards
  *implementing* that fix rather than evaluating whether one is
  needed.

Phase 2 is for when phase 1 has demonstrably failed to produce
either outcome. Skipping straight to phase 2 turns the escalation
into a "rubber-stamp this design" ask, which is the opposite of what
the wider-audience step is for.

### Step 5 — Land the valid/invalid consensus

Finally, if we cannot reach consensus we follow
[voting](https://www.apache.org/foundation/voting.html#apache-voting-process).
A vote on code modification is used, which means that committers have
binding votes, whereas everyone else has advisory votes — and all are
encouraged to vote and express their opinion. If there is no major
disagreement during the discussion, there is no need to formally vote via
a mailing list thread — the voting is done in the PR. However, if there
are differing opinions, voting is done on the `<security-list>`
list. The `needs triage` label should then be removed.

### Step 6 — Allocate the CVE

If we agree the issue is invalid, a team member closes the issue and
responds to the reporter with that information. The
[`invalidate-security-issue`](.claude/skills/invalidate-security-issue/SKILL.md)
skill is the apply mechanism: it labels the tracker `invalid`, posts
a short closing comment, archives the project-board item, and — when
the tracker has an inbound `<security-list>` thread — drafts a
polite-but-firm reply to the reporter on the original Gmail thread,
with reasoning extracted from the tracker's discussion and a fitting
canned response from
[`<project-config>/canned-responses.md`](<project-config>/canned-responses.md)
as the spine. The draft is never sent — the triager reviews in Gmail
before sending. The skill hard-stops if a CVE is already allocated
(a Vulnogram REJECT is required first) or if the advisory has
already shipped (a public retraction needs explicit team
escalation).

If the issue is valid,
**a PMC member of the adopting project** allocates a CVE via the
project's CVE tool (see
[`<project-config>/project.md → CVE tooling`](<project-config>/project.md#cve-tooling)).
The allocation action is PMC-gated on the server side, so a triager
who is not on the PMC cannot complete the allocation themselves —
they prepare the request (using the
[`allocate-cve`](.claude/skills/allocate-cve/SKILL.md) skill, which
strips any redundant project prefix from the title per
`<project-config>/title-normalization.md` and builds a relay
message) and forward it to a PMC member via an `@`-mention on the
tracker or on the `<security-list>` thread. Once the PMC member has
allocated and reported the `CVE-YYYY-NNNNN` back, the skill can be
re-invoked with the ID as an override to wire the allocated CVE into
the tracker: the *CVE tool link* body field, the `cve allocated`
label, a status-change comment, and a refreshed CVE-JSON body embed.
The skill then hands off to `sync-security-issue` to reconcile the
rest of the tracker (milestone, assignee, fix-PR state,
reporter-thread drafts) in the same flow.

The team member (triager or PMC, whoever has the reporter's thread
loaded) then responds in the email thread to confirm creation of the CVE
to the reporter, including the CVE ID, asks the reporter how they would
like to be credited, and updates the reporter name in the issue
description when the reporter answers.

### Step 7 — Self-assign and implement the fix

One of the team members self-assigns the issue (not necessarily the
person who originally started the discussion) and implements the fix.

NOTE: In some cases it is possible to delegate the fix to a trusted
third-party individual. For example, if the security team member assigned
to the issue has access to developers willing or otherwise dedicated to
development on the adopting project, they may delegate to one such
individual, provided that:

1) The individual is trusted.
2) The individual only receives the information required to implement a
   fix (no wholesale sharing of security team emails, GitHub issues,
   etc.).
3) A LAZY CONSENSUS vote is conducted in either the email thread or the
   GitHub issue associated with the security issue (GitHub communications
   are synced to the email group for posterity).

### Step 8 — Open a public PR (straightforward cases)

If the issue is straightforward, it may be followed by a direct PR
in the `<upstream>` repository. The description in the PR should not
reveal the CVE or the security nature of it.

### Step 9 — Open a private PR (exceptional cases)

In exceptional cases — when the issue is highly critical, or when code
discussion is needed and the PR requires input and review before it gets
merged — the person solving it can create a PR in the `<tracker>`
repository with "Closes: #issue". The PR should be raised against the
`main` branch of the `<tracker>` repository (not the default branch
declared in `<project-config>/project.md → tracker_default_branch`).
This allows for detailed code-change discussion in private. For now,
CI is not run for PRs in the `<tracker>` repository, so static checks
and tests should be run manually by the person creating the PR. We
may improve this in the future. Once the PR has been reviewed,
approved, and is ready to merge, the branch with the fix should be
pushed to the `<upstream>` repository and the PR should be re-opened
there by pushing the branch to public `<upstream>` and merging it.

### Step 10 — Link the PR and apply `pr created`

Once the PR is created in the `<upstream>` repository, the team
member who creates it should link to the PR in the description of the
issue and mark the issue with the `pr created` label on `<tracker>`.

### Step 11 — PR merged

**PR merged.** When the `<upstream>` PR merges, the security team
member merging it should move the issue from `pr created` to `pr merged`.
If there is a private variant of the PR in the `<tracker>`
repository, it should be closed. The milestone of the issue should be set
to the milestone of the release it is planned to ship in.

The **milestone naming conventions** are project-specific; for the
currently adopting project see
[`<project-config>/milestones.md`](<project-config>/milestones.md), which
also records the policy for creating missing milestones via `gh api` and
for bumping a fix to the next minor release instead of the next patch
when triage warrants it.

**The issue stays at `pr merged` until the release containing the fix
actually ships.** That may be hours (for core patch releases cut on a
fast cadence) or weeks (for providers waves on a fixed monthly schedule).
During that window the issue is waiting on the release train, not on any
action from the security team — the next transition fires automatically
when the release hits PyPI / the Helm registry (Step 12).

### Step 12 — Fix released

**Fix released.** When the release carrying the fix actually ships
to users — the final release artefact (per the adopting project's
release-train conventions; for Airflow see
[`<project-config>/milestones.md`](<project-config>/milestones.md))
is live on the project's package index — the issue moves from
`pr merged` to `fix released`. The `sync-security-issue` skill
detects the release (by checking the project's package index for
the milestone version) and proposes the label swap on the next run,
so in practice this transition is automatic; a security team member
only needs to confirm the sync proposal.

**Why this is its own step.** The `pr merged` → `fix released` swap is
the cue that ownership of the issue has transferred from the fix author /
triager to the **release manager** for that release. Before
`fix released`, the issue is a code-change artifact; after `fix released`,
it is an advisory-coordination artifact and the release manager is
responsible for steps 13–15 below. Combining the two into one step made
this ownership hand-off implicit; splitting them makes it explicit and
surfaces a `fix released` backlog the release manager can drive from the
board.

### Step 13 — Send the advisory

During releases, the release manager looks through `fix released`
issues on `<tracker>`, updates the project's CVE tool (for Airflow,
[the ASF CVE tool](https://cveprocess.apache.org); in general see
`<project-config>/project.md → CVE tooling`), and updates the
following fields, taking them from the issue:

* CWE (Common Weakness Enumeration) — possible CWEs are available
  [here](https://cwe.mitre.org/data/index.html)
* Product name — per the adopting project's scope-label → product
  mapping (for Airflow, see
  [`<project-config>/scope-labels.md`](<project-config>/scope-labels.md))
* Version affected (`0, < Version released`)
* Short public summary
* Severity score — based on the
  [Severity Rating blog post](https://security.apache.org/blog/severityrating).
  The issue owner should, during discussion on the issue, propose the
  score and update the ticket. In obvious cases with no objections, this
  should work in lazy-consensus mode. If there are differing opinions,
  driving the discussion to achieve consensus is the preferred outcome.
  Voting may be cast if needed. If the severity has not been decided or
  consensus reached during earlier discussion, the Release Manager has
  the final say on the severity score (but should take into account the
  opinions of the security team). This is to prioritize getting the issue
  announcement out in a timely manner.
* References:
    * `patch` — PR to the fix in the `<upstream>` repository
* Credits:
    * `reporter` — reporter(s) of the issue
    * `remediation developer` — PR author(s)

The release manager also generates the CVE description, sets the CVE to
REVIEW if feedback is needed and then to READY, and eventually sends the
announcement emails from the CVE tool. The release manager then adds
the `announced - emails sent` label and removes the `fix released` label.
**The issue stays open** at this point — it is closed only at Step 15
below, after the public archive URL has been captured (Step 14) and the
CVE record has been moved to PUBLIC in Vulnogram (Step 15). This
gives the `sync-security-issue` skill one more handoff where it can
notice a missing archive URL and prompt for it before the issue is
forgotten.

### Step 14 — Capture the public advisory URL

**Capture the public advisory URL and move the tracker to
`announced`.** Once the announcement email has been delivered
and archived, this is done by the next `sync-security-issue` run (or the
release manager, if they want to drive it by hand):

* retrieves the archive URL from the
  [users@ list archive](https://lists.apache.org/list.html?<users-list>) —
  the `sync-security-issue` skill scans the archive for the CVE ID on
  every run and proposes the URL automatically once it finds a match;
* pastes the URL into the tracking issue's **Public advisory URL** body
  field (the field was added to the issue template specifically for this
  handoff — never reuse the *"Security mailing list thread"* field, which
  holds the private `security@` thread);
* regenerates the CVE JSON attachment — `generate-cve-json` now picks up
  the URL from the body automatically and tags it as `vendor-advisory` in
  `references[]`, so the attached CVE record carries a resolvable
  `vendor-advisory` link ready to paste into the ASF CVE tool;
* **adds the `announced` label** to the tracking issue. The
  issue **stays open** at this point — closing is the release manager's
  job in Step 15 below, after they have moved the CVE record to PUBLIC
  in Vulnogram.

Until the *Public advisory URL* field is populated, the
`sync-security-issue` skill will not propose moving the issue to
`announced` — this is deliberate: the field is what the CVE
record's public `vendor-advisory` reference will point at, and publishing
a CVE with an empty reference leaks a broken record into `cve.org`.

### Step 15 — Publish the CVE record and close the issue

**Push the final CVE record and close the issue.** For every issue
carrying the `announced` label, the release manager (the
same person who sent the advisory in Step 13):

* opens the Vulnogram `#source` tab at
  `https://cveprocess.apache.org/cve5/<CVE-ID>#source`;
* copies the latest CVE JSON attachment from the tracking issue (the one
  regenerated in Step 14, now carrying the `vendor-advisory` URL) and
  pastes it into the `#source` form;
* saves and moves the record from `REVIEW` to `PUBLIC` in the ASF CVE
  tool — **this is the final action** that propagates the record to
  [`cve.org`](https://cve.org);
* **closes the issue** — do not update any labels. That closes
  the lifecycle.

This two-step hand-off (sync captures the URL → RM publishes the record)
means nobody has to remember both halves: the sync skill's responsibility
ends when the label is `announced`, and the RM's
responsibility is scoped to taking an `announced` issue to the
closed state. An issue that sits on `announced` for more than
a day or two is a signal to ping the RM.

### Step 16 — Credit corrections

If we need to add missing credits (which sometimes happens due to
copy-and-paste errors and the brittleness of the process), the release
manager:

* responds to the announcement emails and mentions the missing credits
* updates the [ASF CVE tool](https://cveprocess.apache.org) with the
  missing credits
* asks the ASF security team to push the information to
  [cve.org](https://cve.org)

## Label lifecycle

### State diagram

The diagram below shows the typical state flow. Each node is a label (or a
cluster of labels that co-exist); each edge is a process step that moves
the issue forward. Closing dispositions (`invalid`, `not CVE worthy`,
`duplicate`, `wontfix`) can terminate the flow at any point after
`needs triage`.

```mermaid
flowchart TD
    A([report on project security list]) -->|step 2: import-security-issue| B[needs triage]
    A2([security-relevant fix in public PR]) -->|step 2 alt: import-security-issue-from-pr| C
    B -->|step 5: consensus invalid| X1([invalid / not CVE worthy / duplicate / wontfix])
    B -->|step 5: consensus valid| C["scope label<br/>(project-specific — see<br/>projects/&lt;PROJECT&gt;/scope-labels.md)"]
    C -->|step 6: CVE reserved by PMC member| D[cve allocated]
    D -->|step 10: public PR opened| E[pr created]
    E -->|step 11: PR merges| F[pr merged]
    F -->|step 12: release ships| G[fix released]
    G -->|step 13: advisory sent| H[announced - emails sent]
    H -->|step 14: archive URL captured| J[announced]
    J -->|step 15: RM moves CVE to PUBLIC + close| Z([issue closed])

    classDef closed fill:#f8d7da,stroke:#842029,color:#000;
    classDef done fill:#d1e7dd,stroke:#0f5132,color:#000;
    class X1,Z closed;
    class H,J done;
```

The dashed-equivalent entry from `A2` represents the deliberate-import
path described in [Step 2](#step-2--import-the-report) above:
trackers opened from a public PR skip the `needs triage` column and
land directly at `scope label` (the `Assessed` column on the project
board) because the validity assessment has already happened
informally before invocation.

### Label reference

The table below repeats the same flow in tabular form. An issue typically
moves through these labels left-to-right.

**Scope labels are project-specific** — the adopting project's concrete
scope labels live in
[`<project-config>/scope-labels.md`](projects/) (for the currently
adopting project, [`<project-config>/scope-labels.md`](<project-config>/scope-labels.md)).
The table below uses `<scope>` as a placeholder for whichever scope
labels the adopting project defines.

| Label | Meaning | Added at step | Removed at step |
| --- | --- | --- | --- |
| `needs triage` | Freshly filed; assessment not yet started. | 1 | 5 |
| `<scope>` | Scope of the vulnerability. Exactly one project-specific scope label is set. | 5 | never (sticks for the lifetime of the issue) |
| `cve allocated` | A CVE has been reserved for the issue. Allocation itself is PMC-gated (only the adopting project's PMC members can submit the CVE-tool allocation form); a non-PMC triager relays a request to a PMC member via the [`allocate-cve`](.claude/skills/allocate-cve/SKILL.md) skill. | 6 | never |
| `pr created` | A public fix PR has been opened on `<upstream>` but has not yet merged. | 10 | 11 (replaced by `pr merged`) |
| `pr merged` | The fix PR has merged into `<upstream>`; no release with the fix has shipped yet. | 11 | 12 (replaced by `fix released` when the release ships) |
| `fix released` | A release containing the fix has shipped to users; advisory has not been sent yet. | 12 | 13 (replaced by `announced - emails sent`) |
| `announced - emails sent` | The public advisory has been sent to the project's announce and users mailing lists (see `<project-config>/project.md → Mailing lists`). The issue **stays open** after this label is applied; closing is gated on the RM completing Step 15. | 13 | never (stays on the issue after closing for audit history) |
| `announced` | The public advisory URL has been captured in the tracking issue's *Public advisory URL* body field and the attached CVE JSON has been regenerated so its `references[]` now carries the `vendor-advisory` URL. The tracking issue is waiting for the release manager to copy the CVE JSON into the project's CVE tool, move the record to PUBLIC, and close the issue (Step 15). No label changes at close — the issue closes with `announced` still set. | 14 | never (stays on the issue after closing) |
| `wontfix` / `invalid` / `not CVE worthy` / `duplicate` | Closing dispositions for reports that are not valid or not CVE-worthy. | 5 / 6 | — |

The [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md)
skill keeps these labels honest: on every run it detects the current state
of the issue, the fix PR, and the release train, and proposes the label
transitions the process requires.

## Current projects

One row per project configured under
[`projects/`](projects/). The directory name is the resolution key
for the `<PROJECT>` placeholder used throughout the framework (see
[`AGENTS.md` — Placeholder convention](AGENTS.md#placeholder-convention-used-in-skill-files)).

| Project | Directory | Index | Manifest |
|---|---|---|---|
| [Apache Airflow](https://airflow.apache.org/) | [`projects/airflow/`](projects/airflow/) | [`<project-config>/README.md`](<project-config>/README.md) | [`<project-config>/project.md`](<project-config>/project.md) |

Add a new project by copying
[`projects/_template/`](projects/_template/) into
`projects/<name>/`, filling in the TODO placeholders, and adding a
row to the table above. The full bootstrap walk-through lives in
[`projects/README.md`](projects/README.md#bootstrapping-a-new-project).
