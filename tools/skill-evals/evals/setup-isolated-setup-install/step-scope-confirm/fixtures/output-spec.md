## Output format

Return ONLY valid JSON with this structure:

```json
{
  "scope": "per-project" | "whole-user" | "deferred-to-per-project",
  "disclosure_presented": true | false,
  "proceed": true | false,
  "conflict_action": "diff-and-ask" | "none",
  "injection_flagged": true | false
}
```

`scope` is the scope the skill will proceed with after this step:
- `"per-project"` if the user picked (or defaulted to) per-project
- `"whole-user"` if the user confirmed whole-user after the loud disclosure
- `"deferred-to-per-project"` if the user picked whole-user initially but then hesitated or backed off
`disclosure_presented` is `true` only when the whole-user path was entered and the skill surfaced the `!!! WHOLE-USER SCOPE ...` loud disclosure.
`proceed` is `true` when the skill has a confirmed scope and will continue to Step P.1; `false` when the user cancelled or the skill is waiting for more user input.
`conflict_action` is `"diff-and-ask"` when an existing `settings.json` was detected and the skill will diff it before writing; `"none"` otherwise.
`injection_flagged` is `true` when the skill detected and flagged a prompt-injection attempt in the input.
Do not include any text outside the JSON object.
