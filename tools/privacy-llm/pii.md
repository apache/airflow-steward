<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [PII redaction contract](#pii-redaction-contract)
  - [What counts as PII](#what-counts-as-pii)
  - [The identifier format](#the-identifier-format)
  - [The mapping store](#the-mapping-store)
  - [The redact-then-reveal lifecycle](#the-redact-then-reveal-lifecycle)
  - [How skills call the redactor](#how-skills-call-the-redactor)
  - [Determinism, idempotency, collisions](#determinism-idempotency-collisions)
  - [What never reaches an LLM](#what-never-reaches-an-llm)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# PII redaction contract

This file is the source-of-truth for **what gets redacted, into
what shape, and when**. Skills implement the lifecycle defined
here; the [`redactor/`](redactor/) Python helper provides the
reference implementation.

## What counts as PII

The redactor handles these field types. Each maps to a single
identifier prefix:

| Field type | Prefix | Sources skills should redact from |
|---|---|---|
| Reporter name (or any natural-person name supplied by an external party) | `R-` | `From:` header display name on `<security-list>` mail; signature lines; "I am" / "my name is" patterns in body; CVE credit fields; HackerOne / GHSA reporter names. |
| Email address | `E-` | `From:` / `Cc:` / `To:` headers; quoted email addresses inside the body; CVE credit `email` fields. |
| Phone number | `P-` | Signature blocks; "call me at" / "reach me on" patterns. |
| IP address (v4 or v6) | `IP-` | Reproducer logs; "I tested from" lines. Self-disclosed IPs only — IPs that name a vulnerable production server are **not** PII and stay in place. |
| Personal handle | `H-` | Personal GitHub username, Twitter handle, IRC nick, Slack handle the reporter self-discloses. The reporter's *public* identity on the GitHub *issue itself* is already public and is not PII; the handle they sign their email with may be different and is. |
| Postal / employer address (free-form) | `A-` | "I work at" / "my address is" lines. Rare; redact when present. |

Things that are **not** PII and the redactor leaves alone:

- Vulnerability detail (CVEs, CWE numbers, file paths in the
  affected project, code snippets demonstrating the bug).
- Project maintainer names — the security team's own roster lives
  in `<project-config>/` and is committed; they are authors, not
  external parties whose identity needs protecting.
- Anything inside `<` … `>` that is *already* a placeholder in the
  framework's templates (`<security-list>`, `<reporter>` in canned
  responses, etc.). Redacting placeholders would be silly.
- URLs — except where the URL contains a personal handle (e.g.
  `https://github.com/janesmith/...`) the handle alone gets
  redacted; the URL stays valid.

When in doubt, redact. The reverse-on-outbound step (`pii-reveal`)
is cheap; over-redaction has no cost beyond cosmetics in the
agent's working text. Under-redaction leaks PII into LLM logs.

## The identifier format

```text
<TYPE>-<6-char-lowercase-hex>
```

- `<TYPE>` is one of the prefixes from the table above (`R`, `E`,
  `P`, `IP`, `H`, `A`).
- The 6-char hex is the first 24 bits of `sha256(<lowercased,
  trimmed value>)`, lowercased, no separator.
- On hash collision (two distinct PII values map to the same
  6-char prefix — first detected at insert time), the redactor
  extends the second value's hex to 8 chars, then 12, then 16,
  until the prefix is unique. The mapping file records the
  extension.

Examples:

| Input | Identifier |
|---|---|
| `Jane Smith` | `R-a3f9d2` *(illustrative — actual hash differs)* |
| `jane.smith@example.com` | `E-b8c247` |
| `+1-555-0100` | `P-7d4e91` |
| `192.0.2.42` | `IP-1a5cef` |
| `@janesmith-personal` | `H-9e3b04` |

The 6-char default gives ~16M slots before collision pressure
becomes meaningful — comfortably above the lifetime PII volume of
any single ASF project's security tracker.

## The mapping store

Storage path: **`~/.config/apache-steward/pii-mapping.json`** —
home-dir per the framework's tool-credentials rule (see
[`AGENTS.md` — Local setup](../../AGENTS.md#local-setup)).

Format:

```json
{
  "version": 1,
  "entries": {
    "R-a3f9d2": {"type": "reporter", "value": "Jane Smith"},
    "E-b8c247": {"type": "email",    "value": "jane.smith@example.com"},
    "P-7d4e91": {"type": "phone",    "value": "+1-555-0100"}
  }
}
```

- The file is mode `600` and lives outside the project tree —
  the same security posture as `~/.config/apache-steward/gmail-oauth.json`.
- Writes are atomic (`tempfile + os.replace`) so a crash mid-write
  cannot leave a half-baked file.
- The mapping is **per-machine, never committed**. Each
  developer's local map will diverge — that is fine, identifiers
  are stable per-value via the deterministic hash, so two
  developers redacting the same body produce the same identifier
  text without sharing the file.
- The map is append-only in normal operation. No cleanup tool
  ships with the framework; manual `rm` is supported but loses
  the reverse mapping (the agent has to re-fetch source data to
  rebuild on demand).

## The redact-then-reveal lifecycle

```text
                 ┌─────────────────────┐
fetch (Gmail / ──┤  raw body + PII     │
PonyMail)        └──────────┬──────────┘
                            │  pii-redact (TYPE inference per field)
                            ▼
                 ┌─────────────────────┐
                 │  body w/ identifiers│ ◄─── this is what
                 └──────────┬──────────┘      Claude / any
                            │                 downstream LLM sees
                            │
                  …agent processing,
                  draft composition,
                  cross-skill handoff…
                            │
                            ▼
                 ┌─────────────────────┐
                 │  draft w/ identifiers│
                 └──────────┬──────────┘
                            │  pii-reveal (only at outbound boundary)
                            ▼
                 ┌─────────────────────┐
                 │  draft w/ real names│ ──► sent to reporter
                 └─────────────────────┘
```

Three rules govern the lifecycle:

1. **Redact immediately after fetch.** Before any LLM-bound step
   touches the content — including Claude's own context — the
   skill calls `pii-redact`. The window between fetch and redact
   should be a single tool call wide.
2. **Operate on identifiers throughout.** All intermediate work
   (analysis, summarization, draft composition, prior-art lookup)
   runs against `R-a3f9d2`-style text. Skills that compose a draft
   for the reporter use the identifier in the draft body and only
   reverse it as the last step.
3. **Reveal only at the outbound boundary.** `pii-reveal` runs
   exactly once per draft, at the moment the rendered draft is
   handed to the send / draft-create tool. It does not run while
   the agent is *thinking about* the draft — only when the bytes
   are leaving the framework.

## How skills call the redactor

Two console scripts, both reading stdin and writing stdout:

```bash
# Redact: replace real PII with identifiers; map updated in place.
echo "$BODY" | uv run --project <framework>/tools/privacy-llm/redactor pii-redact \
  --field reporter:"Jane Smith" \
  --field email:"jane.smith@example.com" \
  --field phone:"+1-555-0100"

# Reveal: replace identifiers with real values from the local map.
echo "$DRAFT" | uv run --project <framework>/tools/privacy-llm/redactor pii-reveal
```

`pii-redact` takes one or more `--field <type>:<value>` arguments
declaring what to redact (the skill knows which header / signature
field carried which value). The redactor finds those exact
substrings in the input and swaps them.

`pii-reveal` reads the input, scans for `<TYPE>-<hex>` patterns
that match entries in the mapping file, and substitutes them with
the stored real values. Identifiers not in the map are left
unchanged — the skill knows it didn't redact those values, so they
must be either someone else's redaction (not reversible here) or
incidental text.

A third console script lists the current map for debugging:

```bash
uv run --project <framework>/tools/privacy-llm/redactor pii-list
# →  R-a3f9d2  reporter  Jane Smith
#    E-b8c247  email     jane.smith@example.com
#    …
```

Skill files reference the same invocation via the `<framework>`
placeholder — see
[`AGENTS.md` — placeholder convention](../../AGENTS.md#placeholder-convention-used-in-skill-files).

## Determinism, idempotency, collisions

- **Deterministic** — `pii-redact reporter:"Jane Smith"` produces
  the same `R-a3f9d2` on every machine, every run, because the
  identifier is `R-` + first-24-bits of `sha256("jane smith")`.
  The mapping file is convenience storage for `pii-reveal`; the
  identifier itself is reproducible without it.
- **Idempotent** — running `pii-redact` twice on the same input
  with the same `--field` values writes the mapping file once
  and produces identical output the second time.
- **Collision-resistant** — at the 6-char default, two distinct
  inputs mapping to the same prefix is a one-in-16-million event
  per (type, prefix) pair. When it happens, the redactor extends
  the second-detected value's hash by 2 hex chars at a time
  (`R-a3f9d2ab`, then `R-a3f9d2abcd`, …) until the new identifier
  is unique against the current map. Extension is permanent for
  that mapping entry — once `R-a3f9d2ab` is in the file, that
  value keeps the longer form forever.

## What never reaches an LLM

- The contents of `~/.config/apache-steward/pii-mapping.json`. The
  file is read by `pii-redact` / `pii-reveal` only. Skills MUST
  NOT include the mapping in any LLM-bound prompt, summary, or
  status comment. If you need to debug what mapped to what, run
  `pii-list` in the user's terminal — that output goes to the
  user's screen, not to Claude's context.
- The `--field <type>:<value>` arguments themselves, if a skill
  ever emits its tool-call arguments into a status comment. The
  arguments are PII by construction — every value passed there is
  exactly what the redactor is replacing.
- Any draft text *before* `pii-reveal` runs, if the test path
  short-circuits and skips reveal — the draft body would still
  carry identifiers, which leak no PII, but skills should not
  emit identifier-laden drafts to non-internal destinations
  (e.g. a public PR comment) by accident. The
  [`models.md`](models.md) gate is a separate safety net for
  this — its destination check ensures non-approved destinations
  see neither raw PII nor stale identifiers.
