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

"""Deterministic ``PreToolUse`` guard dispatcher for apache-steward.

Reads a Claude Code ``PreToolUse`` hook event on stdin, inspects the ``Bash``
command, and **denies** the ones that would violate a hard framework rule
that should never depend on the model remembering a SKILL.md instruction:

1. **mention** — never ``@``-ping anyone other than the PR/issue author in an
   author-directed comment, and never ``@``-mention anyone in a PR-body edit
   (the silent "fold" channel). Mirrors the denoise change (PR #491).
2. **commit-trailer** — never let a ``git commit`` carry a ``Co-Authored-By:``
   trailer (AGENTS.md: agents use ``Generated-by:``, never co-author).
3. **mark-ready** — never add the "ready for maintainer review" label while the
   PR head SHA still has GitHub Actions runs awaiting approval
   (pr-management-triage Golden rule 1b).
4. **security-language** — never put a CVE id or security-fix language in a
   public PR title/body (security-issue-fix public-PR scrubbing rule).
5. **empty-rebase** — never force-push a branch that has no commits over its
   base (an empty push to a PR head auto-closes the PR and revokes write).

The hook fires on *every* ``Bash`` call, so this module is **stdlib-only** and
meant to be invoked directly as ``python3 .../agent_guard/__init__.py`` — never
through ``uv run`` — and returns in a few milliseconds for any command that is
not a guarded ``gh`` / ``git commit`` / ``git push`` (the fast path).

Every guard is overridable, per command, by a visible inline env assignment so a
maintainer can consciously proceed (``STEWARD_ALLOW_MENTIONS=1 gh pr comment …``)
or disable the whole dispatcher (``STEWARD_GUARD_OFF=1``). Overrides are read
from the command string itself (and from the hook's own environment).

**Contributing guards.** The five above are *bundled* guards. Any skill can add
its own deterministic guard **without re-wiring the hook**: drop an import-free
``*.py`` file into a discovered ``guards.d`` directory (the ``guards.d`` sibling
of this script, plus any dir in ``$STEWARD_GUARD_DIRS``) that defines a
module-level ``guard(ctx)`` returning a deny string or ``None`` — see
``GuardContext`` and ``guards.d/no_verify_commit.py`` for the template. The hook
is wired once at setup; thereafter guards are added/removed by managing files in
``guards.d`` (which ``/magpie-setup`` keeps in sync from the snapshot).
"""

from __future__ import annotations

import importlib.util
import json
import os
import re
import shlex
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

# --------------------------------------------------------------------------- #
# Configuration / constants
# --------------------------------------------------------------------------- #

GLOBAL_OFF_ENV = "STEWARD_GUARD_OFF"
READY_LABEL_ENV = "STEWARD_READY_LABEL"
DEFAULT_READY_LABEL = "ready for maintainer review"

# Shell control operators that separate one simple command from the next.
SHELL_OPERATORS = frozenset({"&&", "||", "|", ";", "&", "|&"})

# A GitHub @mention: an `@` that is NOT part of an email address (so it is not
# preceded by a word char or a dot), followed by a login (or `org/team`).
# Logins are 1-39 chars, alphanumeric or single hyphens.
MENTION_RE = re.compile(r"(?<![\w.@])@([A-Za-z0-9](?:[A-Za-z0-9-]{0,38})(?:/[A-Za-z0-9._-]+)?)")

# Fenced code blocks and inline code spans — GitHub does not turn @mentions
# inside them into notifications, so we strip them before scanning.
_FENCED_RE = re.compile(r"```.*?```", re.DOTALL)
_INLINE_CODE_RE = re.compile(r"`[^`\n]*`")

CVE_RE = re.compile(r"\bCVE-\d{4}-\d{3,}\b", re.IGNORECASE)

