---
name: verify-apache-steward
description: |
  Verify that the `apache-steward` framework is correctly integrated
  into the user's adopter tracker repository — `.apache-steward/`
  directory at the tracker root, the framework checked out as a git
  submodule under `.apache-steward/apache-steward/`, the submodule
  initialised and pointer-aligned with the parent tracker's index,
  the adopter's `<project-config>` (the `.apache-steward/`
  directory itself) populated with no remaining `TODO:`
  placeholders for required fields, and the optional post-merge
  hook wired up. Reports ✓ done / ✗ missing / ⚠ partial for each
  check with concrete remediation commands. Read-only — never
  modifies the tracker, the submodule, or `<project-config>`.
when_to_use: |
  Invoke when the user says "verify apache-steward setup", "is
  the framework integrated correctly?", "check tracker setup",
  "did the submodule init?", or after bootstrapping a new
  adopter tracker per the
  [Adopting the framework](../../../README.md#adopting-the-framework)
  section. Also appropriate after a fresh `git clone` of a
  pre-configured tracker (the `.apache-steward/` is in the index
  but the submodule needs `--init`), and after a tracker
  contributor reports skills are stale or missing — the most
  common cause is a parent `git pull` that bumped the submodule
  pointer without a follow-up `git submodule update`. Do **not**
  invoke from inside the framework checkout itself; the skill
  detects that and reports it as a misuse.
---

<!-- Placeholder convention (see AGENTS.md#placeholder-convention-used-in-skill-files):
     <project-config> → adopting project's `.apache-steward/` directory -->

# verify-apache-steward

This skill is the **integration check** for adopters who consume
the `apache-steward` framework as a git submodule of their
tracker repo (the canonical pattern, documented in
[`README.md` → Adopting the framework](../../../README.md#adopting-the-framework)).
It confirms the framework is wired in correctly so the rest of
the framework's skills and tools resolve from the right paths.

The companion skill is
[`verify-secure-config`](../verify-secure-config/SKILL.md), which
verifies the *secure-agent setup* (sandbox, hooks, status line,
clean-env wrapper). The two are independent: an adopter can have
the framework correctly integrated as a submodule but no secure
setup wired (verify-secure-config catches that), or have the
secure setup wired against a stale / un-init'd framework
submodule (this skill catches that). Run both for a complete
adopter-side health check.

## Golden rules

- **Read-only.** This skill never runs `git submodule update`,
  never edits `<project-config>/project.md`, never wires the
  post-merge hook, never resets the submodule. If a check
  fails, surface the gap and the remediation command for the
  user to run; do not auto-fix.
- **Always run every check, even on early failure.** A missing
  `.apache-steward/` directory is ✗ at check 2 — but checks
  3, 4, 5 (project-config, gitmodules, submodule init) are
  still useful in their own right and might surface a
  separate problem (e.g. partial bootstrap that left
  `.apache-steward/project.md` filled but the submodule never
  added). Report every check; do not stop at the first ✗.
- **Refuse from inside the framework checkout.** If the cwd
  resolves to the framework repo itself
  (`apache/airflow-steward` per the `origin` remote, or a
  worktree of it), surface that and stop — this skill is for
  tracker repos that *consume* the framework, not for
  the framework itself. Suggest `cd <tracker-root>` and re-invoke.
- **Distinguish ✗ from ⚠.** ✗ is a structural integration
  failure (skills cannot resolve, framework path is broken,
  submodule pointer drift). ⚠ is an *intentional or
  recoverable* variant (the post-merge hook is optional;
  some `TODO:` placeholders in `project.md` are for fields
  the adopter has not yet decided about, like which mailing
  list to subscribe to). Use ⚠ for "should be done eventually
  but the framework still works"; ✗ for "skills will fail
  silently or surface stale data".

## Pre-flight: where am I?

Before running checks, resolve the cwd:

1. `git rev-parse --show-toplevel` — the current repo root.
2. Check `git remote get-url origin` — if it resolves to
   `apache/airflow-steward` (or any direct fork of the
   framework), this skill is being invoked from inside the
   framework. Surface and stop.
3. If `<repo-root>/.apache-steward/` does not exist, the user
   may be either (a) in a tracker that does not yet integrate
   the framework, or (b) in some other repo entirely. Surface
   the cwd, name what is missing, and stop with the bootstrap
   pointer.

Otherwise, the cwd is a tracker that integrates the framework —
proceed with the checks.

## The checks

### 1. `.apache-steward/` directory present

`<tracker-root>/.apache-steward/` exists and is a directory.

- ✗ if missing — the framework is not integrated. Remediation:
  follow
  [Adopting the framework](../../../README.md#adopting-the-framework)
  to copy `projects/_template/` into `<tracker-root>/.apache-steward/`
  and add the framework as a submodule under it.

### 2. `<project-config>/project.md` present and required fields filled

`<tracker-root>/.apache-steward/project.md` exists.

Then `grep -nE '^TODO:|: TODO:|^\| TODO:|`grep`-able TODO marker'`
inside `project.md` to enumerate unfilled fields. Distinguish:

- ✗ for unfilled fields the framework relies on at runtime —
  `tracker_repo:`, `upstream_repo:`, `tracker_default_branch:`
  in the `## Repositories` block; the issue-template scope
  labels in `## Issue-template fields`. The skills will fail
  to resolve placeholders without these.
- ⚠ for unfilled fields that are convenience-only or apply
  only to optional flows — mailing-list addresses (only the
  import / sync skills need them), CVE tooling URLs (only
  the allocate-cve skill), Gmail / PonyMail OAuth flags
  (only the email-using skills).

Print the unfilled-field list with line numbers so the user
can grep + edit.

### 3. `.gitmodules` has the framework entry

`<tracker-root>/.gitmodules` exists and has a `[submodule
".apache-steward/apache-steward"]` block with `path =
.apache-steward/apache-steward` and a `url =` pointing at the
upstream framework. Accept either
`https://github.com/apache/airflow-steward.git` (or `.git`
suffix omitted) or any direct ssh-style equivalent
(`git@github.com:apache/airflow-steward.git`); the canonical
remote is `apache/airflow-steward` until the future rename to
`apache/steward`, at which point this skill will accept either.

- ✗ if `.gitmodules` missing or the entry is missing —
  remediation: run `git submodule add` per the README's
  bootstrap, or add the entry by hand if the user is mid-merge.
- ⚠ if `url =` points at a fork (not directly at
  `apache/airflow-steward` / `apache/steward`) — that is
  legitimate when an adopter is testing a framework PR locally,
  but flag it so the user notices.

### 4. Submodule initialised + working tree present

`<tracker-root>/.apache-steward/apache-steward/.git` exists (it
is normally a `.git` *file* pointing into
`<tracker>/.git/modules/.apache-steward/apache-steward/`, not a
directory — both shapes are valid).

`ls <tracker-root>/.apache-steward/apache-steward/` should
list non-empty: at least `README.md`, `AGENTS.md`,
`.claude/skills/`, `tools/`. If those files are missing, the
submodule has been added in the parent's index but never
checked out.

- ✗ if the submodule directory exists but contains no files
  (the most common state after a fresh `git clone` of the
  tracker) — remediation:
  `git submodule update --init --recursive` from the tracker
  root.
- ✗ if the framework's expected top-level files are absent —
  the submodule is checked out at an unexpected commit;
  remediation: investigate, then either commit the new
  pointer in the parent or reset to the recorded SHA.

### 5. Submodule pointer aligned with parent's index

`git -C <tracker-root> submodule status .apache-steward/apache-steward`
output. The leading character classifies the state:

- a single space prefix = aligned, ✓.
- `+` prefix = the submodule's `HEAD` is *ahead of* the SHA
  recorded in the parent's index. The user has either pulled
  the framework directly without committing the new pointer
  in the parent (`upgrade-apache-steward` skill mentions this
  case), or has hand-checked-out a different SHA. Surface as
  ⚠ — the framework still works, but the parent will record
  a different pointer on the next commit. Remediation: commit
  the new pointer in the parent, or reset the submodule to
  the recorded SHA (`git -C
  .apache-steward/apache-steward checkout <sha>`).
- `-` prefix = the submodule is *not initialised* (caught
  earlier in check 4 — should not appear here if 4 already
  ran).
- `U` prefix = merge conflict in the submodule. ✗ — surface
  and stop; the user resolves manually.

### 6. Post-merge hook wired

`<tracker-root>/.git/hooks/post-merge` exists, is executable,
and contains the `git submodule update --init --recursive`
recipe.

- ⚠ if missing — strictly optional, but the adopter-facing
  README recommends it because plain `git pull` on the
  tracker only advances the submodule pointer in the index,
  not the working tree, and a stale submodule means skills
  silently run against a previous version of the framework.
  Print the one-line install recipe from the README.

## After the report

If every check is ✓, say so explicitly and stop — no further
action needed.

If anything is ✗ or ⚠, the report ends with a concrete next-
step list, ordered most → least urgent:

- ✗ on checks 1 / 3 / 4 → run the bootstrap or
  `git submodule update --init --recursive` per the README.
  These block the rest of the framework's skills.
- ✗ on check 2 (required fields unfilled) → name the specific
  fields and the line numbers in `<project-config>/project.md`
  the user must fill. These cause the framework's skills to
  fail when they try to resolve `<tracker>` / `<upstream>` /
  similar placeholders.
- ✗ on check 5 (`U` prefix, merge conflict) → resolve the
  submodule conflict; the user owns this, the skill cannot
  decide.
- ⚠ on check 5 (`+` prefix, pointer ahead) → name the
  remediation choice (commit the new pointer in the parent,
  or reset the submodule). The
  [`upgrade-apache-steward`](../upgrade-apache-steward/SKILL.md)
  skill is the natural place this state usually originates.
- ⚠ on check 6 (no post-merge hook) → print the install
  recipe and tell the user this is optional ergonomics.
- ⚠ on check 2 (optional fields unfilled) → name the
  fields, mention which skills they unlock, suggest filling
  them when the user adopts those skills.

Recommend
[`verify-secure-config`](../verify-secure-config/SKILL.md) as
the natural next-step skill if the user has not run it yet —
the two skills are independent but together cover the
adopter-side health check.
