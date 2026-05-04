<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# adopt — first-time install of apache-steward into an adopter repo

The default sub-action when the user says "adopt apache-steward".

There are two adoption shapes the skill recognises and routes
between automatically:

- **Fresh adoption (no committed lock yet).** The first
  adopter on a project. Runs the full bootstrap: pick the
  install method, fetch the snapshot, write *both* lock
  files, wire up symlinks, scaffold overrides, install
  hooks, update docs.
- **Subsequent adoption (committed lock exists).** A new
  developer joining a project that already adopted. Reads
  `<committed-lock>` to know what to install, fetches per
  that pin, writes only the `<local-lock>`, refreshes
  symlinks. Skips the doc-update + interactive-prompt flow.

> **Note on the bootstrap recipe.** `setup-steward` is **the
> only framework artefact an adopter commits**. Getting it
> *into* a fresh adopter repo is the chicken-and-egg the
> [install-recipes](../../../docs/setup/install-recipes.md)
> doc resolves: copy-pasteable shell recipes per install
> method that fetch the snapshot + place the `setup-steward`
> skill content + add `.gitignore` entries. Once that
> recipe runs and `setup-steward` is on disk, the agent
> follows this file to finish adoption.

## Inputs

- `from:<git-ref>` / `from:<version>` — explicit ref or
  version (overrides the prompt).
- `method:<git-branch | git-tag | svn-zip>` — explicit method
  (overrides the prompt).
- `skill-families:<list>` — comma-separated families to
  symlink (default: prompt).

## Step 0 — Pre-flight

1. Confirm we are in a git repo (`git rev-parse
   --show-toplevel`).
2. Confirm we are **not** in `apache/airflow-steward` itself
   (read `git remote get-url origin` and refuse if it
   resolves to the framework).
3. Detect the adopter's existing skills-dir convention by
   following [`conventions.md`](conventions.md). Pin the
   result as `<adopter-skills-dir>` for the rest of this
   flow.

## Step 1 — Detect adoption shape

```text
if .apache-steward.lock exists:
    → SUBSEQUENT adoption
elif .apache-steward/ exists (snapshot only):
    → manual recipe was run; finish bootstrap (write committed
      lock from the recipe's choices, then continue as FRESH
      from Step 5)
else:
    → FRESH adoption
```

## Step 2 — Pick install method (FRESH only)

If the user passed `method:` and `from:` flags, use those
verbatim. Otherwise, prompt:

| Method | When | Reproducibility |
|---|---|---|
| `svn-zip` | Production once ASF releases ship to dist | Frozen by version |
| `git-tag` | Pin a specific tag | Frozen by tag |
| `git-branch` | Track a branch tip (default: `main`) | Tracks tip — best during pre-release |

The verbatim shell that fetches per each method is in
[`docs/setup/install-recipes.md`](../../../docs/setup/install-recipes.md).
The skill at this point can either:

- Tell the user "your manual recipe already ran — please
  confirm the method you used, I will record it in the
  committed lock", or
- Run the per-method fetch itself if `<snapshot-dir>` does
  not yet exist.

For a SUBSEQUENT adoption (committed lock present), skip the
prompt entirely — re-use the method/url/ref from the
committed lock.

## Step 3 — Fetch the snapshot (if not already on disk)

Per the chosen method (FRESH) or per the committed lock
(SUBSEQUENT):

- **`git-branch`**: `git clone --depth=1 --branch <ref> <url>
  .apache-steward`
- **`git-tag`**: `git clone --depth=1 --branch <tag> <url>
  .apache-steward`. After clone, capture the resolved commit
  SHA for `<committed-lock>` (FRESH only).
- **`svn-zip`**: `curl` the zip + `.sha512` + `.asc`,
  verify, `unzip` to `.apache-steward/`. Re-fetch
  verification details into `<committed-lock>` (FRESH only).

If `<snapshot-dir>/` already exists with content, skip the
fetch — the recipe ran first and left the snapshot in place.

After the fetch (or skip), confirm
`<snapshot-dir>/.claude/skills/` lists the framework skills
(`pr-management-*`, `security-*`, `setup-*`). If not, the
fetch produced an unexpected layout — surface and stop.

