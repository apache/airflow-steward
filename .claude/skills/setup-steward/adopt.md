<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# adopt — first-time install of apache-steward into an adopter repo

The default sub-action when the user says "adopt apache-steward".
Walks through detection, snapshot install, and the small set of
adopter-side artefacts that need to land on disk.

## Inputs

- `from:<git-ref>` — adopt from a specific framework `<git-ref>`
  (default: `main` of `apache/airflow-steward`).
- `skill-families:<list>` — comma-separated families to symlink
  in (`security`, `pr-management`). Default: prompt the user.

## Step 0 — Pre-flight

1. Confirm we are in a git repo (`git rev-parse --show-toplevel`).
   If not, surface and stop — the user opened the agent in the
   wrong directory.
2. Confirm we are **not** in `apache/airflow-steward` itself
   (read `git remote get-url origin` and refuse if it resolves
   to the framework). Adopting the framework into itself is a
   no-op the user did not intend.
3. Detect the adopter's existing skills-dir convention by
   following [`conventions.md`](conventions.md). The result
   pins which directory the framework symlinks land in
   (`<adopter-skills-dir>` from here on).

## Step 1 — Pick the skill families

If `skill-families:` was passed on the invocation, use those
verbatim. Otherwise, present the families to the user and let
them choose:

- **`security`** — eight skills for security-issue handling
  (`security-issue-import`, `security-issue-sync`,
  `security-cve-allocate`, `security-issue-fix`, etc.).
  Maintainer-only; not useful unless the project has a
  security tracker.
- **`pr-management`** — three skills for maintainer-facing PR
  queue work (`pr-management-triage`,
  `pr-management-stats`, `pr-management-code-review`).
- **`setup`** *(implicit)* — the `setup-isolated-setup-*`,
  `setup-steward-*`, `setup-shared-config-sync` skills. The
  `setup` family is always installed because the snapshot
  carries it; the symlinks are wired up regardless of the
  user's other family picks.

