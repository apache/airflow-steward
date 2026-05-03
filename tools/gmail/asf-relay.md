<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Gmail — ASF-security-relay drafting](#gmail--asf-security-relay-drafting)
  - [Rules](#rules)
  - [How the skills detect relay cases](#how-the-skills-detect-relay-cases)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Gmail — ASF-security-relay drafting

Some reports reach the project's security list via the ASF security
team — `security@apache.org` itself, or a personal `@apache.org`
address of an ASF security-team member — forwarding a report that
came in through GHSA, HackerOne, or another channel the project's
security team does not have direct access to. In those cases the
"reporter" on the Gmail thread is the ASF forwarder, and the
**actual external reporter is unreachable to us directly**: we can
only reach them by asking the ASF forwarder to relay questions
through the same external channel.

When drafting any reply on an ASF-security-relay tracker — receipt
of confirmation, credit-preference request, status update — the
threading rules from [`threading.md`](threading.md) all still apply;
the differences are in the headers and body shape.

Placeholder convention:

- `<security-list>` — the project's security list. The concrete
  address is declared in
  [`<project-config>/project.md → Mailing lists`](../../<project-config>/project.md#mailing-lists).

## Rules

- **`threadId`** — the inbound relay thread's `threadId`, per the
  [threading rule](threading.md). Never fabricate a new thread for
  a credit-preference relay; it goes on the same thread as the
  original inbound report.
- **Subject** — `Re: <root subject>`, i.e. the subject of the
  inbound relay message. No fabricated new subject, no
  relay-specific title like *"\<Project\>: credit-preference relay
  for <GHSA-ID>"*.
- **`To:`** — the ASF forwarder (the `From:` address of the
  inbound relay message). Typically this is a personal
  `@apache.org` address; use that, not the `security@apache.org`
  list alias, so the conversation stays with the individual who
  already knows the report.
- **`Cc:`** — `<security-list>` as always.
- **Body** — short, per the *"Brevity: emails state facts, not
  context"* rule in [`../../AGENTS.md`](../../AGENTS.md). The ASF
  security team knows the handling process; do **not** restate the
  vulnerability, the severity analysis, or the project's CVE
  process. Link to the external reference (GHSA ID, HackerOne report
  URL) rather than repeating technical detail. When the purpose of
  the draft is a credit-preference relay, the ask is one sentence:
  *"Please forward the credit-preference question below to the
  external reporter through the original channel."*

## How the skills detect relay cases

The `security-issue-import` skill classifies candidates into
`Report`, `ASF-security relay`, and several non-import classes; the
classification feeds this drafting path.

Relay-specific signals in the inbound message:

- `From:` is `security@apache.org` or a personal `@apache.org`
  address of an ASF-security-team member;
- Body opens with the ASF forwarding preamble — *"Dear PMC, The
  security vulnerability report has been received by the Apache
  Security Team and is being passed to you for action …"* — with
  the original report underneath (often after a `====GHSA-…`
  separator when the report came in via GitHub Security Advisory);
- The body usually ends with a `Credit` line naming the discoverer
  (e.g. *"This vulnerability was discovered and reported by
  bugbunny.ai"*) — use that verbatim for the Reporter-credited-as
  placeholder, not the `From:` header (which is always the
  forwarder's address).

The import skill's Step 3 classification table documents the exact
subject / sender signals; this file describes what to do once the
classification says *"ASF-security relay"*.
