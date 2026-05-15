<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Board resolution — Establish the Apache Magpie Project (draft)](#board-resolution--establish-the-apache-magpie-project-draft)
  - [Resolution text](#resolution-text)
  - [Notes for the chair / proposer](#notes-for-the-chair--proposer)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# Board resolution — Establish the Apache Magpie Project (draft)

> **Status:** *Draft.* Working text for the forthcoming ASF Board resolution
> establishing Apache Magpie as a Top-Level Project. The companion supporting
> document is [`MISSION.md`](../MISSION.md), which the Board is expected to
> read alongside the resolution.
>
> The resolution itself is short and procedural by ASF convention; rationale,
> roster lineage, scope justification, and the donated-code story live in
> `MISSION.md` rather than in the resolution body. The format below follows
> the standard ASF Board-resolution shape for a fresh-PMC establishment.

## Resolution text

> **B. Establish the Apache Magpie Project**
>
> WHEREAS, the Board of Directors deems it to be in the best interests of
> the Foundation and consistent with the Foundation's purpose to establish
> a Project Management Committee charged with the creation and maintenance
> of open-source software, for distribution at no charge to the public,
> related to agent-assisted maintenance and development of open-source
> software projects.
>
> NOW, THEREFORE, BE IT RESOLVED, that a Project Management Committee
> (PMC), to be known as the "Apache Magpie Project", be and hereby is
> established pursuant to Bylaws of the Foundation; and be it further
>
> RESOLVED, that the Apache Magpie Project be and hereby is responsible
> for the creation and maintenance of software related to agent-assisted
> repository maintainership and development, including issue and pull-
> request triage, contributor mentoring, agent-drafted remediation,
> developer-side development-cycle skills, and narrowly-scoped fix-and-
> merge automation; and be it further
>
> RESOLVED, that the office of "Vice President, Apache Magpie" be and
> hereby is created, the person holding such office to serve at the
> direction of the Board of Directors as the chair of the Apache Magpie
> Project, and to have primary responsibility for management of the
> projects within the scope of responsibility of the Apache Magpie
> Project; and be it further
>
> RESOLVED, that the persons listed immediately below be and hereby are
> appointed to serve as the initial members of the Apache Magpie Project:
>
> ```text
> * Andrew Musselman            <akm@apache.org>
> * Amogh Desai                 <amoghdesai@apache.org>
> * Craig L. Russell            <clr@apache.org>
> * Elad Kalif                  <eladkal@apache.org>
> * Pavan Kumar Gopidesu        <gopidesu@apache.org>
> * Ismael Mejia                <iemejia@apache.org>
> * James Fredley               <jamesfredley@apache.org>
> * Jean-Baptiste Onofré        <jbonofre@apache.org>
> * Justin Mclean               <jmclean@apache.org>
> * Calvin Kirs                 <kirs@apache.org>
> * Mike Drob                   <mdrob@apache.org>
> * Paul King                   <paulk@apache.org>
> * Piotr Karwasz               <pkarwasz@apache.org>
> * Jarek Potiuk                <potiuk@apache.org>
> * Rich Bowen                  <rbowen@apache.org>
> * Evan Rusackas               <rusackas@apache.org>
> * Russell Spitzer             <russellspitzer@apache.org>
> * Zili Chen                   <tison@apache.org>
> * Matthew Topol               <zeroshade@apache.org>
> ```
>
> NOW, THEREFORE, BE IT FURTHER RESOLVED, that Jarek Potiuk be appointed
> to the office of Vice President, Apache Magpie, to serve in accordance
> with and subject to the direction of the Board of Directors and the
> Bylaws of the Foundation until death, resignation, retirement, removal
> or disqualification, or until a successor is appointed.
>
> Special Order *[NN]*, Establish the Apache Magpie Project, was
> approved by *[Unanimous]* Vote of the directors present.

## Notes for the chair / proposer

These items are deliberately **not** in the resolution text — the resolution
stays short by ASF convention. They are kept here so the proposer remembers
to land them in the right place at the right time:

- **Donated code lineage** — the project is greenfield in terms of PMC, but
  inherits substantial project-agnostic code from existing ASF projects
  (Apache Airflow, where the framework was first developed and proven;
  Apache Groovy; and other ASF projects whose maintainers have been early
  adopters). All transferred code is already Apache-2.0 licensed and ASF-
  owned, so the moves go through the **standard ASF IP Clearance process**
  — no Software Grant Agreements are needed, since those apply only to
  code originating outside the ASF. The lineage is documented in
  [`MISSION.md` § Source and IP](../MISSION.md#source-and-ip).

- **No "tasked with migration" / "discharge" clauses** — those clauses are
  appropriate when a new PMC takes over an existing sub-project of an
  existing PMC, and the prior PMC is being relieved of responsibilities.
  Magpie is a fresh PMC with no existing PMC losing scope, so the clauses
  are correctly absent here.

- **Membership coordination** — the named roster must be cleared with
  `members@apache.org` and `secretary@apache.org` before the resolution
  goes to the agenda. The 19-member list above reflects MISSION.md's
  *"7 or more members"* size criterion and the diversity / developer-
  experience criteria in MISSION.md § Initial PMC composition.

- **PMC name vs. trademark review** — `MISSION.md` § Proposed Names lists
  four candidates (Magpie / Beacon / Guild / Lichen) pending parallel
  `trademarks@apache.org` review. The first to clear `trademarks@` becomes
  the final name. Replace "Magpie" in the resolution text above with
  whichever name is cleared before the resolution lands on the agenda.

- **Special Order number** — assigned by the Board Secretary when the
  agenda is built. Placeholder `[NN]` above.

- **Vote line** — `Unanimous` is the expected outcome but the Secretary
  records the actual result. Placeholder retained.

- **Supporting document attachment** — `MISSION.md` itself is the
  supporting document the Board reads alongside this resolution. Confirm
  it is included in the agenda packet under the proposing director's name.
