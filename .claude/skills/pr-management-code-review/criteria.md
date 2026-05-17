<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Review criteria — pointers to source

This file is a **navigation map** for the project's review
criteria. It does not restate the rules — those live in the
source files below and are the single source of truth. The
skill's review pass reads them at session start (and re-reads
the per-area `AGENTS.md` files as PRs route into different
trees) and quotes the **source rule verbatim** in any finding
it raises.

If you find yourself wanting to "summarise the rule" in this
file or in a finding body, **stop and link to the source line
or section instead**. Summaries drift; links don't.

---

## Source files

| File | What it covers |
|---|---|
| (read from `<project-config>/pr-management-code-review-criteria.md` → `repo_wide_source_files`) | The rule set every <PROJECT> PR is reviewed against. |

The concrete list of source files is project-specific and lives in
the adopter's `<project-config>/pr-management-code-review-criteria.md`.
The table below shows the **shape** of a typical configuration;
see `projects/_template/pr-management-code-review-criteria.md` for
a concrete example.

| File | What it covers |
|---|---|
| `<repo_wide_review_criteria>` | The rule set every PR is reviewed against (typically architecture / DB / quality / testing / API / UI / generated files / AI-generated-code signals / quality signals). |
| `AGENTS.md` | Repo-wide AI/agent instructions (architecture boundaries, security model, coding standards, testing standards, commits & PR conventions). |
| `<area>/AGENTS.md` | Per-area rules (e.g. tree-specific or subsystem-specific overlays). |
| `<security-model-doc>` | The documented security model — what *is* and *isn't* a vulnerability. |

The per-PR review flow re-runs `git ls-files` against the
touched paths to discover any other `AGENTS.md` not in this
table; see [`review-flow.md#area-specific-overlay`](review-flow.md).

---

## Categories — link out to the source section

The list below is the **abstract canonical category list** the
skill uses when grouping findings. The concrete review-doc URL
for each category lives in the adopter's
`<project-config>/pr-management-code-review-criteria.md` →
`Section anchors` table; the skill resolves a category to its
URL at finding time by matching the category name verbatim
against that table's `Section` column. If a category has no
anchor row, the skill falls back to a plain reference (no
clickable link) and surfaces the missing anchor as a one-line
warning at the top of the review.

The canonical category list:

- Architecture boundaries
- Database / query correctness
- Code quality
- Third-party license compliance
- Testing
- API correctness
- UI (React/TypeScript)
- Generated files
- AI-generated code signals
- Quality signals to check
- Commits and PRs (newsfragments, commit messages, tracking issues)
- Security model