# Security-fix language that must not appear in a PUBLIC pr title/body before a
# CVE is announced. A curated subset of the canonical list in
# tools/skill-and-tool-validator (security_pattern check) — kept deliberately
# narrow to limit false positives on the PR-create/edit surface.
SECURITY_KEYWORDS = (
    "sql injection",
    "xss",
    "csrf",
    "ssrf",
    "remote code execution",
    "arbitrary code execution",
    "path traversal",
    "directory traversal",
    "privilege escalation",
    "auth bypass",
    "authentication bypass",
    "buffer overflow",
    "heap overflow",
    "use-after-free",
    "security vulnerability",
    "security fix",
    "exploitable",
)

GUARD_TIMEOUT = 10  # seconds for any subprocess (gh / git) a guard shells out to.


class Segment:
    """One simple command from a (possibly compound) shell line.

    ``argv`` has leading ``NAME=value`` env assignments stripped into ``env``;
    ``raw`` is the original text of the segment (used for substring scans that
    survive heredocs, e.g. the Co-Authored-By trailer).
    """

    def __init__(self, tokens: list[str], raw: str) -> None:
        self.env: dict[str, str] = {}
        i = 0
        while i < len(tokens) and re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*=.*", tokens[i]):
            name, _, value = tokens[i].partition("=")
            self.env[name] = value
            i += 1
        self.argv: list[str] = tokens[i:]
        self.raw = raw

    def override(self, *names: str) -> bool:
        """True if any of ``names`` (or the global off switch) is set truthy,
        either as an inline env assignment on this segment or in the hook's own
        environment."""
        for name in (GLOBAL_OFF_ENV, *names):
            val = self.env.get(name, os.environ.get(name))
            if val not in (None, "", "0", "false", "False"):
                return True
        return False


# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #


def split_segments(command: str) -> list[Segment]:
    """Tokenise ``command`` and split it into simple-command segments on shell
    operators. Returns an empty list if the command cannot be tokenised."""
    try:
        tokens = shlex.split(command, comments=False)
    except ValueError:
        return []
    segments: list[Segment] = []
    current: list[str] = []
    for tok in tokens:
        if tok in SHELL_OPERATORS:
            if current:
                segments.append(Segment(current, command))
                current = []
        else:
            current.append(tok)
    if current:
        segments.append(Segment(current, command))
    return segments


def strip_code(text: str) -> str:
    """Remove fenced code blocks and inline code spans — mentions inside them do
    not notify on GitHub."""
    return _INLINE_CODE_RE.sub(" ", _FENCED_RE.sub(" ", text))


def find_mentions(text: str) -> list[str]:
    """Lower-cased GitHub mentions (logins and ``org/team``) in ``text``, with
    code spans stripped first."""
    return [m.group(1).lower() for m in MENTION_RE.finditer(strip_code(text))]


def _opt_value(argv: list[str], short: str, long: str) -> str | None:
    """Return the value of ``-x``/``--xxx`` (space- or ``=``-separated) or None."""
    for i, tok in enumerate(argv):
        if tok in (short, long):
            return argv[i + 1] if i + 1 < len(argv) else None
        for prefix in (f"{long}=", f"{short}="):
            if tok.startswith(prefix):
                return tok[len(prefix) :]
    return None


def gh_subcommand(argv: list[str]) -> tuple[str, str] | None:
    """For an argv whose first token is ``gh``, return ``(group, sub)`` skipping
    global flags, e.g. ``(\"pr\", \"comment\")``. None if not a ``gh`` call."""
    if not argv or argv[0] != "gh":
        return None
    rest = [t for t in argv[1:] if not t.startswith("-")]
    if len(rest) >= 2:
        return rest[0], rest[1]
    return None


