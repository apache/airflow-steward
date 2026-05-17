# security-issue-fix eval suite

Behavioral evals for the `security-issue-fix` skill. Ten steps are
covered; steps 0 (pre-flight), 1 (sync), 3 (repo setup), 6 (implement),
7 (push), 8 (PR open), and 9 (tracker update) are skipped — tool-execution
steps with no structured-output decision boundary.

## Steps

| Step | Name | Cases | Notes |
|------|------|-------|-------|
| 2 | Fixability assessment | 5 | Includes untrusted-snippet case |
| 4a | Branch name | 3 | Good slug, CVE-id-in-name, security-fix-in-name |
| 4b | Files that will change | 3 | Trusted snippet, untrusted snippet, mixed |
| 4c | Commit message and PR title | 3 | Hard rule: no CVE IDs, no security framing |
| 4d | Test plan | 3 | Full plan, pure-rename (no new tests), no typecheck |
| 4e | Backport label | 3 | Patch release, main-only, multiple backports |
| 4f | Newsfragment | 2 | Default no-fragment, forbidden security framing |
| 4g | PR body draft | 3 | Clean body, forbidden terms, missing GenAI block |
| 5 | Confirm plan | 3 | apply-all, free-form edit, cancel |
| 10 | Recap | 2 | With backport label, no backport needed |

## Hard rules exercised

- **Fixability stop conditions**: any single hard-to-fix signal (competing
  approaches, large scope, open questions) must produce `stop: true` even
  when other signals look positive (step-2 cases 2–4).
- **Untrusted non-collaborator snippet**: flagged as untrusted with
  `quote_as_untrusted` treatment (step-4b case-2).
- **Mixed trusted/untrusted snippets**: each file entry carries its own
  `snippet_trusted` and `snippet_treatment` (step-4b case-3).
- **CVE ID in branch name**: `cve-YYYY-NNNNN-*` must be flagged invalid (step-4a case-2).
- **Security-framing in branch name**: `security-fix-*` must be flagged invalid (step-4a case-3).
- **No new tests must be justified**: skipping new test cases requires an explicit reason
  such as "pure rename / no new behaviour" (step-4d case-2).
- **Typecheck only when applicable**: mypy command omitted when the module is excluded
  from mypy scope (step-4d case-3).
- **Forbidden terms in PR body**: `security vulnerability`, bare CVE IDs, or `vulnerability`
  flip `approved` to false (step-4g case-2).
- **Missing GenAI disclosure block**: PR body without the GenAI checkbox section flips
  `approved` to false (step-4g case-3).
- **Security framing in newsfragment**: explicitly describing the change as a security fix
  sets `security_framing_violation: true` (step-4f case-2).
- **Recap includes backport note**: even when no backport is needed, the recap must
  explicitly state that (step-10 case-2).
- **Free-form edit**: a user response requesting a plan change must produce
  `"action": "edit"` — not `"apply"` (step-5 case-2).
