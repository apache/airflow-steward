<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Implementation Plan — spec-loop

Maintained by the loop's **plan** mode. It is the prioritised list of
*gaps* found by comparing [`specs/`](specs/) against the actual code
(`.claude/skills/`, `tools/`, `docs/`). The **build** mode takes the
single highest-priority work item, isolates it on its own branch,
implements it, validates it, and commits — **one work item, one branch,
one PR** (the branch-per-feature constraint).

> Priority lives here, not in the specs. The specs describe functional
> areas (unordered); this plan orders the work.

---

## What's been built

- **Spec set** — [`specs/`](specs/): an `overview` plus a functional
  spec per area (the four live modes, the security lifecycle, the
  privacy-LLM gate, the sandbox, CVE tooling, adoption/setup, adapters,
  and meta/quality tooling).
- **Loop scaffolding** — `loop.sh` (plan / build / consolidate; a branch
  per work item; never pushes), `PROMPT_plan.md`, `PROMPT_build.md`,
  `PROMPT_consolidate.md`, `AGENTS.md` (loop-scoped operational context),
  and this plan. Branch-collision guard is inline in `loop.sh`.
- **Pairing — both skills shipped** — `pairing-self-review` and
  `pairing-multi-agent-review` (three independent axis passes; eval
  suites present); `docs/modes.md` Pairing row reflects 2 skills /
  `experimental`. Spec: [`specs/pairing-mode.md`](specs/pairing-mode.md).
- **Mentoring — both skills shipped** — `pr-management-mentor` and
  `good-first-issue-author` (eval suites present); `docs/modes.md`
  Mentoring row reflects 2 skills / `experimental`.
  Spec: [`specs/mentoring-mode.md`](specs/mentoring-mode.md).
- **Contributor skills** — `contributor-nomination`,
  `contributor-activity-sweep`, and `committer-onboarding` shipped with
  eval suites. Formerly tracked under draft PRs #227–#229.
- **Drafting — issue-fix-workflow skill** — `issue-fix-workflow` and
  `audit-finding-fix` shipped with eval suites (covers generic drafting
  from audit findings, formerly tracked as `generic-drafting` / #296).
  Spec: [`specs/drafting-mode.md`](specs/drafting-mode.md).
- **Docs — mode economics page** — `docs/mode-economics.md` exists
  (per-mode token-cost shape, vendor-neutral).
- **Meta — spec-status index** — `tools/spec-status-index/` exists as a
  `uv` tool that prints specs grouped by status.
  Spec: [`specs/meta-and-quality-tooling.md`](specs/meta-and-quality-tooling.md).
- **Meta — spec validator** — `tools/spec-validator/` exists as a `uv`
  project with `pyproject.toml` and `tests/`, validating spec frontmatter
  and body sections. Spec: [`specs/meta-and-quality-tooling.md`](specs/meta-and-quality-tooling.md).
- **Agent isolation — Python packaging + tests** — `tools/agent-isolation/`
  has `pyproject.toml`, `src/`, and a `tests/` directory with pytest
  coverage for the sandbox profiles and clean-env wrapper.
  Spec: [`specs/agent-isolation-sandbox.md`](specs/agent-isolation-sandbox.md).
- **Eval coverage — complete** — 37 skill eval suites exist in
  `tools/skill-evals/evals/`, covering all skills including the full
  setup-family (setup, setup-isolated-setup-doctor,
  setup-isolated-setup-install, setup-isolated-setup-update,
  setup-isolated-setup-verify, setup-override-upstream,
  setup-shared-config-sync).

---

## Work items (planned)

Priority order. Each maps to one branch and one PR. Branch names are
slugs, not numbers (numbering implies an order the specs don't carry).

1. **Prompt-injection defence hardening.** Skills that ingest external
   content — issue bodies, PR descriptions, mail threads — are potential
   injection surfaces. Audit the highest-risk ingestion skills
   (`security-issue-import`, `security-issue-import-from-pr`,
   `security-issue-import-from-md`, `security-issue-import-via-forwarder`)
   and add explicit injection-resistance guidance (e.g. a
   `treat-as-data` framing block at the ingest boundary) or a validator
   rule in `tools/skill-and-tool-validator/` that flags missing
   data-boundary markers. Validation:
   ```bash
   uv run --project tools/skill-and-tool-validator --group dev skill-and-tool-validate
   uv run --project tools/skill-evals skill-eval tools/skill-evals/evals/security-issue-import/
   ```
   Spec: [`specs/security-issue-lifecycle.md`](specs/security-issue-lifecycle.md)
   (import path); [`specs/meta-and-quality-tooling.md`](specs/meta-and-quality-tooling.md)
   (validator surface).
   Branch `injection-guard`.

2. **License-header enforcement.** Skills and tools must carry the
   Apache-2.0 SPDX header (`<!-- SPDX-License-Identifier: Apache-2.0 …
   -->` for Markdown; `# SPDX-License-Identifier: Apache-2.0` for
   Python) per repo-wide `AGENTS.md`. Add a check to
   `tools/skill-and-tool-validator/` that fails when a skill or tool
   source file is missing the header, so new contributions are caught at
   validation time rather than in code review. Validation:
   ```bash
   uv run --project tools/skill-and-tool-validator --group dev skill-and-tool-validate
   uv run --project tools/skill-and-tool-validator --group dev pytest
   ```
   Spec: [`specs/meta-and-quality-tooling.md`](specs/meta-and-quality-tooling.md).
   Branch `check-headers`.

---

## Notes & discoveries

- The general Ralph-loop technique pushes after every iteration. That
  step is intentionally **removed** here: `git push` and `gh pr create`
  are in the repo's `ask` permission list and are the human's step.
- Validation per work item lives in the relevant spec's **Validation**
  section; the build prompt runs it as backpressure before committing.
- Auto-merge is deliberately off and has no work items — building toward
  it would skip the proof MISSION requires.
- When a build iteration creates a new skill, its eval suite is part of
  that same work item — not a separate one.
- **Next plan pass:** the `adapters.md` spec Known Gaps section was not
  fully read in this pass (only the first 40 lines were sampled). If
  both remaining work items are built before the next plan beat, reading
  `adapters.md` in full is the first step to identify additional items.
