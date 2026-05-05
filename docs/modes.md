<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Modes — MISSION taxonomy mapped to current skills](#modes--mission-taxonomy-mapped-to-current-skills)
  - [Status legend](#status-legend)
  - [Modes at a glance](#modes-at-a-glance)
  - [Mode A — triage](#mode-a--triage)
  - [Mode B — conversational mentoring](#mode-b--conversational-mentoring)
  - [Mode C — agent-authored fixes with human review](#mode-c--agent-authored-fixes-with-human-review)
  - [Mode D — narrowly-scoped fix-and-merge](#mode-d--narrowly-scoped-fix-and-merge)
  - [Outside the modes](#outside-the-modes)
  - [Mode lifecycle](#mode-lifecycle)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# Modes — MISSION taxonomy mapped to current skills

[`MISSION.md`](../MISSION.md) frames the framework around four
toggleable **modes** of agent-assisted repository maintainership:
**A** (triage), **B** (mentoring), **C** (agent-authored fixes
with human review), and **D** (narrowly-scoped fix-and-merge).
Each adopting project picks the modes that match its culture and
risk tolerance.

This document maps that taxonomy to the skills that currently
ship in the framework. It is the **honest snapshot** — modes
that are not yet implemented are listed as such, with a tracking
issue or roadmap pointer rather than a placeholder shell. Read
[`MISSION.md`](../MISSION.md) for the *why* of each mode and the
sequencing commitments behind them.

## Status legend

| Status | Meaning |
|---|---|
| **stable** | Implemented, in use by at least one adopter, behaviour expected to remain backward-compatible across minor framework versions. |
| **experimental** | Implemented but not yet covered by an adopter pilot or contributor-sentiment evaluation; shape may change. |
| **proposed** | Designed in [`MISSION.md`](../MISSION.md) but no skill yet exists; tracked for future implementation. |
| **off** | Deliberately not implemented per a MISSION-level sequencing rule (Mode D). |

## Modes at a glance

| Mode | Purpose | Status | Skill count |
|---|---|---|---|
| **A** — triage | Issues, security reports, PRs: spot, classify, route, surface duplicates. Every output is a suggestion the human signs off on. | stable (security) / experimental (pr-management) | 10 |
| **B** — conversational mentoring | Joins issue and PR threads in a teaching register: clarifying questions, pointers to project conventions, paired examples from prior PRs, hand-off to a human when scope exceeds the agent. | proposed | 0 |
| **C** — agent-authored fixes with human review | Agent drafts a fix for a well-scoped problem and opens a PR; every PR is reviewed and merged by a human committer. | stable (security-only); generic case proposed | 1 |
| **D** — narrowly-scoped fix-and-merge | Auto-merge restricted to objectively boring change classes (lint, dependency bumps inside an allow-list, license-header insertion, formatting, broken-link repair). | off | 0 |

A few skills sit **outside** the mode taxonomy by design — see
[Outside the modes](#outside-the-modes) below.

## Mode A — triage

Inbound report and PR triage. The lowest-risk surface and the
foundation everything else builds on. Skills propose labels,
spot duplicates, link related discussions, classify reports
against prior triaged cases, and route to the right human; they
do not act without human review.

| Skill | Domain | Status |
|---|---|---|
| [`pr-management-triage`](../.claude/skills/pr-management-triage/SKILL.md) | Generic PR queue triage. | experimental |
| [`pr-management-stats`](../.claude/skills/pr-management-stats/SKILL.md) | PR-queue reporting (supports triage decisions). | experimental |
| [`pr-management-code-review`](../.claude/skills/pr-management-code-review/SKILL.md) | Maintainer-facing deep code review. | experimental |
| [`security-issue-import`](../.claude/skills/security-issue-import/SKILL.md) | Inbound security-report classification + initial routing. | stable |
| [`security-issue-import-from-pr`](../.claude/skills/security-issue-import-from-pr/SKILL.md) | Open a tracker from a security-relevant public PR. | stable |
| [`security-issue-import-from-md`](../.claude/skills/security-issue-import-from-md/SKILL.md) | Bulk-import findings from a markdown report. | stable |
| [`security-issue-deduplicate`](../.claude/skills/security-issue-deduplicate/SKILL.md) | Merge two trackers describing the same root-cause vulnerability. | stable |
| [`security-issue-invalidate`](../.claude/skills/security-issue-invalidate/SKILL.md) | Close a tracker as invalid with a polite-but-firm reporter reply. | stable |
| [`security-issue-sync`](../.claude/skills/security-issue-sync/SKILL.md) | Reconcile a tracker against its mail thread, fix PR, release train, and archives. | stable |
| [`security-cve-allocate`](../.claude/skills/security-cve-allocate/SKILL.md) | Allocate a CVE for a tracker (Vulnogram URL + paste-ready JSON). | stable |

Two notes on the boundaries:

- `pr-management-code-review` is a deeper variant of triage —
  the agent reads diff and surrounding code rather than only
  metadata, but the output is still a suggestion for the human
  reviewer. It belongs to Mode A by the same rule.
- `security-cve-allocate` is procedural rather than classificatory
  (CVE allocation happens after assessment), but it shares Mode A's
  shape: the agent prepares a paste-ready artefact, the human
  PMC member submits it. Listed here for navigability.

## Mode B — conversational mentoring

**Status: proposed. No skill yet.**

[`MISSION.md` § Mode B](../MISSION.md#technical-scope) names this
the highest-value mode and the one off-the-shelf agent tooling
skips. Implementation is tracked as future work; spec, tone
guide, and adopter configuration template land in a follow-up
PR before any skill code, so the project's tone choices are
reviewable independently from the runtime behaviour.

The closest existing surface is
[`pr-management-triage/comment-templates.md`](../.claude/skills/pr-management-triage/comment-templates.md),
which carries Mode A classification responses — informational,
not pedagogical. It is **not** Mode B.

## Mode C — agent-authored fixes with human review

The agent drafts a fix for a well-scoped problem (a tracked
issue, a triaged security report with team consensus on scope, a
failing test with an obvious cause, a documentation hole) and
opens a PR. Every PR is reviewed and merged by a human committer;
the agent never merges its own work.

| Skill | Domain | Status |
|---|---|---|
| [`security-issue-fix`](../.claude/skills/security-issue-fix/SKILL.md) | Draft a fix PR in `<upstream>` from a triaged, CVE-allocated tracker. | stable (security-only) |

**Generic Mode C is proposed.** [`MISSION.md`](../MISSION.md)
names lint fixes, audit-tool findings (Apache Verum, Apache Caer,
CodeQL, equivalents), failing tests with obvious causes, and
documentation holes as in-scope for Mode C beyond the security
case. None of those are implemented yet; security-issue-fix is
the only Mode C skill in the framework today.

For security-class Mode C PRs, the public surface strips CVE and
private context per the project's disclosure policy, so the
public surface stays clean until the embargo lifts — see
[`AGENTS.md` § Confidentiality](../AGENTS.md#confidentiality-of-the-tracker-repository)
for the rules the skill enforces.

## Mode D — narrowly-scoped fix-and-merge

**Status: off. Deliberately not implemented.**

[`MISSION.md` § Mode D](../MISSION.md#technical-scope) holds
auto-merge off until Modes A, B, and C have been running for
two quarters and contributor-sentiment data says the project is
healthier, not just faster. Security-class changes are
explicitly **out** of Mode D — no auto-merge ever touches
anything embargoed or CVE-tagged.

The framework's current `.asf.yaml` configuration reflects this
posture: `pull_requests.allow_auto_merge` is set to `false`
([`.asf.yaml`](../.asf.yaml)).

When Mode D ships, the eligible change classes will be declared
per-adopter in `<project-config>/` and gated by an allow-list
that the framework refuses to grow without an adopter PR.

## Outside the modes

Several skills are framework infrastructure rather than
maintainership modes. They support adoption, isolation, and
upgrade flows; they do not act on issues, PRs, or contributor
threads on their own.

| Skill | Purpose |
|---|---|
| [`setup-steward`](../.claude/skills/setup-steward/SKILL.md) | Adopt the framework into an adopter repo; manage the snapshot, symlinks, and overrides. |
| [`setup-isolated-setup-install`](../.claude/skills/setup-isolated-setup-install/SKILL.md) | Install the credential-isolation sandbox harness. |
| [`setup-isolated-setup-update`](../.claude/skills/setup-isolated-setup-update/SKILL.md) | Update pinned system tools (`bubblewrap`, `socat`, agent CLI) past the cooldown window. |
| [`setup-isolated-setup-verify`](../.claude/skills/setup-isolated-setup-verify/SKILL.md) | Read-only health check of the sandbox harness. |
| [`setup-override-upstream`](../.claude/skills/setup-override-upstream/SKILL.md) | Promote an adopter's local override into a framework PR. |
| [`setup-shared-config-sync`](../.claude/skills/setup-shared-config-sync/SKILL.md) | Sync shared configuration across worktrees. |

These ship as a single **setup family** — see
[`docs/setup/README.md`](setup/README.md).

## Mode lifecycle

A mode moves through four states as it matures:

1. **proposed** — designed in [`MISSION.md`](../MISSION.md), no
   skill code yet. Spec PRs may land before any skill code so
   tone, scope, and adopter knobs are reviewable in isolation.
2. **experimental** — at least one skill exists, behaviour may
   change, no adopter pilot has run an evaluation. Adopters
   can opt-in but should expect breaking changes between
   framework versions.
3. **stable** — at least one adopter is running the mode in
   production, behaviour is backward-compatible across minor
   framework versions. The default state for skills shipped to
   adopters.
4. **graduated-to-D-eligible** *(future state, Mode A/B/C only)* —
   the mode has run stable for two quarters with positive
   contributor-sentiment evidence, the framework will start
   considering an equivalent change class for Mode D auto-merge.
   This state does not exist yet because Mode D itself is off.

A mode can be **retracted** from any state. The retraction
triggers MISSION names — sustained negative contributor
sentiment, a confidentiality leak, a sandbox bypass that escapes
detection — apply per-adopter and per-mode. A retraction in one
adopter does not auto-retract in another, but the framework
records it for cross-adopter pattern detection.

## Cross-references

- [`MISSION.md`](../MISSION.md) — the *why* of each mode, the
  sequencing commitments, and the privacy/security/vendor-
  neutrality posture each mode inherits.
- [`README.md`](../README.md#skill-families) — adopter-facing
  skill family table; this document is the maintainer-facing
  taxonomy view of the same skills.
- [`AGENTS.md`](../AGENTS.md) — repository-level rules every
  mode inherits (external content as data, polite-but-firm
  tone, brevity, confidentiality).
