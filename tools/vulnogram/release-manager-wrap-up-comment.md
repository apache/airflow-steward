<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [✅ Wrap-up — `CVE_ID`](#-wrap-up--cve_id)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

<!--
     Wrap-up comment posted by `security-issue-sync` AFTER the
     tracker has been auto-closed at the end of the
     post-advisory lifecycle close-out (Step 6 of the
     release-manager hand-off comment templates;
     `Advisory archived on <users-list>` row of Step 2b in
     `.claude/skills/security-issue-sync/SKILL.md`).

     The combined apply that triggers this comment runs when the
     advisory's archive URL is captured on `<users-list>` AND every
     intermediate write (label flip, JSON re-push, REVIEW → PUBLIC
     via `vulnogram-api-record-publish`) succeeded. By the time this
     comment posts the tracker is already closed (`completed`) and
     the `announced` label has moved the board item to the
     `Announced` column.

     Residual manual steps for the RM:

       1. Archive the closed tracker from the project board's
          `Announced` column.
       2. (Conditional, last-sibling case only) Close the milestone
          this tracker belonged to. The comment carries the
          milestone URL as a clickable link ONLY when sync detected
          that every milestone-sibling is also closed at this
          moment. In the more common "other siblings still open"
          case the comment omits the close-milestone line and the
          milestone close happens when the *last* sibling tracker
          reaches this same step.

     Idempotency: the HTML marker on the line below is the skill's
     idempotency anchor. On a re-sync where this comment already
     exists, sync skips the post (the tracker is already closed,
     this comment is informational only — re-posting would be
     noise).

     Placeholders the skill substitutes:

       CVE_ID                    e.g. CVE-2026-40690
       RM_HANDLE                 GitHub handle of the release manager
                                 (with leading `@`)
       TRACKER_URL               Tracker issue URL
       BOARD_URL                 Project-board URL with the
                                 `Announced` column scrolled into
                                 view (e.g.
                                 https://github.com/orgs/<org>/projects/<N>/views/<V>?filterQuery=status%3AAnnounced)
       MILESTONE_URL             Optional. Set ONLY in the
                                 last-sibling case. Sync omits the
                                 close-milestone bullet entirely
                                 when this placeholder is unset.
       MILESTONE_TITLE           Optional. Set alongside
                                 MILESTONE_URL — the human-readable
                                 milestone title for the link text.
       PUBLISH_TIMESTAMP         ISO-8601 timestamp of the
                                 `vulnogram-api-record-publish` call
                                 that flipped REVIEW → PUBLIC.
       ADVISORY_URL              The captured `<users-list>` archive
                                 URL for the advisory.
-->
<!-- apache-steward: release-manager-wrap-up v1 -->

## ✅ Wrap-up — `CVE_ID`

RM_HANDLE — the post-advisory close-out for [`CVE_ID`](ADVISORY_URL)
ran cleanly. This tracker is now closed; the Vulnogram record moved
`REVIEW → PUBLIC` at `PUBLISH_TIMESTAMP` (CNA-feed dispatch to
`cve.org` triggered); the `announced` label has moved the board
item to the [`Announced` column](BOARD_URL).

**Two small residual actions for you:**

1. **Archive this tracker from the [`Announced` column](BOARD_URL)** on the project board. The closed tracker stays accessible via the *Archived items* filter; this just clears it from the active board view.

2. **MILESTONE_BULLET**

<!--
     The skill substitutes the MILESTONE_BULLET placeholder with
     either an empty string (when MILESTONE_URL is unset — other
     milestone-siblings still open) or with the literal:

         Close the [`MILESTONE_TITLE`](MILESTONE_URL) milestone —
         every tracker on it is now closed too.

     This is the only conditional in the template. The numbering
     stays "1." and "2." regardless; in the no-milestone case the
     "2." item just reads as the empty bullet which is harmless
     visual noise — preferable to dropping the numbering and
     keeping the next-pass parse stable.
-->

That's it — nothing else owed on this tracker. Thanks for shepherding `CVE_ID` through the release + advisory.

---

**References:**

- The combined apply that brought the tracker to this state is documented in `.claude/skills/security-issue-sync/SKILL.md` Step 2b (`Advisory archived on <users-list>` row).
- The state-transition tool: [`vulnogram-api-record-publish`](oauth-api/README.md).
