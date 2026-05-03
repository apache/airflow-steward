<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Apache Steward (to be renamed)](#apache-steward-to-be-renamed)
  - [Skill families](#skill-families)
  - [Adopting the framework](#adopting-the-framework)
  - [Keeping the submodule current](#keeping-the-submodule-current)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

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

Reusable, project-agnostic framework for ASF-project automation.
Adopters pull this repository into their own tracker as a git
submodule and ship project-specific configuration alongside it
under `<project-config>/`.

## Skill families

The framework ships three independent skill families. **Setup** is
a prerequisite for every other family — it installs the secure
agent setup that makes the other skills safe to run against
pre-disclosure content. **Security** and **PR management** are
options the adopter picks based on what the project needs to
automate.

| Family | Purpose | Detail |
|---|---|---|
| [**setup**](docs/setup/README.md) | Isolated agent setup — sandboxing, pinned tools, framework upgrades. The prerequisite. | 6 skills, [`docs/setup/`](docs/setup/) |
| [**security**](docs/security/README.md) | 16-step security-issue handling lifecycle — from `security@` import through CVE publication. | 8 skills, [`docs/security/`](docs/security/) |
| [**pr-management**](docs/pr-management/README.md) | Maintainer-facing PR-queue management — triage, stats, deep code review. | 3 skills, [`docs/pr-management/`](docs/pr-management/) |

## Adopting the framework

Three one-time steps to integrate the framework into a new tracker
or upstream repo:

1. **Add the framework as a submodule** at
   `.apache-steward/apache-steward/`:

   ```bash
   cd path/to/your/repo
   git submodule add https://github.com/apache/airflow-steward .apache-steward/apache-steward
   ```

2. **Copy the [`projects/_template/`](projects/_template/)
   scaffold** into `.apache-steward/`, then `grep -rn TODO
   .apache-steward/` to find every placeholder you need to fill in.
   The required files vary by which skill families you adopt —
   see the per-family adopter contract in each
   [`docs/<family>/README.md`](docs/) and the file-by-file index
   in
   [`projects/_template/README.md`](projects/_template/README.md).

   ```bash
   cp -r .apache-steward/apache-steward/projects/_template/. .apache-steward/
   ```

3. **Symlink `.claude/skills/`** to the framework's skill
   directory, so Claude Code (or another `SKILL.md`-aware agent)
   loads the framework's skills against your project configuration:

   ```bash
   ln -s .apache-steward/apache-steward/.claude/skills .claude/skills
   ```

The framework's
[`setup-steward-verify`](.claude/skills/setup-steward-verify/SKILL.md)
skill checks each of these and reports `✓ done / ✗ missing /
⚠ partial` for the adopter integration — run it after step 3 to
confirm the install landed.

## Keeping the submodule current

**Always run `git submodule update --init --recursive` after every
pull on the tracker repository.** A plain `git pull` advances the
framework submodule *pointer* in the index but does **not** update
the framework's working tree — skills will run against the
*previous* version after any pull that bumped the pointer. Wire it
into a post-merge hook to make it automatic:

```bash
cat >.git/hooks/post-merge <<'SH'
#!/bin/sh
exec git submodule update --init --recursive
SH
chmod +x .git/hooks/post-merge
```

The framework's
[`setup-steward-upgrade`](.claude/skills/setup-steward-upgrade/SKILL.md)
skill upgrades the framework checkout itself; if the user is
consuming the framework as a tracker submodule, the skill reminds
them to follow up with submodule update on the parent tracker.

## Cross-references

- [`docs/prerequisites.md`](docs/prerequisites.md) — what a triager,
  remediation developer, release manager, or PR maintainer needs
  installed before invoking any framework skill (Claude Code,
  Gmail MCP, GitHub auth, browser, `uv`, etc.).
- [`AGENTS.md`](AGENTS.md) — agent instructions, placeholder
  convention, framework conventions.
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — for framework
  contributors.
- [`projects/_template/`](projects/_template/) — the adopter-
  scaffold directory you copy into `<project-config>/`.
