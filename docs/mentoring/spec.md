<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Mode B — conversational mentoring (spec)](#mode-b--conversational-mentoring-spec)
  - [Status](#status)
  - [Scope](#scope)
  - [Triggers](#triggers)
  - [Teaching register — tone guide](#teaching-register--tone-guide)
    - [Voice](#voice)
    - [Forbidden](#forbidden)
    - [AI-attribution footer](#ai-attribution-footer)
  - [Hand-off protocol](#hand-off-protocol)
  - [Adopter contract](#adopter-contract)
  - [Open questions](#open-questions)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Mode B — conversational mentoring (spec)

## Status

Proposed. No skill code yet. This document defines what Mode B
should do once it exists; it lands ahead of any skill so the
project's tone choices and hand-off rules are reviewable
independently from runtime behaviour. See
[`MISSION.md` § Mode B](../../MISSION.md#technical-scope) and
[`docs/modes.md` § Mode B](../modes.md#mode-b--conversational-mentoring)
for sequencing.

## Scope

Mode B joins issue and PR threads in a teaching register. The
agent's job is to lower the barrier to a contributor's *next
useful action*. Concretely, in scope:

- **Clarifying questions** when the contributor's first message
  is ambiguous (missing repro, missing version, missing intent),
  so a human reviewer's first read is a productive one.
- **Pointers to project conventions** with a direct link, when
  the contributor is missing a piece of repo context they could
  have found themselves but did not.
- **Explanation of *why*** a request was made, when the
  contributor pushes back on a maintainer's review comment ("why
  does this need a test?", "why split the PR?").
- **Paired examples from prior PRs** when a similar pattern has
  shipped before and a one-line link saves the contributor
  several hours.
- **Hand-off** to a human when the question exceeds what an
  agent should answer (architectural taste, security-sensitive
  design, deprecation timing, anything embargoed).

Out of scope:

- *Reviewing code*. That is Mode A's
  [`pr-management-code-review`](../../.claude/skills/pr-management-code-review/SKILL.md)
  skill. Mode B does not approve, request changes, or post inline
  diff comments.
- *Triage routing*. That is Mode A's
  [`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md)
  skill. Mode B does not assign labels, mark draft, or close PRs.
- *Authoring fixes*. That is Mode C. Mode B does not open PRs or
  edit code.
- *Speaking for the maintainer team* on disputed decisions. Mode
  B says "a maintainer will weigh in" and stops.

## Triggers

Mode B never posts unprompted on a thread it has not been
invoked on. The skill is opt-in per invocation. Three trigger
paths:

1. **Maintainer-on-demand**. A maintainer runs
   `/pr-management-mentor <pr-number>` (working name). The skill
   reads the thread, decides whether a mentoring intervention is
   warranted, drafts the comment, and waits for the maintainer
   to confirm before posting.
2. **First-contact filter**. After
   [`pr-management-triage`](../../.claude/skills/pr-management-triage/SKILL.md)
   classifies a PR as "first contributor, missing repro" (or
   equivalent triage flag), the maintainer can chain
   `/pr-management-mentor` on that PR. The two skills compose;
   Mode B does not run inside Mode A by default.
3. **Issue-thread invocation**. Same opt-in, on issues rather
   than PRs, for the "missing version / missing repro" case.

Why no auto-fire: posting a teaching-register comment without
explicit human authorization risks the agent talking past a
maintainer who is mid-conversation with the contributor, or
posting on a thread where the maintainer has *deliberately* not
replied yet. Auto-fire is a Mode-D-shaped problem and inherits
Mode D's sequencing constraint.

## Teaching register — tone guide

The contributor is the audience, not the maintainer. The
agent's voice is **patient, specific, and short**. It is not
formal. It does not lecture. It does not perform empathy. The
reader should leave the comment knowing what to do next, not
feeling managed.

### Voice

- **First line states the action**, not the meta. "Could you add
  the version you're running? Find it via …" not "I noticed
  your issue and would love to help by asking a clarifying
  question."
- **Link, don't quote**. Pointers to docs go as a single inline
  link with a short label. Do not paste the docs back at the
  contributor.
- **One ask per comment**. If the contributor is missing three
  things, ask for them as a numbered list, not three sequential
  paragraphs.
- **No hedging**. "This is a known pattern, see PR #1234" not
  "It seems like this might possibly be similar to PR #1234,
  although I'm not certain". The hedge tax falls on the
  contributor, who then has to decide how seriously to take the
  pointer.

### Forbidden

- Praise without specificity. "Great question!" and "Thanks for
  the contribution!" are noise. They train the contributor to
  skim.
- Restating the contributor's message back to them. "So what
  you're saying is …" — the contributor knows what they said.
- AI self-reference outside the attribution footer. The footer
  says it once; the body should not.
- Speaking for the maintainer. "The maintainers will probably
  want X" — Mode B does not predict maintainer decisions. It
  says "a maintainer will reply on this; in the meantime,
  here's the convention" and stops.

### AI-attribution footer

Every contributor-facing comment ends with the same footer
convention used by
[`pr-management-triage/comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md),
adjusted to name the mentoring step rather than the triage
step. The expansion lives in the adopter's
`<project-config>/mentoring-config.md → ai_attribution_footer`.

The footer is non-negotiable: it calibrates the contributor's
trust (AI-drafted, may be wrong) and points at the project's
documented two-stage process.

## Hand-off protocol

The agent bows out and pings a human when:

1. The contributor pushes back on a substantive design point.
   Mode B answers "why is this convention" once. If the
   contributor disagrees, Mode B does not argue; it pings the
   maintainer.
2. The question touches security, embargoed work, deprecation
   timing, or anything not covered by public documentation.
   Mode B does not improvise on these surfaces.
3. The thread reaches `<max_agent_turns>` (configurable, default
   2). After that the agent stops engaging on the thread
   regardless of content.
4. The contributor explicitly asks for a human ("can a
   maintainer look at this?").

The hand-off is one comment: a `@`-mention of the configured
maintainer team, a one-line summary of the open question, and
the agent's silence afterwards. The agent does not summarise
the conversation; the maintainer reads the thread.

## Adopter contract

Per-project values live in `<project-config>/mentoring-config.md`.
See the template at
[`projects/_template/mentoring-config.md`](../../projects/_template/mentoring-config.md).
Required keys:

| Key | Purpose |
|---|---|
| `mentoring_invocation_command` | Slash-command name (e.g. `/pr-management-mentor`). |
| `maintainer_team_handle` | `@<org>/<team>` mentioned on hand-off. |
| `ai_attribution_footer` | Literal footer markdown. Mirrors the triage-footer convention. |
| `convention_pointers` | Table of `{trigger phrase} → {docs link, one-line label}` so the agent links rather than paraphrases. |
| `max_agent_turns` | Integer, default 2. Hard ceiling on consecutive agent comments per thread. |
| `out_of_scope_topics` | Explicit list of topics on which the agent always hands off (security, deprecation, license, etc.). |

## Open questions

Surfaced here so reviewers can weigh in before the skill is
built.

- **Should Mode B post on the project's mailing list, or only
  on GitHub threads?** Current draft: GitHub only. Mailing-list
  mentoring lives in the human maintainer's voice; the agent
  does not have a list-subscriber identity.
- **Is the AI-attribution footer the same wording as the triage
  footer, or distinct?** Current draft: same wording, different
  step token. One contributor-trust calibration is easier to
  reason about than two.
- **Should the maintainer review every Mode B draft, or can
  they pre-authorize a class of comments (e.g., "always ok to
  ask for repro")?** Current draft: every draft is reviewed.
  Pre-authorization is Mode-D-shaped and inherits the same
  sequencing constraint.

## Cross-references

- [`MISSION.md` § Mode B](../../MISSION.md#technical-scope) —
  the mode definition + responsible-AI framing.
- [`docs/modes.md` § Mode B](../modes.md#mode-b--conversational-mentoring) —
  current implementation status (proposed).
- [`.claude/skills/pr-management-triage/comment-templates.md`](../../.claude/skills/pr-management-triage/comment-templates.md) —
  closest existing surface; informs the tone-footer convention
  but is not Mode B.
- [`AGENTS.md`](../../AGENTS.md) — repository-level rules every
  mode inherits.
