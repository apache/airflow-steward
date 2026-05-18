# pr-management-code-review evals

Behavioral evals for the `pr-management-code-review` skill.

## Suites (5 cases total)

| Suite | Step | Cases | What it covers |
|---|---|---|---|
| review-disposition | Step 2 (per-PR review loop — disposition) | 5 | APPROVE (clean PR), REQUEST_CHANGES (code issues), COMMENT (failing CI), COMMENT (unresolved maintainer REQUEST_CHANGES), prompt-injection resistance |

## Run

```bash
# All cases
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/pr-management-code-review/

# Single suite
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/pr-management-code-review/review-disposition/fixtures/

# Single case
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/pr-management-code-review/review-disposition/fixtures/case-1-approve
```
