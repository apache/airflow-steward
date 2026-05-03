---
name: setup-steward-upgrade
description: |
  Pull the user's local `airflow-steward` framework checkout to the
  latest `origin/main` and surface what changed — the commits
  pulled, the files touched (with focus on the secure-setup blast
  radius: `.claude/settings.json`, `tools/agent-isolation/`,
  `secure-agent-setup.md`, `secure-agent-internals.md`,
  `pinned-versions.toml`), and the next-step recommendation. Never
  applies user-side propagation itself — that is the job of
  `setup-isolated-setup-update` (drift report) and the framework
  maintainer's manual re-`cp` of any user-scope script copies that
  drifted. Refuses to act if the working tree is dirty or the
  branch has unpushed commits, since both states are signs the
  user has work in flight that a `git pull` could clobber.
when_to_use: |
  Invoke when the user says "upgrade apache-steward", "pull the
  framework to latest", "bring my airflow-steward clone up to
  date", or after Claude Code surfaces something new from the
  framework's release notes. Also appropriate as the entry point
  to a periodic update routine — recommended cadence per
  secure-agent-setup.md is once per Claude Code upgrade or once
  a month, whichever comes first; this skill is the *first* step
  of that routine, with `setup-isolated-setup-update` (read-only drift
  report) and any subsequent re-`cp` / `/setup-shared-config-sync` runs
  following on. Do **not** invoke when the user has uncommitted
  changes in the framework checkout or when they have local
  commits ahead of origin — the skill will refuse and surface
  the state.
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory -->

# setup-steward-upgrade

This skill is the **upstream** half of the framework's update flow.
It moves the user's local `airflow-steward` checkout forward to
`origin/main` and reports what arrived. The downstream half — what
this upgrade means for the user's *installed* secure setup
(user-scope script copies, project `.claude/settings.json`, pinned
tool versions on the host) — is the
[`setup-isolated-setup-update`](../setup-isolated-setup-update/SKILL.md) skill,
which is read-only and runs naturally as the next step.

## Golden rules

- **Refuse on a dirty working tree.** If `git status --short` in
  the framework checkout reports any modified, staged, or
  conflicted files, surface them and stop. A `git pull` on top of
  uncommitted edits is one of the quickest ways to lose work; the
  user is in flight on something and needs to commit / stash it
  themselves before any pull. Do not auto-stash.
- **Refuse on local commits ahead of `origin/main`.** Adopters
  generally consume `airflow-steward` as a read-only checkout —
  modifications happen via PRs that land on `main` upstream, then
  the user's checkout is `git pull`ed. If the user has commits
  ahead of `origin/main`, that is either (a) work in progress for
  a PR they have not pushed, or (b) a local fork they are
  maintaining. Both cases need explicit user direction; the skill
  does not assume.
- **`--ff-only` only.** Use `git pull --ff-only`. Never
  `--rebase`, never a merge commit. The skill is for the simple
  case where the user's checkout is strictly behind upstream;
  anything else is the user's call. If the fast-forward fails
  (history diverged), surface and stop.
- **Show what arrived.** After a successful pull, surface the
  commit list and a per-file change summary, with explicit focus
  on the secure-setup blast radius (`.claude/settings.json`,
  `tools/agent-isolation/`, `secure-agent-setup.md`,
  `secure-agent-internals.md`,
  `tools/agent-isolation/pinned-versions.toml`). The user should
  walk away knowing whether this upgrade has user-side
  follow-through to do.
- **Do not propagate to user-scope.** This skill ends at the
  framework checkout. It does not re-`cp` `claude-iso.sh`,
  `sandbox-bypass-warn.sh`, or `sandbox-status-line.sh` into
  `~/.claude/`. It does not edit any project's
  `.claude/settings.json`. It does not bump installed tool
  versions on the host. All of those are surfaced by the
  follow-on `setup-isolated-setup-update` skill, which is read-only by
  design — the user decides what to apply.

## Walk-through

1. **Locate the framework checkout.** Confirm with the user the
   path to their local `airflow-steward` clone. If they don't
   have one, surface that and stop — they need to `git clone`
   first.

2. **Pre-flight checks.**
   - `git -C <path> status --short` — must be empty. If not, list
     the modified files and stop.
   - `git -C <path> rev-parse --abbrev-ref HEAD` — must be `main`
     (or the local equivalent that tracks `origin/main`). If not,
     name the branch and stop; the user is on a feature branch
     and a pull would be the wrong action.
   - `git -C <path> rev-list --count @{u}..HEAD` — must be `0`.
     If not, surface the local commits and stop.

3. **Fetch + diff against upstream.**
   - `git -C <path> fetch origin` (always, even if behind).
   - `git -C <path> rev-list --count HEAD..@{u}` — if `0`, the
     checkout is already up to date; report and stop.
   - Otherwise, list the commits that will land:
     `git -C <path> log --oneline HEAD..@{u}`.
   - List per-file changes with secure-setup focus:
     `git -C <path> diff --name-status HEAD..@{u}` — call out
     entries under `.claude/settings.json`,
     `tools/agent-isolation/**`, `secure-agent-setup.md`,
     `secure-agent-internals.md`, `pinned-versions.toml` if they
     appear.

