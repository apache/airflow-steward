---
name: setup-isolated-setup-install
description: |
  Guide an adopter through the first-time install of the
  framework's secure agent setup — pinned system tools
  (`bubblewrap`, `socat`, `claude-code`), project + user-scope
  `.claude/settings.json` wiring, the `claude-iso` clean-env
  wrapper, and the user-scope `sandbox-bypass-warn` /
  `sandbox-status-line` hooks. Walks every step interactively;
  never auto-runs sudo, shell-rc edits, or settings overwrites.
when_to_use: |
  Invoke when the user says "set up the secure agent setup",
  "first-time install of the secure config", "install the
  secure setup in this tracker", "walk me through the
  secure-agent-setup install", or starts working on a fresh
  adopter clone without secure-config wiring. Also appropriate
  after a fresh OS install / new dev machine where
  `~/.claude/scripts/` is empty. Skip when the secure setup is
  already in place — use `setup-isolated-setup-verify` (to
  confirm completeness) or `setup-isolated-setup-update` (to
  refresh against the framework's latest) instead.
license: Apache-2.0
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory
     <tracker>        → value of `tracker_repo:` in <project-config>/project.md
     <upstream>       → value of `upstream_repo:` in <project-config>/project.md -->

# setup-isolated-setup-install

This skill is the **on-ramp** for adopters who do not yet have the
secure setup running. It is a thin walkthrough wrapper around the
canonical install path documented in
[`docs/setup/secure-agent-setup.md`](../../../docs/setup/secure-agent-setup.md). The
authoritative content lives there; this skill exists so an adopter
can say *"set up the secure agent setup"* in a fresh session and
land in the right step-by-step flow without first reading the
document.

## Adopter overrides

Before running the default behaviour documented
below, this skill consults
[`.apache-steward-overrides/setup-isolated-setup-install.md`](../../../docs/setup/agentic-overrides.md)
in the adopter repo if it exists, and applies any
agent-readable overrides it finds. See
[`docs/setup/agentic-overrides.md`](../../../docs/setup/agentic-overrides.md)
for the contract — what overrides may contain, hard
rules, the reconciliation flow on framework upgrade,
upstreaming guidance.

**Hard rule**: agents NEVER modify the snapshot under
`<adopter-repo>/.apache-steward/`. Local modifications
go in the override file. Framework changes go via PR
to `apache/airflow-steward`.

---

## Snapshot drift

Also at the top of every run, this skill compares the
gitignored `.apache-steward.local.lock` (per-machine
fetch) against the committed `.apache-steward.lock`
(the project pin). On mismatch the skill surfaces the
gap and proposes
[`/setup-steward upgrade`](../setup-steward/upgrade.md).
The proposal is non-blocking — the user may defer if
they want to run with the local snapshot for now. See
[`docs/setup/install-recipes.md` § Subsequent runs and drift detection](../../../docs/setup/install-recipes.md#subsequent-runs-and-drift-detection)
for the full flow.

Drift severity:

- **method or URL differ** → ✗ full re-install needed.
- **ref differs** (project bumped tag, or `git-branch`
  local is behind upstream tip) → ⚠ sync needed.
- **`svn-zip` SHA-512 mismatches the committed
  anchor** → ✗ security-flagged; investigate before
  upgrading.

---
## Golden rules

- **Do not auto-run privilege-elevating commands.** Anything that
  needs `sudo` (apt / dnf installs, system-wide writes) is *printed*
  for the user to copy-paste into their own terminal. The skill
  never invokes `sudo` itself.
- **Do not edit shell rc files without approval.** `~/.bashrc` /
  `~/.zshrc` modifications (sourcing `claude-iso.sh`, the optional
  `alias claude='claude-iso'`) are surfaced as the exact line to
  add; the user pastes it themselves. The skill confirms the rc
  file path with the user first; it does not assume.
- **Do not overwrite an existing settings file silently.** If the
  user already has a project `.claude/settings.json` or a
  user-scope `~/.claude/settings.json`, the skill *diffs* the
  desired merge against the existing file and asks for explicit
  approval before writing. Re-installs / partial-state recoveries
  are common — the skill must not blow away an unrelated
  pre-existing hook or `permissions.ask` rule.
- **Stop on the first failure.** If a step fails (manifest read
  fails, framework path wrong, an existing file conflicts in a way
  the user has not yet decided about), stop and report. Do not
  push past a failure to the next step.

## Up-front confirmations

Before walking any install step, confirm with the user:

1. **OS / distro.** macOS, Ubuntu / Debian (apt), Fedora / RHEL
   (dnf), or Arch / NixOS / other. macOS skips bubblewrap +
   socat (Seatbelt is built-in); Linux installs both per the
   distro shortcut.
2. **Framework checkout path.** The path to the user's local
   `airflow-steward` clone. Required to read
   `tools/agent-isolation/pinned-versions.toml`,
   `.claude/settings.json`, and the
   `tools/agent-isolation/*.sh` scripts. If the user does not
   have a clone, walk them through `git clone` first.
3. **Fresh install or re-install.** For a re-install on a partial
   existing state, the skill must enumerate the existing wiring
   (project settings.json, user settings.json, hooks dir,
   shell rc) before any merge so the user knows what is being
   preserved vs replaced.
4. **Sync repo (optional).** Whether the user maintains a
   private dotfile-style `~/.claude-config` repo per
   [Syncing user-scope config across machines](../../../docs/setup/secure-agent-setup.md#syncing-user-scope-config-across-machines).
   If yes, the skill installs user-scope scripts as **symlinks**
   into `~/.claude-config/scripts/` rather than `cp`-ing into
   `~/.claude/scripts/` — the symlink approach is what makes
   sync push the upgrades to other machines automatically.

## Walk-through

Follow the canonical step list at
[docs/setup/secure-agent-setup.md → Adopter setup → Via a Claude Code prompt](../../../docs/setup/secure-agent-setup.md#via-a-claude-code-prompt).
Each step in that list maps 1:1 to a step in this skill. Do not
re-write the list here — read the doc, follow it, and surface each
sub-step with the user. The doc names are the source of truth; the
skill is the runner.

For the verification step at the end, hand off to the
`setup-isolated-setup-verify` skill rather than re-walking the checklist
inline.

## After the install lands

Suggest two follow-up routines the user can wire later:

- `setup-isolated-setup-verify` — re-run after every Claude Code upgrade
  or settings-file edit, to confirm denials still fire as
  expected. The "did a denial silently turn into an allow?"
  signal is exactly what this skill exists for.
- `setup-isolated-setup-update` — periodic check for framework
  updates, pinned-tool upgrade candidates, and drift between the
  installed user-scope copies and the framework's
  source-of-truth. Recommend a per-Claude-Code-upgrade or
  monthly cadence, whichever comes first.

If the user has the `~/.claude-config` sync repo in place, also
mention `setup-shared-config-sync` for committing + pushing local
modifications to the shared scripts.
