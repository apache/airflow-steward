<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# verify — read-only health check of the steward integration

Confirms the framework is wired in correctly so the rest of
the framework's skills resolve from the right paths. Read-only
— never modifies anything; surfaces gaps and remediation
commands.

## Inputs

- `--auto-fix-symlinks` — *exception to read-only*. If the
  snapshot is present but symlinks are missing or dangling,
  recreate them. Used by the post-checkout hook
  ([`adopt.md` Step 6](adopt.md)) on a fresh worktree where
  the gitignored symlinks didn't follow the checkout.

## Pre-flight

1. `git rev-parse --show-toplevel` — must succeed; we need a
   repo root to resolve relative paths.
2. Read `git remote get-url origin`. If it resolves to
   `apache/airflow-steward` (or a fork of), refuse — this
   skill is for repos that *adopt* the framework, not for
   the framework itself.
3. If `<repo-root>/.apache-steward.lock` is missing, the
   repo is not adopted. Surface and stop with a pointer at
   `/setup-steward adopt`.

## The checks

Run all checks even on early failure (a missing snapshot at
check 1 doesn't tell us anything about the override
directory or doc updates — surface every check).

### 1. Snapshot present + intact

`<repo-root>/.apache-steward/` exists, is a directory, and
contains the expected top-level files (`README.md`,
`AGENTS.md`, `.claude/skills/`, `tools/`).

- ✗ if missing → run `/setup-steward upgrade` to re-fetch
  (it gracefully handles the recover-snapshot case when the
  lock file exists but the snapshot doesn't).
- ✗ if missing top-level files → snapshot is corrupted; same
  remediation.

### 2. Snapshot pinned to a real commit

`<repo-root>/.apache-steward.lock` parses, the recorded
`commit:` SHA matches `git -C .apache-steward rev-parse HEAD`.

- ⚠ if mismatch — somebody modified the snapshot manually.
  Suggest `/setup-steward upgrade` to re-pin or `git -C
  .apache-steward checkout <locked-sha>` to revert.

### 3. `.gitignore` correctly excludes the snapshot + symlinks

Check that the entries from
[`adopt.md` Step 3](adopt.md) are present in
`<repo-root>/.gitignore`. The snapshot path
`/.apache-steward/` is **required**; the symlink patterns are
**recommended** (otherwise a fresh clone may try to commit
dangling symlinks).

- ✗ if `/.apache-steward/` is not gitignored — the snapshot
  is at risk of being accidentally committed; remediation:
  add the line.
- ⚠ if symlink patterns are not gitignored.

### 4. Symlinks point at live framework skills

For each symlink under `<adopter-skills-dir>` that resolves
into `.apache-steward/.claude/skills/<name>/`:

- ✓ if the target exists.
- ✗ if dangling (target deleted or snapshot missing).
  Remediation: `/setup-steward adopt` (idempotent re-run) or
  this same skill with `--auto-fix-symlinks`.

For each framework skill in the snapshot that is **not**
symlinked in the adopter — surface as ⚠ with the family
classification (`security`, `pr-management`, `setup`). The
user may have intentionally not picked that family; the
warning prompts a decision.

### 5. `.apache-steward-overrides/` exists + has the README

`<repo-root>/.apache-steward-overrides/` is a directory with
the `README.md` scaffold from
[`adopt.md` Step 5](adopt.md).

- ✗ if missing → `/setup-steward adopt` (idempotently
  re-creates).
- ⚠ if present but `README.md` is missing — the directory
  may have been hand-created. Suggest re-running
  `/setup-steward adopt`.

### 6. The `setup-steward` skill itself is up to date

Compare the adopter-side committed `setup-steward` skill
against the snapshot's `.apache-steward/.claude/skills/setup-steward/`.

- ✓ if same content.
- ⚠ if different — the adopter's committed copy has drifted.
  Suggest re-copying from the snapshot. The user may have
  intentional local tweaks; surface as ⚠ not ✗.

### 7. Post-checkout hook installed

`<repo-root>/.git/hooks/post-checkout` exists, is executable,
and contains the `setup-steward verify --auto-fix-symlinks`
recipe.

- ⚠ if missing — strictly optional, but worktrees off this
  repo will need a manual `/setup-steward verify
  --auto-fix-symlinks` after checkout. Print the install
  recipe.

### 8. Project documentation mentions the framework

`<repo-root>/README.md` (or another committed doc the
adopter picked) mentions the steward adoption with a link
into the framework. Cheap to skip if absent — surface as
⚠ only.

## After the report

If every check is ✓ (or ⚠ on items the adopter has
intentionally opted out of), say so explicitly and stop.

If anything is ✗, end the report with a concrete next-step
list, ordered most → least urgent:

- ✗ on check 1 → `/setup-steward upgrade` (re-fetches).
- ✗ on check 4 → `/setup-steward verify
  --auto-fix-symlinks` (cheap; no-op when symlinks already
  correct).
- ✗ on check 5 → `/setup-steward adopt` (idempotent
  re-create).
- All other ✗ / ⚠ → name the gap, give the one-line
  remediation.
