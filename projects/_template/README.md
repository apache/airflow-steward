<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [New project — TODO: replace with `<Project Name>`](#new-project--todo-replace-with-project-name)
  - [What each file is for](#what-each-file-is-for)
    - [Authoritative manifest (fill this in first)](#authoritative-manifest-fill-this-in-first)
    - [Release state](#release-state)
    - [Scope + product mapping](#scope--product-mapping)
    - [Security-model references](#security-model-references)
    - [CVE-allocation mechanics](#cve-allocation-mechanics)
    - [Remediation workflow](#remediation-workflow)
    - [Editorial + reporter-facing](#editorial--reporter-facing)
  - [Checklist after copying](#checklist-after-copying)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# New project — TODO: replace with `<Project Name>`

Skeleton directory for a new project under this framework. **Do not
edit the template in place**; copy it to `projects/<name>/` and fill
in every `TODO` placeholder:

```bash
# From the repo root:
cp -R projects/_template projects/<name>
$EDITOR projects/<name>/project.md
grep -rn TODO projects/<name>     # work through the remaining TODOs
```

The `_template` prefix keeps this directory out of the way of the
active-project resolver (the skills only load `projects/<active>/`,
so a directory that starts with `_` is never accidentally picked up).

## What each file is for

Once you have copied the template and renamed the directory, update
this `README.md` to be your project's **file index**. The template
below mirrors the structure of
[`../airflow/README.md`](../airflow/README.md); delete the sections
your project does not need and fill in the rest.

### Authoritative manifest (fill this in first)

| File | Purpose |
|---|---|
| [`project.md`](project.md) | **Project manifest.** Identity, repositories, mailing lists, tools enabled, CVE tooling, GitHub project-board + issue-template field declarations. The single file every skill reads to resolve project-scoped references. |

### Release state

| File | Purpose |
|---|---|
| [`release-trains.md`](release-trains.md) | Active release branches, release-manager attribution per cut, rotation rosters, security-team roster. |
| [`milestones.md`](milestones.md) | Milestone naming conventions + create-and-assign recipe. |

### Scope + product mapping

| File | Purpose |
|---|---|
| [`scope-labels.md`](scope-labels.md) | Scope label → CVE product / `packageName` / collection-URL mapping. Exactly one scope label per tracker. |

### Security-model references

| File | Purpose |
|---|---|
| [`security-model.md`](security-model.md) | Authoritative URL for the project's Security Model + known-useful anchors + drafting rule. |

### CVE-allocation mechanics

| File | Purpose |
|---|---|
| [`title-normalization.md`](title-normalization.md) | Regex cascade the `allocate-cve` skill applies to tracker titles before pasting them into the CVE-tool allocation form. |

### Remediation workflow

| File | Purpose |
|---|---|
| [`fix-workflow.md`](fix-workflow.md) | Fork / clone / toolchain specifics, backport-label policy, commit-trailer wording, PR scrubbing, private-PR fallback. |

### Editorial + reporter-facing

| File | Purpose |
|---|---|
| [`naming-conventions.md`](naming-conventions.md) | Project-specific editorial rules. Keep only the ones that differ from the generic rules in `../../AGENTS.md`. |
| [`canned-responses.md`](canned-responses.md) | Reusable reporter-facing reply templates. |

## Checklist after copying

- [ ] `cp -R projects/_template projects/<name>` done.
- [ ] Every `TODO` in `project.md` resolved (grep: `grep -n TODO projects/<name>/project.md`).
- [ ] `scope-labels.md` lists at least one scope label (exactly-one-of rule).
- [ ] `security-model.md` points at the project's authoritative Security-Model URL.
- [ ] `release-trains.md` has at least one current release branch + its RM.
- [ ] `canned-responses.md` has at least the *"Confirmation of receiving the report"* template filled in (the `import-security-issue` skill sends this verbatim).
- [ ] `config/active-project.md` updated to the new directory name if this working tree should target the new project.
- [ ] Root `README.md` *"Current projects"* table updated with a row for the new project + a link to this `README.md`.
- [ ] `prek run --all-files` passes.

## Cross-references

- [`../README.md`](../README.md) — framework-level *"Current
  projects"* view + bootstrap walk-through.
- [`../../config/active-project.md`](../../config/active-project.md) —
  the selector that picks which project under `projects/` the skills
  load.
- [`../airflow/`](../airflow/) — a fully-populated example to
  reference while filling in your own project.
