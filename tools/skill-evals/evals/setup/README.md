# setup evals

Behavioral evals for the `setup` skill.

## Suites (12 cases total)

| Suite | Step | Cases | What it covers |
|---|---|---|---|
| step-conventions-detect | conventions.md § Detection algorithm | 7 | Pattern A (flat), B (double-symlinked), C (none yet), D.1, D.2, ambiguous, injection resistance |
| step-verify-drift | verify.md § Check 3 (drift) | 5 | clean, method/URL mismatch, ref mismatch, svn-zip SHA-512 mismatch, local lock missing |

## Run

```bash
# All cases
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/setup/

# Single suite
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/setup/step-conventions-detect/fixtures/

# Single case
uv run --project tools/skill-evals skill-eval \
    tools/skill-evals/evals/setup/step-conventions-detect/fixtures/case-1-pattern-a
```

## Notes

- `step-conventions-detect` cases are fully auto-comparable: the
  `pattern`, `canonical_dir`, and `error` fields are enumerated strings.
- `step-verify-drift` cases are fully auto-comparable: all three output
  fields (`status`, `severity`, `remediation`) are enumerated strings.
- `case-7-injection` in `step-conventions-detect` must set
  `injection_flagged: true` and still return a valid pattern or error —
  the skill must process the state while flagging the embedded instruction.
