<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [`tools/agent-isolation/` — secure agent setup helpers](#toolsagent-isolation--secure-agent-setup-helpers)
  - [Files](#files)
  - [Usage at a glance](#usage-at-a-glance)
  - [Referenced by](#referenced-by)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# `tools/agent-isolation/` — secure agent setup helpers

This directory ships the moving pieces the framework's
[`secure-agent-setup.md`](../../secure-agent-setup.md) document
references. It is not a Python project (unlike the sibling tools
under `tools/vulnogram/` and `tools/gmail/oauth-draft/`) — these are
plain shell scripts plus a TOML manifest of pinned upstream
versions.

## Files

| File | Purpose |
|---|---|
| [`pinned-versions.toml`](pinned-versions.toml) | Machine-readable manifest of pinned upstream versions for `bubblewrap`, `socat`, and `claude-code`. Each entry carries a `released` date that satisfies the framework's 7-day cooldown convention. |
| [`check-tool-updates.sh`](check-tool-updates.sh) | Reads the manifest and reports upstream releases that are newer than the pin AND have themselves aged past the 7-day cooldown. Side-effect-free — no installs, no edits, no PRs. |
| [`claude-iso.sh`](claude-iso.sh) | Shell function to launch Claude Code with `env -i` and a tiny passthrough list, stripping every credential-shaped environment variable from the parent shell. The framework's "layer 0" of the secure setup. |
| [`sandbox-bypass-warn.sh`](sandbox-bypass-warn.sh) | Claude Code `PreToolUse` hook (Bash matcher). Prints a bold-red banner to stderr whenever the model invokes the Bash tool with `dangerouslyDisableSandbox: true`. Belt-and-braces visibility for the sandbox-bypass permission prompt. Recommended user-scope (`~/.claude/settings.json`) so it fires across every session on the host. |
| [`sandbox-status-line.sh`](sandbox-status-line.sh) | Claude Code `statusLine` helper. Renders `<model> [sandbox]` (green) or `<model> [NO SANDBOX]` (bold red) based on `sandbox.enabled` in the active `settings.json`, so the terminal footer always shows whether the current session is sandboxed. Recommended user-scope. |

## Usage at a glance

```bash
# Initial install (read pinned-versions.toml for the version pin):
sudo apt-get install --no-install-recommends bubblewrap=0.11.1-* socat=1.8.1.1-*
npm install -g --no-save @anthropic-ai/claude-code@2.1.117

# Source the wrapper into your shell:
source /path/to/airflow-steward/tools/agent-isolation/claude-iso.sh

# Optional: make claude-iso the default `claude` (see secure-agent-setup.md
# for the trade-off — the alias also strips env in non-tracker sessions):
alias claude='claude-iso'

# Launch a session with no inherited credentials:
cd ~/code/<tracker>
claude-iso

# Periodically (or via /schedule weekly), check for upgrade candidates:
bash /path/to/airflow-steward/tools/agent-isolation/check-tool-updates.sh
```

## Referenced by

- [`../../secure-agent-setup.md`](../../secure-agent-setup.md) —
  the user-facing setup document. Read that first.
- [`../../.claude/settings.json`](../../.claude/settings.json) — the
  framework's own dogfooded secure config. Adopters scaffold their
  own version from the example block in `secure-agent-setup.md`.
