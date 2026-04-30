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
# sandbox-bypass-warn.sh — Claude Code PreToolUse hook (Bash matcher).
#
# Loudly warns whenever the model invokes the Bash tool with
# `dangerouslyDisableSandbox: true` — i.e. when the model is asking
# to leave Claude Code's filesystem/network sandbox for one call.
#
# Claude Code already prompts the user before honouring a sandbox
# bypass, but the prompt is easy to skim past in long sessions.
# This hook makes every bypass attempt visually impossible to miss:
# a bold-red banner with the command and the model's stated reason.
#
# Recommended placement: user-scope `~/.claude/settings.json`, so
# the warning fires for *every* Claude Code session on the host —
# not only sessions inside a tracker repo whose project-level
# `.claude/settings.json` would otherwise have to wire it itself.
#
# Behaviour:
# - Reads tool input as JSON on stdin.
# - If `"dangerouslyDisableSandbox": true` appears anywhere in the
#   payload (matched as a JSON field, robust to schema changes
#   across Claude Code versions), prints a bold-red banner to
#   stderr with the command and the model's stated reason.
# - Exits 1: a non-zero exit code that is *not* 2 means stderr is
#   shown to the user in the terminal and the tool call still
#   proceeds through the normal permission prompt. We want
#   visibility, not block.
# - Exit 2 would block the call entirely — *not* what we want; the
#   user will be asked to authorise the bypass anyway, and a hard
#   block here would defeat the model's ability to do work the
#   user explicitly asked for.
# - Otherwise exits 0 silently.
#
# Wiring (user-scope, applies to every session on the host):
#
#   {
#     "hooks": {
#       "PreToolUse": [
#         {
#           "matcher": "Bash",
#           "hooks": [
#             { "type": "command",
#               "command": "~/.claude/scripts/sandbox-bypass-warn.sh" }
#           ]
#         }
#       ]
#     }
#   }
#
# See `secure-agent-setup.md` → "Sandbox-bypass visibility hook"
# for the install steps and the "Syncing user-scope config across
# machines" section for the private-repo pattern that keeps this
# hook in lockstep across hosts.

set -u

input=$(cat)

# Match the JSON field anywhere in the payload. This is intentionally
# more permissive than `jq -r '.tool_input.dangerouslyDisableSandbox'`
# so the hook keeps working if Claude Code ever reshuffles where in
# the payload the flag lives.
if printf '%s' "$input" | grep -qE '"dangerouslyDisableSandbox"[[:space:]]*:[[:space:]]*true'; then
  cmd=$(printf '%s' "$input"  | jq -r '.tool_input.command // ""'     2>/dev/null || true)
  desc=$(printf '%s' "$input" | jq -r '.tool_input.description // ""' 2>/dev/null || true)

  esc=$(printf '\033')
  red="${esc}[1;31m"
  reset="${esc}[0m"

  {
    printf '%s\041\041\041 SANDBOX BYPASS REQUESTED \041\041\041%s\n' "$red" "$reset"
    [ -n "$desc" ] && printf '%sReason :%s %s\n' "$red" "$reset" "$desc"
    [ -n "$cmd"  ] && printf '%sCommand:%s %s\n' "$red" "$reset" "$cmd"
    printf '%sThis call will run OUTSIDE the sandbox.%s\n' "$red" "$reset"
  } >&2
  exit 1
fi

exit 0
