<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — reassessment pool defaults

Named issue pools for [`issue-reassess`](../../.claude/skills/issue-reassess/SKILL.md)
sweep campaigns. Each pool is a query against `<issue-tracker>` that
surfaces a particular kind of candidate.

Express each pool as a query the tracker accepts (JQL for JIRA,
`gh search` for GitHub Issues, etc.). The skill picks one pool per
sweep; the user can override per-invocation.

This file extends the default-triage-pool query in
[`issue-tracker-config.md`](issue-tracker-config.md) with named
named-and-rationalised pools tuned to specific reassessment goals.

## Pool: `open-eol`

Open issues whose `fixVersion` is end-of-life. Often contains:

- Long-fixed-but-never-closed issues (silent fixes).
- Wishlists that the team has resisted.
- Real bugs that fell through the cracks at end-of-life.

```text
TODO: project-specific query for open-eol
```

JIRA example:
```text
project = <KEY> AND resolution = Unresolved AND
  fixVersion in releasedVersions() AND
  fixVersion was in unreleasedVersions() AND status = Open
```

## Pool: `reopened`

Issues that were closed and later reopened. Surfaces:

- Persistent wishlists the team keeps resisting (often classified
  `feature-request-disguised-as-bug` per the nature taxonomy in
  [`issue-reproducer/verdict-composition.md`](../../.claude/skills/issue-reproducer/verdict-composition.md)).
- True regressions where a fix was reverted or didn't stick.

```text
TODO: project-specific query for reopened
```

JIRA example:
```text
project = <KEY> AND status changed FROM "Closed" TO "Open"
```

## Pool: `stale-unresolved`

Open issues with no activity in the last 12 months. Useful for
periodic hygiene sweeps to confirm-or-close.

```text
TODO: project-specific query for stale-unresolved
```

JIRA example:
```text
project = <KEY> AND resolution = Unresolved AND
  updated < -52w
```

## Pool: project-specific

Adopters can add pools tuned to their specific concerns — e.g.,
issues lacking a component label, issues filed before a specific
major release, issues with specific keyword overlap.

## Pool-selection guidance

The skill picks one pool per sweep. Hints for picking:

- **First-ever sweep** of an existing project: start with
  `open-eol` (highest density of silent fixes; fastest to clear).
- **Periodic hygiene** sweeps: rotate through pools each quarter.
- **Pre-release** sanity sweeps: `stale-unresolved` and any
  release-version-specific pool.
- **Specific concern** (e.g., complaint about wishlist accumulation):
  `reopened`.

## Cross-references

- [`issue-tracker-config.md`](issue-tracker-config.md) — the
  default-triage pool (distinct from these reassess pools).
- [`reproducer-conventions.md`](reproducer-conventions.md) —
  evidence layout for each issue in a sweep.
