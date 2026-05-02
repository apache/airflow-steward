<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Gmail — MCP operation catalogue](#gmail--mcp-operation-catalogue)
  - [Pre-flight](#pre-flight)
  - [Read](#read)
    - [Search threads](#search-threads)
    - [Get thread](#get-thread)
  - [Write — drafts only, never send](#write--drafts-only-never-send)
    - [Drafting backends](#drafting-backends)
    - [Create draft — `claude_ai_mcp` backend](#create-draft--claude_ai_mcp-backend)
    - [Create draft — `oauth_curl` backend](#create-draft--oauth_curl-backend)
    - [Hard rules that apply to both backends](#hard-rules-that-apply-to-both-backends)
    - [List drafts](#list-drafts)
  - [Hard limitation — no update, no delete](#hard-limitation--no-update-no-delete)
  - [Confidentiality of drafts](#confidentiality-of-drafts)
  - [Error handling](#error-handling)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Gmail — MCP operation catalogue

Shared reference for the `mcp__claude_ai_Gmail__*` tool calls the
skills make against the active user's Gmail account. The skills
reference this file for the call shape and for the limitations that
constrain their flow.

Placeholder convention used below:

- `<security-list>` — the project's private security mailing list (the
  list the user's Gmail account subscribes to). For Airflow, the value
  is `<project manifest>.security_list` =
  `<security-list>`; see
  [`../../<project-config>/project.md`](../../<project-config>/project.md#mailing-lists).
- `<threadId>` — an opaque Gmail thread identifier.

## Pre-flight

Every skill that talks to Gmail does a one-call pre-flight in Step 0
to confirm the MCP is reachable and the user's account subscribes to
the project's security list:

```text
mcp__claude_ai_Gmail__search_threads(
  query='list:<security-list-domain>',
  pageSize=1,
)
```

Substitute the `<security-list-domain>` with the domain suffix of the
project manifest's `security_list` (for
`<security-list>`, the value is
`<security-list-domain>`).

A non-empty result means Gmail is connected and indexed; an empty
result means either the account does not subscribe, or the MCP is
misconfigured. In either case the skill stops and asks the user to
fix the setup rather than guessing.

## Read

### Search threads

```text
mcp__claude_ai_Gmail__search_threads(
  query='<gmail search expression>',
  pageSize=<N>,
)
```

Returns an array of `{threadId, snippet, …}` objects. Use `pageSize`
deliberately — some skills (e.g. `sync-security-issue`) impose a
hard Gmail-call budget per issue to avoid running up the MCP quota
on many-tracker sweeps.

For the search expression syntax and the canonical query templates
the skills use, see [`search-queries.md`](search-queries.md).

### Get thread

```text
mcp__claude_ai_Gmail__get_thread(
  threadId='<threadId>',
  messageFormat='FULL_CONTENT',   # or 'METADATA' when bodies are not needed
)
```

Returns the full message history of a thread. Body reads are
expensive — most skills filter candidates down on metadata first and
only fetch bodies for the narrow set that actually warrants it
(`import-security-issue` does this explicitly at Step 3).

## Write — drafts only, never send

### Drafting backends

Draft creation runs through one of two backends, selected by the user
in [`config/user.md`](../../config/user.md) under
`tools.gmail.draft_backend`. The full comparison and rationale live
in [`draft-backends.md`](draft-backends.md); the call shape per
backend is here.

| Backend | Value | `threadId` attach? |
|---|---|---|
| claude.ai Gmail MCP | `claude_ai_mcp` (default) | **no** (see below) |
| OAuth + `curl` | `oauth_curl` | **yes** |

### Create draft — `claude_ai_mcp` backend

The claude.ai Gmail MCP's `create_draft` tool does **not** accept a
`threadId` parameter. The Gmail REST API supports it on
`drafts.create`, but the MCP does not plumb it through. Drafts
created via this backend always start a new conversation on the
**sender's** Gmail side; recipients' mail clients thread-attach via
subject + `In-Reply-To` / `References` matching, which usually works
but is not guaranteed.

```text
mcp__claude_ai_Gmail__create_draft(
  subject='Re: <root subject of the inbound message>',
  to=['<primary>'],
  cc=['<security-list>', ...],
  body='<body>',
)
```

- **Subject is always `Re: <root subject>`**, never fabricated. A
  drifted subject defeats subject-based threading on every client.
- **Never send.** The skills only *create* drafts; a human
  review-and-send step is required before every outbound message.
- **Subject-fallback threading is the only path.** See the
  [fallback rule](threading.md#fallback--subject-matched-draft-when-threadid-is-unavailable)
  in `threading.md` for when this applies and when it does not.

When the user needs `threadId`-attached drafts (so the draft threads
on their own Gmail view and the drafts queue stays in lock-step with
the inbound thread), switch the backend to `oauth_curl` — see below.

### Create draft — `oauth_curl` backend

The `oauth-draft-create` console script (in
[`oauth-draft/`](oauth-draft/README.md)) creates drafts by talking
directly to the Gmail REST API with a user-provided OAuth refresh
token. It sets `threadId` on the Gmail API call **and** populates
`In-Reply-To` / `References` from the thread's last message, so every
client threads consistently.

```bash
uv run --project <framework>/tools/gmail/oauth-draft oauth-draft-create \
  --thread-id <gmail-threadId> \
  --to reporter@example.com \
  --cc <security-list> \
  --subject "Re: <root subject>" \
  --body-file /tmp/body.txt
```

See [`oauth-draft/README.md`](oauth-draft/README.md) for one-time
setup (creating the Google Cloud OAuth client, obtaining a refresh
token, and populating the credentials file) and for the full flag
list.

Every bullet from the `claude_ai_mcp` section above applies to this
backend too — drafts only, never send; subject is always
`Re: <root subject>`; composition happens under user review.

### Hard rules that apply to both backends

- **Never send.**
- **Subject is always `Re: <root subject>`**, never fabricated.
- **Surface which backend was used** in the proposal / recap so the
  user can tell at a glance whether the draft threads on their own
  Gmail view (`oauth_curl`) or only on the recipient's
  (`claude_ai_mcp` subject fallback).
- **Record the backend + draft ID on the tracker's status rollup**
  so subsequent sync passes can find and (optionally) re-verify the
  draft.

For the ASF-security-relay special case (different `to` /
`cc` shape), see [`asf-relay.md`](asf-relay.md).

### List drafts

```text
mcp__claude_ai_Gmail__list_drafts(
  query='<optional filter>',    # e.g. 'list:<security-list-domain>'
)
```

Used by `sync-security-issue` to verify that a draft flagged as stale
in a previous status comment still exists before carrying the flag
forward. See the *"self-replicating stale-draft flag"* paragraph in
that skill.

## Hard limitation — no update, no delete

The Gmail MCP exposes **`create`, `list`, and `read` only** for
drafts. There is no `update_draft` and no `delete_draft` tool. The
skills must treat every existing draft as immutable:

- If a correction is needed, surface the existing draft's `draftId`
  to the user with an explicit *"discard this one manually in Gmail"*
  note, then create a fresh draft with the corrected content.
- Do **not** silently create a second draft that shadows the first —
  that leaves two near-identical drafts in the user's Gmail and
  invariably one of them gets sent by accident.
- On the sync skill's stale-draft-forward-flagging path: verify the
  `draftId` still exists via `list_drafts` before copying the flag
  into a new sync status comment. Without verification, a one-time
  flag self-replicates forever.

## Confidentiality of drafts

Drafts land in the user's personal Gmail account and are visible only
to that user until sent. Draft content may reference the private
tracker's URL (reporter is on the private thread and is expected to
keep it confidential), but anything destined for a public list must
obey the confidentiality rules in
[`../../AGENTS.md`](../../AGENTS.md) — no `<tracker>` URLs, no CVE
IDs before publication, no *"security fix"* leakage.

## Error handling

If any Gmail call fails (MCP unreachable, 429, transient 5xx),
**stop** and report the failure. The skills explicitly budget Gmail
calls; silently retrying turns one flaky call into a quota-exhaustion
storm.
