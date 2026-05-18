<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [🚀 Release-manager hand-off — `CVE_ID` (CVE JSON auto-pushed)](#-release-manager-hand-off--cve_id-cve-json-auto-pushed)
  - [Step-by-step](#step-by-step)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     OAuth-pushed variant of the release-manager hand-off comment
     posted by `security-issue-sync` at the `pr merged` → `fix released`
     transition (Step 12 of the lifecycle), when the operator's machine
     had a valid Vulnogram OAuth session at sync time **and** the
     `vulnogram-api-record-update` push of the regenerated CVE JSON
     succeeded.

     This template is the counterpart to `release-manager-handoff-
     comment.md` (the manual-paste variant). The sync skill picks
     between the two based on the outcome of `vulnogram-api-check` +
     `vulnogram-api-record-update` — see Step 5b of
     `.claude/skills/security-issue-sync/SKILL.md` for the decision
     flow.

     Idempotency: the marker on the line below is the **same** as the
     manual-paste variant's. The skill's idempotency grep keys on the
     marker only; the variant choice is detected by re-reading the
     comment body and checking which template's signature it carries.
     On a re-sync where the previous comment is the manual-paste
     variant but the current push succeeded, the skill PATCH-edits the
     comment body in place to the OAuth-pushed body (no second comment).

     The OAuth-pushed variant intentionally carries **no `uv run`
     invocations as RM-facing instructions** — the API push (and any
     re-push triggered by a body change) is run by `security-issue-sync`
     during sync, not by the release manager. The RM's surface is
     restricted to Vulnogram UI clicks, reviewer-thread responses, and
     the advisory send.

     Placeholders the skill substitutes:

       CVE_ID                    e.g. CVE-2026-40690
       RM_HANDLE                 GitHub handle of the release manager
                                 (with leading `@`)
       SECURITY_LIST             e.g. security@<project>.apache.org
       USERS_LIST                e.g. users@<project>.apache.org
       ANNOUNCE_LIST             e.g. announce@apache.org
       SOURCE_TAB_URL            <cve_tool_record_url_template>#source
       EMAIL_TAB_URL             <cve_tool_record_url_template>#email
       JSON_ANCHOR_URL           Tracker body deep-link to the embedded
                                 CVE JSON section
       ARCHIVE_SCAN_URL          The PonyMail / archive search URL for
                                 USERS_LIST (parameterised on CVE_ID)
       MILESTONE_URL             Tracker-side URL of the milestone this
                                 tracker belongs to (used in the
                                 conditional close-milestone line of the
                                 wrap-up comment in Step 6)
       FRAMEWORK_RECORD_MD_URL   Link to tools/vulnogram/record.md on
                                 the framework's GitHub
       FRAMEWORK_SYNC_SKILL_URL  Link to .claude/skills/security-issue-sync/
                                 SKILL.md on the framework's GitHub
       FRAMEWORK_README_URL      Link to README.md on the framework's
                                 GitHub
       CANNED_RESPONSES_URL      Link to <project-config>/canned-
                                 responses.md on the tracker's GitHub
       PUSH_TIMESTAMP            ISO-8601 timestamp of the most-recent
                                 successful `vulnogram-api-record-
                                 update` call (re-rendered on each
                                 sync that re-pushes)
-->
<!-- apache-steward: release-manager-handoff v1 -->

## 🚀 Release-manager hand-off — `CVE_ID` (CVE JSON auto-pushed)

RM_HANDLE, the release containing the fix has shipped — this tracker
now belongs to you. **The CVE JSON has already been pushed to
[`#source`](SOURCE_TAB_URL) by the security team via the OAuth API at
`PUSH_TIMESTAMP`**, and `security-issue-sync` keeps the record in
lock-step with the tracker body on every subsequent sync run. Your
remaining work is a small handful of Vulnogram-UI clicks plus the
advisory send — no shell commands required.

### Step-by-step

1. **Confirm the record is in `REVIEW`.** Open
   [`#source`](SOURCE_TAB_URL). If the record is still in `DRAFT`,
   click the Vulnogram UI button to move `DRAFT` → `REVIEW`. (The
   data is already in place — `PUSH_TIMESTAMP`.)

2. **Respond to any pending reviewer asks** in the
   [`#email` tab](EMAIL_TAB_URL). Reviewer comments arrive by email on
   `SECURITY_LIST` with the CVE ID in the subject line —
   [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL) detects them
   automatically and updates the tracker body if a field needs to
   change. If the body changes, the JSON regenerates and re-pushes as
   part of the next sync; you do not push manually.

3. **Set `READY`** via the Vulnogram UI button when the reviewer
   thread closes. The record is now ready for the advisory-send step.

4. **Preview the advisory email** on the
   [`#email` tab](EMAIL_TAB_URL). Inspect how the email will render:
   subject, body, recipient list. The preview surfaces formatting
   issues (truncation, broken markdown, missing patch links) that the
   JSON view does not. If anything needs to change, edit the
   corresponding tracker body field — the JSON regenerates and
   re-pushes; re-preview before sending.

5. **Send the advisory** from the Vulnogram form. The form sends to
   `USERS_LIST` and `ANNOUNCE_LIST`. **Do not touch the tracker
   labels** — sync handles the label flips automatically when it sees
   the advisory on the users-list (see Step 6).

6. **(fully automatic — sync skill drives the lifecycle close-out.)**
   On the next sync run after the advisory lands in the
   [users-list archive](ARCHIVE_SCAN_URL),
   [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL):
   - Captures the published advisory URL into the *Public advisory
     URL* body field.
   - **Extracts the public-facing short summary** from the advisory
     email body and writes it back to the *Short summary for the
     publish* body field, so the tracker matches what actually
     shipped.
   - **Flips the tracker labels**: adds `announced - emails sent` and
     `announced`; removes `fix released`. The `announced` label
     triggers the project-board automation to move the item from the
     `Fix released` column to the `Announced` column.
   - Regenerates the embedded CVE JSON (now picking up the updated
     short summary as `descriptions[].value` and the archive URL as a
     `vendor-advisory` reference) and **re-pushes the JSON to the
     Vulnogram record** over the OAuth API.
   - **Moves the record `REVIEW → PUBLIC`** via the OAuth API. This
     triggers the CNA-feed dispatch to `cve.org`. (Previously a
     manual UI click; sync now drives it on the same trigger as the
     archive-URL capture, since the archive URL is the real-world
     signal that the advisory has actually shipped.)
   - **Closes the tracker** as `completed`.
   - **Posts a follow-up comment** tagging the RM with the wrap-up
     checklist: archive the now-closed tracker from the project
     board's `Announced` column, and — **if every sibling on the
     tracker's milestone is also closed** at that moment — close the
     milestone via the link in the comment ([`MILESTONE_URL`](MILESTONE_URL)).
     If other siblings on the milestone are still open, the wrap-up
     comment omits the close-milestone line; the close happens when
     the *last* sibling tracker reaches the same Step 6.

7. **Follow the wrap-up comment** posted by sync in Step 6. Archive
   the closed tracker from the project board's `Announced` column
   (it stays accessible via the *Archived items* filter). If the
   comment also linked the milestone (last-sibling case), click
   through and close it — that's the explicit *"everything destined
   for this release has shipped and been announced"* signal.

---

**If the OAuth push fails on a future sync** (session expired, schema
rejection, transient HTTP error), the sync's recap surfaces the
failure and PATCH-edits this comment back to the manual-paste variant
([`release-manager-handoff-comment.md`](FRAMEWORK_RECORD_MD_URL)). The
most common cause is a stale OAuth session cookie on the operator
machine — the security team re-runs `vulnogram-api-setup`, the next
sync resumes auto-pushing, and the comment flips back to this
variant. **You as the RM are never asked to run shell commands** in
this fallback path.

---

**References:**

- Vulnogram state machine: [`tools/vulnogram/record.md`](FRAMEWORK_RECORD_MD_URL).
- Reusable email wording (if you draft anything by hand): [`canned-responses.md`](CANNED_RESPONSES_URL).
- Full lifecycle (Steps 12-15): [`README.md`](FRAMEWORK_README_URL#for-release-managers--steps-1215).
