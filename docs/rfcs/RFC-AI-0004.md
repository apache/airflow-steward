<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [RFC-AI-0004: Principles of agentic interaction for open-source maintainers](#rfc-ai-0004-principles-of-agentic-interaction-for-open-source-maintainers)
  - [Abstract](#abstract)
  - [Status of this document](#status-of-this-document)
  - [Motivation](#motivation)
  - [Definitions](#definitions)
  - [Principle 1 — Human-in-the-Loop on every state change](#principle-1--human-in-the-loop-on-every-state-change)
    - [Normative statement](#normative-statement)
    - [Why this is the load-bearing principle](#why-this-is-the-load-bearing-principle)
    - [Five concrete consequences](#five-concrete-consequences)
    - [Narrow auto-merge carve-out](#narrow-auto-merge-carve-out)
    - [Anti-patterns to avoid](#anti-patterns-to-avoid)
  - [Principle 2 — Secure sandbox by default](#principle-2--secure-sandbox-by-default)
    - [Normative statement](#normative-statement-1)
    - [Why this is necessary](#why-this-is-necessary)
    - [Architecture: three layers, layered](#architecture-three-layers-layered)
    - [Five concrete consequences](#five-concrete-consequences-1)
    - [Anti-patterns to avoid](#anti-patterns-to-avoid-1)
  - [Principle 3 — Vendor neutrality](#principle-3--vendor-neutrality)
    - [Normative statement](#normative-statement-2)
    - [Two axes of neutrality](#two-axes-of-neutrality)
    - [Five concrete consequences](#five-concrete-consequences-2)
    - [Anti-patterns to avoid](#anti-patterns-to-avoid-2)
  - [Principle 4 — Conversational, correctable agentic skills](#principle-4--conversational-correctable-agentic-skills)
    - [Normative statement](#normative-statement-3)
    - [Why this is structurally different](#why-this-is-structurally-different)
    - [Five concrete consequences](#five-concrete-consequences-3)
    - [Anti-patterns to avoid](#anti-patterns-to-avoid-3)
  - [How the four principles compose](#how-the-four-principles-compose)
  - [Adoption guidance for non-Steward projects](#adoption-guidance-for-non-steward-projects)
  - [What this RFC does NOT specify](#what-this-rfc-does-not-specify)
  - [References](#references)
    - [Internal (this repository)](#internal-this-repository)
    - [External](#external)
  - [Acknowledgements](#acknowledgements)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# RFC-AI-0004: Principles of agentic interaction for open-source maintainers

| Field | Value |
|---|---|
| **RFC** | AI-0004 |
| **Title** | Principles of agentic interaction for open-source maintainers |
| **Status** | Draft |
| **Authors** | The Apache Steward project (see [`MISSION.md`](../../MISSION.md) for roster) |
| **Initial draft** | 2026-05-07 |
| **Supersedes** | None |
| **Superseded by** | None |
| **Reference implementation** | [`apache/airflow-steward`](https://github.com/apache/airflow-steward) |
| **License** | Apache License 2.0 |

---

## Abstract

This RFC describes four principles that govern how AI agents should
interact with open-source projects when **the human in the
interaction is a project maintainer** — committer, PMC member,
release manager, security-team member, triager. The four
principles —
**(1) human-in-the-loop on every state change**,
**(2) secure sandbox by default**,
**(3) vendor neutrality across LLM backends and project
governance**, and
**(4) conversational, correctable agentic skills** —
are framed as *a baseline*. They define the minimum trust posture
under which agentic tooling can be ethically deployed against the
public artefacts of a community-governed project (issues, PRs,
mailing lists, releases, security reports, contributor data).

The RFC is normative for the Apache Steward framework
([`apache/airflow-steward`](https://github.com/apache/airflow-steward),
the working draft of which is summarised in
[`MISSION.md`](../../MISSION.md)) and is offered as a
**pattern other projects can adopt or adapt** when integrating
agentic tooling into their own maintainership workflow.

It is **not** a specification of any particular implementation
detail (LLM choice, prompt format, model size, scaffolding
library). The principles are independent of those choices.

---

## Status of this document

This is a **Draft**. The Apache Steward project's reference
implementation operationalises every principle in this RFC, but
the RFC itself is the project's first attempt to extract the
principles from the implementation and frame them as a portable
contract. The next two milestones are:

1. **Public review** — comments solicited from ASF Members,
   non-ASF maintainers running similar agentic frameworks, and
   the [ASF Responsible AI Initiative](https://incubator.apache.org/projects/responsible-ai.html)
   working group.
2. **Pilot validation** — the four principles tested against the
   Apache Steward pilot cohort (one ASF PMC running the full
   security-issue flow, one ASF PMC running just triage +
   mentoring, at least one non-ASF project) before promotion
   from `Draft` to `Stable`.

Substantive comments → open an issue in
[`apache/airflow-steward`](https://github.com/apache/airflow-steward/issues)
with the label `area:docs`; the project's discussion thread
will be linked here in the next revision.

---

## Motivation

Maintainers of open-source projects increasingly find themselves
at the receiving end of agent-shaped tooling — bots that triage,
auto-mergers that touch their default branch, scanners that file
issues, AI-suggested PRs that propose code. The volume of such
tooling is growing faster than the conventions for **how that
tooling should behave**. The result, today, is a stack of
implicit choices made by individual tool authors that vary
across projects in ways that erode trust:

- A maintainer cannot tell, from a tool's surface alone, whether
  it operates **autonomously** or **with confirmation**, where
  the boundary lies, and what the rollback story is.
- Sandbox posture varies wildly. Some agents read everything in
  `~`; some read nothing. Some can `gh pr create`; some can
  silently push to the default branch. The maintainer is on the
  hook for figuring this out.
- Vendor lock-in is largely silent. A skill that "uses Claude"
  is a skill that *requires* Claude — not a skill that happens
  to use Claude today and would work on a local model
  tomorrow. The lock-in is rarely surfaced as a choice.
- "How do I correct this?" has become an afterthought. The
  maintainer who notices the agent is doing the wrong thing
  often has no path to fix it short of opening an upstream PR
  to the tool author.

This RFC names the four shifts that, taken together, make
agentic tooling acceptable on a maintainer-governed project.
Each shift is independently necessary; the combination is
sufficient.

---

## Definitions

| Term | Definition |
|---|---|
| **Agent** | A program that selects and executes actions to advance a maintainer-stated goal, where at least one of those actions is mediated by an LLM and where action selection is conditioned on natural-language conversation rather than a pre-coded flow chart. |
| **Skill** | A package of agent-readable text (typically a markdown file with YAML frontmatter and bundled scripts/references) that scopes the agent to a single workflow. The Apache Steward framework's skills (`security-issue-import`, `pr-management-triage`, etc.) are reference instances. |
| **Maintainer** | A human with write access (or comparable governance authority) on the target project. PMC members, committers, triagers, release managers all qualify; bots and agents do not. |
| **State change** | Any operation observable by parties outside the maintainer's local machine: posted comment, edited issue body, applied label, merged PR, sent email, written file under the repo's tracked path, etc. Operations that touch only the maintainer's `/tmp` or `~/.config/<framework>/` cache are **not** state changes. |
| **Confirmation** | An explicit, in-session, reversible-only-by-history act by the maintainer that authorises one specific state change. Standing approvals, "yes to all", and pre-approved-via-config are explicitly **not** confirmations. |
| **Sandbox** | An OS-level isolation boundary (filesystem namespacing, network filtering, syscall mediation) plus a tool-permissions layer plus a clean-environment wrapper, applied to every agent-launched subprocess. |

---

## Principle 1 — Human-in-the-Loop on every state change

### Normative statement

> Every state change an agent proposes against project artefacts
> MUST be presented to a maintainer as a *proposal*, and MUST NOT
> be applied until the maintainer issues an explicit per-proposal
> confirmation. The agent never confirms on the maintainer's
> behalf, never persists "always yes" approvals across sessions,
> and never bundles multiple state changes under one
> confirmation in a way that hides any single one from review.

### Why this is the load-bearing principle

A skill that triages 200 PRs in 10 minutes is doing 200 state
changes. If the maintainer is not in the loop on each one, what
they are doing is **delegating their committer authority to a
program**. That is not what "AI-assisted maintainership" should
mean. The committer's signature on every artefact is the entire
basis of the project's trust model; the agent does not own that
signature.

### Five concrete consequences

1. **Propose-then-apply, always.** The agent's natural unit of
   work is "here is the proposal, will you confirm?". The
   "apply" pass that follows confirmation is mechanical — no
   reasoning, no surprises, no second proposal hidden inside.

2. **Per-proposal confirmation, no batch yes.** Multiple
   state changes in the same response require a confirmation
   surface that lets the maintainer say "1, 3, 4 yes; 2 no".
   `all` as a one-keystroke shortcut is acceptable; the agent
   must still surface every item before honouring it.

3. **No standing pre-approvals.** A skill MUST NOT support a
   config switch that says "auto-approve every X-class
   proposal". The boundary between Mode C (agent-authored fix
   with human review) and Mode D (narrowly-scoped auto-merge)
   is exactly this; Mode D is governed by a separate, much
   stricter contract (see Principle 1, *narrow auto-merge
   carve-out* below).

4. **Drafts, never sends.** Outbound communication (email,
   chat) is **drafted** by the agent and stored in the
   communication system's drafts folder. The maintainer
   reviews and presses Send. The framework MUST NOT have a
   "yes, send the draft" path that bypasses the human read.

5. **Audit log of every confirmation.** Every applied state
   change writes a structured audit-log entry: timestamp,
   maintainer identity, proposal text, applied diff,
   triggering skill. Open-source maintenance is a
   public-trust activity; the trail makes future review
   possible.

### Narrow auto-merge carve-out

Mode D ("narrowly-scoped fix-and-merge", in Apache Steward's
terminology) is the explicit exception. It permits auto-merge,
but only after **all** of the following gate conditions hold:

- The change class is on a per-project, per-class allow-list
  (lint fixes, dependency bumps within an allow-list, license
  headers, formatting, broken-link repair). Security-class
  changes are explicitly out.
- The project has been running Modes A/B/C with HITL
  confirmation for at least two release cycles, and a
  contributor-sentiment evaluation says the project is
  healthier, not just faster.
- Every auto-merged change is reversibly logged; reverts are
  one keystroke away.

The carve-out exists because lint-rebase-format has marginal
human value and should not require a human in the loop forever.
It is **off by default** in the reference implementation. A
project that turns it on without first running the manual loop
has skipped the proof.

### Anti-patterns to avoid

- **Standing "always-yes" tokens.** "Auto-approve all my agent's
  proposals for the next week" is a delegation, not a
  confirmation.
- **Implicit confirmation via inactivity.** "Will apply in
  10 seconds unless cancelled" is not a confirmation; it is a
  default-yes that survives interruption.
- **Bundling.** "I'll apply changes A, B, C, D, E now" with one
  confirmation hides four of those changes from per-item review.
- **Server-side approval.** A web endpoint that accepts a
  pre-signed approval token bypasses the in-session boundary.
  The approval lives in the maintainer's terminal, not in the
  framework.

---

## Principle 2 — Secure sandbox by default

### Normative statement

> The agent's executing process MUST run inside an OS-level
> sandbox at all times. The sandbox MUST default-deny filesystem
> reads outside the project working tree and a small set of
> explicitly-permitted user-config paths, default-deny network
> egress to all hosts not on a project-declared allow-list, and
> default-deny invocation of binaries that the project's
> permission policy has not explicitly allowed. The sandbox is
> in addition to — not in replacement of — Principle 1's
> human-in-the-loop confirmation gate.

### Why this is necessary

LLM-driven agents read attacker-controlled text every time they
run. Email subjects, PR titles, scanner findings, public commit
messages, mailing-list archives, third-party PR comments — all
of these are content the agent treats as input and that an
attacker can shape. **No prompt-engineering technique
neutralises this surface.** The fallback when prompt
engineering fails has to be the operating system telling the
agent's subprocess "no, you cannot read `~/.aws/credentials`"
or "no, you cannot connect to `attacker.example.com`".

### Architecture: three layers, layered

The reference implementation
(see [`docs/setup/secure-agent-internals.md`](../setup/secure-agent-internals.md))
uses a three-layer model. Other implementations MAY choose
different mechanisms; the layering MUST be preserved:

| Layer | What it stops | Mechanism (reference) |
|---|---|---|
| **0. Clean environment** | Inherited credential-shaped env vars (`$AWS_*`, `$GH_TOKEN`, `$ANTHROPIC_API_KEY`, …). | A shell wrapper (`claude-iso`) that strips the agent's process env to a project-declared whitelist before exec. |
| **1. Filesystem + network sandbox** | Bash subprocess reads outside the project tree; outbound HTTPS to non-allowed hosts. | Linux: `bubblewrap` user-namespace + `socat` SNI proxy. macOS: `sandbox-exec`. |
| **2. Tool permissions** | The agent's own Read/Edit/Write/Bash tools touching denied paths or binaries. | The agent host's permission system (e.g., Claude Code's `permissions.deny`). |
| **3. Forced confirmation** | Visible-to-others writes that haven't been seen by a human. | `permissions.ask` for every state-mutating shell call (e.g., `gh pr create`, `gh issue edit`, `gh gist *`, `gh secret *`). Implements Principle 1 at the OS layer. |

### Five concrete consequences

1. **Default deny, allow-list opt-in.** New paths and new hosts
   require an explicit project-policy edit, surfaced in code
   review on the framework's `settings.json` (or equivalent).
   "I'll just allow `~/`" is not an answer.

2. **Permission patterns are advisory; the OS layer is the
   enforcement.** The deny list (`Bash(curl *)`, `Bash(wget *)`)
   is a friction layer that catches sloppy injection. The
   network allow-list is the actual control. Document this
   honestly; do not pretend the permission layer is the boundary.

3. **The clean-env wrapper is not optional.** A maintainer who
   typed `export GITHUB_TOKEN=…` in their shell once should not
   have that token visible to every agent subprocess thereafter.
   The wrapper is the only reason the agent's child `gh` call
   does not see your personal access token by accident.

4. **Tempfile + `printf '%s'` for attacker-controlled text** —
   any string that originated outside the framework (email
   subject, PR title, scanner finding, reporter-supplied free
   text) MUST NOT be inlined into a single- or double-quoted
   shell argument. Write it to a tempfile via
   `printf '%s' "$value" > /tmp/x` (no expansion) and pass via
   `gh api ... -F field=@/tmp/x` (verbatim from disk).

5. **Wrap untrusted bodies as inert text** when persisting them
   to project-visible artefacts. A four-backtick fenced code
   block defangs tracking pixels and markdown directives so
   future re-reads in fresh agent contexts see them as data,
   not instructions.

### Anti-patterns to avoid

- **`Bash(*)` and pray.** A blanket allow-bash with a long
  deny-list misses every wrapper-interpreter trick (`python3 -c`,
  `node -e`, `bash -c '…'`, `c''url …`, `/usr/bin/curl …`,
  chained pipelines on macOS). The deny-list is *advisory*; the
  control is the network allow-list.
- **`--body "$x"` interpolation.** Shell expansion of
  attacker-controlled text inside double quotes is the most
  common shell-breakout vector and the prek hooks do not catch
  it. Use `--body-file <path>` instead, always.
- **Implicit network egress.** Allowing `github.com`
  silently authorises `gh gist create` / `gh repo create
  --public`. Confirmation prompts (`permissions.ask`) on every
  state-mutating `gh` call are how Principle 1 meets Principle
  2 at the OS layer.

---

## Principle 3 — Vendor neutrality

### Normative statement

> The framework MUST NOT bind a maintainer's workflow to any
> single LLM vendor, model size class, hosting provider, or
> project-governance model. A skill that "works with Claude"
> MUST be expressible in a form that other LLM agents can
> consume; a workflow that integrates an ASF release process
> MUST work, with config substitution only, against a non-ASF
> project's release process.

### Two axes of neutrality

**Axis A — LLM backend neutrality.** Skills are
markdown-with-YAML, not vendor-specific prompts. The agentic
host (Claude Code, Codex, Gemini CLI, a local-Ollama wrapper,
a future Apache-aligned agent runtime) consumes the same
skill file and behaves comparably. The reference implementation
documents this explicitly: skills are "language-independent,
since SKILLs are English; standard Python ecosystem
dependencies for the deterministic-output scripts; no AI SDK
integration needed".

**Axis B — Project-governance neutrality.** ASF integrations
(private mailing lists, Vulnogram CVE flows, PMC roles, ASF
release process) are configurable, not hardcoded. A non-ASF
adopter swaps in a private GitHub repo, GitHub Security
Advisories, a maintainer roster, their own release process —
and the same skill executes. The reference implementation's
placeholder convention (`<tracker>`, `<upstream>`,
`<security-list>`, `<private-list>`) and the
`<project-config>/` adapter dir are how this is operationalised.

### Five concrete consequences

1. **Pluggable backend.** The framework's skills cite no
   model name in their flow logic. "Use the strongest model
   available" / "use a fast model for this lookup step" are
   acceptable hints; "must be Claude Sonnet 4.5" is not.

2. **Pluggable adapters.** Private-mailing-list, CVE-tool,
   release-process, and audit-finding ingest MUST live behind
   adapter modules. The reference implementation's
   `tools/<adapter>/` directories (`tools/vulnogram/`,
   `tools/gmail/`, `tools/ponymail/`) are this pattern.

3. **Pilot diversity.** Validation runs (per the Apache
   Steward MISSION.md) cover at least one frontier-model
   backend, at least one fully-local inference setup
   (Ollama / vLLM / equivalent), and at least one
   Apache-hosted or Apache-aligned endpoint. A framework that
   only validates against one vendor is a vendor-locked
   framework that has not noticed yet.

4. **Privacy-LLM gating is vendor-neutral by construction.**
   Private content (security reports, embargoed CVE detail,
   PMC-private mail) flows only to LLMs the project's PMC has
   explicitly approved. "Approved" is per-PMC, not
   per-framework — the framework's contribution is the gate
   check, not the policy. See
   [`tools/privacy-llm/`](../../tools/privacy-llm/) for the
   reference gate.

5. **License + IP posture.** Framework code AL2.0 / MIT.
   Skills AL2.0. Generated artefacts (commit messages, PR
   bodies, advisory drafts) inherit the maintainer's commit
   licence; the framework MUST NOT introduce a vendor's
   model-output licence by reference.

### Anti-patterns to avoid

- **"Cloud-only"-shaped skills.** A skill whose flow assumes a
  remote model with internet round-trip is a skill that locks
  the project to a vendor *and* breaks for offline / sovereign
  / air-gapped pilots. Skill flows assume the agent runtime
  exists; they do not assume what's behind it.
- **Vendor-named tools.** A skill called `claude-pr-review` is
  a skill that ages out the day a maintainer wants to use
  another agent. Tools are named for what they do, not what
  runs them.
- **Hardcoded ASF assumptions.** `apache/<project>` strings
  hardcoded into a skill make the skill ASF-only by accident.
  Placeholder discipline (`<upstream>`, `<tracker>`,
  `<security-list>`) is the cheapest way to keep the option
  open.

---

## Principle 4 — Conversational, correctable agentic skills

### Normative statement

> The agent's behaviour MUST be expressed as **agent-readable
> markdown** (skill files) that the maintainer can read,
> understand, override locally, and contribute back upstream
> through the normal patch workflow. The conversation between
> maintainer and agent — including the corrections the
> maintainer makes when the agent gets it wrong — MUST be the
> primary mechanism by which the framework's skills evolve.

### Why this is structurally different

The instinct from twenty years of writing services is to encode
behaviour in code, configuration files, or YAML. **An agent's
prompts and skill files are code in every meaningful sense, but
their "compile" step is the conversation that follows.** The
maintainer notices the agent is using the wrong tone in mentor
replies, edits the skill's tone block, the next invocation
behaves differently, and (after a stabilisation period) the
edit is upstreamed.

The shift the maintainer makes is from "this tool needs a code
change" to "this skill needs a markdown edit". The shift the
framework makes is from "user-of-tool" to
"co-author-of-tool".

### Five concrete consequences

1. **Skills are markdown.** Not YAML. Not JSON. Not a DSL.
   Markdown with YAML frontmatter and inline code blocks. The
   maintainer reads them like documentation; the agent reads
   them like instructions; the diff between two revisions is
   reviewable in the normal PR review surface.

2. **Local override before upstream PR.** The reference
   implementation's `.apache-steward-overrides/<skill>.md`
   convention lets a maintainer encode "for this project, do
   X differently" without forking the framework. The override
   file is committed in the adopter's repo; the framework
   reads it at runtime and merges agent-readable
   modifications before executing the default behaviour.

3. **Upstream loop is first-class.** When an override has
   stabilised — typically after a few weeks of running — the
   `setup-override-upstream` skill (or equivalent) walks the
   maintainer through promoting the override into a framework
   PR. Some overrides stay local forever (project-specific
   policy); some belong upstream (general improvement). The
   framework MUST surface the choice explicitly.

4. **Correction is in-conversation.** The maintainer says
   "stop using `--repo` argument; my project uses
   `--repository`" and the agent acknowledges, applies the
   change in this session, and surfaces the override-file
   path so the correction persists across sessions. The
   maintainer is not expected to know the framework's source
   layout to make a behaviour change stick.

5. **Skills carry their own provenance.** Every skill cites
   what it does, what it does **not** do, the placeholders it
   uses, the adapter-config knobs it consults, and (where
   applicable) the upstream commit it was derived from. The
   maintainer who reads the skill knows what they are trusting.

### Anti-patterns to avoid

- **Black-box agents.** "The agent does what the agent does"
  is the worst possible posture. The maintainer must be able
  to read *why* the agent is doing X and *change* the
  governing instruction.
- **Forks as the correction mechanism.** "Fork the framework,
  fix the skill, run your fork" makes everyone the maintainer
  of their own framework. The local-override path keeps the
  maintainer in their lane.
- **Hidden state.** A skill whose behaviour depends on
  conversation history that is not surfaced in the skill file
  cannot be corrected. State that lives only in the LLM's
  context window is invisible to git; it cannot be reviewed,
  cannot be diff'd, cannot be tested.
- **Implicit "training".** A framework that quietly fine-tunes
  on the maintainer's corrections without surfacing the
  resulting drift is making model changes the maintainer did
  not consent to. Corrections live in the skill files
  (visible, version-controlled), not in the model weights
  (invisible, opaque).

---

## How the four principles compose

The four principles are independently necessary; together they
form a cycle the maintainer can repeatedly apply:

```text
   ┌──────────────────────────────────────────────────────┐
   │                                                      │
   ▼                                                      │
[Skill]  ─── proposes ──▶  [Maintainer]  ─── confirms ──▶ │
 ▲                              │                         │
 │                              │ corrects                │
 │                              ▼                         │
 │                        [Override file]  ─── upstream ──┘
 │                              │
 └────── reads at runtime ──────┘

         Sandbox is under everything.
         Vendor neutrality means any LLM
         can play the [Skill] role.
```

- **(1)** says the [Maintainer → confirms] arrow is mandatory.
- **(2)** says the [Skill] runs in a fenced room.
- **(3)** says the [Skill] is portable across the agentic
  hosts — Claude Code today, a different host tomorrow.
- **(4)** says the [Maintainer → corrects → Override → Skill]
  loop is how the framework gets better.

Drop any one of the four and the system regresses to a
recognisable bad pattern: drop (1) and you have an autonomous
agent the maintainer is on the hook for; drop (2) and one
prompt injection ruins the day; drop (3) and the project
becomes a vendor's cost centre; drop (4) and the skill is a
black box only the framework's authors can fix.

---

## Adoption guidance for non-Steward projects

A project that wants to adopt these principles without adopting
Apache Steward as a whole has the following minimum bar:

1. **Pick an agent host with HITL primitives.** Claude Code,
   Cursor's Composer, and Aider all support per-action
   confirmation. Avoid hosts that default to "auto-apply
   suggested changes".

2. **Wrap the host in an OS sandbox.** On Linux,
   `bubblewrap` + a network-allow-list HTTP proxy is one
   day's work. On macOS, a `sandbox-exec` profile is similar.
   The agent's parent shell runs in the sandbox; every
   subprocess inherits.

3. **Treat skill files as code.** Land them in a `skills/`
   directory under your project's main repo or a sibling
   `<project>-steward` repo. PR them. Review them. Diff
   them. Don't hand-edit them on production machines without
   committing.

4. **Document the adapter boundaries.** What is
   project-specific (your release process, your CVE flow,
   your private mailing list)? Move those into a
   `<project-config>/` directory with documented placeholders
   and let the skills consult them.

5. **Pilot before scale.** Run the agent against your
   project's own backlog for a release cycle before letting
   it touch contributor-facing artefacts at full speed. The
   contributor-sentiment data you collect during the pilot is
   the only honest signal that the framework is helping, not
   just speeding up the harm.

The Apache Steward project is happy to consult on the lift —
see [`MISSION.md`](../../MISSION.md) for the maintainer-
education stream.

---

## What this RFC does NOT specify

- **Specific LLM choice.** The principles are independent of
  the model. Pick the model that meets the project's
  privacy / cost / latency / sovereignty constraints.
- **Specific UI.** A terminal-based CLI, a CI bot, an IDE
  extension, a web dashboard — all are valid surfaces. The
  principles apply identically.
- **Specific scaffolding library.** LangGraph, BAML, raw
  Anthropic SDK, raw OpenAI SDK, ollama-cli, llamafile — pick
  one. The skills are the contract; the runtime is an
  implementation detail.
- **Pricing or hosting.** The project is the buyer; the
  vendor is the seller. The framework declines to express a
  preference on either.
- **Mandatory model evaluation.** Per-skill eval is recommended
  but not required by this RFC. A separate RFC may cover
  evaluation methodology — see the
  [Apache Plumb](https://incubator.apache.org/projects/plumb.html)
  collaboration in
  [`MISSION.md`](../../MISSION.md).

---

## References

### Internal (this repository)

- [`MISSION.md`](../../MISSION.md) — Apache Steward TLP
  proposal: motivation, scope, design commitments, initial
  PMC composition target.
- [`AGENTS.md`](../../AGENTS.md) — agent-authoring
  conventions, placeholder convention, prompt-injection
  absolute rule.
- [`docs/setup/secure-agent-setup.md`](../setup/secure-agent-setup.md)
  — adopter-facing install of the secure agent setup.
- [`docs/setup/secure-agent-internals.md`](../setup/secure-agent-internals.md)
  — the *why* behind every layer of the sandbox.
- [`docs/setup/agentic-overrides.md`](../setup/agentic-overrides.md)
  — the override → upstream loop that operationalises
  Principle 4.
- [`docs/modes.md`](../modes.md) — the A/B/C/D mode taxonomy
  the principles ride on top of.
- [`tools/privacy-llm/`](../../tools/privacy-llm/) — the
  vendor-neutral privacy gate referenced in Principle 3.

### External

- [Apache Software Foundation Responsible AI Initiative](https://incubator.apache.org/projects/responsible-ai.html)
  — the broader policy context this RFC participates in.
- [ASF Generative-Tooling Policy](https://www.apache.org/legal/generative-tooling.html)
  — the licence and contribution-attribution baseline every
  agentic-tooling RFC under the ASF umbrella inherits.
- [Anthropic Responsible Scaling Policy](https://www.anthropic.com/responsible-scaling-policy)
  — vendor-side counterpart to the maintainer-side principles
  in this RFC. The two are complementary; neither
  substitutes the other.

---

## Acknowledgements

This RFC distils principles operationalised in the Apache
Steward reference implementation. The PMC roster and
collaborator list (see [`MISSION.md`](../../MISSION.md))
includes the people whose discussion, code, and incident-review
work shaped these principles. The framing of the principles
here owes a particular debt to the 2026-05 prompt-injection
audit
([gist](https://gist.github.com/andrew/0bc8bdaac6902656ccf3b1400ad160f0))
that surfaced the Principle 2 specifics, and to the Mode A/B/C/D
swimlane discussion that surfaced the carve-out structure of
Principle 1.
