<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [TODO: `<Project Name>` — repo-health audit configuration](#todo-project-name--repo-health-audit-configuration)
  - [`ci_runner_audit` — GitHub-hosted runner label audit](#ci_runner_audit--github-hosted-runner-label-audit)
  - [`workflow_security_audit` — GitHub Actions security findings (zizmor)](#workflow_security_audit--github-actions-security-findings-zizmor)
  - [`dependency_audit` — dependency vulnerability and freshness audit](#dependency_audit--dependency-vulnerability-and-freshness-audit)
  - [`license_compliance_audit` — SPDX header and NOTICE compliance](#license_compliance_audit--spdx-header-and-notice-compliance)
  - [`flaky_test_triage` — flaky-test detection from CI run history](#flaky_test_triage--flaky-test-detection-from-ci-run-history)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# TODO: `<Project Name>` — repo-health audit configuration

Per-project switches for the repo-health audit family
(`docs/repo-health/README.md` — see the family overview once the
`repo-health-family-spec` PR merges).
Copy this file into your `<project-config>/` directory, rename it
`repo-health-config.md`, and fill in every `TODO` comment.  Leave
a key at its default value by keeping the shipped default; remove a
section entirely only if the corresponding skill will never run for
this project.

Each skill reads only its own sub-key (`repo_health.<skill_key>`) and
ignores the rest — adding a key for a skill that is not yet enabled does
no harm.

---

## `ci_runner_audit` — GitHub-hosted runner label audit

```yaml
repo_health:
  ci_runner_audit:
    # Runner label families the skill flags as obsolete.
    # The list below matches GitHub's current deprecation schedule.
    # Add entries if your project pins labels not on this list; remove
    # entries to suppress a class of finding.
    # TODO: review against https://github.com/actions/runner-images for
    #       the latest deprecation timeline.
    deprecated_runner_labels:
      - ubuntu-18.04
      - ubuntu-20.04
      - windows-2019
      # - macos-11   # uncomment if your workflows reference this

    # Extra repos to include in the audit beyond the project's own
    # repository set (resolved from project.md).  Leave empty to audit
    # only the project-owned repos.
    # Format: "org/repo-name" strings.
    # TODO: add any community-managed repos that use shared CI config.
    extra_repos: []
```

---

## `workflow_security_audit` — GitHub Actions security findings (zizmor)

```yaml
repo_health:
  workflow_security_audit:
    # zizmor rule classes to enable.  All four are enabled by default.
    # Remove a class to suppress that finding category project-wide.
    # Allowed values:
    #   injection              - ${{ github.event.* }} in run: steps
    #   excessive-permissions  - write-all or unnecessary write scopes
    #   unpinned-actions       - floating @main / @tag references
    #   fork-secrets           - secrets exposed to fork PRs
    # TODO: disable classes your team has accepted as unavoidable, with
    #       a comment explaining why.
    enabled_rules:
      - injection
      - excessive-permissions
      - unpinned-actions
      - fork-secrets
```

---

## `dependency_audit` — dependency vulnerability and freshness audit

```yaml
repo_health:
  dependency_audit:
    # Dependency manager(s) in use for this project.  The skill selects
    # the appropriate audit-tool adapter for each manager.
    # Allowed values: pip, npm, cargo, maven, gradle
    # TODO: list every manager your project's repos use.  A project with
    #       both Python and a Helm chart would list [pip, helm].
    managers:
      - pip   # TODO: replace or extend with your project's managers
```

---

## `license_compliance_audit` — SPDX header and NOTICE compliance

```yaml
repo_health:
  license_compliance_audit:
    # SPDX expression every source file must carry.
    # ASF default: Apache-2.0.
    # TODO: change only if your project uses a different inbound license.
    required_spdx_expression: "Apache-2.0"

    # Source paths to audit for SPDX headers (relative to the upstream
    # repo root).  The skill checks every file under these paths.
    # TODO: add the directories where your project's source files live.
    source_paths:
      - src/
      - lib/

    # Paths to skip entirely (test fixtures, vendored code, generated
    # files, etc.).  Relative to the upstream repo root.
    # TODO: add any directories where SPDX headers are not expected.
    skip_paths:
      - tests/fixtures/
      - vendor/
      # - docs/_static/   # uncomment if your docs tree has vendored JS
```

---

## `flaky_test_triage` — flaky-test detection from CI run history

```yaml
repo_health:
  flaky_test_triage:
    # Number of days of GitHub Actions run history to analyse.
    # A shorter window misses infrequent flakes; a longer window
    # increases API call volume.  30 days is a reasonable starting point.
    # TODO: increase to 60–90 if your project's CI is low-frequency.
    window_days: 30

    # Minimum per-test failure rate (as a fraction of total runs) to
    # flag the test as a flaky candidate.  0.1 = fails in ≥10 % of runs.
    # Tests that always fail (rate ≈ 1.0) are classified as consistently
    # broken rather than flaky.
    # TODO: lower to 0.05 for a noisier-but-broader sweep; raise to 0.2
    #       to focus only on highly-recurrent flakes.
    failure_rate_threshold: 0.1

    # Test-name patterns to include (regex, matched against the test's
    # full name as reported by the CI runner).  Leave empty to include
    # all tests.
    # TODO: add patterns to restrict the sweep to a subset of test suites.
    include_patterns: []

    # Test-name patterns to exclude (regex).  Useful for known-flaky
    # tests under active investigation that you don't want re-surfaced.
    # TODO: add patterns for tests your team has already triaged.
    exclude_patterns: []
```

---

## Cross-references

- `docs/repo-health/README.md` — family overview, candidate-skill
  descriptions, and adopter-contract rationale (lands once the
  `repo-health-family-spec` PR merges).
- [`magpie-ci-runner-audit`](../../.claude/skills/magpie-ci-runner-audit/SKILL.md)
  — first shipped member of the family; reads `ci_runner_audit` above.
- [`tools/spec-loop/specs/triage-mode.md`](../../tools/spec-loop/specs/triage-mode.md)
  — parent spec; repo-health audits are the "Repo-health audits" Known Gap
  under the Triage mode.
- [`project.md`](project.md) — project identity; repo-health skills resolve
  the default repo set from `upstream_repo` declared there.
