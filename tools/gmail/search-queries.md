<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Gmail — search query templates](#gmail--search-query-templates)
  - [Gmail operator cheat-sheet](#gmail-operator-cheat-sheet)
  - [GitHub-notification exclusions](#github-notification-exclusions)
  - [Query templates by skill](#query-templates-by-skill)
    - [`security-import-issues` — candidate-listing query](#security-import-issues--candidate-listing-query)
    - [`security-import-issues` — prior-rejection search](#security-import-issues--prior-rejection-search)
    - [`security-sync-issues` — reporter-thread lookup by distinctive phrase](#security-sync-issues--reporter-thread-lookup-by-distinctive-phrase)
    - [`security-sync-issues` — CVE-review-comment search](#security-sync-issues--cve-review-comment-search)
    - [Release `[RESULT][VOTE]` attribution](#release-resultvote-attribution)
  - [Budget discipline](#budget-discipline)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Gmail — search query templates

The Gmail search-expression language the `mcp__claude_ai_Gmail__search_threads`
call accepts (see [`operations.md`](operations.md#search-threads) for the
call shape). This file catalogues the **generic** operator patterns the
skills use plus the **skill-specific** query templates.

Placeholder convention:

- `<security-list>` — the project's security mailing list (for Airflow,
  `<security-list>`; see
  [`../../<project-config>/project.md`](../../<project-config>/project.md#mailing-lists)).
- `<security-list-domain>` — the domain suffix of that list (for
  `<security-list>`, the value is
  `<security-list-domain>`). Gmail's `list:` operator uses the
  domain form, not the plain address.
- `<dev-list>` — the project's public release-vote list (for Airflow,
  `<dev-list>`).

## Gmail operator cheat-sheet

| Operator | Purpose |
|---|---|
| `list:<domain>` | Match messages sent to a mailing list. Domain form — `list:<security-list-domain>`, not `list:<security-list>`. |
| `from:<addr>` / `-from:<addr>` | Match (or exclude) a sender. |
| `to:<addr>` / `cc:<addr>` | Match a recipient / copy-recipient. |
| `subject:"<substring>"` | Match a substring in the subject line (quoted for multi-word). |
| `"<quoted phrase>"` | Match a phrase anywhere in the message (body + headers). |
| `newer_than:<Nd>` | Time window — e.g. `newer_than:30d`. Preferred over `since:` / `after:` for relative windows. |
| `after:YYYY/MM/DD` / `before:YYYY/MM/DD` | Absolute date bounds. |
| `-<operator>:<value>` | Negation — applies to any operator. |

## GitHub-notification exclusions

The project's tracker repo mirrors GitHub issue activity onto its
security list, producing a large volume of bot messages that match
most content searches. Every skill that searches beyond a pure list
scan excludes the mirror senders up front:

```text
-from:notifications@github.com
-from:noreply@github.com
-from:<tracker-noreply>
-from:security-noreply@github.com
```

For projects that host their tracker elsewhere (or do not mirror to
the list), trim or replace these as needed.

## Query templates by skill

### `security-import-issues` — candidate-listing query

Inbound threads that might be new reports, minus GitHub-notification
bots, within a time window:

```text
list:<security-list-domain>
  -from:notifications@github.com
  -from:noreply@github.com
  -from:<tracker-noreply>
  -from:security-noreply@github.com
  newer_than:30d
```

**Do not exclude `-from:security@apache.org`.** That address is used
for CVE-tool bookkeeping *and* for ASF-security-team forwarding of
inbound reports *and* for ad-hoc ASF Security discussion.
Blanket-excluding the sender would drop forwarded reports along with
the bookkeeping noise, so the bookkeeping emails are filtered out in
the import skill's Step 3 classification table by subject pattern
instead.

Adjust the time window per the user's selector (`since:` →
`newer_than:` or `after:`; `import all` → `newer_than:90d`).

### `security-import-issues` — prior-rejection search

Run in Step 2b of the import skill on candidates heading for a
negative-response disposition. The goal is to find **prior similar
reports the security team rejected without creating a tracker** so
the same canned response can be reused and any past reporter
pushback can be pre-empted.

Two templates, one search each — stay within the skill's ≤ 2 calls
per candidate budget.

**1. Prior rejections by the security team** (outbound replies from
a team member that open with a canned-response cue):

```text
list:<security-list-domain>
  "<keyword-1>" "<keyword-2>"
  newer_than:180d
  -from:notifications@github.com
  -from:noreply@github.com
```

Pick `<keyword-1>` / `<keyword-2>` from the current report's
distinctive noun-phrase set — the same 3–5 tokens the skill's Step
2a uses for the subject-keyword GitHub search. Filter the results
down to messages whose sender is on the security-team roster AND
whose body opens with a canned-response preamble
(*"Thank you for reporting … this isn't a security issue"*,
*"Per the project's security model"*, *"This is expected behaviour
for a Dag author"*, *"We treat this as out of scope of the Security
Model"*). Those are the prior-rejection precedents.

**2. Inbound reports that never became a tracker** (same keywords,
same window, filtered to inbound-only):

```text
list:<security-list-domain>
  "<keyword-1>" "<keyword-2>"
  newer_than:180d
  -from:me
  -from:<security-team-member>
  -from:notifications@github.com
  -from:noreply@github.com
```

For each returned `threadId`, cross-reference against existing
trackers (`gh search issues "<threadId>" --repo <tracker>`). Hits
with **no** matching tracker are the inbound side of prior
rejections.

Substitute `<security-list-domain>` from
[`<project-config>/project.md`](../../<project-config>/project.md#gmail-and-ponymail).
Substitute `<security-team-member>` with the handles / emails
listed in the roster subsection of
[`<project-config>/release-trains.md`](../../<project-config>/release-trains.md)
when you need to exclude a specific sender; for a blanket
outbound-team exclusion, repeat the `-from:` clause once per
roster member, or rely on `list:` + the no-`from:notifications@github.com`
filter as in template 1 and classify the result set by sender
after the fact.

### `security-sync-issues` — reporter-thread lookup by distinctive phrase

When a tracking issue's GitHub title does not match the original
email subject (common — the triager paraphrases the subject when
copying into GitHub), search Gmail with a distinctive phrase from
the issue body, excluding the GitHub-notification mirror:

```text
"<distinctive phrase>" -from:notifications@github.com -from:noreply@github.com
```

Example: `"HITL" "ui/dags" -from:notifications@github.com -from:noreply@github.com`.

Pick a phrase that is rare in the security list's volume — a
function name, an endpoint path, an error string — rather than a
common word.

### `security-sync-issues` — CVE-review-comment search

The project's CVE tool (Vulnogram for ASF) notifies the security
list by email when a reviewer leaves a comment on the CVE record.
The tool's JSON API is OAuth-gated and not readable from skill
context, so Gmail is the load-bearing signal path.

```text
<CVE-ID> -from:notifications@github.com -from:noreply@github.com -from:<tracker-noreply> list:<security-list-domain>
```

A second search without the `list:` filter catches CNA-tooling
emails that went to individual security-team members first:

```text
<CVE-ID> -from:notifications@github.com -from:noreply@github.com -from:<tracker-noreply>
```

Sync-style skills impose a hard per-issue Gmail-call budget. Keep
this path to **≤ 2 extra searches per issue** on top of the
reporter-thread search.

### Release `[RESULT][VOTE]` attribution

When resolving *"who was the release manager of X.Y.Z"*, the
authoritative source is the `[RESULT][VOTE]` thread on the project's
public dev list (the sender of the `[RESULT][VOTE]` message **is**
the release manager). For Airflow:

```text
"[RESULT][VOTE]" "Airflow Providers" from:<dev-list>
```

Narrow with a date range if needed. Per-project lookup rules live in
the project's release-trains file (for Airflow,
[`../../<project-config>/release-trains.md`](../../<project-config>/release-trains.md#current-release-managers)).

## Budget discipline

Gmail MCP calls are metered. Skill-level rules:

- `security-import-issues` runs exactly one list scan per invocation.
- `security-sync-issues` runs at most one reporter-thread search +
  two CVE-review searches per tracking issue (i.e. ≤ 3 per tracker;
  ≤ ~60 on a 20-tracker sweep).
- No skill retries on its own. If a search fails, surface the
  failure and ask the user before retrying.
