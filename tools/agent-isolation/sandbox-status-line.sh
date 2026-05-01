#!/usr/bin/env bash
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# sandbox-status-line.sh — Claude Code statusLine helper.
#
# Renders one line for the terminal footer that always shows whether
# Claude Code's filesystem/network sandbox is active in the current
# session. Designed to make a session that is *not* sandboxed
# obvious at a glance, so it cannot drift unnoticed for hours.
#
# Output:
# - "<model> [sandbox]"   — green, when the active settings.json
#                           sets `"sandbox": { "enabled": true }`.
# - "<model> [NO SANDBOX]" — bold red, otherwise.
#
# Lookup order for `sandbox.enabled` (most-specific first, matches
# Claude Code's settings precedence):
#   1. <workspace.current_dir>/.claude/settings.local.json
#   2. <workspace.current_dir>/.claude/settings.json
#   3. ~/.claude/settings.local.json
#   4. ~/.claude/settings.json
# First file with `.sandbox.enabled` set (true *or* false) wins. The
# `/sandbox` slash command persists its toggle to project-scope
# `settings.local.json`, so reading that file is what makes the prefix
# update after an in-session toggle.
#
# Caveat — the script reads settings *files*, not the live runtime
# state. CLI flags (`--bypass-permissions`, `--no-sandbox`) are not
# visible here. Pair with the sibling `sandbox-bypass-warn.sh`
# PreToolUse hook for a per-call signal.
#
# Wiring (user-scope, applies to every session on the host):
#
#   {
#     "statusLine": {
#       "type": "command",
#       "command": "~/.claude/scripts/sandbox-status-line.sh"
#     }
#   }
#
# See `secure-agent-setup.md` → "Sandbox-state status line" for
# install steps and the trade-off discussion.

set -u

input=$(cat)

model=$(printf '%s' "$input" | jq -r '.model.display_name // .model.id // ""' 2>/dev/null || true)
cwd=$(printf '%s' "$input"   | jq -r '.workspace.current_dir // ""'           2>/dev/null || true)

sandbox=""
for f in \
  "${cwd:+$cwd/.claude/settings.local.json}" \
  "${cwd:+$cwd/.claude/settings.json}" \
  "$HOME/.claude/settings.local.json" \
  "$HOME/.claude/settings.json"; do
  [ -n "$f" ] && [ -f "$f" ] || continue
  # `.sandbox.enabled | tostring` yields "true" / "false" / "null"; we
  # treat "null" (key absent or `sandbox` block missing) as unset and
  # fall through to the next file. Using `// empty` here would be
  # wrong — jq's `//` operator treats `false` as a fallback trigger,
  # so an explicit `"enabled": false` would be mis-read as missing.
  v=$(jq -r '.sandbox.enabled | tostring' "$f" 2>/dev/null || true)
  if [ "$v" = "true" ] || [ "$v" = "false" ]; then
    sandbox="$v"
    break
  fi
done

esc=$(printf '\033')
green="${esc}[1;32m"
red="${esc}[1;31m"
reset="${esc}[0m"

if [ "$sandbox" = "true" ]; then
  tag="${green}[sandbox]${reset}"
else
  tag="${red}[NO SANDBOX]${reset}"
fi

if [ -n "$model" ]; then
  printf '%s %s\n' "$model" "$tag"
else
  printf '%s\n' "$tag"
fi
