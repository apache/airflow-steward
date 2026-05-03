<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Apache Steward (to be renamed)](#apache-steward-to-be-renamed)
  - [How adoption works](#how-adoption-works)
  - [Adopting the framework](#adopting-the-framework)
  - [Skill families](#skill-families)
  - [Maintenance](#maintenance)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# Apache Steward (to be renamed)

> **Heads-up — rename in flight, name not yet chosen.** This
> repository is currently served from `apache/airflow-steward`
> and is going to be renamed to a **different** name — *not*
> `apache/steward`. The current name carries `airflow` for
> legacy reasons, but the framework is project-agnostic (it
> stewards multiple ASF project workflows, not just Airflow's),
> so the working group steering it will pick a new name that
> reflects that. The final name will be chosen by **discussion
> followed by a poll** among the working-group members.
>
> **Current candidate names** (the list is open for additions
> during the **week of 4–9 May 2026**, after which the poll
> opens):
>
> - Apache Mentor
> - Apache Reeve
> - Apache Guild
> - Apache Minerva
> - Apache Magpie
> - Apache Beacon
> - Apache Compass
> - Apache Lexicon
> - Apache Polyglot
>
> Until the rename lands on the GitHub side, every clone URL,
> git-submodule reference, and CI integration still uses the
> legacy `apache/airflow-steward` slug — all path examples in
> this README and the linked docs use that slug verbatim. The
> rename will only change the GitHub repository slug; existing
> checkouts will keep working with a single `git remote set-url`.

A reusable, project-agnostic framework for ASF-project automation.
Currently in development for ASF projects + Python Core team
friendlies. **Not** a public marketplace skill — adoption is by
invitation while the framework is pre-release; once we ship via
the [ASF release policy](https://www.apache.org/legal/release-policy.html),
the marketplace path opens up. See
[release-distribution](https://infra.apache.org/release-distribution.html)
for the canonical distribution mechanism we will adopt.

## How adoption works

The framework uses a **snapshot + agentic-override** adoption
model. An adopter project commits a single skill —
[`setup-steward`](.claude/skills/setup-steward/SKILL.md) —
into their repo. That skill manages everything else:

1. **Snapshot.** `setup-steward` downloads the framework into
   a **gitignored** `<adopter>/.apache-steward/` directory.
   The snapshot is a build artefact, not source — refreshed
   by `/setup-steward upgrade`, never committed.
2. **Symlinks.** `setup-steward` symlinks the framework's
   skills (security, pr-management, the rest of setup) into
   the adopter's existing skill directory, matching whichever
   convention the adopter uses (flat `.claude/skills/`, or the
   double-symlink `.claude/skills/<n>` → `.github/skills/<n>/`
   pattern apache/airflow uses). The symlinks are **also
   gitignored** — they target the gitignored snapshot, so they
   would dangle on a fresh clone before `/setup-steward` runs.
3. **Overrides.** Adopter-specific modifications to framework
   workflows live as agent-readable markdown under
   `<adopter>/.apache-steward-overrides/<skill>.md`,
   **committed** in the adopter repo. The framework's skills
   consult those files at run-time and apply the overrides
   before executing default behaviour. See
   [`docs/setup/agentic-overrides.md`](docs/setup/agentic-overrides.md)
   for the contract.

**No git submodules. No marketplace. No vendored copies of
framework skills.** Just one committed skill (the bootstrap),
a gitignored snapshot, and agent-readable override files.

## Adopting the framework

Tell your agent: **"adopt apache/airflow-steward in my repo"**.

The agent should:

1. Read this README (you're here).
2. Copy the
   [`setup-steward`](.claude/skills/setup-steward/SKILL.md)
   skill from this framework into your repo's skill directory,
   matching your existing convention (flat `.claude/skills/` or
   the double-symlinked pattern — see
   [`conventions.md`](.claude/skills/setup-steward/conventions.md)).
   This is the **only** framework artefact the adopter commits.
3. Invoke `/setup-steward` to do the rest:

   - download the snapshot into `.apache-steward/` (gitignored),
   - create symlinks in your skill directory for the families
     you pick (security and/or pr-management),
   - scaffold `.apache-steward-overrides/` (committed),
   - update your repo's `.gitignore`,
   - install a `post-checkout` git hook so worktrees re-create
     the gitignored symlinks automatically,
   - update your project documentation with a brief mention.

After the skill finishes, you commit the small, focused
diff — the bootstrap skill, the `.gitignore` entries, the
overrides scaffold, the doc note — and you're done. Open a PR.

## Skill families

Three skill families ship in the framework. Pick whichever the
adopter wants to use; symlinks for the picked families land in
the adopter's skill directory.

| Family | Purpose | Detail |
|---|---|---|
| [**setup**](docs/setup/README.md) | Isolated agent setup, framework adoption + maintenance, shared-config sync. The prerequisite — at minimum the `setup-steward` skill itself runs out of this family. | 6 skills, [`docs/setup/`](docs/setup/) |
| [**security**](docs/security/README.md) | 16-step security-issue handling lifecycle — from `security@` import through CVE publication. Maintainer-only. | 8 skills, [`docs/security/`](docs/security/) |
| [**pr-management**](docs/pr-management/README.md) | Maintainer-facing PR-queue management — triage, stats, deep code review. | 3 skills, [`docs/pr-management/`](docs/pr-management/) |

## Maintenance

After the initial adoption, the same skill handles ongoing
maintenance:

- `/setup-steward upgrade` — refresh the snapshot to a newer
  framework version + reconcile any overrides against the new
  framework structure.
- `/setup-steward verify` — read-only health check (snapshot
  intact, symlinks live, `.gitignore` correct, etc.).
- `/setup-steward override <framework-skill>` — open or
  scaffold an override file for a framework skill.

## Cross-references

- [`docs/setup/agentic-overrides.md`](docs/setup/agentic-overrides.md) — the contract between adopters who write overrides and framework skills that read them.
- [`docs/prerequisites.md`](docs/prerequisites.md) — what a maintainer needs installed before invoking any framework skill (Claude Code, Gmail MCP, GitHub auth, browser, `uv`, etc.).
- [`AGENTS.md`](AGENTS.md) — agent instructions, placeholder convention, framework conventions.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — for framework contributors.
