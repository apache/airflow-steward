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

import json

import pytest

import agent_guard


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch):
    for name in (
        "STEWARD_GUARD_OFF",
        "STEWARD_ALLOW_MENTIONS",
        "STEWARD_ALLOW_COAUTHOR",
        "STEWARD_ALLOW_MARK_READY",
        "STEWARD_ALLOW_SECURITY_LANG",
        "STEWARD_ALLOW_EMPTY_PUSH",
        "STEWARD_READY_LABEL",
    ):
        monkeypatch.delenv(name, raising=False)


def fake_run(handler):
    """Install a stub for agent_guard._run that dispatches on the argv."""

    def _stub(args, cwd=None):
        return handler(args)

    return _stub


# --------------------------------------------------------------------------- #
# find_mentions / strip_code
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "text, expected",
    [
        ("hello @alice and @bob-1", ["alice", "bob-1"]),
        ("email announce@apache.org is not a mention", []),
        ("team ping @apache/airflow-committers", ["apache/airflow-committers"]),
        ("code span `@alice` does not notify", []),
        ("fenced\n```\n@alice\n```\nblock", []),
        ("user@host.com and plain text", []),
        ("`backtick login` mention of @carol", ["carol"]),
    ],
)
def test_find_mentions(text, expected):
    assert agent_guard.find_mentions(text) == expected


# --------------------------------------------------------------------------- #
# mention guard
# --------------------------------------------------------------------------- #


def test_mention_author_allowed(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    assert dispatch('gh pr comment 5 --body "@alice thanks for the fix"') is None


def test_mention_non_author_denied(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    reason = dispatch('gh pr comment 5 --body "@bob please review"')
    assert reason and "bob" in reason and "mention" in reason


def test_mention_mixed_denies_only_non_author(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    reason = dispatch('gh pr comment 5 --body "@alice @bob done"')
    assert reason and "bob" in reason and "alice" not in reason.split("refusing")[-1]


def test_mention_issue_comment(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    assert dispatch('gh issue comment 9 --body "@bob ping"') is not None


def test_fold_any_mention_denied():
    # No author lookup needed for a pr-edit body.
    reason = dispatch('gh pr edit 5 --body "@alice heads up"')
    assert reason and "fold" in reason


def test_fold_clean_allowed():
    assert dispatch('gh pr edit 5 --body "rebased onto main, fixed conflicts"') is None


def test_fold_backtick_login_allowed():
    assert dispatch('gh pr edit 5 --body "see `alice` review"') is None


def test_mention_body_file(monkeypatch, tmp_path):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    body = tmp_path / "b.md"
    body.write_text("@bob please look", encoding="utf-8")
    assert dispatch(f"gh pr comment 5 --body-file {body}") is not None


def test_mention_no_mention_no_lookup(monkeypatch):
    def boom(args):
        raise AssertionError("should not shell out when no mention present")

    monkeypatch.setattr(agent_guard, "_run", fake_run(boom))
    assert dispatch('gh pr comment 5 --body "thanks, looks good"') is None


def test_mention_author_unresolved_fails_closed(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: None))
    reason = dispatch('gh pr comment 5 --body "@bob hi"')
    assert reason and "could not be verified" in reason


def test_mention_override(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    assert dispatch('STEWARD_ALLOW_MENTIONS=1 gh pr comment 5 --body "@bob ping"') is None


def test_global_off(monkeypatch):
    assert dispatch('STEWARD_GUARD_OFF=1 gh pr edit 5 --body "@alice @bob"') is None


# --------------------------------------------------------------------------- #
# commit-trailer guard
# --------------------------------------------------------------------------- #


def test_commit_coauthor_denied():
    reason = dispatch('git commit -m "fix\n\nCo-Authored-By: Someone <x@y.z>"')
    assert reason and "Co-Authored-By" in reason


def test_commit_coauthor_case_insensitive():
    assert dispatch('git commit -m "x\n\nco-authored-by: a"') is not None


def test_commit_generated_by_allowed():
    assert dispatch('git commit -m "fix\n\nGenerated-by: Claude Code"') is None


def test_commit_coauthor_override():
    assert dispatch('STEWARD_ALLOW_COAUTHOR=1 git commit -m "x\nCo-Authored-By: a"') is None


# --------------------------------------------------------------------------- #
# mark-ready guard
# --------------------------------------------------------------------------- #


def _mark_ready_handler(pending):
    def handler(args):
        if "headRefOid" in args:
            return "deadbeefcafebabe1234"
        if any("actions/runs" in a for a in args):
            return pending
        return None

    return handler


def test_mark_ready_pending_denied(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_mark_ready_handler("2")))
    reason = dispatch('gh pr edit 5 --repo o/r --add-label "ready for maintainer review"')
    assert reason and "awaiting approval" in reason


def test_mark_ready_clean_allowed(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_mark_ready_handler("0")))
    assert dispatch('gh pr edit 5 --repo o/r --add-label "ready for maintainer review"') is None


def test_mark_ready_other_label_allowed(monkeypatch):
    def boom(args):
        raise AssertionError("no lookup for an unrelated label")

    monkeypatch.setattr(agent_guard, "_run", fake_run(boom))
    assert dispatch('gh pr edit 5 --repo o/r --add-label "area:scheduler"') is None


def test_mark_ready_failopen_when_head_unknown(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: None))
    assert dispatch('gh pr edit 5 --repo o/r --add-label "ready for maintainer review"') is None


def test_mark_ready_override(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_mark_ready_handler("3")))
    cmd = 'STEWARD_ALLOW_MARK_READY=1 gh pr edit 5 --repo o/r --add-label "ready for maintainer review"'
    assert dispatch(cmd) is None