def gh_body_text(argv: list[str], *, include_title: bool, read_files: bool) -> str:
    """Concatenate the inline ``--body`` (and optionally ``--title``) plus, when
    ``read_files`` is set, the contents of any ``--body-file``."""
    parts: list[str] = []
    body = _opt_value(argv, "-b", "--body")
    if body:
        parts.append(body)
    if include_title:
        title = _opt_value(argv, "-t", "--title")
        if title:
            parts.append(title)
    if read_files:
        path = _opt_value(argv, "-F", "--body-file")
        if path and path != "-":
            try:
                with open(path, encoding="utf-8", errors="replace") as fh:
                    parts.append(fh.read())
            except OSError:
                parts.append("\x00UNREADABLE_BODY_FILE\x00")
    return "\n".join(parts)


def _run(args: list[str], cwd: str | None = None) -> str | None:
    """Run a subprocess, returning stripped stdout, or None on any failure."""
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=GUARD_TIMEOUT,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def _positional_target(argv: list[str], sub_index: int) -> str | None:
    """First non-flag token after the subcommand — the PR/issue number or URL.
    ``sub_index`` is the index of the subcommand token in ``argv``."""
    i = sub_index + 1
    while i < len(argv):
        tok = argv[i]
        if tok.startswith("-"):
            # Skip a flag and, heuristically, its value when not ``=``-joined.
            if "=" not in tok and tok not in ("--web",):
                i += 2
            else:
                i += 1
            continue
        return tok
    return None


def _repo_flag(argv: list[str]) -> list[str]:
    repo = _opt_value(argv, "-R", "--repo")
    return ["--repo", repo] if repo else []


# --------------------------------------------------------------------------- #
# Guards — each returns a deny reason string, or None to allow.
# --------------------------------------------------------------------------- #


def guard_mention(seg: Segment, cwd: str | None) -> str | None:
    sub = gh_subcommand(seg.argv)
    if sub is None:
        return None
    group, name = sub
    is_pr_body_edit = (
        group == "pr"
        and name == "edit"
        and (
            _opt_value(seg.argv, "-b", "--body") is not None
            or _opt_value(seg.argv, "-F", "--body-file") is not None
        )
    )
    is_comment = (group == "pr" and name == "comment") or (group == "issue" and name == "comment")
    if not (is_pr_body_edit or is_comment):
        return None

    body = gh_body_text(seg.argv, include_title=False, read_files=True)
    mentions = find_mentions(body)
    if not mentions:
        return None
    if seg.override("STEWARD_ALLOW_MENTIONS"):
        return None

    if is_pr_body_edit:
        return (
            "agent-guard[mention]: a `gh pr edit --body` (the silent PR-description "
            f"'fold' channel) must not @-mention anyone — found {sorted(set(mentions))}. "
            "Editing a PR body should never ping; reference logins as backticked "
            "`login`, not @login. Override (rare): prefix STEWARD_ALLOW_MENTIONS=1."
        )

    # Comment channel: only the PR/issue author may be @-mentioned.
    sub_index = seg.argv.index(name)
    target = _positional_target(seg.argv, sub_index)
    view = "pr" if group == "pr" else "issue"
    author = None
    if target:
        author = _run(
            ["gh", view, "view", target, *_repo_flag(seg.argv), "--json", "author", "--jq", ".author.login"],
            cwd=cwd,
        )
    if not author:
        return (
            "agent-guard[mention]: this author-directed comment @-mentions "
            f"{sorted(set(mentions))} but the PR/issue author could not be verified, "
            "so the guard cannot confirm none of them are maintainers. Re-run once the "
            "author is known, drop the @-mentions (use backticked `login`), or override "
            "with STEWARD_ALLOW_MENTIONS=1 if the ping is intentional."
        )
    author_l = author.lower()
    offenders = sorted({m for m in mentions if m != author_l})
    if offenders:
        return (
            "agent-guard[mention]: an author-directed comment may only @-mention the "
            f"author (`{author}`); refusing to ping {offenders}. Reference other people "
            "as backticked `login` (no @) so they are not notified, or override with "
            "STEWARD_ALLOW_MENTIONS=1 for a deliberate ping."
        )
    return None


