<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Contributing](#contributing)
  - [Project structure](#project-structure)
    - [Directory tree](#directory-tree)
  - [Getting set up](#getting-set-up)
  - [Making changes](#making-changes)
  - [Running the dev loop](#running-the-dev-loop)
  - [Opening a pull request](#opening-a-pull-request)
  - [Confidentiality](#confidentiality)
  - [Authoritative references](#authoritative-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Contributing

Thanks for helping improve this repository. It is a reusable framework
for running the ASF security-disclosure process as a set of agent-driven
skills. Adopting projects ship a per-project configuration layer
(`<project-config>/`) in their own tracker repo and consume this
framework as a submodule — see [`projects/_template/`](projects/_template/)
for the scaffold an adopter copies and fills in.

Before sending a patch, please skim this file end-to-end: it lays out
the layering the repository depends on, and a patch that ignores the
layering is hard to land no matter how correct it is in isolation.

## Project structure

The tree has four layers, each with a clearly-scoped job. The invariant
is that a skill running against an adopting project should be able to
resolve every piece of context it needs from some combination of the
four — no hard-coded project assumptions anywhere.

- **Root docs** carry the cross-cutting rules every contributor, agent,
  and reviewer is expected to have read. [`README.md`](README.md) is the
  canonical 16-step handling process, from report-arrival to CVE
  publication. [`AGENTS.md`](AGENTS.md) is the editorial contract: tone,
  brevity, confidentiality, linking conventions, the placeholder
  substitution rule (`<PROJECT>`, `<tracker>`, `<upstream>`), and the
  informational-only treatment of reporter-supplied CVSS scores.
  [`how-to-fix-a-security-issue.md`](how-to-fix-a-security-issue.md) and
  [`new-members-onboarding.md`](new-members-onboarding.md) are
  human-facing guides that sit alongside those.
- **Skills** live under
  [`.claude/skills/`](.claude/skills/). Each is a `SKILL.md` that
  encodes one workflow — importing a new report, syncing a tracker
  against the world, allocating a CVE, drafting a fix PR, or
  deduplicating two trackers. Skills use the `<PROJECT>` /
  `<tracker>` / `<upstream>` placeholders everywhere and resolve them
  at runtime. They must not contain project-specific strings.
- **Config** lives under [`config/`](config/) and wires the runtime
  together.
  [`config/active-project.md`](config/active-project.md) declares which
  subtree under `projects/` is active (checked in);
  [`config/user.md`](config/README.md#what-the-user-layer-does) carries
  per-user preferences (tool access, PMC status, local clone paths) and
  is **gitignored**. Two prek hooks keep `user.md` off the remote. See
  [`config/README.md`](config/README.md) for the full tutorial.
- **Projects** live under [`projects/`](projects/), one subtree per
  supported ASF project. The active subtree holds every
  project-specific fact the skills depend on — the security model, the
  scope labels, the milestone conventions, the release trains, the
  canned reporter replies, the title-normalisation rules.
  [`projects/_template/`](projects/_template/) is the bootstrap
  scaffold for adding a new project.
- **Tools** live under [`tools/`](tools/), one subtree per external
  system the skills talk to. Each subtree is project-agnostic; it
  documents the adapter surface (search queries, threading rules, API
  semantics, state machines) in terms of placeholders that the active
  project fills in. The `vulnogram/generate-cve-json/` subtree is the
  only Python package — a `uv`-managed CLI that emits paste-ready CVE
  5.x JSON from a tracker body.

### Directory tree

```
.
├── README.md                      # Canonical 16-step handling process + conventions
├── AGENTS.md                      # Editorial rules: tone, brevity, confidentiality,
│                                  # placeholder substitution, reporter-CVSS policy
├── CONTRIBUTING.md                # This file
├── how-to-fix-a-security-issue.md # Human-facing fix guide
├── new-members-onboarding.md      # Human-facing onboarding guide
│
├── .claude/
│   └── skills/                    # Agent workflows (invoked via the Skill tool)
│       ├── import-security-issue/SKILL.md
│       ├── import-security-issue-from-pr/SKILL.md
│       ├── sync-security-issue/SKILL.md
│       ├── allocate-cve/SKILL.md
│       ├── fix-security-issue/SKILL.md
│       ├── deduplicate-security-issue/SKILL.md
│       └── invalidate-security-issue/SKILL.md
│
├── config/                        # Runtime configuration layer
│   ├── README.md                  # Configuration tutorial + placeholder rule
│   ├── active-project.md          # Declares active_project (checked in)
│   ├── user.md                    # Per-user — gitignored, auto-bootstrapped by prek
│   ├── user.md.template           # Bootstrap template with TODOs
│   └── user.md.example            # Filled-in example
│
├── projects/                      # Templates for adopting projects' configs
│   └── _template/                 # Scaffold for bootstrapping a new project's
│                                  # `<project-config>/` (the per-project layer
│                                  # an adopter ships in their tracker repo).
│                                  # Files: project.md (manifest), security-model.md,
│                                  # canned-responses.md, release-trains.md,
│                                  # milestones.md, scope-labels.md, naming-
│                                  # conventions.md, title-normalization.md,
│                                  # fix-workflow.md, README.md — all stubbed
│                                  # with TODO placeholders.
│
├── tools/                         # Project-agnostic adapters per external system
│   ├── gmail/
│   │   ├── tool.md                # Adapter overview
│   │   ├── operations.md          # MCP call signatures + no-update-no-delete rule
│   │   ├── threading.md           # threadId and subject-matched fallback
│   │   ├── search-queries.md      # Canonical reusable query templates
│   │   ├── ponymail-archive.md
│   │   └── asf-relay.md
│   ├── github/
│   │   ├── tool.md
│   │   ├── operations.md
│   │   ├── labels.md
│   │   ├── issue-template.md
│   │   └── project-board.md       # GraphQL introspection + column-move recipe
│   ├── vulnogram/
│   │   ├── tool.md
│   │   ├── record.md              # DRAFT / REVIEW / PUBLIC state machine
│   │   ├── allocation.md
│   │   └── generate-cve-json/     # Python package (uv-managed CLI)
│   │       ├── pyproject.toml
│   │       ├── src/generate_cve_json/
│   │       ├── tests/
│   │       ├── SKILL.md
│   │       └── README.md
│   └── cve-org/
│       └── tool.md                # MITRE CVE Services v2 publication check
│
├── .pre-commit-config.yaml        # prek hooks: doctoc, EOF, forbid/bootstrap
│                                  # user.md, ruff/mypy/pytest for generate-cve-json
└── .github/                       # CI: pre-commit.yml, zizmor.yml, ISSUE_TEMPLATE
```

## Getting set up

You need three tools on your machine:

- **`uv`** — the Python runner used for `generate-cve-json`. Install via
  `curl -LsSf https://astral.sh/uv/install.sh | sh` or your package
  manager.
- **`prek`** — the `pre-commit`-compatible hook runner. Install via
  `uv tool install prek` or `pipx install prek`.
- **`gh` CLI** — needed to drive tracker reads (and, later, writes) if
  you plan to run any of the skills end-to-end. `brew install gh` or
  platform equivalent.

First-time clone:

```bash
git clone git@github.com:<tracker>.git
cd <tracker-repo-name>
prek install                   # wire the hooks into .git/hooks
prek run --all-files           # runs every hook on every file; does a
                               # one-time bootstrap of config/user.md
                               # from the template
```

The `bootstrap-user-config` hook will create
[`config/user.md`](config/README.md#what-the-user-layer-does) on the
first run. Open it, grep for `TODO`, and fill in the lines that apply
to your setup. The file is gitignored; a second hook
(`forbid-user-config`) refuses any commit that stages it, so you
cannot accidentally publish your local configuration.

Read [`config/README.md`](config/README.md) for the end-to-end
configuration tutorial, including the placeholder convention and how
the skills consume both layers.

## Making changes

Think about **which layer the change belongs in** before you start
editing:

| You want to change … | Edit under … |
|---|---|
| A step of the disclosure process that applies to every project | [`README.md`](README.md) |
| An editorial / confidentiality / style rule | [`AGENTS.md`](AGENTS.md) |
| Anything project-specific (canned reply, milestone convention, scope label, release-train state) | the adopter's own `<project-config>/` (lives in their tracker repo, not here) |
| An adapter surface for an external system (a new Gmail search template, a new GraphQL recipe, a new `gh` invocation, a new CVE-tool endpoint) | the matching [`tools/<system>/`](tools/) subtree |
| A skill's workflow | [`.claude/skills/<name>/SKILL.md`](.claude/skills/) |
| Bootstrap scaffolding for a new project | [`projects/_template/`](projects/_template/) |

Rules of thumb for each layer:

- **Root docs and skills are project-agnostic.** Never paste concrete
  names like `<upstream>` or `<tracker>` into them. Use
  the placeholders `<PROJECT>`, `<tracker>`, `<upstream>` in backticked
  labels. URL targets in markdown links can point at concrete paths so
  the links stay clickable during review — the placeholder lives in
  the visible label only. The convention is documented in
  [`AGENTS.md`](AGENTS.md) and enforced by reviewer taste.
- **Tool adapters are project-agnostic.** If a recipe varies per
  project (different Gmail domains, different GitHub org, different
  board node IDs), the adapter declares variables and the active
  project's [`project.md`](<project-config>/project.md) fills them.
- **An adopter's `<project-config>/` carries concrete names freely** —
  it exists for exactly that. The adopter's own per-project files can
  reference their `<upstream>` repo directly, paste concrete package
  versions, name release managers, etc. — none of that lives in this
  framework repo.
- **Skills never mutate state without user confirmation.** If you add
  a new action, write the proposal/confirm/apply shape into the skill
  and the guardrails into `AGENTS.md`. See the existing skills for
  the pattern.

## Running the dev loop

Every change should pass `prek run --all-files` locally before you
open a PR — CI runs the same config. The hook set:

- `doctoc` regenerates TOCs on every `.md` file (except skill `SKILL.md`
  files, which keep YAML frontmatter at the top);
- `end-of-file-fixer`, `trailing-whitespace`, `mixed-line-ending`,
  `check-merge-conflict`, `detect-private-key` — standard hygiene;
- `forbid-user-config` — refuses any commit that stages
  `config/user.md`;
- `bootstrap-user-config` — creates `config/user.md` from the template
  on first run;
- `ruff check` / `ruff format --check` / `mypy` / `pytest` against the
  `tools/vulnogram/generate-cve-json/` Python package.

For the Python package directly:

```bash
cd tools/vulnogram/generate-cve-json
uv run pytest                  # unit tests
uv run ruff check              # lint
uv run ruff format             # auto-format (check-only in CI)
uv run mypy                    # type-check
```

The package is invoked by the [`sync-security-issue`](.claude/skills/sync-security-issue/SKILL.md)
and [`allocate-cve`](.claude/skills/allocate-cve/SKILL.md) skills via
`uv run --project tools/vulnogram/generate-cve-json generate-cve-json
<N> --attach` from the repo root — that is the canonical invocation
any new behaviour has to stay compatible with.

## Opening a pull request

- **Base branch:** `main`. Do not open PRs against any other branch
  unless explicitly coordinated.
- **Scope:** keep one concern per PR. A skill-behaviour change, a
  tool-adapter addition, and a doc update should land as separate PRs.
- **Commit message shape:** imperative-present subject, ≤72 chars,
  plain prose body explaining *why*. Look at
  [recent merged commits](https://github.com/apache/airflow-steward/commits/main)
  for the cadence.
- **PR description:** one `## Summary` section with 1–3 bullets of
  *what changed and why*, and one `## Test plan` section listing how
  you verified the change.
- **CI:** `prek run --all-files` must pass. `zizmor` (GitHub Actions
  linting) must pass. Both run automatically on every PR.
- **Reviews:** at least one approval from a repo collaborator. Any
  change that edits [`AGENTS.md`](AGENTS.md) or the skill files should
  get an extra set of eyes because those ripple into every future
  sync.

## Confidentiality

This repository is private — only security-team members can read its
tracker contents. The repo's *contents* (issue bodies, comments,
labels, rollup entries, severity assessments) must never appear on
a public surface. The repo's *identifiers* (URLs, `#NNN`) are
public-safe and may be cross-referenced from public PRs, reporter
emails, and advisory text — see the
[Confidentiality of the tracker repository](AGENTS.md#confidentiality-of-the-tracker-repository)
section of `AGENTS.md` for the three-layer rule. Practical rules:

- A `<tracker>` URL or `#NNN` reference may appear in a public PR
  description as a cross-reference identifier, **so long as the
  surrounding text does not characterise the change as a security
  fix** (no `CVE-`, no *"vulnerability"* / *"security fix"* /
  *"advisory"* phrasing) before the advisory ships.
- Never paste tracker comment text, label transitions, or body
  excerpts into a public surface — those are *contents*, not
  identifiers.
- Never put reporter-identifying information into a `<upstream>` PR.
- When sharing a tracker URL with an external reporter, pair it with
  a one-line note that the link is an identifier-only reference (the
  page will 404 for them, and that is expected).
- Reporter-supplied CVSS scores are informational only. The security
  team scores independently during CVE allocation. Full rationale in
  [`AGENTS.md`](AGENTS.md).
- `config/user.md` stays gitignored. If you need to share a snippet
  with someone, paste it in chat — do not commit it.

Anything you are unsure about, stop and ask on `security@apache.org`
before pushing.

## Authoritative references

When this file and a layer-specific doc disagree, the layer-specific
doc wins. Re-read it first:

- [`README.md`](README.md) — the 16-step disclosure process.
- [`AGENTS.md`](AGENTS.md) — editorial and confidentiality rules.
- [`config/README.md`](config/README.md) — configuration layer tutorial.
- [`projects/README.md`](projects/README.md) — current-projects index
  and the new-project bootstrap path.
- [`projects/_template/`](projects/_template/) — scaffold to clone when
  adding a new project.
- [`.claude/skills/<name>/SKILL.md`](.claude/skills/) — the workflow
  spec each skill enforces.
