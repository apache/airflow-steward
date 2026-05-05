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

# agent-pre-commit.sh
#
# Wrapper for `prek run --all-files` tailored for AI agent use.
#
# This script exists because agents (Claude Code, Kimi CLI, etc.)
# may run `pytest`, `ruff`, and `mypy` individually during
# development, but the CI gate runs the full `prek` suite which
# includes additional checks (doctoc, markdownlint, typos,
# check-placeholders, etc.).  Running this wrapper before every
# commit ensures the agent catches the same failures the CI will.
#
# Usage (from repo root):
#   tools/dev/agent-pre-commit.sh
#
# Exit codes:
#   0 — all checks passed, safe to commit
#   1 — one or more checks failed, review output and fix
#   2 — prek not installed or not in PATH

set -euo pipefail

repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$repo_root"

if ! command -v prek >/dev/null 2>&1; then
  echo "agent-pre-commit: prek not found in PATH" >&2
  echo "Install:  uv tool install prek    # or: pipx install prek" >&2
  echo "Then:     prek install             # installs git hook" >&2
  exit 2
fi

if [[ ! -f .git/hooks/pre-commit ]]; then
  echo "agent-pre-commit: warning — .git/hooks/pre-commit not found" >&2
  echo "Run 'prek install' to set up the git hook." >&2
fi

echo "agent-pre-commit: running prek run --all-files ..."
echo ""

# Run prek and capture output while preserving exit code.
# We intentionally do NOT use 'set -e' here so we can print
# a friendly summary even when checks fail.
set +e
prek_output=$(prek run --all-files --color=always 2>&1)
prek_rc=$?
set -e

if [[ $prek_rc -eq 0 ]]; then
  echo "$prek_output"
  echo ""
  echo "agent-pre-commit: ✅ all checks passed — safe to commit"
  exit 0
fi

# Checks failed — print the full output and a summary.
echo "$prek_output"
echo ""
echo "agent-pre-commit: ❌ one or more checks failed (exit $prek_rc)" >&2
echo "Review the output above, fix the issues, and run this script again." >&2

# Extract which hooks failed for a quick summary.
failed_hooks=$(echo "$prek_output" | grep -E '\[41mFailed\[49m' | sed 's/.*\[41mFailed\[49m.*/  - FAILED/' | sed 's/^  - FAILED //')
if [[ -n "$failed_hooks" ]]; then
  echo "" >&2
  echo "Failed hooks:" >&2
  echo "$failed_hooks" >&2
fi

exit 1
