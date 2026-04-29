<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [📰 Advisory archived — ready for `PUBLIC`](#-advisory-archived--ready-for-public)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     Comment-template body for the publication-ready notification
     comment posted by `sync-security-issue` when the *Public advisory
     URL* body field has just been populated and the CVE JSON has been
     regenerated to carry the archive URL as a `vendor-advisory`
     reference (Step 14 of the lifecycle).

     This comment is the explicit follow-up referenced in step 6 of
     the release-manager hand-off comment (see
     `release-manager-handoff-comment.md`); together they form a
     two-comment narrative the RM can drive without consulting the
     status rollup.

     Placeholders the skill substitutes:

       CVE_ID                e.g. CVE-2026-40690
       RM_HANDLE             GitHub handle of the release manager
                             (with leading `@`)
       ARCHIVE_URL           The captured users-list archive URL (the
                             value just populated into the *Public
                             advisory URL* body field)
       SOURCE_TAB_URL        <cve_tool_record_url_template>#source
       JSON_ANCHOR_URL       Tracker body deep-link to the embedded
                             CVE JSON section
       CVE_ORG_URL           https://www.cve.org/CVERecord?id=CVE_ID
                             (the public mirror, post-PUBLIC)

     The HTML marker on line 1 is load-bearing: the skill detects an
     already-posted publication-ready comment by grepping for this
     exact string and skips the post on subsequent sync runs
     (idempotency).
-->
<!-- apache-steward: release-manager-publication-ready v1 -->

## 📰 Advisory archived — ready for `PUBLIC`

RM_HANDLE, the advisory you sent in step 5 of the hand-off above has
been archived on the public users-list. This sync pass made the
following deterministic updates on this tracker:

- **Public advisory URL** body field populated: [ARCHIVE_URL](ARCHIVE_URL)
- The embedded CVE JSON regenerated to include the archive URL as a
  `vendor-advisory` reference in `references[]`.
- The `announced` label added.

You can now do the final paste + state move:

1. Open the [`#source` tab](SOURCE_TAB_URL) on the CVE record.
2. Copy the regenerated JSON from this tracker's [issue body](JSON_ANCHOR_URL) and paste into the form. **Save**.
3. Move the record `REVIEW` → `PUBLIC` via the Vulnogram UI. The record propagates to [`cve.org`](CVE_ORG_URL) once the state lands.
4. **Close this tracker** — close as completed; do not update any labels. The `sync-security-issue` skill archives the project-board item afterwards.

That terminates the lifecycle. Thanks for driving this one.
