<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Vulnogram — record management](#vulnogram--record-management)
  - [Record URLs](#record-urls)
  - [Two record-write paths — API (default) and copy-paste (fallback)](#two-record-write-paths--api-default-and-copy-paste-fallback)
  - [`#source` paste flow](#source-paste-flow)
  - [State machine](#state-machine)
  - [Reviewer-comment signal](#reviewer-comment-signal)
  - [Record-generator round trip](#record-generator-round-trip)
  - [Release-manager checklist](#release-manager-checklist)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Vulnogram — record management

The Vulnogram-side mechanics of **maintaining** a CVE record from
allocation through publication. The generic handling process (steps
13–15 of [`../../README.md`](../../README.md)) describes *what* has
to happen; this file documents the **Vulnogram-specific** *how*.

Per-project URL templates live in
[`../../<project-config>/project.md`](../../<project-config>/project.md#cve-tooling)
(`cve_tool_record_url_template`, `cve_tool_source_tab_url_template`).

## Record URLs

| Purpose | URL |
|---|---|
| Record page (human-readable + edit surface) | `https://cveprocess.apache.org/cve5/<CVE-ID>` |
| `#source` tab (paste-the-JSON target) | `https://cveprocess.apache.org/cve5/<CVE-ID>#source` |
| `#json` tab (rendered view of the stored JSON) | `https://cveprocess.apache.org/cve5/<CVE-ID>#json` |
| `#email` tab (preview the advisory email before sending) | `https://cveprocess.apache.org/cve5/<CVE-ID>#email` |

The `#email` tab is the **email-preview** surface: it renders the
advisory exactly as Vulnogram will send it to `<users-list>` and
`<announce-list>` — same subject, same body, same recipient list.
The release-manager checklist in
[the *Release-manager checklist* section below](#release-manager-checklist)
calls this out as a load-bearing checkpoint **before** hitting Send,
because the preview surfaces formatting issues (truncation, broken
markdown, missing patch links) that the JSON view does not.

The ASF CVE tool requires ASF OAuth; non-security-team members can
see a record only after it has moved to `PUBLIC` (at which point the
mirrored record at `cve.org/CVERecord?id=<CVE-ID>` is the canonical
public link per the *"Linking CVEs"* section of
[`../../AGENTS.md`](../../AGENTS.md)).

## Two record-write paths — API (default) and copy-paste (fallback)

The release manager has two ways to push the CVE JSON onto a
Vulnogram record. **The API path is the default proposal** — it
runs from the same shell the rest of the skills do and removes
the manual paste round-trip. The copy-paste flow stays documented
because (a) ASF-OAuth sessions expire and the API path needs a
re-setup once a session ages out, and (b) some operators prefer
not to keep a session-cookie file on disk at all.

| Path | When | One-liner | Setup |
|---|---|---|---|
| **API (default)** | Every paste step in the *Release-manager checklist* below | `uv run --project <framework>/tools/vulnogram/oauth-api vulnogram-api-record-update --cve-id <CVE-ID> --json-file <path>` | One-time `vulnogram-api-setup` per machine — see [`oauth-api/README.md`](oauth-api/README.md) |
| **Copy-paste (fallback)** | Operator opted out (`tools.vulnogram.api_backend: copy_paste` in `.apache-steward-overrides/user.md`), or the API path returned `SessionExpired` and re-setup is deferred | Open `#source`, paste, **Save** (see *[`#source` paste flow](#source-paste-flow)*) | None |

The agentic skills (`security-cve-allocate`, `security-issue-sync`)
run `vulnogram-api-check` before proposing the paste step. Possible
outcomes drive the proposal:

- **`valid` (exit 0)** — propose the API one-liner; the copy-paste
  recipe stays available as a one-line *"or open `#source` and
  paste"* fallback for users who want the visual confirmation.
- **`expired` (exit 1)** — propose `vulnogram-api-setup` first and
  the API one-liner second, with the copy-paste recipe as the
  fallback if the operator wants to skip re-setup for this CVE.
- **`not-configured` (exit 2)** — propose `vulnogram-api-setup`
  with a one-line *"or skip setup and use the copy-paste flow
  below"* hint. **Do not** force setup on an unwilling operator.

The state-transition clicks (`DRAFT` → `REVIEW`,
`REVIEW` → `READY`, `READY` → `PUBLIC`) stay in the Vulnogram UI
in **both** paths. The state lives in the document body's
`CNA_private.state` field — pre-setting it before the API call
works for `DRAFT` ↔ `REVIEW`, but the `READY` → `PUBLIC` push has
out-of-band side effects (CNA-feed dispatch to `cve.org`) and we
deliberately do not automate it.

## `#source` paste flow

The generic release-manager workflow is *"push the final CVE record
and close the issue"* (step 15). On Vulnogram that decomposes into:

1. Open the record's `#source` tab at
   `https://cveprocess.apache.org/cve5/<CVE-ID>#source`.
2. Copy the CVE JSON from the tracking issue's embedded attachment
   (regenerated by the `generate-cve-json` tool on every sync —
   see the *"Record-generator round trip"* section below).
3. Paste into the `#source` form and **Save**.
4. Use the UI action to move the record from `REVIEW` to `PUBLIC`
   (or from `DRAFT` to `REVIEW` first if the record is still in the
   pre-review state).

`PUBLIC` is the terminal state — Vulnogram pushes the record to
`cve.org` via the CNA feed once the state lands there.

## State machine

Vulnogram wraps every record in a `CNA_private` envelope whose
`state` field drives the visibility + CNA-feed push. The four
states the generic skills interact with:

| State | Set by | What it means |
|---|---|---|
| `DRAFT` | Allocation (initial state post-allocation) | Record exists, ID is reserved, but content is still being filled in. Not visible on `cve.org`. |
| `REVIEW` | Release manager once the content is complete | Ready for CNA review. ASF CNA reviewers may leave reviewer comments at this point (see *"Reviewer-comment signal"* below). Still not on `cve.org`. |
| `READY` | Release manager once review feedback is addressed (or immediately after `REVIEW` if no feedback arrived) | Content is final and the record is staged for the advisory-send step. The advisory emails are dispatched from Vulnogram while in `READY`. Still not on `cve.org`. |
| `PUBLIC` | Release manager as the terminal step | Record pushed to `cve.org`. World-readable. The generic tracking-issue lifecycle terminates at the `close` action once this state has been reached. |

**`DRAFT` → `REVIEW`** happens when all required fields are populated.
The release manager moves the record to `REVIEW` after the first
JSON paste, opening the window for CNA reviewers to leave comments.

**`REVIEW` → `READY`** happens once any reviewer comments have been
addressed (via the body-field round-trip described in the
*Record-generator round trip* section below), or immediately after
`REVIEW` when no comments arrive. `READY` is the state Vulnogram
expects when the release manager triggers the advisory email send.

**`READY` → `PUBLIC`** is a human release-manager click in Vulnogram
after the advisory archive URL has been captured on the tracker. The
generic `security-issue-sync` skill's Step 2b does not propose this
transition — it is a Step 15 release-manager action. The
publication-ready notification comment (see
[*Release-manager checklist*](#release-manager-checklist) below)
gives the RM the explicit go-ahead.

`PUBLISHED` is sometimes used as a synonym for `PUBLIC` in older
Vulnogram documentation; the current action is literally labelled
`PUBLIC` in the UI.

The `generate-cve-json` tool decides `REVIEW` versus `DRAFT` for the
generated `CNA_private.state` field by inspecting whether the tracker's
*public-advisory-url* body field is populated and whether a
`vendor-advisory` reference landed in the generated `references[]`;
see the *`_is_cna_ready_for_review`* helper in
`generate-cve-json/src/…/cve_json.py` for the exact predicate. The
`READY` state itself is set by hand in Vulnogram after the
post-`REVIEW` body-field stabilisation — the generator does not emit
`READY` directly because it cannot tell, from the tracker body alone,
whether reviewer comments are still pending.

## Reviewer-comment signal

ASF CNA reviewers leave comments on `REVIEW`-state records. Those
comments do **not** surface on the tracking issue directly —
Vulnogram notifies by email to the project's `security_list`
instead, with the CVE ID in the subject line. The `security-issue-sync`
skill's Step 1e reads those emails (Gmail search recipe lives in
[`../gmail/search-queries.md`](../gmail/search-queries.md#security-issue-sync--cve-review-comment-search))
and surfaces each open reviewer comment in Step 2b as an actionable
body-field proposal on the tracker.

The round trip is: reviewer leaves comment in Vulnogram → Vulnogram
emails `security_list` → sync skill reads email → sync skill proposes
a tracker body-field update → user confirms → `generate-cve-json`
re-emits the JSON attachment on the next sync → release manager
re-pastes the updated JSON into `#source` → `sync` detects the
comment is resolved on the next run. This indirection keeps the
single source of truth on the **tracking issue body** (which the
skills can read + write) rather than inside Vulnogram (which is
OAuth-gated and not readable from skill context).

The `cveprocess.apache.org/cve5/<CVE-ID>.json` endpoint exists but
is behind ASF OAuth and is **not** readable from agent-skill
context — the `security-issue-sync` skill therefore never curls it;
Gmail is the load-bearing signal source.

## Record-generator round trip

The `generate-cve-json` tool under
[`generate-cve-json/`](generate-cve-json/) reads a tracker issue and
emits a paste-ready CVE JSON record in the exact shape Vulnogram's
`#source` tab accepts — CNA container, `CNA_private` envelope,
sorted references, deterministic byte output. The tool's behavioural
contract lives in
[`generate-cve-json/SKILL.md`](generate-cve-json/SKILL.md); the
local-setup / test workflow lives in
[`generate-cve-json/README.md`](generate-cve-json/README.md).

Skills that update the tracker body call the tool with `--attach` so
the embedded CVE JSON in the tracker body stays in lock-step with
the body fields — every sync, every allocate-CVE wire-back, every
dedupe merge regenerates the attachment. The release manager then
has one canonical JSON to paste into `#source` at step 15.

## Release-manager checklist

When the `<upstream>` release containing a fix ships, the
`security-issue-sync` skill swaps the tracker's `pr merged` label to
`fix released`, reassigns the issue to the release manager, and posts
an explicit **release-manager hand-off comment** on the tracker (the
template body lives in
[`release-manager-handoff-comment.md`](release-manager-handoff-comment.md)).
The numbered checklist below is the standalone authoritative recipe
the comment links to — keep them in lock-step when one changes.

The flow has **two writes** in the common case (no reviewer comments)
and **three** when reviewer comments arrive. Each write lands on the
record via either the API (default — see
[*Two record-write paths*](#two-record-write-paths--api-default-and-copy-paste-fallback))
or copy-paste (fallback). The instructions below show the API form
inline; the copy-paste form is the *"open `#source`, paste, Save"*
flow described in [*`#source` paste flow*](#source-paste-flow):

1. **First write — `DRAFT` → `REVIEW`.** Push the CVE JSON
   embedded in the tracking issue (regenerated by `generate-cve-json`
   on every sync — see
   [*Record-generator round trip*](#record-generator-round-trip)
   above). Then move the record `DRAFT` → `REVIEW` via the Vulnogram
   UI button.

   ```bash
   # API path (default). Save the embedded JSON to a file first if
   # you only have it in the tracker body — `gh issue view <N>
   # --jq .body` + an editor's selection-to-file works, or use
   # `generate-cve-json --out <path>` to write the canonical artefact.
   uv run --project <framework>/tools/vulnogram/oauth-api vulnogram-api-record-update \
     --cve-id <CVE-ID> --json-file <path>
   ```

2. **(conditional) Re-write after reviewer comments.** ASF CNA
   reviewers may leave comments while the record sits in `REVIEW`
   (see [*Reviewer-comment signal*](#reviewer-comment-signal) above).
   The `security-issue-sync` skill detects them automatically and
   proposes matching body-field updates on the tracker; the security
   team confirms and the embedded JSON regenerates. Once the body has
   settled (no more pending reviewer-comment proposals), re-push the
   regenerated JSON via the same `vulnogram-api-record-update` call
   (or, fallback, re-paste into `#source` and **Save**). **Skip this
   step if no reviewer comments arrived** (the common case for
   well-formed records).

3. **Set `READY`.** Vulnogram UI action — moves the record from
   `REVIEW` to `READY` and stages it for the advisory-send step.

4. **Preview the advisory email** on the
   [`#email` tab](#record-urls). The preview renders the advisory
   exactly as Vulnogram will send it — same subject, same body, same
   recipient list. The preview is the load-bearing checkpoint for
   formatting issues (truncation, broken markdown, missing patch
   links) that the JSON view does not surface. **Always preview
   before sending.** If anything needs to change, edit the
   corresponding body field on the tracker, wait for the JSON to
   regenerate, re-paste in `#source`, and re-preview.

5. **Send the advisory emails.** Vulnogram dispatches to
   `<users-list>` and `<announce-list>`. On the tracker, add the
   `announced - emails sent` label and remove `fix released`.

6. **Wait for the publication-ready notification comment.** The
   `security-issue-sync` skill scans the public users-list archive
   for the CVE ID on every run. Once it finds the archived advisory,
   it populates the tracker's *Public advisory URL* body field,
   regenerates the CVE JSON to carry the archive URL as a
   `vendor-advisory` reference, adds the `announced` label, **and
   posts a publication-ready notification comment** on the tracker
   (the template body lives in
   [`release-manager-publication-comment.md`](release-manager-publication-comment.md)).
   That comment is the explicit go-ahead for steps 7-8.

7. **Second write — `READY` → `PUBLIC`.** *Only after the
   publication-ready notification fires.* Push the now-final JSON
   (carrying the archive URL in `references[]`) via the API path
   (or, fallback, re-open `#source` and paste). Then move the record
   `READY` → `PUBLIC` via the Vulnogram UI button — the
   `READY` → `PUBLIC` transition is intentionally not automated
   because it triggers the CNA-feed dispatch to `cve.org`.

   ```bash
   uv run --project <framework>/tools/vulnogram/oauth-api vulnogram-api-record-update \
     --cve-id <CVE-ID> --json-file <path-to-final-json>
   ```

8. **Close the tracker.** Close as completed; do not update any
   labels. The `security-issue-sync` skill's apply step archives the
   project-board item afterwards (per the *archive-from-board* recipe
   in [`../github/project-board.md`](../github/project-board.md))
   so the closed tracker leaves the active board.

The "twice write" framing in the hand-off comment maps to steps 1
and 7 of the checklist above; step 2 is the rare conditional middle
write. The hand-off comment (template at
[`release-manager-handoff-comment.md`](release-manager-handoff-comment.md))
proposes the API one-liner inline and links the copy-paste fallback;
keep both in lock-step when one changes.
