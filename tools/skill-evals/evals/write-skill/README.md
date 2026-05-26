<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# write-skill evals

Behavioral evals for the `write-skill` skill.

## Suites (5 cases total)

| Suite | Step | Cases | What it covers |
|---|---|---|---|
| step-5-security-checklist | Step 5 (apply security checklist) | 5 | reads-public-pr-comments, reads-gmail-private, local-only (no external reads), prompt-injection-in-description, reads-public-issue-bodies |

## Run

```bash
# All cases
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/write-skill/

# Single suite
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/write-skill/step-5-security-checklist/fixtures/

# Single case
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/write-skill/step-5-security-checklist/fixtures/case-1-reads-pr-comments
```
