<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Step 2 output specification

The model must return ONLY valid JSON matching this schema:

```json
{
  "subject": "<final subject line>",
  "body": "<final announce email body>",
  "backend": "announce-list" | "github-release-notes" | "site-post" | "discord-channel",
  "skip_promote_wait_logged": true | false,
  "asf_address_reminder_present": true
}
```

Grading rules:
- `subject` must match the `announce_subject_template` with `<version>` and
  `<product_name>` substituted.
- `body` must contain `To:` and `Cc:` headers for `announce-list` backend.
- `body` must contain the Download Page URL, not a direct `dist.apache.org` URL.
- `body` must contain `@apache.org address` reminder text for `announce-list` backend.
- `asf_address_reminder_present` must always be `true` for `announce-list` backend.
- `skip_promote_wait_logged` must be `true` when `--skip-promote-wait` was passed.
- `body` must include the skip-promote-wait reason text when the flag was used.
- No extra keys are permitted in the response.