# --------------------------------------------------------------------------- #
# security-language guard
# --------------------------------------------------------------------------- #


def test_security_cve_in_pr_create_denied():
    reason = dispatch('gh pr create --title "Fix CVE-2026-1234" --body "patch"')
    assert reason and "security" in reason.lower()


def test_security_keyword_in_pr_body_denied():
    assert dispatch('gh pr create --title "fix" --body "patches a SQL injection"') is not None


def test_security_clean_pr_create_allowed():
    assert dispatch('gh pr create --title "Add retry policy" --body "implements AIP-105"') is None


def test_security_language_in_comment_allowed():
    # Comments are NOT in scope (avoids colliding with the triage security warning).
    assert dispatch('gh pr comment 5 --body "this looks like a SQL injection risk"') is None


def test_security_override():
    cmd = 'STEWARD_ALLOW_SECURITY_LANG=1 gh pr create --title "Fix CVE-2026-1234" --body "x"'
    assert dispatch(cmd) is None


# --------------------------------------------------------------------------- #
# empty-rebase guard
# --------------------------------------------------------------------------- #


def _push_handler(count):
    def handler(args):
        if args[:3] == ["git", "rev-parse", "--abbrev-ref"]:
            return "origin/main"
        if args[:2] == ["git", "merge-base"]:
            return "base1234"
        if args[:3] == ["git", "rev-list", "--count"]:
            return count
        if args[:3] == ["git", "rev-parse", "--verify"]:
            return "sha"
        return None

    return handler


def test_empty_rebase_denied(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_push_handler("0")))
    reason = dispatch("git push --force-with-lease origin mybranch:mybranch")
    assert reason and "0 commits" in reason


def test_nonempty_force_push_allowed(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_push_handler("3")))
    assert dispatch("git push --force-with-lease origin mybranch") is None


def test_non_force_push_allowed(monkeypatch):
    def boom(args):
        raise AssertionError("non-force push is not guarded")

    monkeypatch.setattr(agent_guard, "_run", fake_run(boom))
    assert dispatch("git push origin mybranch") is None


def test_empty_rebase_failopen_no_base(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: None))
    assert dispatch("git push --force origin mybranch") is None


def test_empty_rebase_override(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(_push_handler("0")))
    assert dispatch("STEWARD_ALLOW_EMPTY_PUSH=1 git push --force origin b:b") is None


# --------------------------------------------------------------------------- #
# dispatch / fast path / compound commands
# --------------------------------------------------------------------------- #