See
[`projects/_template/pr-management-code-review-criteria.md` § Section anchors](../../../projects/_template/pr-management-code-review-criteria.md#section-anchors)
for a worked example.

---

## Third-party license compliance

When the diff adds or modifies a file that contains a non-Apache licence
header (`SPDX-License-Identifier:` value other than `Apache-2.0`, or a
recognised licence block — MIT, BSD, GPL, LGPL, CDDL, MPL, EPL, etc.) or a
third-party copyright line (`Copyright (c) <non-ASF entity>`), classify the
licence against the ASF `resolved_licenses` policy
(`https://www.apache.org/legal/resolved.html`) and apply the following
severity rules:

| Category | Licences (examples) | Severity |
|---|---|---|
| X | GPL, AGPL, LGPL, CDDL, BUSL, SSPL | `blocking` — cannot be included in an ASF release in any form |
| B | MPL, EPL | `blocking` — cannot be included in source form; binary-only inclusion requires explicit justification |
| A | MIT, BSD-2, BSD-3, ISC, Apache 2.0 (other orgs) | `major` if `LICENSE` / `LICENSE.txt` / `licenses/` was **not** also updated in this PR — attribution is required before shipping |
| A + LICENSE updated | any Category A | ✅ no finding |

For Category A findings, check whether the same PR modifies `LICENSE`,
`LICENSE.txt`, or any file under a `licenses/` directory. If it does, the
inclusion is correctly attributed and no finding is raised.

**Relationship to "License headers":** when a new file's header is non-Apache
but not third-party (e.g. a contributor accidentally used the wrong SPDX
identifier), the "License headers" finding applies. When the header is
clearly from an upstream library or external author, route to this category
instead — the fix is to preserve the original header and update `LICENSE`,
not to replace it with an Apache header.

Source: `https://www.apache.org/legal/resolved.html` and
`https://www.apache.org/legal/apply-license.html`.

---

## Per-area / subtree-specific signals

When a PR touches a subtree the adopter listed in
`<project-config>/pr-management-code-review-criteria.md` →
`Per-area source files`, the skill reads (and quotes from) those
per-area files in addition to the repo-wide ones. The skill also
auto-discovers any `AGENTS.md` under the touched paths via
`git ls-files`, so an `AGENTS.md` not listed in the table is
still loaded if the diff touches its tree.

If a touched subtree has no `AGENTS.md` and no entry in the
adopter table, only the repo-wide rules apply.

---

## Security model — calibration

> This category also includes a **public-disclosure signal scan**
> that runs in Step 3 (PR title, body, and commit messages),
> before the diff is examined. See
> [`review-flow.md` § Security-disclosure signal scan](review-flow.md#security-disclosure-signal-scan).

Before flagging anything that looks security-flavoured in the
diff, read the documented security model at the path declared in
`<project-config>/pr-management-code-review-criteria.md` →
`security_model_calibration.file`. The framework's reference
threat model lives at
[`docs/security/threat-model.md`](../../../docs/security/threat-model.md);
read both before deciding. Use the calibration to distinguish:

1. an **actual vulnerability** that violates the documented
   model — flag as blocking,
2. a **known limitation** that's already documented as
   intentional — do not flag,
3. a **deployment-hardening opportunity** — belongs in
   deployment guidance, not as a code finding.

When the skill downgrades what looked like a finding because
the documented model permits it, the review body **quotes the
relevant model paragraph** so the contributor sees the
calibration explicitly. Don't paraphrase.

---

## Quality signals to check — image IP

The "Quality signals to check" category is primarily driven by the adopter's
source files. The following is a **framework-level default** that applies
regardless of adopter-specific rules.

When the diff adds one or more binary image files (`.png`, `.jpg`, `.jpeg`,
`.gif`, `.svg`, `.ico`, `.webp`), use judgment rather than raising an
automatic finding:

- **Contributor-created screenshots, diagrams, and documentation graphics**
  are legitimate by default — no finding.
- **Logos, brand assets, or illustrations** that look professionally produced
  warrant a short comment asking the contributor to confirm the source and
  licence: *"Could you confirm this image is original work or confirm its
  licence? If it's from a third-party source, it may need a `LICENSE` entry
  or a different approach."*

Do not flag every image addition. The signal is the visual character of the
asset — a hand-drawn architecture diagram is different from a polished brand
logo. When in doubt, ask rather than block.

## Quality signals to check — compiled artifacts

ASF releases must be source-only. Compiled or binary build artifacts added to
the repository risk ending up in a release, violating the ASF Release Policy
(`https://www.apache.org/legal/release-policy.html`).

When the diff adds any of the following file types, raise a `major` finding:

- **JVM**: `.class`, `.jar` (non-empty), `.war`, `.ear`
- **Python**: `.pyc`, `.pyo`, `.pyd`
- **Native**: `.so`, `.dll`, `.dylib`, `.exe`, `.o`, `.a`
- **Packages**: `.whl`, `.egg`

The finding is `major` with the text: *"Compiled artifacts must not be
committed to the source tree — ASF releases are source-only. Remove this
file and ensure it is generated at build time."* If the file would be
included in a release archive, escalate to `blocking`.

---

## Backports and version-specific PRs

If the adopter's
`<project-config>/pr-management-code-review-criteria.md` declares
a backport branch pattern (see its `Backports / version-specific
PRs` table), PRs whose base branch matches the pattern are
treated as backports of already-merged `main` work and get a
lighter-touch calibration:

- **Diff parity**: does this match what was merged on `main`?
- **Cherry-pick conflicts**: did the resolution introduce new
  changes that need scrutiny?
- **API/migration version markers**: backports should not
  introduce new version bumps in any
  versioning-sensitive subsystem the adopter calls out; if they
  do, cite the relevant `API correctness` anchor from the
  adopter's `Section anchors` table.

For these PRs, prefer `COMMENT` over `REQUEST_CHANGES` unless
the cherry-pick has clearly drifted from the `main` change.

If the adopter config has no backport pattern declared, this
section is a no-op and every PR is reviewed under the same
calibration.

---

## Conflict between source rules

If the per-area `AGENTS.md` rules **conflict** with the
repo-wide ones (rare; usually a more specific override), the
more specific one wins — but the conflict is surfaced to the
maintainer for explicit acceptance during disposition pick
(see [`review-flow.md`](review-flow.md)).

---

## When in doubt — defer

If after reading the diff you're not sure whether something is
a finding or just a style preference, **do not flag it**.
Surface the uncertainty to the maintainer (one line:
*"Hmm — line N does X, which I'm not sure violates the rules;
flagging for your eye."*) and let them decide. The cost of an
over-zealous auto-finding is a contributor who feels
nitpicked; the cost of a missed nit is one round of
back-and-forth a maintainer can catch easily on their own
pass.
