<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# worktree-init — share the main checkout's snapshot from a worktree

`adopt` and `upgrade` are **main-checkout-only**. A new git
worktree of an already-adopted tracker repo gets the framework
state by **symlinking** its `.apache-steward/` directory to the
main checkout's snapshot, rather than maintaining its own copy.
One snapshot on disk, one upgrade source, every worktree always
current.

This sub-action is the worktree counterpart of `adopt`:

- **`adopt`** runs in the main checkout, fetches the snapshot,
  writes both lock files, and wires up symlinks.
- **`worktree-init`** runs in a worktree, validates the main is
  adopted, and points the worktree's `<snapshot-dir>` at the
  main's. Nothing is fetched; no lock files are written.

The skill is idempotent: re-running on a worktree that already
has the right symlink is a no-op.

## Step 0 — Pre-flight

1. **Confirm we are in a git worktree, not the main checkout.**
   Compare `git rev-parse --git-dir` against
   `git rev-parse --git-common-dir`. They are equal in the main
   checkout and different in a worktree. If equal, stop:

   > *"You appear to be in the main checkout (`<path>`).
   > `worktree-init` only runs in a worktree. Use
   > `/setup-steward` (or `/setup-steward upgrade`) here
   > instead."*

2. **Resolve the main checkout's path.** Take
   `$(cd "$(git rev-parse --git-common-dir)" && pwd)`; the
   parent of that is the main checkout's working tree. Pin
   the result as `<main>` for the rest of this flow.

3. **Confirm the main checkout is adopted.** Check that
   `<main>/.apache-steward/` exists and that
   `<main>/.apache-steward.lock` exists. If either is missing,
   stop:

   > *"The main checkout at `<main>` is not adopted yet. From
   > the main checkout: `cd <main> && /setup-steward`. Re-run
   > `worktree-init` here once that is complete."*

4. **Inspect the worktree's `<snapshot-dir>` state.** Four
   possibilities, each handled below:

   | Current state | Action |
   |---|---|
   | Missing | Step 1 — create the symlink. |
   | Symlink to `<main>/.apache-steward/` | No-op. Surface "already wired" and stop. |
   | Symlink to **something else** | Step 1 with a move-aside warning. The skill backs the existing link up, names what it pointed at, and asks the user to confirm before replacing. |
   | Regular directory (per-worktree snapshot from before this convention) | Step 1 with a move-aside warning. Back up the directory to `.apache-steward.bak.<timestamp>` and create the symlink. **Do not** `rm -rf` without confirmation — the directory may hold uncommitted local edits the operator wants to preserve before the framework standardised on snapshot-from-main. |

## Step 1 — Create the symlink

```bash
ln -s <main>/.apache-steward <worktree>/.apache-steward
```

Then verify the chain end-to-end:

- `ls -la <worktree>/.apache-steward` returns a symlink pointing
  at `<main>/.apache-steward`.
- `ls <worktree>/.apache-steward/.claude/skills/` lists the
  same skills as `ls <main>/.apache-steward/.claude/skills/`.
- Pick any committed skill symlink (e.g.
  `<worktree>/.claude/skills/security-issue-sync/SKILL.md`) and
  confirm `readlink -f` resolves it into
  `<main>/.apache-steward/...` rather than dangling.

## Step 2 — Recap

Print a short summary:

- The symlink that was just created.
- The main checkout's resolved path.
- The framework version the main is pinned at (read from
  `<main>/.apache-steward.lock`).
- A reminder: `upgrade` from the main, not from the worktree.

## Inputs

| Flag | Effect |
|---|---|
| `--force` | Replace an existing `<snapshot-dir>` (symlink or regular dir) without the confirmation prompt. Skips the move-aside backup. Use only when you are sure the existing state holds nothing worth keeping. |
| `dry-run` | Show what the skill would do without writing anything. |

## Adopter overrides

This sub-action does **not** touch `.apache-steward-overrides/`.
That directory is committed in the tracker repo and is
worktree-local by design — different branches may carry
different overrides. Symlinking it would conflate branches.

## What this sub-action is NOT for

- **Fetching the framework.** Use `adopt` in the main checkout
  first.
- **Upgrading the framework version.** Use `upgrade` in the
  main checkout; the symlink means every worktree sees the
  refreshed snapshot immediately.
- **Auto-running on `git worktree add`.** Adopters who want
  automatic worktree initialisation can wrap `git worktree add`
  with a script that calls `/setup-steward worktree-init` —
  the framework does not install that wrapper.

## Failure modes

| Symptom | Likely cause | Fix |
|---|---|---|
| Step 0 step 3 stops with "main checkout not adopted" | The main has never run `adopt`. | `cd <main> && /setup-steward`, then re-run `worktree-init` here. |
| `worktree-init` runs but skills still fail to resolve | The `<adopter-skills-dir>/<skill>` symlinks are missing from this worktree's commit (the worktree was branched from before `adopt` ran on main). | Re-run `worktree-init` from main's `adopt` flow afterwards, or `git merge` / `git rebase` the branch carrying the symlink commits. |
| `<snapshot-dir>` is a regular directory and `--force` is not passed | A previous worktree snapshot is still on disk. | Re-run the skill, accept the move-aside prompt, then optionally inspect `.apache-steward.bak.<timestamp>` for any non-snapshot content before deleting. |
