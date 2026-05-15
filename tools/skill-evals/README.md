# skill-evals

Behavioral eval harness for Apache Steward skills.

Prints fixture-based prompts (system prompt + user prompt + expected output)
for each eval case. Paste the prompts into any model and compare the response
against the expected JSON to verify correctness. The harness is intentionally
model-agnostic — no API key or CLI dependency required.

## Run

```bash
# All cases for a skill step
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/security-issue-import/step-2a-semantic-sweep/fixtures/

# Single case
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/security-issue-import/step-2a-semantic-sweep/fixtures/case-1-clear-duplicate
```

## Structure

```
evals/
  <skill-name>/
    <step-name>/
      fixtures/
        corpus.json          # shared mock tracker summaries
        reporter-roster.json # shared reporter email map
        case-N-<name>/
          report.md          # incoming report for this case
          expected.json      # expected classification output
```
