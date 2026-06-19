<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

---
title: Triage mode
status: experimental
kind: feature
mode: Triage
source: >
  MISSION.md § Technical scope (Triage). docs/modes.md § Triage.
  Implemented by the pr-management, issue, and security skill families.
acceptance:
  - Every triage skill is read-only on tracker state or proposes-then-
    confirms; none transitions, closes, or labels without confirmation.
  - Classifications are grounded in prior triaged cases / the project's
    Security Model, not invented categories.
  - Security-side import/dedupe/sync/invalidate/allocate skills are
    stable; PR and general-issue triage are experimental.
---

# Triage mode

## What it does

The lowest-risk, foundational mode: spot inbound issues / security
reports / PRs, classify them, surface likely duplicates, link related
discussions, and propose routing to the right human. Every output is a
suggestion the human signs off on.

## Where it lives

- PR queue: `pr-management-triage`, `pr-management-stats`,
  `pr-management-code-review` (deep review is a triage variant),
  `pr-management-quick-merge` (read-only express-lane surfacing of
  trivial, low-risk PRs a maintainer can review in seconds).
  Reference implementation: `tools/pr-management-stats/`.
- General issues: `issue-triage`, `issue-reassess`, `issue-reproducer`,
  `issue-stale-sweep` (configurable inactivity sweep: nudge or
  propose-close after a warning window; waits for confirmation before
  posting). Companion reporting skill: `issue-reassess-stats`
  (read-only dashboard over `verdict.json` files produced by
  `issue-reassess` campaigns).
- Contributor readiness: `contributor-nomination` (read-only brief for a
  named contributor — activity breadth, consistency, and nomination-
  evidence prose for a committer or PMC thread);
  `contributor-activity-sweep` (read-only GitHub activity card for a
  named contributor over a configurable window);
  `committer-onboarding` (post-vote ICLA/account/permissions/welcome
  checklist for committer and PMC promotions).
- Security inbound: `security-issue-import`, `-import-from-pr`,
  `-import-from-md`, `-import-from-scan` (triage-first scanner-output
  import via pluggable scan-format adapters),
  `-import-via-forwarder` (relay-broker variant: reports relayed by an
  upstream broker such as the ASF security team),
  `security-issue-triage` (batch-triage open tracker issues carrying
  `needs triage`), `security-issue-deduplicate`,
  `security-issue-invalidate`, `security-issue-sync`,
  `security-cve-allocate`.
- Adapters it reads through: `tools/github`, `tools/jira`,
  `tools/ponymail`, `tools/gmail`, `tools/mail-source`.

## Behaviour & contract

- **Read-only or propose-then-confirm.** `issue-triage` and
  `security-issue-triage` post a *proposal comment* on confirmation and
  never flip labels, close, or allocate. Reproducers produce evidence
  (`verdict.json`), never post.
- Six-class disposition vocabulary on the security side
  (`VALID` / `DEFENSE-IN-DEPTH` / `INFO-ONLY` / `INVALID` /
  `PROBABLE-DUP` / `FIX-ALREADY-PUBLIC`).
- Duplicate detection keys on stable identifiers (Gmail `threadId`,
  GHSA-ID), not on fuzzy body text alone.

## Out of scope

- Authoring fixes (that is Drafting, [Drafting](drafting-mode.md)).
- Any state change a human has not confirmed in-session.

## Acceptance criteria

1. No triage skill performs an unconfirmed state change.
2. `skill-and-tool-validate` passes on all triage-family skills.
3. docs/modes.md Triage table matches the shipped skill set.

## Validation

```bash
uv run --project tools/skill-and-tool-validator --group dev skill-and-tool-validate
```

## Known gaps

- PR and general-issue triage are `experimental` — no adopter-pilot eval
  has run; behaviour may change.
- **General-issue triage lacks a deduplication skill and a backlog
  dashboard.** `issue-stale-sweep` now provides the stale-handling /
  close-proposal capability. There is still no general-issue
  deduplication skill (only `security-issue-deduplicate` exists), and no
  general open-issue backlog dashboard (`pr-management-stats` covers
  PRs; `issue-reassess-stats` only covers reassess-campaign
  `verdict.json` output). Each is a candidate work item.
- **The contributor-growth skills span the path but are not yet a named
  family.** `contributor-nomination`, `contributor-activity-sweep`,
  `committer-onboarding`, and `good-first-issue-author` (Mentoring) are
  now all catalogued in the specs. Missing members of the
  contributor-to-committer path: PMC-member nomination (distinct from
  committer), emeritus / inactive-committer handling, and contributor
  offboarding. Worth deciding whether this becomes a named family with
  its own spec.
- **Repo-health audits are a one-off with no family around them.**
  `ci-runner-audit` is a standalone read-only audit (obsolete runner
  labels, macOS arch mismatches) with no sibling skills. A repo-health
  family is a candidate: GitHub Actions workflow security audit (the repo
  already runs `zizmor` in pre-commit), dependency-update triage,
  license / NOTICE compliance, and flaky-test detection.
