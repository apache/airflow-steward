<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Tool: GitHub](#tool-github)
  - [What this tool provides](#what-this-tool-provides)
  - [When to replace this tool with another](#when-to-replace-this-tool-with-another)
  - [Confidentiality note](#confidentiality-note)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Tool: GitHub

This directory documents the **GitHub** tool adapter — the set of
capabilities the skills use when the adopting project declares GitHub
as its issue-tracking / source-control / project-board backend.

A project opts into this tool by naming it in its manifest under
*Tools enabled*. For the adopting project see
[`../../<project-config>/project.md`](../../<project-config>/project.md#tools-enabled).

## What this tool provides

The skills use GitHub for five distinct capabilities. Each has its own
reference file in this directory:

| Capability | File | What it covers |
|---|---|---|
| CLI / API operations | [`operations.md`](operations.md) | `gh` CLI + `gh api` recipes the skills invoke (issue edit, milestone create, label edit, comment post, PR create, collaborator lookup, auth sanity check) |
| Issue-body schema | [`issue-template.md`](issue-template.md) | The body-field schema pattern: skills read named `### <field>` sections from the issue body; the per-project field names are declared in the project manifest |
| Lifecycle labels | [`labels.md`](labels.md) | Generic lifecycle-label taxonomy (`needs triage`, `cve allocated`, `pr created`, `pr merged`, `fix released`, `announced - emails sent`, `announced`, closing dispositions) |
| Project board (Projects V2) | [`project-board.md`](project-board.md) | GraphQL introspection + `updateProjectV2ItemFieldValue` pattern; per-project node IDs live in the project manifest |
| Credentials | [`operations.md#authentication`](operations.md#authentication) | `gh auth status` pre-flight that every skill's Step 0 runs |

## When to replace this tool with another

The generic skills are written around an abstract *"issue tracker with
body fields, labels, milestones, comments, a project board, and a
CLI"*. Any backend that provides those primitives can be plugged in by:

1. Creating a sibling `tools/<name>/` directory with the same files
   (`tool.md`, `operations.md`, `issue-template.md`, `labels.md`,
   `project-board.md` — the last only if the backend has a board-
   equivalent).
2. Listing that tool in the project's manifest under *Tools enabled*.
3. Declaring the backend-specific values (repo slug / project key / URL
   templates / field names / board IDs) in the project manifest.

A JIRA adapter, for instance, would replace:

- `gh issue view/edit/create/comment` with JIRA REST calls;
- body-field `### <name>` sections with JIRA custom fields;
- GitHub labels with JIRA labels (or component / status, depending on
  how the project chooses to model lifecycle);
- Projects V2 columns with JIRA workflow states.

The generic skill logic — *"when CVE is allocated, move the tracker's
status column / workflow state to `CVE allocated`"* — does not change
when the tool changes.

## Confidentiality note

Some of the recipes below operate on the **private** tracker repo
(e.g. `<tracker>` for the adopting project) and others on a
public repo (e.g. `<upstream>`). The confidentiality rules in
[`../../AGENTS.md`](../../AGENTS.md) still bind regardless of which
tool is in use: anything that lands on a public surface must be
scrubbed for the project's private-tracker URLs, CVE IDs, and
security-nature signals.
