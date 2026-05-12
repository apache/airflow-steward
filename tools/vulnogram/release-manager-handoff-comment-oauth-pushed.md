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

     Idempotency: the marker on line below is the **same** as the
     manual-paste variant's. The skill's idempotency grep keys on the
     marker only; the variant choice is detected by re-reading the
     comment body and checking which template's signature it carries.
     On a re-sync where the previous comment is the manual-paste
     variant but the current push succeeded, the skill PATCH-edits the
     comment body in place to the OAuth-pushed body (no second comment).

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
       FRAMEWORK_RECORD_MD_URL   Link to tools/vulnogram/record.md on
                                 the framework's GitHub
       FRAMEWORK_OAUTH_API_README_URL  Link to tools/vulnogram/oauth-
                                 api/README.md on the framework's
                                 GitHub
       FRAMEWORK_PROJECT_PATH    Substitution for `<framework>` in the
                                 `uv run --project ...` invocations
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
`PUSH_TIMESTAMP`**, so the only remaining writes for you are the
Vulnogram-UI state-transition clicks, the advisory send, and the
close.

The paste-ready CVE JSON is embedded in this tracker's
[issue body](JSON_ANCHOR_URL) and is regenerated automatically on
every body change by the [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL)
skill — *and re-pushed via the OAuth API on the same sync run*, so the
Vulnogram record at [`#source`](SOURCE_TAB_URL) stays in lock-step with
the tracker body. No paste step is required from you in the normal
case.

### Step-by-step

1. **Verify the record content.** Open [`#source`](SOURCE_TAB_URL) and
   confirm it matches the [tracker body's embedded JSON](JSON_ANCHOR_URL).
   The two should be byte-identical; if they diverge, the OAuth push
   failed silently and the sync's recap will have flagged it — fall
   back to the manual-paste instructions further down.

2. **Move `DRAFT` → `REVIEW`** via the Vulnogram UI button.

3. **Wait for CNA review.** Reviewer comments arrive by email on
   `SECURITY_LIST` with the CVE ID in the subject line.
   [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL) detects them and
   proposes matching body-field updates on this tracker; the security
   team confirms, the embedded JSON regenerates, and the API re-push
   lands automatically on the same sync run. Each push lands a fresh
   entry on this tracker's rollup comment so you can see what changed
   without opening Vulnogram. **If no reviewer comments arrive (common
   case), skip to step 5.**

4. **Re-verify** the record at [`#source`](SOURCE_TAB_URL) when the
   rollup shows a subsequent push entry (the body has changed since
   `PUSH_TIMESTAMP`).

5. **Set `READY`.** Vulnogram UI button.

6. **Preview the advisory email** on the [email tab](EMAIL_TAB_URL).
   If anything needs to change, edit the corresponding tracker body
   field; the JSON regenerates + auto-pushes; then re-preview.

7. **Send advisory emails** from Vulnogram. The form sends to
   `USERS_LIST` and `ANNOUNCE_LIST`. Then on this tracker, add the
   `announced - emails sent` label and remove `fix released`.

8. **(automatic) Archive URL captured.**
   [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL) scans the
   [users-list archive](ARCHIVE_SCAN_URL) for the CVE ID on every run.
   Once it finds the advisory, it populates the *Public advisory URL*
   body field, regenerates the JSON to include the archive URL as a
   `vendor-advisory` reference, **re-pushes via the OAuth API**, adds
   the `announced` label — **and posts a follow-up comment on this
   tracker** giving you the explicit go-ahead for the final state
   move below.

9. **Move `REVIEW` → `PUBLIC`** via the Vulnogram UI button. *Only
   after the follow-up comment in step 8 fires.* The data write is
   already done; the state transition is intentionally human-only
   because it triggers the CNA-feed dispatch to `cve.org`.

10. **Close the tracker** — close as completed; do not update any
    labels. [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL) archives
    the project-board item so the closed tracker leaves the active
    board.

---

**If the OAuth push fails on a future sync** (session expired, schema
rejection, transient HTTP error), the sync's recap will flag it and
this comment will be edited to the manual-paste variant — re-open
[`#source`](SOURCE_TAB_URL), paste the JSON from the
[tracker body](JSON_ANCHOR_URL), click **Save**, then continue with the
state transitions above. The most common cause is a stale session
cookie — re-run `uv run --project FRAMEWORK_PROJECT_PATH/tools/vulnogram/oauth-api vulnogram-api-setup`
(see [`oauth-api/README.md`](FRAMEWORK_OAUTH_API_README_URL)) and the
next sync will resume auto-pushing.

---

**References:**

- Vulnogram state machine + paste flow: [`tools/vulnogram/record.md`](FRAMEWORK_RECORD_MD_URL).
- OAuth API setup + record-update one-liner: [`oauth-api/README.md`](FRAMEWORK_OAUTH_API_README_URL).
- Reusable email wording (if you draft anything by hand): [`canned-responses.md`](CANNED_RESPONSES_URL).
- Full lifecycle (Steps 12-15): [`README.md`](FRAMEWORK_README_URL#for-release-managers--steps-1215).
