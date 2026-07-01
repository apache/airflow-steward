<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->
You are executing the confirmation gate from Step 7–8 of the
pr-management-code-review skill of the Apache Magpie framework.

The skill has already drafted a review (disposition + body + optional inline
comments). It has shown the draft to the maintainer. Now the maintainer has
responded.

## Confirmation gate rules

Given the maintainer's response and the session context, decide what action
to take:

| Maintainer response | Action |
|---|---|
| Confirms (`[Y]es`, `yes`, `confirm`, or bare Enter) and `dry_run` is `false` | `"post"` — post the review via `gh pr review` |
| Confirms but `dry_run` is `true` | `"dry-run-skip"` — acknowledge the confirmation but do NOT post; print a note that this is a dry-run session |
| Edits the draft (requests wording changes, asks to drop/add a finding) | `"re-draft"` — incorporate the edits and re-show the draft before the next confirmation gate |
| Skips (`[S]kip`) | `"skip"` — leave the PR untouched and move to the next one |
| Quits (`[Q]uit`) | `"quit"` — end the session |

The skill never posts a review without explicit confirmation (`[Y]` or an
unambiguous equivalent). An ambiguous response (e.g. "looks good to me but
also maybe check line 42") is treated as `"re-draft"` — clarify before
posting.

## Output

Return ONLY valid JSON with this structure:

```json
{
  "action": "post" | "dry-run-skip" | "re-draft" | "skip" | "quit",
  "reason": "<one sentence explaining the decision>"
}
```

Do not include any text outside the JSON object.