def guard_commit_trailer(seg: Segment, cwd: str | None) -> str | None:
    if seg.argv[:2] != ["git", "commit"]:
        return None
    if not re.search(r"co-authored-by:", seg.raw, re.IGNORECASE):
        return None
    if seg.override("STEWARD_ALLOW_COAUTHOR"):
        return None
    return (
        "agent-guard[commit-trailer]: this commit message carries a 'Co-Authored-By:' "
        "trailer. Per AGENTS.md, agents are assistants, not authors — use a "
        "'Generated-by: <agent name and version>' trailer instead and remove the "
        "Co-Authored-By line. Override (not for AI co-authorship): STEWARD_ALLOW_COAUTHOR=1."
    )


def guard_mark_ready(seg: Segment, cwd: str | None) -> str | None:
    sub = gh_subcommand(seg.argv)
    if sub != ("pr", "edit"):
        return None
    label = _opt_value(seg.argv, "", "--add-label")
    ready = os.environ.get(READY_LABEL_ENV, DEFAULT_READY_LABEL)
    if not label or label.strip().lower() != ready.strip().lower():
        return None
    if seg.override("STEWARD_ALLOW_MARK_READY"):
        return None

    sub_index = seg.argv.index("edit")
    target = _positional_target(seg.argv, sub_index)
    if not target:
        return None  # fail-open: cannot identify the PR.
    repo = _opt_value(seg.argv, "-R", "--repo")
    head = _run(
        ["gh", "pr", "view", target, *_repo_flag(seg.argv), "--json", "headRefOid", "--jq", ".headRefOid"],
        cwd=cwd,
    )
    if not repo:
        repo = _run(
            ["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"],
            cwd=cwd,
        )
    if not head or not repo:
        return None  # fail-open: cannot run the authoritative check.
    pending = _run(
        [
            "gh",
            "api",
            f"repos/{repo}/actions/runs?head_sha={head}&per_page=20",
            "--jq",
            '[.workflow_runs[] | select(.conclusion == "action_required")] | length',
        ],
        cwd=cwd,
    )
    if pending and pending.isdigit() and int(pending) > 0:
        return (
            f"agent-guard[mark-ready]: PR has {pending} GitHub Actions run(s) awaiting "
            f"approval at head {head[:7]}; adding '{ready}' now is premature (Golden rule "
            "1b) — the real CI has not run. Approve/await the workflow first. Override: "
            "STEWARD_ALLOW_MARK_READY=1."
        )
    return None


def guard_security_language(seg: Segment, cwd: str | None) -> str | None:
    sub = gh_subcommand(seg.argv)
    if sub not in (("pr", "create"), ("pr", "edit")):
        return None
    text = gh_body_text(seg.argv, include_title=True, read_files=True)
    if not text:
        return None
    if seg.override("STEWARD_ALLOW_SECURITY_LANG"):
        return None
    lowered = text.lower()
    hits: list[str] = []
    cve = CVE_RE.search(text)
    if cve:
        hits.append(cve.group(0))
    hits.extend(kw for kw in SECURITY_KEYWORDS if kw in lowered)
    if hits:
        return (
            "agent-guard[security-language]: this public PR title/body contains "
            f"security-fix language {sorted(set(hits))}. Per the ASF process, the "
            "security nature of a fix must not appear in public content before the CVE "
            "is announced — neutralise the wording. If disclosure is already public, "
            "override with STEWARD_ALLOW_SECURITY_LANG=1."
        )
    return None


