<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Apache Airflow: release-management configuration](#apache-airflow-release-management-configuration)
  - [Identifiers](#identifiers)
  - [Distribution URLs](#distribution-urls)
  - [Signing](#signing)
  - [Vote](#vote)
  - [Announce](#announce)
  - [Archive](#archive)
  - [Audit log](#audit-log)
  - [Category-X dependency denylist](#category-x-dependency-denylist)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Apache Airflow: release-management configuration

**This file is a placeholder ahead of the release-management skill
family landing.** None of the `release-*` skills exist in the
framework yet (the family is proposed per
[`docs/release-management/README.md`](../../docs/release-management/README.md)
and [`docs/modes.md`](../../docs/modes.md#drafting)). The keys
below match the
[release-management spec](../../docs/release-management/spec.md#adopter-contract)
and are the values the future skills will read. New adopters
should copy this file into their own
`<project-config>/release-management-config.md` and replace every
Airflow-specific value with their project's equivalents.

This file is the *family-wide* contract. Three related scaffolds
ship in the same adopter directory and are referenced from here:

- [`release-build.md`](release-build.md), build invocation,
  expected artefact list, digest set, binary-exclude rules.
- [`release-trains.md`](release-trains.md), existing scaffold,
  shared with the security family (release-train identity).
- [`pmc-roster.md`](pmc-roster.md), PMC member roster used by
  `release-vote-tally` to classify binding vs non-binding votes.
- [`site-repo.md`](site-repo.md), site-bump PR target for
  `release-announce-draft`.

## Identifiers

| Key | Value |
|---|---|
| `project_dist_name` | `airflow` |
| `release_planning_issue_template` | `<project-config>/release-planning-issue.md` |
| `release_branch_base` | `main` |
| `version_manifest_files` | `setup.cfg`, `airflow/__init__.py` |

## Distribution URLs

| Key | Value |
|---|---|
| `release_dist_url_template` | `https://dist.apache.org/repos/dist/<bucket>/airflow/<version>/` |
| `archive_url_template` | `https://archive.apache.org/dist/airflow/` |

`<bucket>` resolves to `dev` (staging) or `release` (promoted)
depending on the lifecycle step the skill is executing.

## Signing

| Key | Value |
|---|---|
| `keys_file_url` | `https://dist.apache.org/repos/dist/release/airflow/KEYS` |
| `keyserver` | `keys.openpgp.org` |
| `rm_key_fingerprint` | *(per-RM; lives in `.apache-steward-overrides/user.md` under `release_manager.gpg_fingerprint`)* |

The agent never reads or stores the private key half. The
fingerprint is the only signing-related value the skill consumes;
it uses the fingerprint to fetch the *public* counterpart from the
keyserver and verify that the matching public block already
appears in `KEYS` (or draft a `KEYS` diff to add it via
`release-keys-sync`).
See
[spec § Boundary 1](../../docs/release-management/spec.md#boundary-1-agent-never-holds-the-rms-signing-key).

## Vote

| Key | Value |
|---|---|
| `vote_dev_list` | `dev@airflow.apache.org` |
| `mail_archive` | `ponymail` |
| `mail_archive_url_template` | `https://lists.apache.org/list.html?dev@airflow.apache.org` |
| `vote_window_hours` | `72` |
| `vote_pass_rule_overrides` | *(none, uses ASF baseline: 3 binding +1 minimum, more binding +1 than -1)* |
| `vote_subject_template` | `[VOTE] Release Apache Airflow <version> from <version>-rcN` |
| `result_subject_template` | `[RESULT] [VOTE] Release Apache Airflow <version> from <version>-rcN` |

The configured `vote_window_hours` is a floor per
[`release-policy.html § release approval`](https://www.apache.org/legal/release-policy.html#release-approval).
Projects may extend (e.g. `120` for a longer window) but not
shorten.

`vote_pass_rule_overrides` can only *strengthen* the baseline
(e.g. require 5 binding +1 instead of 3). Attempts to weaken the
baseline are refused by `release-vote-tally`.

## Announce

| Key | Value |
|---|---|
| `announce_list` | `announce@apache.org` |
| `announce_cc_lists` | `dev@airflow.apache.org`, `users@airflow.apache.org` |
| `announce_subject_template` | `[ANNOUNCE] Apache Airflow <version> released` |
| `site_repo` | `apache/airflow-site` |
| `site_pr_files` | `landing-pages/site/content/en/_index.md`, `landing-pages/site/content/en/announcements/<version>.md` |

`announce@apache.org` is mandatory for ASF TLP releases per
[`release-policy.html § announcements`](https://www.apache.org/legal/release-policy.html#release-announcements).
Non-ASF adopters replace `announce_list` with their project's
equivalent (a public-announce mailing list, a Discord channel,
a static-site post, etc.) and drop ASF-only fields.

## Archive

| Key | Value |
|---|---|
| `archive_retention_rule` | `latest_of_each_supported_line` |

Default per
[`release-distribution`](https://infra.apache.org/release-distribution.html):
only the latest version of each supported release line stays on
`dist/release/`; older versions move to `archive.apache.org`.
Projects with longer support windows can name additional lines
to retain (e.g. `2.x-stable`), but cannot remove the latest-of-
each-line floor.

## Audit log

| Key | Value |
|---|---|
| `audit_log_path` | `<adopter-repo>/audit/releases/` |

`release-audit-report` appends one markdown record per release at
`<audit_log_path>/<version>.md`. The append is proposed as a PR
on the adopter repo, never committed directly.

## Category-X dependency denylist

| Key | Value |
|---|---|
| `category_x_dependencies` | *(empty for the template, populated per project)* |

The release-prepare skill refuses to advance the prep PR if any
identifier in this list appears in the dependency tree of the
target version. The list is the project's curated subset of the
[ASF licensing-howto Category-X list](https://www.apache.org/legal/resolved.html#category-x);
the broader Category-X list itself is consulted by the skill as a
fallback, but the per-project list is the source of truth for
denial. Reviewing and updating this list is the PMC's
responsibility, not the skill's.

Example shape (replace with the project's actual entries):

```yaml
category_x_dependencies:
  - "com.example:gpl-licensed-lib"   # GPL-2.0, Category-X
  - "another-pkg::cc-by-nc"          # CC-BY-NC, Category-X
```
