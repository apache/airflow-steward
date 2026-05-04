<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Tool: privacy-llm](#tool-privacy-llm)
  - [What this tool provides](#what-this-tool-provides)
  - [Why this is its own tool](#why-this-is-its-own-tool)
  - [The two mechanisms — what is gated, and what is redacted](#the-two-mechanisms--what-is-gated-and-what-is-redacted)
  - [How skills consume this tool](#how-skills-consume-this-tool)
  - [What this tool is NOT for](#what-this-tool-is-not-for)
  - [Failure modes](#failure-modes)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# Tool: privacy-llm

This directory documents the **privacy-llm** tool adapter — the
contract every framework skill follows when it touches private mail
content (`<security-list>` reporter mail, `<private-list>` PMC
escalation mail) or routes that content through any LLM step.

The tool exists because two distinct, easily-confused privacy
concerns share a single workflow:

1. **Reporter PII** in `<security-list>` content — the body is OK to
   process, but the reporter's *identity* (name, email, phone, IP,
   personal handles) must never enter any LLM in the clear.
2. **Wholly private list content** on `<private-list>` and other
   PMC-private foundation lists — the body itself must never reach
   a non-approved LLM.

These two concerns produce different remediations. Mixing them up
(e.g. assuming PII redaction is enough for `<private-list>` content)
is a real foot-gun the framework guards against.

A project opts into this tool by naming it in its manifest under
*Tools enabled*. For the adopting project see
[`../../<project-config>/project.md`](../../<project-config>/project.md#tools-enabled).
The tool is **mandatory** for any project that uses `tools/gmail/`
or `tools/ponymail/` — those tools surface private content into the
agent's context, and `privacy-llm` is what stops it from leaking.

## What this tool provides

| Capability | File | What it covers |
|---|---|---|
| PII redaction contract | [`pii.md`](pii.md) | Which fields are PII, the hash-prefixed identifier format (`R-a3f9d2`, `E-b8c247`, …), the local mapping store at `~/.config/apache-steward/pii-mapping.json`, the redact-then-reveal lifecycle. |
| Approved-LLM registry | [`models.md`](models.md) | Which LLMs the framework treats as privacy-approved (Claude Code by default; anything at `*.apache.org`; local Ollama / vLLM; everything else opt-in), how to declare additions in `<project-config>/privacy-llm.md`, and what the pre-flight gate checks. |
| Setup recipes | [`../../docs/setup/privacy-llm.md`](../../docs/setup/privacy-llm.md) | Copy-pasteable configurations for the supported variants — local inference, Apache-hosted endpoint, AWS Bedrock, opt-in third-party. Marked **provisional pending ASF Legal Affairs ratification** of an authoritative approved-model list. |
| Reference Python helper | [`redactor/`](redactor/) | A small `uv` project exposing three console scripts — `pii-redact`, `pii-reveal`, `pii-list` — that skills shell out to so the redaction lifecycle is consistent across every consumer. |

## Why this is its own tool

The redaction lifecycle is **cross-cutting**: it sits between every
private-data fetch tool (Gmail, PonyMail, future mail backends) and
every LLM consumer of that data (Claude itself, any future
delegated-summarization step, any non-Claude analysis hop). Hosting
it under `tools/gmail/` or `tools/ponymail/` would couple it to one
backend; hosting it under any single skill would create N copies
that drift. A dedicated `tools/privacy-llm/` directory keeps the
contract in one place and the helper code in one project.

The same argument applies to the approved-model registry — it gates
*outbound* LLM calls regardless of which skill is making the call,
so it must live above the per-skill / per-tool layer.

## The two mechanisms — what is gated, and what is redacted

The framework's two privacy mechanisms apply to different data
classes and run at different points in the pipeline:

| Data class | Source | What `privacy-llm` does | Gate runs at |
|---|---|---|---|
| `<security-list>` body without PII | Gmail / PonyMail public archive | Body flows to any LLM (including Claude). No gate. | n/a |
| `<security-list>` reporter PII | Gmail / PonyMail | **Always redacted** — name, email, phone, IP, personal handle replaced with hash-prefixed identifiers. Mapping kept local; never sent to any LLM. | Immediately after fetch, before any further processing. |
| `<private-list>` content | Gmail / PonyMail (PMC-private archive) | **Pre-flight gate** — refuse to fetch unless the active LLM stack is in the approved-model registry. No redaction (the body is private as a whole). | Step 0 pre-flight on every skill that may read a `<private-list>` thread. |
| Outbound drafts to the reporter | Skill draft assembly | Reverse identifiers → real names just before the draft is written. | Final assembly, after the LLM step that composed the draft body. |

The decision tree the skill follows on every fetch is captured in
[`pii.md`](pii.md) (redaction lifecycle) and [`models.md`](models.md)
(gate semantics).

## How skills consume this tool

Three integration points:

1. **Step 0 — pre-flight gate.** Skills that may read
   `<private-list>` content (`security-issue-import`,
   `security-issue-sync`, `security-issue-fix`,
   `security-issue-deduplicate` when escalating to PMC) read the
   adopter's `<project-config>/privacy-llm.md` and refuse to run if
   no approved model is wired. The check is implemented per
   [`models.md`](models.md#the-pre-flight-check).
2. **After fetch — redact PII.** Any skill that fetches Gmail or
   PonyMail content shells out to `pii-redact` on the body before
   doing further processing. The redactor is idempotent — running
   twice on already-redacted text produces the same identifiers and
   does not double-encode.
3. **Before send — reveal identifiers.** When assembling a draft
   that needs real names (the reporter reply, a CVE credit line),
   shell out to `pii-reveal` on the rendered draft text. Reveal
   only happens at the *outbound boundary* — the LLM step that
   composes the draft operates on identifiers throughout.

Concrete invocation patterns are in
[`pii.md`](pii.md#how-skills-call-the-redactor) and
[`models.md`](models.md#how-skills-call-the-gate).

## What this tool is NOT for

- **Not a substitute for the existing confidentiality rules in
  [`AGENTS.md`](../../AGENTS.md#confidentiality-of-the-tracker-repository).**
  Those rules govern *human-visible* surfaces (public PRs, public
  issue comments, public mailing-list replies). `privacy-llm`
  governs *machine-routed* surfaces (LLM context, LLM API calls,
  delegated-summarization hops). Both apply; they are layered.
- **Not a content classifier.** The redactor doesn't try to *guess*
  which strings are PII — skills hand it the field values
  explicitly (reporter name from the parsed `From:` header, email
  from the same, etc.). PII discovery is the skill's job; redaction
  is the redactor's job.
- **Not an MCP-layer interception.** Claude Code's MCP runtime does
  not (yet) support per-tool transformation hooks. The redactor
  runs as an explicit step *inside the skill*, not as a transparent
  MCP middleware. If a future MCP gains hook support, the skill
  layer can move the redactor call into the hook without changing
  the contract.

## Failure modes

| Symptom | Likely cause | Remediation |
|---|---|---|
| Skill refuses to run with "no approved privacy LLM configured" | Adopter has not yet written `<project-config>/privacy-llm.md`, or it lists no approved entries | Follow [`docs/setup/privacy-llm.md`](../../docs/setup/privacy-llm.md) — the default `Claude Code` entry is enough for the local-only case |
| `pii-reveal` returns text with `R-a3f9d2`-style identifiers still in place | The mapping file at `~/.config/apache-steward/pii-mapping.json` was deleted, truncated, or moved | Re-fetch the source; the redactor regenerates identifiers deterministically from the raw values, but it cannot reverse identifiers it has no mapping for |
| `pii-redact` produces different identifiers across runs | Identifier format was changed (the framework bumped the hash length, or the prefix scheme) — see the version field in `pii-mapping.json` | Migration logic lives in the next framework version's release notes; until then keep the mapping file pinned |
| Skill is meant to read `<security-list>` but is being gated by the approved-model pre-flight | Adopter has incorrectly classified `<security-list>` as private in `<project-config>/privacy-llm.md` | Remove `<security-list>` from the private-list set; PII redaction (which IS required for `<security-list>`) is independent of the gate |
