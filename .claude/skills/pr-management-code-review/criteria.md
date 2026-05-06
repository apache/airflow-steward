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

The category headings below are the **abstract names** the skill
uses when grouping findings. The concrete URL each one links to
lives in the adopter's
`<project-config>/pr-management-code-review-criteria.md` →
`Section anchors` table — every adopter substitutes their own
review-doc URLs there. The skill resolves a category to its URL
at finding time by matching the heading verbatim against the
adopter table's `Section` column.

If a category has no anchor row in the adopter config, the skill
falls back to a plain reference (no clickable link) and surfaces
the missing anchor as a one-line warning at the top of the
review.

The canonical category list:

- Architecture boundaries
- Database / query correctness
- Code quality
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

Before flagging anything that looks security-flavoured, read
the documented security model at the path declared in
`<project-config>/pr-management-code-review-criteria.md` →
`security_model_calibration.file`, and the
[`AGENTS.md` § Security Model](../../../AGENTS.md#security-model)
calibration guide. The latter is short and tells you how to
distinguish:

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
