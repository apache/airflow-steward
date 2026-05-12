<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [📰 Advisory archived — ready for `PUBLIC` (CVE JSON auto-pushed)](#-advisory-archived--ready-for-public-cve-json-auto-pushed)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     OAuth-pushed variant of the publication-ready notification
     comment posted by `security-issue-sync` when the *Public advisory
     URL* body field has just been populated, the CVE JSON has been
     regenerated to carry the archive URL as a `vendor-advisory`
     reference, **and** the regenerated JSON has been pushed to
     Vulnogram via the OAuth API on the same sync pass (Step 14 of
     the lifecycle).

     This template is the counterpart to `release-manager-publication-
     comment.md` (the manual-paste variant). The sync skill picks
     between the two based on the outcome of `vulnogram-api-check` +
     `vulnogram-api-record-update` — see Step 5b of
     `.claude/skills/security-issue-sync/SKILL.md` for the decision
     flow.

     Idempotency: the marker on line below is the **same** as the
     manual-paste variant's; the skill keys idempotency on the marker
     and detects the variant by re-reading the body. On a re-sync
     where the previous comment was manual-paste but the current push
     succeeded, the skill PATCH-edits the body in place.

     Placeholders the skill substitutes:

       CVE_ID                e.g. CVE-2026-40690
       RM_HANDLE             GitHub handle of the release manager
                             (with leading `@`)
       ARCHIVE_URL           The captured users-list archive URL
       SOURCE_TAB_URL        <cve_tool_record_url_template>#source
       JSON_ANCHOR_URL       Tracker body deep-link to the embedded
                             CVE JSON section
       CVE_ORG_URL           https://www.cve.org/CVERecord?id=CVE_ID
       PUSH_TIMESTAMP        ISO-8601 timestamp of the
                             `vulnogram-api-record-update` call
                             this sync pass made
-->
<!-- apache-steward: release-manager-publication-ready v1 -->

## 📰 Advisory archived — ready for `PUBLIC` (CVE JSON auto-pushed)

RM_HANDLE, the advisory you sent in step 7 of the hand-off above has
been archived on the public users-list. This sync pass made the
following deterministic updates on this tracker — *and pushed the
regenerated JSON to Vulnogram via the OAuth API at `PUSH_TIMESTAMP`*,
so the record at [`#source`](SOURCE_TAB_URL) now carries the archive
URL as a `vendor-advisory` reference:

- **Public advisory URL** body field populated: [ARCHIVE_URL](ARCHIVE_URL)
- The embedded CVE JSON regenerated to include the archive URL.
- The regenerated JSON pushed to the CVE record via
  `vulnogram-api-record-update` (no manual paste needed).
- The `announced` label added.

You can now do the final state move:

1. **Verify the record content** at [`#source`](SOURCE_TAB_URL)
   matches the [tracker body](JSON_ANCHOR_URL) — they should be
   byte-identical. If they diverge, the push failed silently; fall
   back to the manual paste below.

2. **Move `REVIEW` → `PUBLIC`** via the Vulnogram UI. The record
   propagates to [`cve.org`](CVE_ORG_URL) once the state lands.

3. **Close this tracker** — close as completed; do not update any
   labels. The `security-issue-sync` skill archives the project-board
   item afterwards.

That terminates the lifecycle. Thanks for driving this one.

---

**Manual paste fallback** (only if step 1's record content does not
match): open [`#source`](SOURCE_TAB_URL), paste the JSON from this
tracker's [issue body](JSON_ANCHOR_URL), click **Save**, then move
`REVIEW` → `PUBLIC`.
