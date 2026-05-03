---
name: setup-steward
description: |
  Adopt and maintain the apache-steward framework in a project
  repo using the snapshot-based adoption mechanism. The single
  framework artefact that lives **committed** in an adopter's
  repo — every other framework skill is a symlink into a
  gitignored snapshot this skill manages. Sub-actions:
    `/setup-steward`         — first-time adoption (default)
    `/setup-steward upgrade` — refresh the gitignored snapshot
    `/setup-steward verify`  — health check the integration
    `/setup-steward override <skill>` — open or scaffold an
                               agentic override for a framework
                               skill in `.apache-steward-overrides/`
when_to_use: |
  Invoke when the user says "adopt apache-steward", "adopt
  apache/airflow-steward", "set up steward in this repo", or
  the agent equivalent triggered by following the framework's
  README adoption instructions. Also for periodic maintenance:
  "upgrade steward", "verify steward setup", "update the
  steward snapshot". This is the only framework skill that
  should be **copied** into an adopter's repo (every other
  framework skill is a symlink the adopt sub-action wires up).
license: Apache-2.0
---

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

<!-- Placeholder convention (see ../../AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config>           → adopter's `.apache-steward-overrides/` directory
     <snapshot-dir>             → `.apache-steward/` (gitignored snapshot of the framework)
     <upstream>                 → adopter's public source repo (the repo this skill is being run in)
     <framework-source>         → the apache-steward source we download a snapshot from
                                   (currently `https://github.com/apache/airflow-steward.git`,
                                    later `https://downloads.apache.org/airflow/...` (e.g.) once
                                    official ASF releases ship). -->

# setup-steward

This skill is **the only framework artefact an adopter
project commits**. Every other apache-steward skill (security,
pr-management) is a gitignored symlink into the gitignored
snapshot at `<snapshot-dir>` that this skill manages.

The adoption model is **snapshot + agentic overrides** (not
submodule, not marketplace, not vendored copy):

- The framework is downloaded as a `--depth=1` git checkout (or,
  once official ASF releases ship, a signed tarball) into
  `<snapshot-dir>` and **gitignored** in the adopter repo. The
  snapshot is a build artefact, not source.
- Symlinks from the adopter's skill directory into
  `<snapshot-dir>/.claude/skills/<framework-skill>/` make the
  framework's skills callable as if they lived in the adopter
  repo. The symlinks are also **gitignored** because their
  targets disappear on a fresh clone before `/setup-steward`
  runs.
- Adopter-specific modifications to framework workflows live as
  agent-readable instructions under
  `.apache-steward-overrides/<skill-name>.md` (committed). They
  invalidate or change steps the framework's skill would
  otherwise run. See
  [`overrides.md`](overrides.md) for the contract and
  [`docs/setup/agentic-overrides.md`](../../../docs/setup/agentic-overrides.md)
  for the design rationale.

## Detail files in this directory

| File | Purpose |
|---|---|
| [`adopt.md`](adopt.md) | First-time adoption walk-through — detect the adopter's skills-dir convention, download the snapshot, set up `.gitignore`, create the framework-skill symlinks, scaffold `.apache-steward-overrides/`, update the adopter's project docs. The default sub-action. |
| [`upgrade.md`](upgrade.md) | Refresh the gitignored snapshot to a newer framework version, reconcile any agentic overrides against the new framework structure, surface conflicts. |
| [`verify.md`](verify.md) | Read-only health check — snapshot present + intact, symlinks point at live targets, `.gitignore` correct, `.apache-steward-overrides/` exists, the `setup-steward` skill itself is current. |
| [`conventions.md`](conventions.md) | Adopter skills-dir convention auto-detection — flat `.claude/skills/<name>/`, the `.claude/skills/<name>` → `.github/skills/<name>/` double-symlink pattern (e.g. apache/airflow), or neither yet. |
| [`overrides.md`](overrides.md) | Agentic-override file management — open / scaffold an override for a framework skill, list existing overrides, help reconcile when the framework changes the underlying skill's structure on upgrade. |

## Golden rules

**Golden rule 1 — never modify the snapshot.** The
`<snapshot-dir>` is a build artefact, gitignored, and **read-
only** from an adopter's perspective. Every modification an
adopter wants must go into `.apache-steward-overrides/` (where
it is *committed* and survives the next `upgrade`). The skill,
and any other framework skill consulting overrides at run-time,
**never** writes to `<snapshot-dir>`. If the user wants to
upstream a framework change, the agent reads the latest
`apache/airflow-steward` `main`, implements the change there,
and opens a PR against the framework repo.

**Golden rule 2 — `.gitignore` keeps the adopter repo clean.**
Three things gitignored in the adopter repo:

- `<snapshot-dir>` (the entire framework snapshot)
- the symlinks `setup-steward adopt` creates in the adopter's
  skills directory (they target the gitignored snapshot, so
  they would dangle in a fresh clone)
- the adopter's own scratch artefacts that other framework
  skills might create (`/tmp/...` style state caches)

**Committed**: this skill (`setup-steward`), the
`.apache-steward-overrides/` directory, the `.gitignore`
entries themselves, any project-doc updates the `adopt`
sub-action makes.

**Golden rule 3 — follow the adopter's existing skills-dir
convention.** Different ASF projects already organise their
`.claude/skills/` differently (see
[`conventions.md`](conventions.md)):

- **flat**: `.claude/skills/<name>/SKILL.md` — directly in the
  Claude Code-discovered location.
- **double-symlinked** (e.g. apache/airflow today): the actual skill
  content lives under `.github/skills/<name>/` and
  `.claude/skills/<name>` is a symlink into it. Claude Code
  discovers via `.claude/skills/`; the user maintains under
  `.github/skills/`.

The `adopt` sub-action detects which pattern is in place and
matches it. **The framework's symlinks land at the same depth
as the adopter's existing skills**, not one level off.

**Golden rule 4 — copy this skill, symlink the rest.** This
skill (`setup-steward`) is the **only** framework skill that
gets copied into an adopter repo. All other framework skills
(`security-issue-import`, `pr-management-triage`, etc.) are
symlinked into the gitignored snapshot. Mixing the two — for
example, copying a security skill — creates a maintenance
hazard: copies drift from the framework's source-of-truth, and
agentic overrides (which assume the framework version is the
one in the snapshot) silently mis-apply.

**Golden rule 5 — agentic overrides are read at run-time.**
Every framework skill that supports overrides starts its run
by checking `.apache-steward-overrides/<this-skill>.md` for
adopter-specific instructions and applying them before
executing the default behaviour. The override file is plain
markdown the agent interprets — no templating engine, no
patch tool. See
[`docs/setup/agentic-overrides.md`](../../../docs/setup/agentic-overrides.md)
for the contract.

## Sub-actions

The skill dispatches by the first positional argument:

| Invocation | Loads | Purpose |
|---|---|---|
| `/setup-steward` (no args) | [`adopt.md`](adopt.md) | First-time adoption (default). |
| `/setup-steward adopt` | [`adopt.md`](adopt.md) | Same as no-arg — explicit form. |
| `/setup-steward upgrade` | [`upgrade.md`](upgrade.md) | Refresh snapshot + reconcile overrides. |
| `/setup-steward verify` | [`verify.md`](verify.md) | Read-only health check. |
| `/setup-steward override <skill>` | [`overrides.md`](overrides.md) | Open / scaffold an override file. |

If the snapshot is missing (no `<snapshot-dir>/`), the skill
treats that as `adopt` regardless of which sub-action was
named — the user has invoked on a repo that has not yet been
adopted, and the right next step is to walk through adoption.

## Inputs

The skill is mostly driven by detection (it reads the adopter
repo's state) but accepts these optional flags:

| Flag | Effect |
|---|---|
| `from:<git-ref>` | Adopt / upgrade from a specific framework `<git-ref>` (branch, tag, or commit SHA) instead of `main`. Useful for testing a framework PR locally before it merges. |
| `skill-families:<list>` | Comma-separated list of skill families to symlink (`security`, `pr-management`). Default on adopt: prompt the user. Default on upgrade: re-symlink the families currently linked. |
| `dry-run` | Show what the skill would do without writing anything. |

## What this skill is NOT for

- Not for installing the secure agent setup (sandbox, hooks,
  pinned tools). That is
  [`setup-isolated-setup-install`](../setup-isolated-setup-install/SKILL.md).
  The two are independent: an adopter can have steward set up
  but no isolated-setup wired (run setup-isolated-setup-install
  to fix), or have isolated-setup wired against a stale
  snapshot (run `setup-steward upgrade`).
- Not for upgrading framework tools installed on the host
  (`bubblewrap`, `socat`, `claude-code` itself). Those go via
  [`setup-isolated-setup-update`](../setup-isolated-setup-update/SKILL.md).
- Not for syncing the user's `~/.claude-config` across
  machines. That is
  [`setup-shared-config-sync`](../setup-shared-config-sync/SKILL.md).
- Not for committing framework changes. Framework PRs go
  against `apache/airflow-steward` directly — the snapshot is
  read-only.

## Failure modes

| Symptom | Likely cause | Remediation |
|---|---|---|
| `/setup-steward verify` reports the snapshot present but the symlinks dangle | adopter ran a `git clone` but not `/setup-steward` after — symlinks are gitignored but persist in their target's absence | run `/setup-steward adopt` (it idempotently re-creates symlinks) |
| `/setup-steward upgrade` surfaces conflicts in `.apache-steward-overrides/<skill>.md` | the framework restructured the skill in a way that invalidates an existing override | open the override file, follow the conflict markers, or invoke `/setup-steward override <skill>` to re-scaffold |
| Worktree off the adopter repo can't find framework skills | worktrees off the adopter don't auto-inherit the gitignored snapshot | the `adopt` sub-action installs a `post-checkout` git hook that re-runs the snapshot install on worktree creation; verify the hook is present (`/setup-steward verify`) |
| `git clone` of an upstream PR sees no framework skills | expected — the snapshot is gitignored, so a fresh clone has no `<snapshot-dir>`. The clone needs `/setup-steward` once before any framework skill is invocable | run `/setup-steward` from the cloned repo |
