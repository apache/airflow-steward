---
name: setup-verify-secure-config
description: |
  Walk the verification checklist documented in
  `secure-agent-setup.md` and report ✓ done / ✗ missing / ⚠ partial
  for each piece of the secure agent setup — project + user-scope
  `settings.json` wiring, hook scripts present + executable,
  `claude-iso` sourced, pinned tool versions installed at the
  pinned versions, status-line state in this session, and the three
  denial commands that prove the sandbox + permissions + clean-env
  layers are actually firing. Read-only — never modifies anything.
when_to_use: |
  Invoke when the user says "verify my secure setup", "is my
  secure config done?", "check that the secure agent setup is
  installed", "did setup work?", or after running
  `setup-secure-config` to confirm the install landed completely.
  Also appropriate as a routine — after every Claude Code upgrade,
  after every project / user-scope `settings.json` edit, and any
  time a previously-blocked Bash call appears to have succeeded
  (the "did a denial silently turn into an allow?" canary). Cheap
  to re-run; never destructive.
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory -->

# setup-verify-secure-config

This skill is the **assertion** layer over the secure setup. It
runs the checklist documented in
[`secure-agent-setup.md` → Verification → Via a Claude Code prompt](../../../secure-agent-setup.md#via-a-claude-code-prompt-1)
and reports each check's status to the user with concrete evidence
(file paths, command output, version strings).

## Golden rules

- **Read-only.** This skill does not edit any file, copy any
  script, install any package, or modify any settings. If a check
  surfaces a missing or misconfigured piece, surface the gap and
  point at the install path (`setup-secure-config` for a missing
  install, `setup-update-secure-config` for drift); do not auto-fix.
- **Report every check, even on early failure.** Do not stop at
  the first ✗ — the value of the report is in the full picture.
  If check 3 fails, continue to checks 4 / 5 / 6 / 7 anyway and
  surface every gap so the user can address them in one round.
- **Distinguish ✗ (missing) from ⚠ (variant or drift).** A missing
  hook script is ✗. A user installing the doc-allowed "richer
  custom statusLine" path that embeds the framework's
  sandbox-prefix logic into a larger script is ⚠ (the by-name
  helper is not present, but the equivalent functionality is). Use
  ⚠ for any *intentional* variation from the doc default; ✗ only
  for genuine gaps.
- **Surface evidence.** Each check's report line names the file
  path, the version string, the command output, the
  `sandbox.enabled` value — never just "✓" or "✗" alone.

## The 7 checks

The canonical list lives in
[secure-agent-setup.md → Verification → Via a Claude Code prompt](../../../secure-agent-setup.md#via-a-claude-code-prompt-1).
Walk each in order:

1. Project `.claude/settings.json` shape — `sandbox.enabled: true`,
   `permissions.deny`, `permissions.ask`, `sandbox.network.allowedDomains`.
2. User-scope `~/.claude/settings.json` wiring — `PreToolUse`
   `Bash` matcher → `sandbox-bypass-warn.sh`, `statusLine` →
   `sandbox-status-line.sh` (or a custom statusline script that
   embeds the framework's prefix logic — that is the doc-allowed
   variant; report ⚠).
3. Hook scripts present + executable — both
   `~/.claude/scripts/sandbox-bypass-warn.sh` and
   `~/.claude/scripts/sandbox-status-line.sh`. Symlinks into a
   `~/.claude-config` sync repo are equivalent to direct files;
   resolve the link target and check that.
4. `claude-iso` shell function defined + sourced. The grep
   pattern is the source line in `~/.bashrc` / `~/.zshrc`. Check
   whether `alias claude='claude-iso'` is set; report it as a
   note (it is optional per the doc).
5. Pinned tool versions installed match
   `tools/agent-isolation/pinned-versions.toml`. On macOS,
   skip `bubblewrap` and `socat` (Seatbelt is built-in); only
   check `claude-code`. Report drift in either direction —
   newer-than-pin or older-than-pin — as ⚠.
6. Status-line prefix in this session is `[sandbox]`, not
   `[NO SANDBOX]`. Resolve the precedence:
   `<cwd>/.claude/settings.local.json` →
   `<cwd>/.claude/settings.json` →
   `~/.claude/settings.local.json` →
   `~/.claude/settings.json`; report the `sandbox.enabled` value
   from each.
7. Denial commands actually deny. **Important: run each as a
   standalone Bash invocation**, not as a chained pipeline —
   `permissions.deny` patterns match only on the *first* command
   of a Bash tool call, so a chained `curl` later in the
   pipeline can slip past on macOS (where there is no socat
   network proxy as a backstop). The three commands are:
   - `cat ~/.aws/credentials` — should deny with
     `Operation not permitted` (Seatbelt) or
     `No such file or directory` (bubblewrap).
   - `echo $AWS_ACCESS_KEY_ID` — should print empty (claude-iso
     stripped the env).
   - `curl https://example.com` — should deny at the
     permission-prompt layer
     (`Permission to use Bash with command curl … has been denied`).

## After the report

If every check is ✓, say so explicitly and stop — no further
suggestion needed.

If anything is ✗ or ⚠, suggest the appropriate follow-up skill
without invoking it:

- ✗ on checks 1 / 2 / 3 / 4 → `setup-secure-config` (missing
  install pieces).
- ⚠ on check 5 (pinned-version drift) or any user-scope script
  copy that is older than the framework's source-of-truth →
  `setup-update-secure-config`.
- The user-scope script copies live under `~/.claude-config/`
  for users who maintain that sync repo; uncommitted local edits
  there → `setup-sync-shared-config`.
