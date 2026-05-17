# security-issue-sync eval suite

Behavioral evals for the `security-issue-sync` skill. Seven steps are
covered; steps 0 (pre-flight), 1a–1e (data gathering), 1g (cve.org API
check), 4 (shell apply), and 5/5b/5c (CVE artifact regeneration) are
skipped — all low-signal for structured-output evals.

## Steps

| Step | Name | Cases | Notes |
|------|------|-------|-------|
| 1f | Process step identification | 7 | Decision table covering steps 1-2 through 14 |
| 2a | Observed state | 3 | Step 11 (PR merged), step 6 (CVE needed), step 2 (stale) |
| 2b | Proposed changes | 3 | Label swap, milestone create, providers wave |
| 2c | Next-step recommendation | 4 | Steps 3, 6, 11, 13 |
| Guardrails | Guardrail violation detection | 3 | CVSS propagation, ASF project naming, clean pass |
| 3 | Confirm with user | 3 | apply-all, selective, cancel |
| 6 | Recap | 2 | Structural assertions; with and without CVE/draft |

## Hard rules exercised

- **CVSS not propagated**: Reporter-supplied CVSS score in proposed body patch or status comment is flagged (guardrails case-1).
- **Other ASF project vulnerabilities not named**: Naming a specific CVE from another ASF project is flagged (guardrails case-3).
- **Observed state is tight**: 2a summary is a bullet list of facts only — no proposed actions embedded.
- **Milestone create needed**: When the target milestone does not exist on the repo, `milestone_create_needed: true` must be set (2b case-2).
- **Providers milestone is never the PR milestone**: For providers scope the milestone is the next wave date (2b case-3).
- **CVE allocate skill explicitly named and linked**: Step-6 next-step must name and link `security-cve-allocate` (2c case-2).
- **No-action parking**: Step-11 produces `has_concrete_action: false` (2c case-3).
- **Golden rule 2 — no bare issue numbers**: `has_bare_issue_numbers` must always be false.
