# pr-management-code-review evals

Behavioral evals for the `pr-management-code-review` skill.

## Suites (49 cases total)

| Suite | Step | Cases | What it covers |
|---|---|---|---|
| step-2.5-slop-detection | Step 2.5 | 9 | Slop hard/soft signal firing (H1–H5 / S1–S5) + early-exit threshold; prompt-injection resistance. Includes two regression guards for issues raised in review of PR #454: `case-7` (the H3+H4 correlation rule must keep a legitimate team-fork PR on the note-only path, not over-detect it as early-exit) and `case-9` (H1 must still fire from the real `gh --json files` payload by reading `new file mode` headers in the unified diff, since `--json files` exposes no `changeType` field). |
| step-3-security-disclosure-scan | Step 3 | 6 | CVE/security-phrase detection in title, body, commits; prompt-injection resistance |
| step-4-third-party-license | Step 4 | 6 | X/B/A licence classification, LICENSE update check; licenses/ dir alone is insufficient |
| step-4-compiled-artifacts | Step 4 | 5 | .jar/.pyc/.so/.whl detection; major vs blocking escalation |
| step-4-image-ip | Step 4 | 4 | Diagram vs logo judgement; screenshot exemption |
| step-4-license-headers | Step 4 | 8 | Tooling deference, exclusion masking, broad exclusions, exemptions (JSON, .md, README, LICENSE) |
| step-6-disposition | Step 6 | 6 | APPROVE / REQUEST_CHANGES / COMMENT auto-pick logic |
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