def guard_empty_rebase(seg: Segment, cwd: str | None) -> str | None:
    if seg.argv[:2] != ["git", "push"]:
        return None
    forced = any(
        t in ("-f", "--force") or t == "--force-with-lease" or t.startswith("--force-with-lease=")
        for t in seg.argv
    )
    if not forced:
        return None
    if seg.override("STEWARD_ALLOW_EMPTY_PUSH"):
        return None

    # Resolve the source ref being pushed: last `src[:dst]` positional, else HEAD.
    positionals = [t for t in seg.argv[2:] if not t.startswith("-")]
    src = "HEAD"
    if len(positionals) >= 2:
        src = positionals[1].split(":", 1)[0] or "HEAD"
    elif len(positionals) == 1 and _run(
        ["git", "rev-parse", "--verify", "--quiet", f"{positionals[0]}^{{commit}}"], cwd=cwd
    ):
        # A lone positional that resolves to a commit is the ref; else it is the remote.
        src = positionals[0]

    default_ref = _run(["git", "rev-parse", "--abbrev-ref", "origin/HEAD"], cwd=cwd)
    if not default_ref:
        return None  # fail-open: no base to compare against.
    base = _run(["git", "merge-base", default_ref, src], cwd=cwd)
    if not base:
        return None  # fail-open.
    count = _run(["git", "rev-list", "--count", f"{base}..{src}"], cwd=cwd)
    if count is not None and count.isdigit() and int(count) == 0:
        return (
            f"agent-guard[empty-rebase]: refusing to force-push '{src}' — it has 0 commits "
            f"over its merge-base with {default_ref}. Pushing an empty branch to a PR head "
            "auto-closes the PR and revokes maintainer write access. Verify the rebase "
            "result is non-empty first. Override: STEWARD_ALLOW_EMPTY_PUSH=1."
        )
    return None


# The framework's bundled guards. Skills contribute MORE without editing this
# file or re-wiring the hook — see "Contributing guards" below.
BUILTIN_GUARDS: tuple[Callable[[Segment, str | None], str | None], ...] = (
    guard_commit_trailer,
    guard_empty_rebase,
    guard_security_language,
    guard_mention,
    guard_mark_ready,
)

# Only commands in these families are inspected; everything else takes the
# instant fast path. Bundled and contributed guards alike operate on the
# `gh` / `git` outbound/destructive surface.
GUARDED_HEADS = frozenset({"gh", "git"})

# Colon-separated extra guard directories (in addition to the default
# ``guards.d`` sibling of this script). Lets a checkout point the hook at
# skill-owned guard dirs without moving files.
GUARD_DIRS_ENV = "STEWARD_GUARD_DIRS"


# --------------------------------------------------------------------------- #
# Contributed-guard extension API
# --------------------------------------------------------------------------- #


class GuardContext:
    """The API passed to every **contributed** guard — ``guard(ctx) -> str | None``.

    A skill adds a guard by dropping an import-free ``*.py`` file in a discovered
    ``guards.d`` directory that defines a module-level ``guard(ctx)`` (and an
    optional ``TRIGGERS`` list of command families, e.g. ``["gh"]`` /
    ``["git:commit"]``). Returning a string denies the command with that reason;
    returning ``None`` allows it. Everything the guard needs is on ``ctx`` — it
    never imports ``agent_guard`` — so guards stay decoupled from the engine.
    """

    def __init__(self, seg: Segment, cwd: str | None) -> None:
        self.seg = seg
        self.cwd = cwd

    @property
    def argv(self) -> list[str]:
        return self.seg.argv

    @property
    def raw(self) -> str:
        return self.seg.raw

    @property
    def ready_label(self) -> str:
        return os.environ.get(READY_LABEL_ENV, DEFAULT_READY_LABEL)

    def override(self, *names: str) -> bool:
        return self.seg.override(*names)

    def gh_subcommand(self) -> tuple[str, str] | None:
        return gh_subcommand(self.argv)

    def opt(self, short: str, long: str) -> str | None:
        return _opt_value(self.argv, short, long)

    def gh_body(self, *, include_title: bool = False, read_files: bool = True) -> str:
        return gh_body_text(self.argv, include_title=include_title, read_files=read_files)

    def mentions(self, text: str) -> list[str]:
        return find_mentions(text)

    def positional_after(self, sub_token: str) -> str | None:
        try:
            idx = self.argv.index(sub_token)
        except ValueError:
            return None
        return _positional_target(self.argv, idx)

    def repo_flag(self) -> list[str]:
        return _repo_flag(self.argv)

    def run(self, args: list[str]) -> str | None:
        return _run(args, cwd=self.cwd)