Show the user a short description of each family and ask which
to install. Default to whichever family the user named in
their initial "adopt" request (e.g. *"adopt apache-steward for
PR triage"* → `pr-management`).

## Step 2 — Download the snapshot

Place the snapshot at `<repo-root>/.apache-steward/`. Use the
WIP path for now (a `--depth=1` git checkout of the framework's
`main` branch). The signed-tarball path
(e.g. `https://downloads.apache.org/airflow/...` once ASF official
releases ship per
[release-policy](https://www.apache.org/legal/release-policy.html))
is a future upgrade; both paths produce the same on-disk
shape.

```bash
# WIP path — works today
git clone --depth=1 \
  --branch <git-ref-or-main> \
  https://github.com/apache/airflow-steward.git \
  .apache-steward
```

If `<repo-root>/.apache-steward/` already exists with content,
the user is in upgrade territory — refuse and suggest
`/setup-steward upgrade` instead. (Idempotent re-run after a
*partial* adopt is fine — see Step 6.)

Pin the snapshot version into a small `.apache-steward.lock`
file at the repo root (committed) — record the source URL,
the resolved commit SHA, and the date. The `verify` and
`upgrade` sub-actions read this file.

```text
# .apache-steward.lock (committed)
source: https://github.com/apache/airflow-steward.git
ref: main
commit: <SHA>
fetched: <ISO-8601 date>
```

## Step 3 — `.gitignore` entries

Add (if not already present) to `<repo-root>/.gitignore`:

```text
# apache-steward — gitignored snapshot of the framework, refreshed
# by the setup-steward skill. The snapshot is a build artefact, not
# source. To re-create: /setup-steward (in your agent of choice).
/.apache-steward/

# Symlinks the setup-steward skill creates into the snapshot. They
# would dangle on a fresh clone before /setup-steward is run.
/.claude/skills/security-*
/.claude/skills/pr-management-*
/.claude/skills/setup-isolated-setup-*
/.claude/skills/setup-steward-*
/.claude/skills/setup-shared-config-sync
# ...mirror the same patterns under .github/skills/ if the adopter
# uses the double-symlinked convention (see conventions.md).
```

Show the diff to the user before writing. The `setup-steward`
skill itself (`*/setup-steward/`) is **not** gitignored — it
is committed.

## Step 4 — Wire up the framework-skill symlinks

For each skill family the user picked plus the `setup` family,
walk the snapshot's `.apache-steward/.claude/skills/` and create
a gitignored symlink for every matching skill at
`<adopter-skills-dir>/<skill>` → relative path into
`.apache-steward/.claude/skills/<skill>/`.

If the adopter uses the double-symlinked convention
(`.claude/skills/<n>` → `.github/skills/<n>/` per
[`conventions.md`](conventions.md)), create both layers — the
inner one in `.github/skills/` points at the snapshot, the
outer `.claude/skills/` points at the inner.

**Never overwrite an existing committed skill** of the same name.
If the adopter repo already has e.g. `.github/skills/pr-triage`
(an old-name in-repo copy), surface the conflict and stop. The
user resolves manually — likely by deleting the stale copy and
re-running.

Show the symlinks the skill is about to create, ask the user
to confirm, then create them.

## Step 5 — Scaffold `.apache-steward-overrides/`

Create `<repo-root>/.apache-steward-overrides/` (directory) if
it doesn't exist, with a small `README.md` inside that explains
the contract:

```markdown
# apache-steward overrides

Agent-readable instructions that **override** specific steps or
behaviours of the apache-steward framework's skills, scoped to
this adopter repo. Each override file is named after the
framework skill it modifies (e.g. `pr-management-triage.md`
overrides the `pr-management-triage` skill).

The framework skills consult this directory at run-time before
executing default behaviour. See
[`docs/setup/agentic-overrides.md`](https://github.com/apache/airflow-steward/blob/main/docs/setup/agentic-overrides.md)
in the framework for the full contract.

**Hard rule**: never modify the snapshot under
`<repo-root>/.apache-steward/`. Local mods go here. Framework
changes go via PR to `apache/airflow-steward`.
```

This directory is **committed** (the whole point is for
overrides to ship with the adopter repo).

## Step 6 — Worktree-aware post-checkout hook

Install a `post-checkout` git hook at
`<repo-root>/.git/hooks/post-checkout` that re-creates the
gitignored symlinks if a fresh worktree is checked out off
this repo. (The snapshot itself is gitignored and won't follow
the worktree, but the hook keeps the symlink shape consistent.)

The hook is a one-liner that re-invokes
`/setup-steward verify --auto-fix-symlinks` against the new
worktree path.

Surface the hook content to the user before writing.

## Step 7 — Project doc updates

Add (or extend) a brief paragraph in the adopter's `README.md`
or `CONTRIBUTING.md` (whichever already mentions agents /
skills) noting that this repo adopts apache-steward via the
snapshot mechanism, and pointing at:

- [`apache-steward`'s top-level README](https://github.com/apache/airflow-steward) for the framework's overview;
- the local `.apache-steward-overrides/` for adopter-specific
  modifications.

Surface the doc diff to the user before writing.

## Step 8 — Sanity check

Run [`verify.md`](verify.md)'s checklist as a final step. Every
check should be ✓ before the skill reports success.

## Output to the user

A summary of what was written:

```text
✓ Snapshot installed at .apache-steward/ (commit <SHA>)
✓ .gitignore updated (.apache-steward/, .claude/skills/security-*, ...)
✓ Symlinks created:
  .claude/skills/security-issue-import → .apache-steward/.claude/skills/security-issue-import/
  .claude/skills/security-issue-sync → ...
  ...
✓ .apache-steward-overrides/ scaffold created (committed)
✓ post-checkout hook installed
✓ README.md updated with adoption note

Committed (you'll see in `git status`):
  .gitignore
  .apache-steward.lock
  .apache-steward-overrides/README.md
  .claude/skills/setup-steward/   (this skill itself)
  README.md (or CONTRIBUTING.md)

Gitignored (do NOT commit):
  .apache-steward/
  .claude/skills/security-*
  .claude/skills/pr-management-*  (depending on family pick)
  ...
```

Then suggest the user `git add` the committed files and open a
PR.

## Failure modes

- **Existing `<repo-root>/.apache-steward/`** → suggest
  `/setup-steward upgrade`.
- **Existing committed skill conflicts with a framework skill
  symlink** → stop, name the conflict, let the user resolve.
- **Network failure on the snapshot download** → stop, surface
  the curl/git error. The user retries.
- **`.gitignore` already mentions `.apache-steward/` but no
  snapshot is present** → either a partial adopt or a manual
  cleanup. Re-run is safe; the skill detects this and proceeds.