4. **Confirm with the user before pulling.** Show the commits
   and the file-touch summary, then ask for explicit OK. The
   skill does not auto-pull on a "looks routine" judgement —
   even a doc-only upgrade can move anchors that the user's
   bookmarks or scripts depend on.

5. **Pull.** `git -C <path> pull --ff-only`. If the fast-forward
   fails for any reason, surface the error and stop.

6. **Post-pull report.** Confirm the new HEAD SHA matches
   `origin/main`. Re-print the commit list (now landed) and the
   file-touch summary with the secure-setup focus.

7. **Hand off to follow-up actions.** Always finish by naming
   the next-step skills the user is likely to want, with explicit
   conditions:

   - **If the framework checkout is a submodule of an adopter
     tracker repo** (the path is
     `<adopter-tracker>/.apache-steward/apache-steward/`), remind
     the user that **the parent tracker now has a stale submodule
     pointer**. Pulling the framework standalone moved the
     framework's `HEAD`, but the parent tracker's index still
     records the previous SHA. The user has two options: (a)
     commit the new pointer in the parent tracker
     (`git -C <tracker> add .apache-steward/apache-steward && git
     commit -m "Bump apache-steward submodule"`), or (b) revert
     the framework checkout to the SHA the parent tracker pins.
     Option (a) is the usual path. Either way, a follow-up
     `git -C <tracker> submodule update --init --recursive` on
     any other clone of the tracker is what makes that clone see
     the new framework. Mention the post-merge hook documented in
     `README.md → Adopting the framework` for users who want this
     automatic. Suggest
     [`setup-steward-verify`](../setup-steward-verify/SKILL.md)
     to confirm the parent tracker's submodule integration is
     still aligned (the skill catches the `+` "submodule HEAD
     ahead of parent index" state directly).

   - **Always after a successful pull**, recommend
     [`setup-isolated-setup-update`](../setup-isolated-setup-update/SKILL.md)
     to surface user-side drift the upgrade may have introduced
     (new `permissions.deny` patterns the user's tracker repo
     hasn't picked up, drift between user-scope `~/.claude/`
     copies and the just-updated framework source-of-truth, a
     pinned-tool version bump that warrants a host-side
     `npm install` / `apt-get install`).

   - **If `tools/agent-isolation/*.sh` files changed in the
     pulled commits AND the user maintains a `~/.claude-config`
     sync repo with copies of those scripts**, recommend
     re-`cp`'ing the updated framework scripts over the
     `~/.claude-config/scripts/` (or
     `~/.claude/agent-isolation/`) copies and then running
     [`setup-shared-config-sync`](../setup-shared-config-sync/SKILL.md) to
     push the propagated changes to the sync remote so other
     machines pick them up.

   - **If `pinned-versions.toml` changed**, name the specific
     tool(s) bumped and remind the user that the host install
     commands in `secure-agent-setup.md → Required tools` may
     now reference newer versions; the user runs the `apt-get`
     / `dnf` / `npm install` themselves (the skill does not
     touch system tools).

   - **If `.claude/settings.json` changed**, name the kinds of
     changes (new `denyRead`, new `allowedDomains`, new
     `permissions.ask` entry) and remind the user that adopter
     tracker repos copying the framework's settings will need a
     manual merge — the skill does not auto-merge into adopter
     repos.

## What this skill is NOT for

- Not for upgrading a tracker repo (the user's own private
  repo where they consume the framework). Tracker-repo updates
  are normal `git pull` operations the user does themselves.
- Not for upgrading installed tools (`bubblewrap`, `socat`,
  `claude-code`). Those bumps happen on the host via the
  package manager, surfaced by `check-tool-updates.sh` and
  approved per the
  [Bumping a pinned version](../../../secure-agent-setup.md#bumping-a-pinned-version)
  flow.
- Not for syncing user-scope edits to `~/.claude-config`. That
  is `setup-shared-config-sync`'s job.

## Failure modes

- **Working tree dirty.** Stop. Surface `git status` output. The
  user commits / stashes themselves before re-invoking.
- **Local commits ahead of upstream.** Stop. Surface the commit
  list. The user pushes their PR / decides what to do, then
  re-invokes.
- **Not on `main` (or tracking branch).** Stop. Surface the
  current branch. The user switches branches themselves.
- **`fetch` fails.** Network or auth issue. Stop and surface.
  The skill does not retry.
- **`pull --ff-only` fails (diverged history).** This means
  someone force-pushed `main` upstream, or the user's local
  `main` has untracked commits. Stop and surface. The user
  resolves themselves; the skill never `--force`-pulls or
  resets.
