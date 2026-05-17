<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [JIRA bridge](#jira-bridge)
  - [Layout](#layout)
  - [Invocation](#invocation)
  - [Subcommands](#subcommands)
    - [`search <JQL>`](#search-jql)
    - [`issue <KEY>`](#issue-key)
    - [`projects`](#projects)
  - [Configuration](#configuration)
  - [Output contract](#output-contract)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# JIRA bridge

Read-only JIRA REST helpers for the `issue-*` skill family.
Adopters with JIRA-based issue trackers wire this in as their
tracker bridge; adopters using GitHub Issues or other trackers
contribute a parallel `tools/<tracker>/` directory.

The bridge is **read-only by design**. It does not post comments,
transition issues, or change fields — those mutations belong to
the skills' apply phases (which use a separate write-path with
explicit user confirmation).

## Layout

```text
tools/jira/
├── README.md          (this file)
└── bridge.groovy      (Groovy reference implementation)
```

Other languages (Python, Bash + curl) are welcome via PR.

## Invocation

```bash
groovy tools/jira/bridge.groovy <subcommand> [args]
```

The Groovy implementation uses `@Grab` for HTTP client dependencies
— no separate install step. Requires Groovy 3.x or newer on
`PATH`.

## Subcommands

### `search <JQL>`

Run a JQL query against `<issue-tracker>` and emit matching issues
as JSON to stdout:

```bash
groovy tools/jira/bridge.groovy search \
  'project = <KEY> AND status = Open AND resolution = Unresolved'
```

Output (truncated):

```json
{
  "total": 42,
  "issues": [
    {"key": "<KEY>-9999", "title": "...", "status": "Open", "components": [...], "fixVersion": "..."},
    ...
  ]
}
```

The `--limit <N>` flag caps the result count (default: 50).

### `issue <KEY>`

Fetch a single issue's full state (body, comments, attachments
list, labels, fixVersion, etc.) as JSON:

```bash
groovy tools/jira/bridge.groovy issue <KEY>-9999
```

Output is the JIRA REST `/rest/api/2/issue/<KEY>` response,
shaped for skill consumption.

### `projects`

List the JIRA projects available at the configured
`<issue-tracker>` URL. Useful during initial adoption to confirm
the project key is correct.

```bash
groovy tools/jira/bridge.groovy projects
```

## Configuration

The bridge reads its configuration from the environment:

| Variable | Notes |
|---|---|
| `ISSUE_TRACKER_URL` | required; e.g. `https://issues.apache.org/jira` |
| `ISSUE_TRACKER_PROJECT` | project key (e.g. `FOO`) |

The caller is responsible for exporting these (a skill resolves them
from [`<project-config>/issue-tracker-config.md`](../../projects/_template/issue-tracker-config.md)
and passes them in the environment). Direct file-fallback inside the
bridge is a possible future enhancement — it is **not** implemented
today; the bridge exits if `ISSUE_TRACKER_URL` is unset.

For anonymous-read trackers, no auth is required. For
authenticated reads, set `JIRA_API_TOKEN` (basic auth, base64-
encoded `email:token` per JIRA convention).

## Output contract

Every subcommand emits JSON to stdout on success, or a non-zero
exit code with a human-readable error to stderr on failure.

The output schema is documented per subcommand above. Skills
parse the JSON via standard JSON tooling — no special envelope,
no wrapper.

## Cross-references

- [`issue-triage`](../../.claude/skills/issue-triage/SKILL.md) —
  primary consumer (selector resolution + per-issue fetch).
- [`issue-reassess`](../../.claude/skills/issue-reassess/SKILL.md) —
  campaign-level consumer (pool fetch).
- [`<project-config>/issue-tracker-config.md`](../../projects/_template/issue-tracker-config.md) —
  the adopter's tracker URL + project key.
