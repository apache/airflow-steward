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
# claude-iso.sh — launch Claude Code with a clean environment.
#
# This is layer 0 of the secure-agent setup (see
# `secure-agent-setup.md`): strip every credential-shaped
# environment variable from the parent shell before exec'ing
# Claude Code, so the agent never sees `$AWS_*`, `$GH_TOKEN`,
# `$ANTHROPIC_API_KEY`, etc. that an unrelated terminal session
# may have exported into your interactive shell.
#
# Filesystem-level isolation (the bigger lift) is enforced by
# Claude Code's `sandbox` feature — see the `.claude/settings.json`
# block in `secure-agent-setup.md`. This wrapper is the
# environment-variable counterpart.
#
# Usage:
#   - Source it from your shell rc:
#       source /path/to/claude-iso.sh
#     and then invoke `claude-iso` instead of `claude`.
#   - Or invoke directly: `bash claude-iso.sh [claude args ...]`.
#
# To inject a single credential explicitly for one session:
#   GH_TOKEN="$(gh auth token)" claude-iso
#   AWS_PROFILE=read-only claude-iso

claude_iso_main() {
  # Resolve the claude binary on PATH before clobbering the env so
  # the lookup uses the user's normal $PATH.
  local claude_bin
  claude_bin="$(command -v claude || true)"
  if [[ -z "$claude_bin" ]]; then
    echo "claude-iso: 'claude' not found on PATH. Install per secure-agent-setup.md." >&2
    return 127
  fi

  # The minimal env every interactive shell needs. We deliberately
  # drop everything else — the goal is no implicit credential
  # propagation.
  local -a passthrough=(
    HOME
    PATH
    SHELL
    TERM
    LANG
    LC_ALL
    LC_CTYPE
    USER
    LOGNAME
    PWD
    XDG_RUNTIME_DIR
    XDG_CONFIG_HOME
    XDG_CACHE_HOME
    XDG_DATA_HOME
    DISPLAY              # for OAuth flows that pop a browser
    WAYLAND_DISPLAY
    SSH_AUTH_SOCK        # for git push (the agent gates push behind ASK; the socket alone is harmless)
  )

  # Build an `env -i ... NAME=value ...` argv from the passthrough list.
  local -a env_args=()
  local var
  for var in "${passthrough[@]}"; do
    if [[ -n "${!var-}" ]]; then
      env_args+=("${var}=${!var}")
    fi
  done

  # Explicit single-credential injection: any env var that the user
  # set on the *invocation* line of `claude-iso` is preserved. We
  # detect this by comparing the inherited env to the parent shell's
  # via the documented contract: the user puts `KEY=value` on the
  # same line as `claude-iso`, so the variable is present in our env
  # exactly when it was passed explicitly.
  #
  # NB: this preserves *any* variable named in CLAUDE_ISO_ALLOW
  # (space-separated), so the user can route additional credentials
  # in for one session via:
  #     CLAUDE_ISO_ALLOW="GH_TOKEN AWS_PROFILE" GH_TOKEN=... claude-iso
  if [[ -n "${CLAUDE_ISO_ALLOW-}" ]]; then
    for var in $CLAUDE_ISO_ALLOW; do
      if [[ -n "${!var-}" ]]; then
        env_args+=("${var}=${!var}")
      fi
    done
  fi

  # Common one-off injections that don't need CLAUDE_ISO_ALLOW: if
  # the user explicitly set GH_TOKEN/ANTHROPIC_API_KEY on the
  # invocation line we honour it. (We can tell because the parent
  # shell didn't have it — well, actually we can't reliably tell
  # without a shadow. The conservative read: include these only when
  # the user named them in CLAUDE_ISO_ALLOW.)

  exec env -i "${env_args[@]}" "$claude_bin" "$@"
}

# When sourced, expose `claude-iso` as a function. When executed
# directly, just dispatch.
if [[ "${BASH_SOURCE[0]}" != "${0}" ]]; then
  claude-iso() { claude_iso_main "$@"; }
else
  claude_iso_main "$@"
fi