@pytest.mark.parametrize(
    "command",
    [
        "ls -la",
        "git status",
        "git log --oneline -5",
        "grep -r foo .",
        "gh pr view 5 --json title",
        "",
    ],
)
def test_fast_path_allows(command):
    assert dispatch(command) is None


def test_compound_command_guarded(monkeypatch):
    monkeypatch.setattr(agent_guard, "_run", fake_run(lambda a: "alice"))
    assert dispatch('cd /tmp && gh pr comment 5 --body "@bob hi"') is not None


def test_malformed_command_allows():
    # Unbalanced quotes -> cannot tokenise -> allow (never break the shell).
    assert dispatch('gh pr comment 5 --body "oops') is None


# --------------------------------------------------------------------------- #
# main() stdin contract
# --------------------------------------------------------------------------- #


def test_main_emits_deny(monkeypatch, capsys):
    event = {"tool_name": "Bash", "tool_input": {"command": 'gh pr edit 5 --body "@bob"'}}
    monkeypatch.setattr("sys.stdin", _Stdin(json.dumps(event)))
    rc = agent_guard.main()
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert rc == 0
    assert payload["hookSpecificOutput"]["permissionDecision"] == "deny"


def test_main_allows_non_bash(monkeypatch, capsys):
    event = {"tool_name": "Read", "tool_input": {"file_path": "x"}}
    monkeypatch.setattr("sys.stdin", _Stdin(json.dumps(event)))
    rc = agent_guard.main()
    assert rc == 0
    assert capsys.readouterr().out == ""


def test_main_allows_malformed_stdin(monkeypatch, capsys):
    monkeypatch.setattr("sys.stdin", _Stdin("not json"))
    assert agent_guard.main() == 0
    assert capsys.readouterr().out == ""


# --------------------------------------------------------------------------- #
# contributed-guard discovery
# --------------------------------------------------------------------------- #


def test_bundled_no_verify_guard_discovered():
    # The bundled example guard in src/agent_guard/guards.d is auto-discovered
    # from the default sibling dir — no env needed.
    reason = dispatch('git commit -m "x" --no-verify')
    assert reason and "no-verify" in reason


def test_no_verify_override():
    assert dispatch('STEWARD_ALLOW_NO_VERIFY=1 git commit -n -m "x"') is None


def test_plain_commit_not_blocked_by_no_verify_guard():
    assert dispatch('git commit -m "ordinary commit"') is None


def test_contributed_guard_from_env_dir(monkeypatch, tmp_path):
    # A skill contributes a guard by dropping a file in a guards.d dir; pointing
    # STEWARD_GUARD_DIRS at it wires it in with no change to settings.json.
    gdir = tmp_path / "guards.d"
    gdir.mkdir()
    (gdir / "block_merge_admin.py").write_text(
        'TRIGGERS = ["gh"]\n'
        "def guard(ctx):\n"
        "    sub = ctx.gh_subcommand()\n"
        "    if sub == ('pr', 'merge') and any(t in ('--admin',) for t in ctx.argv):\n"
        "        if ctx.override('STEWARD_ALLOW_ADMIN_MERGE'):\n"
        "            return None\n"
        "        return 'contributed[admin-merge]: refusing gh pr merge --admin'\n"
        "    return None\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("STEWARD_GUARD_DIRS", str(gdir))
    assert dispatch("gh pr merge 5 --admin") is not None
    assert dispatch("STEWARD_ALLOW_ADMIN_MERGE=1 gh pr merge 5 --admin") is None
    # Unrelated gh command is unaffected by the contributed guard.
    assert dispatch("gh pr view 5 --json title") is None


def test_broken_contributed_guard_fails_open(monkeypatch, tmp_path):
    gdir = tmp_path / "guards.d"
    gdir.mkdir()
    (gdir / "broken.py").write_text("this is not valid python !!!", encoding="utf-8")
    monkeypatch.setenv("STEWARD_GUARD_DIRS", str(gdir))
    # A guard file that cannot import must never break the shell.
    assert dispatch("gh pr view 5") is None


# Convenience wrapper so each test reads cleanly.
def dispatch(command):
    return agent_guard.dispatch(command, cwd=None)


class _Stdin:
    def __init__(self, text):
        self._text = text

    def read(self):
        return self._text
