<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# non-asf-profile-smoke evals

Smoke eval that drives the `issue-stale-sweep` skill through the
[`projects/non-asf-example/`](../../../../projects/non-asf-example/)
fixture profile and asserts that acceptance criterion 3 of
[`specs/project-agnosticism.md`](../../../../tools/spec-loop/specs/project-agnosticism.md)
holds:

> A non-ASF profile can be declared without editing any skill body.

Every case in this suite uses the same unmodified `issue-stale-sweep`
SKILL.md. The `report.md` for each case carries non-ASF project config
values (no `apache.org` addresses, no PMC roster, no Vulnogram, no
PonyMail, no ASF-specific flags) and asserts that the skill still produces
correct output — demonstrating that config substitution alone is
sufficient.

## Suites (6 cases total)

| Suite | Step | Cases | What it covers |
|---|---|---|---|
| step-1-fetch-pool | Step 1 (fetch candidate pool) | 3 | non-ASF GitHub Issues clean pass; framework-default fallback; component-filter selector |
| step-3-classify | Step 3 (classify each issue) | 3 | stale request-update; active skip; security-label skip (no ASF label names required) |

## What it proves

- `step-1-fetch-pool` cases pass with `tracker_type: github-issues` and
  thresholds from a non-ASF `stale-sweep-config.md` — no `apache.org`
  fields, no PonyMail, no PMC roster required.
- `step-3-classify` cases pass using non-ASF label names (e.g.,
  `security-team` rather than the ASF default `security`) — the label
  name comes from `<project-config>/project.md` → `tracker.labels`, not
  from the skill body.
- The SKILL.md file path in every `step-config.json` is identical to the
  one used by the ASF eval suite — the same skill, different config.

## Run

```bash
# All cases
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/non-asf-profile-smoke/

# Single suite
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/non-asf-profile-smoke/step-1-fetch-pool/fixtures/

# Single case
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/non-asf-profile-smoke/step-1-fetch-pool/fixtures/case-1-non-asf-github-issues-clean-pass
```
