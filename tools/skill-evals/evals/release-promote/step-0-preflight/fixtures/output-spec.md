<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Step 0 output specification

The model must return ONLY valid JSON matching this schema:

```json
{
  "verdict": "proceed" | "blocked" | "handoff-non-pmc",
  "blockers": ["<string>"],
  "rm_is_pmc": true | false,
  "non_asf": true | false,
  "version": "<version string>",
  "rc": "<rcN string>",
  "dist_backend": "svnpubsub" | "github-releases" | "s3" | "self-hosted"
}
```

Grading rules:
- `verdict` must be `"proceed"` when all blockers are resolved and the RM
  is on the PMC roster (or `--non-asf` was passed).
- `verdict` must be `"handoff-non-pmc"` when the RM fails the PMC gate but
  all other checks pass.
- `verdict` must be `"blocked"` when any hard blocker (other than non-PMC)
  remains.
- `blockers` must be an empty array when `verdict` is `"proceed"` or
  `"handoff-non-pmc"`.
- `version` and `rc` must be correctly parsed from the trigger argument.
- `dist_backend` must match the value in `release-management-config.md`.
- No extra keys are permitted in the response.
