<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [🚀 Release-manager hand-off — `CVE_ID`](#-release-manager-hand-off--cve_id)
  - [Step-by-step](#step-by-step)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     Manual-paste variant of the release-manager hand-off comment
     posted by `security-issue-sync` at the `pr merged` → `fix released`
     transition (Step 12 of the lifecycle), when the OAuth API push
     did not succeed (no OAuth credentials configured on the operator
     machine, session expired, transient HTTP error, schema rejection).

     This template is the counterpart to
     `release-manager-handoff-comment-oauth-pushed.md`. The sync skill
     picks between the two based on the outcome of `vulnogram-api-check`
     + `vulnogram-api-record-update` — see Step 5b of
     `.claude/skills/security-issue-sync/SKILL.md` for the decision
     flow.

     **No `uv run` invocations are RM-facing in this template either.**
     When the OAuth push fails, the security team's next sync resolves
     the issue (re-run `vulnogram-api-setup`, retry the push, etc.).
     The RM's surface stays the same as in the OAuth-pushed variant
     plus an explicit "you may need to paste the JSON into #source"
     fallback if the security team cannot resolve the OAuth path. The
     paste itself is a UI action — click Edit → paste → Save — not a
     shell command.

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
       MILESTONE_URL             Tracker-side URL of the milestone this
                                 tracker belongs to (used in the
                                 conditional close-milestone line of the
                                 wrap-up comment in Step 6)
       FRAMEWORK_RECORD_MD_URL   Link to tools/vulnogram/record.md on
                                 the framework's GitHub
       FRAMEWORK_SYNC_SKILL_URL  Link to .claude/skills/security-issue-sync/
                                 SKILL.md on the framework's GitHub
       FRAMEWORK_README_URL      Link to README.md on the framework's
                                 GitHub (Steps 12-15 anchor)
       CANNED_RESPONSES_URL      Link to <project-config>/canned-
                                 responses.md on the tracker's GitHub

     The HTML marker on line 60 is load-bearing: the skill detects an
     already-posted hand-off comment by grepping for this exact string
     and skips the post on subsequent sync runs (idempotency).

     Do not paraphrase the marker. Do not move it off line 60. Do not
     add a `<!-- v2 -->` until the schema actually changes — the
     skill's grep is anchored on `v1`.
-->
<!-- apache-steward: release-manager-handoff v1 -->

## 🚀 Release-manager hand-off — `CVE_ID`

RM_HANDLE, the release containing the fix has shipped — this tracker
now belongs to you. The OAuth-API push of the CVE JSON did not
succeed during the last sync (the security team will retry on the
next pass); until that lands, the paste-ready CVE JSON in this
tracker's [issue body](JSON_ANCHOR_URL) is the canonical version. If
the OAuth path remains blocked when you start working through the
checklist below, the manual-paste fallback at the bottom tells you
what to copy where — **all via the Vulnogram UI, no shell commands
required from you**.

The Vulnogram-specific recipe lives in
[`tools/vulnogram/record.md` — *Release-manager checklist*](FRAMEWORK_RECORD_MD_URL);
the high-level numbered checklist below is here for at-a-glance
reference without leaving this issue.

### Step-by-step

1. **Confirm the record content matches the tracker body.** Open
   [`#source`](SOURCE_TAB_URL) and compare to the
   [tracker body's embedded JSON](JSON_ANCHOR_URL). If they diverge
   (the OAuth push remained blocked), follow the manual-paste
   fallback at the bottom of this comment — open
   [`#source`](SOURCE_TAB_URL), paste the embedded JSON, click
   **Save**. Then click `DRAFT → REVIEW` via the Vulnogram UI button.

2. **Respond to any pending reviewer asks** in the
   [`#email` tab](EMAIL_TAB_URL). Reviewer comments arrive by email on
   `SECURITY_LIST` with the CVE ID in the subject line —
   [`security-issue-sync`](FRAMEWORK_SYNC_SKILL_URL) detects them
   automatically and updates the tracker body if a field needs to
   change. If the body changes and the OAuth push is healthy by then,
   the JSON re-push runs in the next sync; if not, follow the
   manual-paste fallback again to land the regenerated JSON.

3. **Set `READY`** via the Vulnogram UI button when the reviewer
   thread closes. The record is now ready for the advisory-send step.

4. **Preview the advisory email** on the
   [`#email` tab](EMAIL_TAB_URL). If anything needs to change, edit
   the corresponding tracker body field; the JSON regenerates and (if
   the OAuth push is healthy) re-pushes; re-preview before sending.

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
     `vendor-advisory` reference).
   - **If the OAuth push is healthy**: re-pushes the regenerated JSON
     and **moves the record `REVIEW → PUBLIC`** via the OAuth API.
   - **If the OAuth push is still blocked**: the wrap-up comment from
     this step names the `#source`-tab paste-and-Save + UI-click
     `REVIEW → PUBLIC` as your manual fallback (single UI session).
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

**Manual-paste fallback** — only when the OAuth push remained blocked
through to the advisory-send pass:

- Open [`#source`](SOURCE_TAB_URL) for the CVE record.
- Open the [tracker body's embedded JSON](JSON_ANCHOR_URL) section.
- Copy the JSON block; paste it into Vulnogram's `#source` editor;
  click **Save**.
- Repeat after any subsequent body-field change on the tracker (the
  embedded JSON regenerates automatically on each change; the paste
  is the only step that does not happen automatically when the OAuth
  push is blocked).

The security team's next sync run resolves the underlying OAuth
issue (re-run `vulnogram-api-setup`, retry the push) and the comment
PATCH-edits back to the OAuth-pushed variant. **You as the RM are
never asked to run `vulnogram-api-*` shell commands** in this
fallback path.

---

**References:**

- Vulnogram state machine + paste flow: [`tools/vulnogram/record.md`](FRAMEWORK_RECORD_MD_URL).
- Reusable email wording (if you draft anything by hand): [`canned-responses.md`](CANNED_RESPONSES_URL).
- Full lifecycle (Steps 12-15): [`README.md`](FRAMEWORK_README_URL#for-release-managers--steps-1215).
