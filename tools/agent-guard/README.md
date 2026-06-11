<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [agent-guard](#agent-guard)
  - [Guards](#guards)
  - [Per-command overrides](#per-command-overrides)
  - [Wiring](#wiring)
  - [Tests](#tests)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# agent-guard

**Capability:** capability:setup

A deterministic Claude Code [`PreToolUse`](https://code.claude.com/docs/en/hooks)
guard dispatcher. It inspects every `Bash` command **before it runs** and
**denies** the ones that would break a hard framework rule — protections that
must not depend on the model remembering a `SKILL.md` instruction.

It is **stdlib-only** and is invoked directly as
`python3 <path>/agent_guard/__init__.py` (never via `uv run`) so it returns in a
few milliseconds for any command that is not a guarded `gh` / `git commit` /
`git push`.

## Guards

| Guard | Blocks | Rule it enforces |
|---|---|---|
| `mention` | `gh pr comment` / `gh issue comment` that `@`-mentions anyone other than the PR/issue author; **any** `@`-mention in `gh pr edit --body[-file]` (the silent "fold" channel) | denoise: author-directed feedback never pings maintainers; body edits stay silent |
| `commit-trailer` | `git commit` whose message contains `Co-Authored-By:` | AGENTS.md: agents use a `Generated-by:` trailer, never co-author |
| `mark-ready` | adding the `ready for maintainer review` label while the PR head SHA has GitHub Actions runs awaiting approval | pr-management-triage Golden rule 1b |
| `security-language` | a CVE id or security-fix language in a **public** `gh pr create` / `gh pr edit` title/body (not comments) | security-issue-fix public-PR scrubbing |
| `empty-rebase` | `git push --force[-with-lease]` of a branch with 0 commits over its base | an empty push to a PR head auto-closes it + revokes write |

A denied command is **not** posted/run; the model is shown the reason and the
deterministic fix (e.g. "use a backtick `` `login` `` instead of `@login`").

## Per-command overrides

Each guard is overridable by a **visible inline env assignment** so a maintainer
can consciously proceed:

```bash
STEWARD_ALLOW_MENTIONS=1     gh pr comment 123 --body "@reviewer please take another look"
STEWARD_ALLOW_COAUTHOR=1     git commit -m "…"            # not for AI co-authorship
STEWARD_ALLOW_MARK_READY=1   gh pr edit 123 --add-label "ready for maintainer review"
STEWARD_ALLOW_SECURITY_LANG=1 gh pr create --title "…"    # disclosure already public
STEWARD_ALLOW_EMPTY_PUSH=1   git push --force …
STEWARD_GUARD_OFF=1          <any command>                # disable all guards once
```

`STEWARD_READY_LABEL` overrides the label string the `mark-ready` guard watches
for (default `ready for maintainer review`).

## Wiring

The guard is registered as a `PreToolUse` hook on the `Bash` matcher in
`.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          { "type": "command", "command": "python3 \"$CLAUDE_PROJECT_DIR/.claude/hooks/agent-guard.py\"", "timeout": 30 }
        ]
      }
    ]
  }
}
```

`/magpie-setup` ships `agent_guard/__init__.py` as a single self-contained file
into the adopter tree (`.claude/hooks/agent-guard.py`) and into the user-scope
secure setup (`~/.claude/scripts/agent-guard.py`); `/magpie-setup upgrade`,
`verify`, and the `setup-isolated-setup-install` / `…-update` skills keep it and
the settings.json entry in sync. See those skills for the exact steps.

## Tests

```bash
uv run --project tools/agent-guard pytest
```

Table-driven tests feed synthetic `PreToolUse` events to `dispatch()` and assert
allow vs. deny. The `gh` / `git` lookups the guards make are monkeypatched.
