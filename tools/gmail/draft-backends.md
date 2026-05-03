<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Gmail drafting backends](#gmail-drafting-backends)
  - [Why there are two](#why-there-are-two)
  - [How the skills pick a backend](#how-the-skills-pick-a-backend)
  - [Detecting drafts that already exist on a thread](#detecting-drafts-that-already-exist-on-a-thread)
  - [Limitations that apply to both backends](#limitations-that-apply-to-both-backends)
  - [Known issue — `oauth_curl` thread-attached drafts may not surface in the global Drafts folder](#known-issue--oauth_curl-thread-attached-drafts-may-not-surface-in-the-global-drafts-folder)
    - [Recommended workflow when re-drafting on a thread that already carries a pending draft](#recommended-workflow-when-re-drafting-on-a-thread-that-already-carries-a-pending-draft)
    - [Concrete steps when the pile-up has already happened](#concrete-steps-when-the-pile-up-has-already-happened)
    - [When this rule does not apply](#when-this-rule-does-not-apply)
  - [Migration — when the claude.ai MCP adds `threadId`](#migration--when-the-claudeai-mcp-adds-threadid)
  - [Referenced by](#referenced-by)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Gmail drafting backends

The skills create Gmail drafts via one of two backends, selected by the
user in [`config/user.md`](../../config/user.md) under
`tools.gmail.draft_backend`:

| Backend | Value | `threadId` attach? | Setup |
|---|---|---|---|
| claude.ai Gmail MCP | `claude_ai_mcp` (default) | **no** (subject-matched fallback only) | none — works as soon as the Gmail connector is authenticated on claude.ai |
| OAuth + `curl` script | `oauth_curl` | **yes** | one-time Google OAuth client + refresh-token setup, automated via `uv run --project <framework>/tools/gmail/oauth-draft oauth-draft-setup` — see [`oauth-draft/README.md`](oauth-draft/README.md) |

Both backends create **drafts** — never send. The human review-and-send
step is still required before any outbound message leaves the user's
Gmail.

## Why there are two

The first-party claude.ai Gmail MCP is easy to set up and exposes
everything the skills need for reading, searching, and listing drafts.
It is the default.

The MCP's `create_draft` tool, however, does not accept a `threadId`
parameter — a gap between the underlying Gmail REST API (which
supports it on `drafts.create`) and the MCP's surface area. As a
consequence, drafts created via the MCP start a new conversation on
the **sender's** Gmail side. Recipients' mail clients thread-match by
subject (`Re: <exact subject>` + matching `In-Reply-To` / `References`
chain) and usually attach the reply correctly on their side, but the
sender sees a new conversation in their drafts queue. That makes
pre-send auditing harder and means subsequent sync runs cannot rely
on a single `threadId` to find every draft for a tracker.

The `oauth_curl` backend closes the gap by talking to the Gmail REST
API directly, with a user-provided refresh token. It is opt-in because
it requires a one-time OAuth setup (create a Google Cloud OAuth
client, obtain a refresh token, drop it in a credentials file).

## How the skills pick a backend

Every skill step that currently reads *"create a Gmail draft via
`mcp__claude_ai_Gmail__create_draft`"* actually means *"create a draft
via the project's preferred drafting backend, with `oauth_curl` always
preferred when it is available"*.

**Precedence — `oauth_curl` wins whenever it is configured**, regardless
of what `tools.gmail.draft_backend` is set to. The point of having
`oauth_curl` set up is `threadId` attachment; if the credentials are
on disk, the skills should always use them. Resolution:

1. **Probe for `oauth_curl` credentials** in this order:
   - `tools.gmail.oauth_credentials_path` from
     [`config/user.md`](../../config/user.md) when set;
   - the `$GMAIL_OAUTH_CREDENTIALS` environment variable;
   - the default path `~/.config/apache-steward/gmail-oauth.json`.

   The probe is a single `test -f <path>` — actually parsing the file
   or doing a token-refresh probe at this stage would burn HTTP
   round-trips on every draft and is wasted work; if the file exists,
   trust it and let the script's first call surface any auth failure
   with a clear error.
2. **If credentials are found → use `oauth_curl`** unconditionally.
   Invoke
   `uv run --project <framework>/tools/gmail/oauth-draft oauth-draft-create`
   with `--thread-id`, `--to`, `--cc`, `--subject`, `--body-file` —
   see [`oauth-draft/README.md`](oauth-draft/README.md) for the full
   shape.
   `threadId` attachment is guaranteed; the draft surfaces in both the
   conversation view (recipient-side threading) and — when no pile-up
   blocks it — the global Drafts folder. The user's
   `tools.gmail.draft_backend` setting is **ignored** in this branch.
3. **If credentials are not found, fall back to `claude_ai_mcp`** —
   call `mcp__claude_ai_Gmail__create_draft`. `threadId` attachment is
   unavailable; the draft uses the subject-matched path documented in
   [`threading.md`](threading.md#fallback--subject-matched-draft-when-threadid-is-unavailable).
4. **Hard explicit override**: a user who has oauth credentials on
   disk **but** wants to force `claude_ai_mcp` for a specific reason
   (e.g. the pile-up workaround in the next section) sets
   `tools.gmail.draft_backend: claude_ai_mcp_force` (note the
   `_force` suffix). The plain `claude_ai_mcp` value is treated as
   *"OK with either, prefer oauth_curl"* — it is the default, so a
   user who explicitly set it that way had no oauth set up at the
   time and the precedence rule covers them automatically once they
   add credentials. The `_force` suffix is the explicit *"never use
   oauth_curl"* signal.

The skills **surface which backend was used** in the proposal / recap
so the user can tell at a glance whether the draft threads on their
own Gmail view or only on the recipient's. The format is one line:

> *Draft created via `oauth_curl` (threadId-attached on
> `<thread-id-prefix>...`)*

or

> *Draft created via `claude_ai_mcp` (subject-matched fallback —
> `oauth_curl` credentials not found at default path; install via
> `uv run --project <framework>/tools/gmail/oauth-draft oauth-draft-setup`
> to get threadId attachment)*

The fallback line is intentionally noisy when oauth credentials are
absent — a user who would benefit from threadId attachment should
see the install hint on every draft creation until they set it up.

## Detecting drafts that already exist on a thread

Before drafting a reply on a thread, skills check whether a pending
draft already exists so they do not silently shadow it (the claude.ai
MCP cannot update or delete drafts; see
[`operations.md`](operations.md#hard-limitation--no-update-no-delete)).
The detection rule depends on which backend created the prior draft:

- **`claude_ai_mcp` drafts** live as standalone server-side
  conversations on the user's Gmail. Detect them via
  `mcp__claude_ai_Gmail__list_drafts`, optionally narrowed by
  `query: "<recipient-email>"` or a distinctive subject substring.
  Each MCP-created draft surfaces as a separate top-level entry in
  the Drafts folder.
- **`oauth_curl` drafts** attach to the inbound thread by `threadId`.
  They carry the `DRAFT` label but **may not surface in the global
  Drafts folder when multiple drafts pile up on the same thread**
  (see the *Known issue* section below). Detect them by reading the
  thread directly:

  ```
  mcp__claude_ai_Gmail__get_thread(threadId: "<inbound-thread-id>", messageFormat: MINIMAL)
  ```

  and scanning the returned messages for any whose `labelIds` (or
  the snippet's metadata) include `DRAFT`. Every `oauth_curl`-
  created draft on a thread is reachable this way regardless of
  pile-up. **`list_drafts` alone is not sufficient** when oauth
  credentials are configured — always do the per-thread check too.

The composite rule: when a skill is about to draft a reply, run
**both** detection paths (list_drafts + get_thread on the inbound
threadId) and treat any hit as *"a draft already exists; surface it
to the user before drafting a new one"*.

## Limitations that apply to both backends

- **No update, no delete** on the claude.ai MCP side — see
  [`operations.md` — Hard limitation](operations.md#hard-limitation--no-update-no-delete).
  The `oauth_curl` script could in principle update or delete drafts
  too (the Gmail API supports it), but the skills deliberately do
  not, to keep the drafts queue immutable and auditable.
- **Drafts are always drafts** — both backends skip the `send`
  operation. A human review step is non-negotiable.
- **Confidentiality** — both leave drafts in the user's personal
  Gmail account. The `oauth_curl` backend additionally requires the
  user to manage a refresh token on disk; treat it like an SSH key.

## Known issue — `oauth_curl` thread-attached drafts may not surface in the global Drafts folder

Caught live on 2026-04-25 during the [`<tracker>#346`](https://github.com/<tracker>/issues/346)
fix-skill flow: when **multiple `oauth_curl`-backed drafts pile up on
the same Gmail thread** within a single skill flow (typical sequence:
security-cve-allocate drafts a CVE-allocated message → security-issue-sync
drafts a corrected version with updated state → security-issue-fix
drafts the final version after a state change), the drafts all carry
the `DRAFT` label in the Gmail API but **only the most recent surfaces
in the user's global Drafts folder in Gmail's UI**. The earlier ones
become reachable only by direct URL or by opening the conversation
view of the thread. The user's own report from that session:
*"Can't see the draft — I see some old drafts on the list but they
are missing"*.

This appears to be a Gmail UI behaviour where multiple `threadId`-
attached drafts on a single conversation collapse / hide in the
global Drafts list rather than rendering as N separate entries. The
drafts exist (a `gh api repos/.../drafts` round-trip confirms `DRAFT`
labels and full message bodies); they are simply not navigable from
the standard Drafts folder when stacked.

The MCP-backed `claude_ai_mcp` path does not have this problem because
each draft lives on its own server-side conversation (no `threadId`
attachment), so each draft is a separate top-level entry in the
Drafts folder.

### Recommended workflow when re-drafting on a thread that already carries a pending draft

When a skill is about to draft a reply on a thread that **already
has a pending draft on it from an earlier skill pass in the same
session**, prefer the `claude_ai_mcp` backend for the new draft —
even when `tools.gmail.draft_backend` is set to `oauth_curl`. The
trade-off:

- **Visibility wins:** the new draft is guaranteed to surface in the
  user's Gmail Drafts folder, so they can actually see and review it.
- **Sender-side threading lost:** the new draft will start a new
  server-side thread on the user's own Gmail (Evan's mail client will
  still thread it onto the existing conversation via the
  `Re: <exact subject>` match, so the recipient experience is
  unaffected).

The pile-up case is the only situation where this trade-off applies.
For the **first** draft on a thread, `oauth_curl` remains the
default — that draft is visible in both the conversation view and
the Drafts folder.

### Concrete steps when the pile-up has already happened

1. **Delete the stale `oauth_curl` drafts** via the Gmail API
   (`DELETE https://gmail.googleapis.com/gmail/v1/users/me/drafts/<draft-id>`
   with the OAuth bearer token from the same `oauth_curl` credentials
   file). Drafts created via `oauth_curl` are deletable via that same
   OAuth client; drafts created via the claude.ai MCP can only be
   discarded from the Gmail UI (the MCP is no-update / no-delete per
   [`operations.md`](operations.md#hard-limitation--no-update-no-delete)).
2. **Recreate the consolidated message via the claude.ai MCP** —
   `mcp__claude_ai_Gmail__create_draft` with the `Re: <exact subject>`
   line so it threads on the recipient's side via subject match.
3. **Surface the path change in the tracker's status rollup**
   so the audit trail shows why the draft moved from `oauth_curl`
   to `claude_ai_mcp` — a future triager looking at the rollup
   should see *"draft re-routed to claude_ai_mcp because oauth_curl
   pile-up was hidden from the Drafts folder"* rather than wondering
   why the threading suddenly degraded.

### When this rule does not apply

- **The thread has no pending draft yet** — keep using `oauth_curl`
  (per the user's `draft_backend` config). This is the single-draft
  case and the visibility issue does not trigger.
- **The user is configured for `claude_ai_mcp` to begin with** —
  no change. Subject-matched threading is the default for that
  backend; the recommendation above is specifically for `oauth_curl`
  users who hit a pile-up.

## Migration — when the claude.ai MCP adds `threadId`

If a future version of the claude.ai Gmail MCP accepts `threadId` on
`create_draft`, this backend split can retire. The probe that checks
for this — see the scheduled routine under
[`/schedule`](../../README.md#scheduled-routines) named
`gmail-mcp-threadid-probe` — runs monthly. When it detects the new
parameter, it comments on a tracking issue so we can swap the default
back to `claude_ai_mcp` and deprecate this directory.

## Referenced by

- [`operations.md`](operations.md#drafting-backends) — per-backend call
  shape.
- [`threading.md`](threading.md) — per-backend threading guarantees.
- [`tool.md`](tool.md) — top-level Gmail tool overview.
- [`oauth-draft/README.md`](oauth-draft/README.md) — the `oauth_curl`
  setup walkthrough.
