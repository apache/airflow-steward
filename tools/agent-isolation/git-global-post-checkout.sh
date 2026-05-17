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
# git-global-post-checkout.sh — the universal post-checkout hook
# installed under ~/.claude/git-hooks/post-checkout when the
# operator picks **whole-user** scope in
# `setup-isolated-setup-install`.
#
# Activated by:
#   git config --global core.hooksPath ~/.claude/git-hooks/
#
# After that, every `git checkout`, `git clone` (which runs an
# implicit checkout of the default branch), and `git worktree add`
# across the operator's host invokes this script — for any repo,
# not just apache-steward adopters.
#
# Two responsibilities, both best-effort + idempotent + `|| true`
# so the hook never breaks the surrounding git operation:
#
#   1. **apache-steward symlink reconciliation.** If the working
#      tree carries `.apache-steward.lock`, this is a steward-
#      adopted repo and its gitignored framework-skill symlinks
#      may need re-creating after a checkout (the symlinks point
#      into `.apache-steward/`, which is itself gitignored). The
#      hook calls `/setup-steward verify --auto-fix-symlinks` if
#      that command is on PATH; if not, it falls through silently
#      (the operator may not be in a Claude Code session, or may
#      not have the framework installed beyond this hook).
#
#   2. **Sandbox-allowlist for the current worktree.** If the
#      working tree has a `.claude/` directory (i.e. it is
#      Claude-Code-aware) and the framework's
#      `sandbox-add-project-root.sh` helper is installed at
#      `~/.claude/scripts/`, the hook calls the helper to populate
#      `<worktree>/.claude/settings.local.json` with the
#      worktree's absolute path. Defensive against the harness
#      behaviour documented at
#      https://github.com/apache/airflow-steward/issues/197 .
#
# IMPORTANT — `core.hooksPath` shadowing. When `core.hooksPath` is
# set globally, git looks ONLY in that directory for hooks. Every
# per-repo `<repo>/.git/hooks/*` becomes inert across every repo
# on the host. If the operator has hooks they care about in
# specific repos (per-commit linters, pre-push checks, etc.) those
# need to be migrated into the global hooks dir or invoked from
# within these global hooks. The install skill warns the operator
# about this trade-off loudly before setting `core.hooksPath`.
#
# This hook only handles `post-checkout`. Other hook types
# (pre-commit, commit-msg, pre-push, ...) need their own files in
# the global hooks dir if the operator wants them to fire after
# setting `core.hooksPath`. The framework does not ship them; it
# is up to the operator to migrate them.

set -u

# Resolve the current working tree's root. The hook fires inside a
# git checkout — `git rev-parse --show-toplevel` should always
# succeed; the `2>/dev/null` is defensive against odd worktree
# states.
worktree=$(git rev-parse --show-toplevel 2>/dev/null || true)
if [ -z "$worktree" ]; then
  exit 0
fi

# 1. apache-steward symlink reconciliation
if [ -f "$worktree/.apache-steward.lock" ] \
    && command -v /setup-steward >/dev/null 2>&1; then
  /setup-steward verify --auto-fix-symlinks 2>/dev/null || true
fi

# 2. Sandbox-allowlist helper
if [ -x "$HOME/.claude/scripts/sandbox-add-project-root.sh" ] \
    && [ -d "$worktree/.claude" ]; then
  "$HOME/.claude/scripts/sandbox-add-project-root.sh" 2>/dev/null || true
fi

exit 0