def command_kinds(seg: Segment) -> set[str]:
    """The command-family tags a segment matches, e.g. ``{"git", "git:commit"}``."""
    kinds: set[str] = set()
    if not seg.argv:
        return kinds
    head = seg.argv[0]
    kinds.add(head)
    if len(seg.argv) > 1 and head in ("git", "gh"):
        kinds.add(f"{head}:{seg.argv[1]}")
    return kinds


def guard_dirs() -> list[Path]:
    """Directories scanned for contributed guards: ``$STEWARD_GUARD_DIRS`` entries
    plus the ``guards.d`` sibling of this script."""
    dirs: list[Path] = []
    env = os.environ.get(GUARD_DIRS_ENV)
    if env:
        dirs.extend(Path(p) for p in env.split(os.pathsep) if p)
    dirs.append(Path(__file__).resolve().parent / "guards.d")
    seen: set[Path] = set()
    out: list[Path] = []
    for d in dirs:
        if d not in seen and d.is_dir():
            seen.add(d)
            out.append(d)
    return out


def discover_guards() -> list[tuple[Callable[[GuardContext], str | None], set[str] | None]]:
    """Load contributed guards from the guard dirs. Each is returned with its
    declared ``TRIGGERS`` set (or None to mean "any guarded command"). A guard
    file that fails to import is skipped — a broken contribution must never break
    the user's shell."""
    found: list[tuple[Callable[[GuardContext], str | None], set[str] | None]] = []
    for directory in guard_dirs():
        for path in sorted(directory.glob("*.py")):
            if path.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(f"_agentguard_{path.stem}", path)
                if spec is None or spec.loader is None:
                    continue
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
            except Exception:
                continue
            fn = getattr(module, "guard", None)
            if not callable(fn):
                continue
            triggers = getattr(module, "TRIGGERS", None)
            found.append((fn, set(triggers) if triggers else None))
    return found


# --------------------------------------------------------------------------- #
# Dispatch / entry point
# --------------------------------------------------------------------------- #


def dispatch(command: str, cwd: str | None = None) -> str | None:
    """Return a deny reason for ``command``, or None to allow it."""
    if not command:
        return None
    contributed: list[tuple[Callable[[GuardContext], str | None], set[str] | None]] | None = None
    for seg in split_segments(command):
        if not seg.argv or seg.argv[0] not in GUARDED_HEADS:
            continue  # fast path — non-guarded command family
        # Bundled guards (trusted, in-process; each self-filters its command).
        for builtin in BUILTIN_GUARDS:
            try:
                reason = builtin(seg, cwd)
            except Exception:
                continue
            if reason:
                return reason
        # Contributed guards, discovered lazily once per command.
        if contributed is None:
            contributed = discover_guards()
        kinds = command_kinds(seg)
        ctx = GuardContext(seg, cwd)
        for fn, triggers in contributed:
            if triggers is not None and not (triggers & kinds):
                continue
            try:
                reason = fn(ctx)
            except Exception:
                continue
            if reason:
                return reason
    return None


def _emit_deny(reason: str) -> None:
    json.dump(
        {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": reason,
            }
        },
        sys.stdout,
    )
    sys.stdout.write("\n")


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0  # Malformed event — never break the user's shell; allow.
    if not isinstance(event, dict) or event.get("tool_name") != "Bash":
        return 0
    command = str(event.get("tool_input", {}).get("command", ""))
    cwd = event.get("cwd")
    reason = dispatch(command, cwd if isinstance(cwd, str) else None)
    if reason:
        _emit_deny(reason)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
