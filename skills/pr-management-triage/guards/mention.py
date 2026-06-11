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

"""pr-management-triage mention guard (skill-contributed).

Deterministically enforces the denoise rule (Golden rule 11): author-directed
feedback never @-pings a maintainer, and the silent PR-body "fold" channel never
@-mentions anyone. Discovered by the agent-guard PreToolUse dispatcher from a
guards.d directory — see tools/agent-guard for the engine and the GuardContext
API. Import-free: everything comes from ``ctx``.
"""

TRIGGERS = ["gh"]


def guard(ctx):
    sub = ctx.gh_subcommand()
    if sub is None:
        return None
    group, name = sub
    is_pr_body_edit = (
        group == "pr"
        and name == "edit"
        and (ctx.opt("-b", "--body") is not None or ctx.opt("-F", "--body-file") is not None)
    )
    is_comment = (group == "pr" and name == "comment") or (group == "issue" and name == "comment")
    if not (is_pr_body_edit or is_comment):
        return None

    mentions = ctx.mentions(ctx.gh_body(read_files=True))
    if not mentions:
        return None
    if ctx.override("STEWARD_ALLOW_MENTIONS"):
        return None

    if is_pr_body_edit:
        return (
            "agent-guard[mention]: a `gh pr edit --body` (the silent PR-description "
            f"'fold' channel) must not @-mention anyone — found {sorted(set(mentions))}. "
            "Editing a PR body should never ping; reference logins as backticked "
            "`login`, not @login. Override (rare): prefix STEWARD_ALLOW_MENTIONS=1."
        )

    # Comment channel: only the PR/issue author may be @-mentioned.
    target = ctx.positional_after(name)
    view = "pr" if group == "pr" else "issue"
    author = None
    if target:
        author = ctx.run(
            ["gh", view, "view", target, *ctx.repo_flag(), "--json", "author", "--jq", ".author.login"]
        )
    if not author:
        return (
            "agent-guard[mention]: this author-directed comment @-mentions "
            f"{sorted(set(mentions))} but the PR/issue author could not be verified, "
            "so the guard cannot confirm none of them are maintainers. Re-run once the "
            "author is known, drop the @-mentions (use backticked `login`), or override "
            "with STEWARD_ALLOW_MENTIONS=1 if the ping is intentional."
        )
    offenders = sorted({m for m in mentions if m != author.lower()})
    if offenders:
        return (
            "agent-guard[mention]: an author-directed comment may only @-mention the "
            f"author (`{author}`); refusing to ping {offenders}. Reference other people "
            "as backticked `login` (no @) so they are not notified, or override with "
            "STEWARD_ALLOW_MENTIONS=1 for a deliberate ping."
        )
    return None
