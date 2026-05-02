<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [🚀 Release-manager hand-off — `CVE_ID`](#-release-manager-hand-off--cve_id)
  - [Step-by-step](#step-by-step)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     Comment-template body for the release-manager hand-off comment
     posted by `security-sync-issues` at the `pr merged` → `fix released`
     transition (Step 12 of the lifecycle).

     Placeholders the skill substitutes:

       CVE_ID                    e.g. CVE-2026-40690
       RM_HANDLE                 GitHub handle of the release manager
                                 (with leading `@`)
       SECURITY_LIST             e.g. security@<project>.apache.org
       USERS_LIST                e.g. users@<project>.apache.org
       ANNOUNCE_LIST             e.g. announce@apache.org
       SOURCE_TAB_URL            <cve_tool_record_url_template>#source
       EMAIL_TAB_URL             <cve_tool_record_url_template>#email
                                 (Vulnogram's email-preview tab URL)
       JSON_ANCHOR_URL           Tracker body deep-link to the embedded
                                 CVE JSON section (e.g.
                                 https://github.com/<tracker>/issues/<N>#cve-json--paste-ready-for-cve-yyyy-nnnn)
       ARCHIVE_SCAN_URL          The PonyMail / archive search URL for
                                 USERS_LIST (parameterised on CVE_ID)
       FRAMEWORK_RECORD_MD_URL   Link to tools/vulnogram/record.md on
                                 the framework's GitHub
       FRAMEWORK_SYNC_SKILL_URL  Link to .claude/skills/sync-security-
                                 issue/SKILL.md on the framework's GitHub
       FRAMEWORK_README_URL      Link to README.md on the framework's
                                 GitHub (Steps 12-15 anchor)
       CANNED_RESPONSES_URL      Link to <project-config>/canned-
                                 responses.md on the tracker's GitHub

     The HTML marker on line 1 is load-bearing: the skill detects an
     already-posted hand-off comment by grepping for this exact string
     and skips the post on subsequent sync runs (idempotency).

     Do not paraphrase the marker. Do not move it off line 1. Do not
     add a `<!-- v2 -->` until the schema actually changes — the
     skill's grep is anchored on `v1`.
-->
<!-- apache-steward: release-manager-handoff v1 -->

## 🚀 Release-manager hand-off — `CVE_ID`

RM_HANDLE, the release containing the fix has shipped — this tracker
now belongs to you. The Vulnogram-specific recipe lives in
[`tools/vulnogram/record.md` — *Release-manager checklist*](FRAMEWORK_RECORD_MD_URL);
the high-level numbered checklist below is here for at-a-glance
reference without leaving this issue.

The paste-ready CVE JSON is embedded in this tracker's
[issue body](JSON_ANCHOR_URL) and is regenerated automatically on
every body change by the [`security-sync-issues`](FRAMEWORK_SYNC_SKILL_URL) skill.

### Step-by-step

1. **First paste — `DRAFT` → `REVIEW`.** Open the [`#source` tab](SOURCE_TAB_URL) on the CVE record. Copy the embedded JSON from the tracker body above, paste into the form, **Save**. Move the record `DRAFT` → `REVIEW` via the Vulnogram UI.
2. **Wait for CNA review.** Reviewer comments arrive by email on `SECURITY_LIST` with the CVE ID in the subject line. The `security-sync-issues` skill detects them automatically and proposes matching body-field updates on this tracker; the security team confirms and the embedded JSON regenerates. **If no reviewer comments arrive (common case), skip to step 4.** Otherwise, once the body has settled, re-paste the regenerated JSON into `#source` and **Save** again.
3. **Set `READY`.** Vulnogram UI action — the record is now ready for the advisory-send step.
4. **Preview the advisory email** on the [email tab](EMAIL_TAB_URL) of the CVE record. Inspect how the email will render: subject, body, recipient list. The preview surfaces formatting issues (truncation, broken markdown, missing patch links) that the JSON view does not. If anything needs to change, edit the corresponding body field on this tracker, wait for the JSON to regenerate, re-paste in `#source`, and re-preview before sending.
5. **Send advisory emails** from Vulnogram. The form sends to `USERS_LIST` and `ANNOUNCE_LIST`. Then on this tracker, add the `announced - emails sent` label and remove `fix released`.
6. **(automatic) Archive URL captured.** The `security-sync-issues` skill scans the [users-list archive](ARCHIVE_SCAN_URL) for the CVE ID on every run. Once it finds the advisory, it populates the *Public advisory URL* body field, regenerates the CVE JSON to carry the archive URL as a `vendor-advisory` reference, and adds the `announced` label — **and posts a follow-up comment on this tracker** giving you the explicit go-ahead for the final paste below.
7. **Second paste — `REVIEW` → `PUBLIC`.** *Only after the follow-up comment in step 6 fires.* Re-open [`#source`](SOURCE_TAB_URL), paste the now-final JSON (carrying the archive URL in `references[]`), **Save**, move `REVIEW` → `PUBLIC` via the Vulnogram UI. The record propagates to `cve.org` once the state lands.
8. **Close the tracker** — close as completed; do not update any labels. The `security-sync-issues` skill archives the project-board item so the closed tracker leaves the active board.

---

**References:**

- Vulnogram state machine + paste flow: [`tools/vulnogram/record.md`](FRAMEWORK_RECORD_MD_URL).
- Reusable email wording (if you draft anything by hand): [`canned-responses.md`](CANNED_RESPONSES_URL).
- Full lifecycle (Steps 12-15): [`README.md`](FRAMEWORK_README_URL#for-release-managers--steps-1215).
