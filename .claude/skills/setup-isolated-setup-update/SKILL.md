---
name: setup-isolated-setup-update
description: |
  Surface drift between the user's installed secure agent setup and
  the framework's latest. Reports framework-checkout updates
  (`git pull` on `airflow-steward`), pinned-tool upgrade candidates
  (`bubblewrap`, `socat`, `claude-code` newer than the manifest's
  7-day-cooldown floor), drift between the user-scope script
  copies (`~/.claude/scripts/`, `~/.claude/agent-isolation/`) and
  the framework's source-of-truth, and any newly-allowed denial
  command that should still be denied. Read-only — surfaces
  candidates and diffs, never auto-applies. The user decides what
  to update.
when_to_use: |
  Invoke when the user says "update secure setup", "check for
  secure-config drift", "is my setup at the framework's latest?",
  "should I bump the pinned tools?", or after a Claude Code
  upgrade / a substantial tracker-repo merge / when a previously
  blocked Bash call now appears to succeed. Recommended cadence
  per the doc: once per Claude Code upgrade or once a month,
  whichever comes first. Cheap to re-run; never destructive.
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory -->

# setup-isolated-setup-update

This skill is the **drift report** for an already-installed secure
setup. It walks the canonical update-check at
[`secure-agent-setup.md` → Keeping the setup updated → Via a Claude Code prompt](../../../secure-agent-setup.md#via-a-claude-code-prompt-2)
and surfaces what is older / newer / has drifted, without applying
any change.

## Golden rules

- **Read-only.** This skill does not bump the manifest, does not
  edit `~/.claude/scripts/`, does not `git pull`, does not
  `npm install -g`, does not modify the user's shell rc. It
  reports drift and points at the doc / the install skill;
  the user runs the actual updates by hand or by re-invoking
  `setup-isolated-setup-install` for the touched piece.
- **Surface upstream changelog links.** For every pinned-tool
  upgrade candidate, include the upstream changelog / release-
  notes URL so the user can read the diff before deciding. A
  bump is not a foregone conclusion — the framework's policy is
  "wait for a feature you actually want or a security fix",
  not "always run latest".
- **Distinguish framework changes from local drift.** "The
  framework's `tools/agent-isolation/claude-iso.sh` has new
  comments" is a *framework update* (resolved by `git pull`).
  "The user's `~/.claude/agent-isolation/claude-iso.sh` no longer
  matches the framework's copy" is *local drift* (resolved by
  re-`cp` or, for sync-repo users, by syncing the framework
  changes into `~/.claude-config/scripts/`). Report each
  separately.
- **Re-verify after surfacing the drift.** Run the same denial
  checks `setup-isolated-setup-verify` runs (one Bash invocation per
  command, not chained), so a regression that turned a deny into
  an allow shows up as part of the update report. A *passing*
  verification at the end of an update report is the signal that
  no surprise allow was introduced by something that already
  drifted.

## What to check

The canonical step list is in
[secure-agent-setup.md → Keeping the setup updated → Via a Claude Code prompt](../../../secure-agent-setup.md#via-a-claude-code-prompt-2).
Walk each:

1. **Framework checkout.** `cd` into the user's `airflow-steward`
   clone, `git fetch origin main`, report what changed under
   `tools/agent-isolation/`, `.claude/settings.json`, and
   `secure-agent-setup.md` since the local checkout was last
   updated. Print the `git pull --ff-only` command for the user
   to run; do not run it.
2. **Pinned upstream tools.** Run
   `tools/agent-isolation/check-tool-updates.sh` and surface every
   upgrade candidate (`bubblewrap`, `socat`, `claude-code`) that
   has aged past the framework's 7-day cooldown. Include the
   upstream changelog link for each. Do not bump the manifest;
   that is a separate
   [Bumping a pinned version](../../../secure-agent-setup.md#bumping-a-pinned-version)
   PR by hand.
3. **User-scope script-copy drift.** For every user-scope file
   the doc tells the adopter to install
   (`~/.claude/scripts/sandbox-bypass-warn.sh`,
   `~/.claude/scripts/sandbox-status-line.sh` or whatever the
   user's actual statusLine command resolves to,
   `~/.claude/agent-isolation/claude-iso.sh` for the global
   wrapper install), `diff` the user copy against the framework's
   source-of-truth in `tools/agent-isolation/`. Report any drift
   as a unified diff; do not re-`cp`.
4. **Settings.json shape drift.** Diff the user's project
   `.claude/settings.json` against the framework's dogfooded
   one — the framework occasionally adds new `denyRead` paths
   (a credential type the team newly cares about), new
   `allowedDomains` entries, new `permissions.deny` patterns
   for newly-discovered exfiltration paths. Report new entries
   the user does not have; do not auto-merge.
5. **Re-verify.** Run the three denial commands as standalone
   Bash invocations (not chained — see
   [setup-isolated-setup-verify](../setup-isolated-setup-verify/SKILL.md) for
   why). Report any newly-allowed call as a regression that
   warrants attention.

## After the report

If everything is in sync and verification still passes, say so
explicitly and stop.

If something is out-of-date or has drifted, name the concrete
follow-up:

- Framework checkout behind → run
  [`setup-steward-upgrade`](../setup-steward-upgrade/SKILL.md),
  which performs the `git pull --ff-only` after the same
  pre-flight checks this skill recommends, surfaces what
  arrived, and reminds the user to handle the parent-tracker
  submodule pointer if applicable.
- Pinned-tool upgrade candidate worth adopting → manifest bump PR
  per [Bumping a pinned version](../../../secure-agent-setup.md#bumping-a-pinned-version).
- User-scope script drift → re-`cp` from the framework checkout,
  or — if the script lives in `~/.claude-config/` and the user
  wants the change propagated to other machines — invoke
  `setup-shared-config-sync` to commit + push.
- Settings.json shape drift → the user merges the new
  framework block into their tracker's `.claude/settings.json`
  by hand (the section to copy from is documented in
  [The framework's own `.claude/settings.json`](../../../secure-agent-setup.md#the-frameworks-own-claudesettingsjson)).
- A previously-blocked denial command now succeeds → stop and
  surface as a regression, not a routine update; the user
  should investigate before bumping anything.