## Step 4 — Write `<committed-lock>` (FRESH only)

Create `<repo-root>/.apache-steward.lock`:

```text
# .apache-steward.lock — committed; the project's pin.
# Edited only by /setup-steward; do not modify by hand.

method: <method>
url:    <url>

# Per-method fields:
ref:    <branch | tag | version>
# git-tag: also `commit: <SHA>`
# svn-zip: also `sha512: <hash>`
```

## Step 5 — Pick the skill families

(SUBSEQUENT adoption: re-use the families currently
symlinked, if any. Or re-prompt if none.)

If `skill-families:` was passed, use those. Otherwise,
prompt the user:

- **`security`** — eight skills for security-issue
  handling. Maintainer-only; not useful unless the project
  has a security tracker.
- **`pr-management`** — three skills for maintainer-facing
  PR queue work.
- **`setup`** *(implicit)* — always installed because the
  snapshot carries it.

Default to whichever family the user named in their
initial "adopt" request (e.g. *"adopt apache-steward for PR
triage"* → `pr-management`).

## Step 6 — Write `<local-lock>`

Always written, both FRESH and SUBSEQUENT. Records what
this machine fetched.

```text
# .apache-steward.local.lock — gitignored; per-machine.

source_method:    <method>
source_url:       <url>
source_ref:       <ref>
fetched_commit:   <commit SHA — for git-branch and git-tag>
fetched_at:       <ISO-8601 timestamp>
```

## Step 7 — `.gitignore` entries (FRESH only)

The bootstrap recipe wrote these already; this step is
idempotent — re-add them if they're missing.

```text
/.apache-steward/
/.apache-steward.local.lock
/.claude/skills/security-*
/.claude/skills/pr-management-*
/.claude/skills/setup-isolated-setup-*
/.claude/skills/setup-shared-config-sync
/.github/skills/security-*
/.github/skills/pr-management-*
/.github/skills/setup-isolated-setup-*
/.github/skills/setup-shared-config-sync
```

Mirror under `.github/skills/` only if the adopter uses the
double-symlinked convention.

## Step 8 — Wire up the framework-skill symlinks

For each skill family the user picked, walk
`<snapshot-dir>/.claude/skills/` and create a gitignored
symlink for every matching skill at
`<adopter-skills-dir>/<skill>` → relative path into
`<snapshot-dir>/.claude/skills/<skill>/`.

If the adopter uses the double-symlinked convention
(see [`conventions.md`](conventions.md)), create both
layers — the inner one in `.github/skills/` points at the
snapshot, the outer `.claude/skills/` points at the
inner. Both gitignored.

**Never overwrite an existing committed skill** of the same
name. Surface conflicts and stop.

Show the symlinks the skill is about to create, ask the
user to confirm, then create them.

## Step 9 — Scaffold `.apache-steward-overrides/` (FRESH only)

Create `<repo-root>/.apache-steward-overrides/` (directory)
with a small `README.md` inside:

```markdown
# apache-steward overrides

Agent-readable instructions that override specific steps or
behaviours of apache-steward framework skills, scoped to
this adopter repo. Each override file is named after the
framework skill it modifies (e.g. `pr-management-triage.md`
overrides the `pr-management-triage` skill).

The framework skills consult this directory at run-time
before executing default behaviour. See
[`docs/setup/agentic-overrides.md`](https://github.com/apache/airflow-steward/blob/main/docs/setup/agentic-overrides.md)
in the framework for the full contract.

**Hard rule**: never modify the snapshot under
`<repo-root>/.apache-steward/`. Local mods go here.
Framework changes go via PR to `apache/airflow-steward`.
```

This directory is **committed** (overrides ship with the
adopter repo).

## Step 9b — Scaffold `.apache-steward-overrides/user.md` (FRESH only)

Create `<repo-root>/.apache-steward-overrides/user.md` with a
project-agnostic template. The security skills read this file at
run-time to resolve per-user preferences (PMC status, local clone
paths, optional tool backends). If the file is missing, the skills
fall back to interactive prompting and offer to save the answer
back into this file.

```markdown
# Per-user configuration for apache-steward

This file is committed in the adopter repo and holds preferences
that vary per developer (GitHub handle, local clone paths, optional
tool backends). It is **not** project-specific — those facts live in
`<project-config>/project.md`. Fill in the fields that apply to your
setup; the skills skip any block that is missing or marked `TODO`.

## `role_flags`

- `pmc_member: TODO` — set to `true` if you are a PMC member of the
  adopting project. Used by `security-cve-allocate` to decide whether
  you can submit the CVE allocation form directly or need to relay
  the request to a PMC member.

## `environment`

- `upstream_clone: TODO` — absolute path to your local clone of the
  public `<upstream>` repo. Used by `security-issue-fix` when it
  writes changes and opens PRs. The skill validates that the clone
  has a remote pointing at your fork before proceeding.
- `upstream_fork_remote: TODO` — name of the git remote that points
  at your personal fork (e.g. `fork`, `your-github-handle`). If
  omitted, the skill uses the first non-`origin` remote that looks
  like a fork. Explicitly setting this avoids ambiguity when you
  have multiple remotes.

## `tools`

### `ponymail`

- `enabled: false` — set to `true` if you have registered the
  PonyMail MCP in your Claude Code `mcpServers` block. When enabled
  and authenticated, the security skills use PonyMail as the primary
  read backend for mailing-list archive queries; Gmail remains the
  fallback for just-arrived inbound mail and the only backend for
  draft composition.
- `private_lists: []` — list of private mailing-list addresses that
  PonyMail should query (e.g. `["security@<project>.apache.org"]`).
  Only used when `enabled: true`.
```

Show the file to the user and offer to fill in the `TODO` fields
interactively (one prompt per field, skipping any the user does not
yet know). After the interactive fill, write the file to disk and
git-add it.

## Step 10 — Worktree-aware post-checkout hook (FRESH only)

Install
`<repo-root>/.git/hooks/post-checkout` that re-creates the
gitignored symlinks if a fresh worktree is checked out. The
hook is a one-liner that re-invokes
`/setup-steward verify --auto-fix-symlinks`. Surface the
hook content to the user before writing.

## Step 11 — Project doc updates (FRESH only)

Add (or extend) a brief paragraph in the adopter's
`README.md` or `CONTRIBUTING.md` (whichever already mentions
agents / skills) noting:

- the project adopts apache-steward via the snapshot
  mechanism;
- a fresh clone needs `/setup-steward` to populate the
  framework before any framework skill is invocable;
- adopter-specific modifications live in
  `.apache-steward-overrides/`.

Surface the doc diff to the user before writing.

## Step 12 — Sanity check

Run [`verify.md`](verify.md)'s checklist as a final step.
Every check should be ✓ before the skill reports success.

## Output to the user

A summary of what was written:

```text
✓ Method:   <method>
✓ Source:   <url>@<ref>
✓ Snapshot: .apache-steward/ (commit <SHA>)
✓ Locks:    .apache-steward.lock (committed) + .apache-steward.local.lock (gitignored)
✓ Symlinks: <list of created symlinks>
✓ Overrides scaffold: .apache-steward-overrides/ (committed)
✓ post-checkout hook installed
✓ <repo>/README.md updated with adoption note

Committed (you'll see in `git status`):
  .gitignore
  .apache-steward.lock
  .apache-steward-overrides/README.md
  <adopter-skills-dir>/setup-steward/   (this skill itself)
  README.md (or CONTRIBUTING.md)

Gitignored (do NOT commit):
  .apache-steward/
  .apache-steward.local.lock
  .claude/skills/{security,pr-management,setup-isolated-setup,setup-shared-config-sync}-*
  (and same patterns under .github/skills/ for double-symlinked layouts)
```

Then suggest the user `git add` the committed files and open
a PR.

## Failure modes

- **Existing `<repo-root>/.apache-steward/` and
  `<committed-lock>` are out of sync** → drift; suggest
  `/setup-steward upgrade`.
- **Existing committed skill conflicts with a framework
  skill symlink** → stop, name the conflict, let the user
  resolve.
- **Network failure on the snapshot download** → stop,
  surface the curl/git error.
- **`<committed-lock>` references a method/URL the runtime
  cannot reach** (e.g. svn-zip URL 404) → surface, ask the
  user whether the project has retired that release; the
  user updates `<committed-lock>` deliberately and re-runs.
