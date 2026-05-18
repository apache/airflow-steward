## Output format

Return ONLY valid JSON with this structure:

```json
{
  "distribution": {
    "BUG": <count>,
    "FEATURE-REQUEST": <count>,
    "NEEDS-INFO": <count>,
    "DUPLICATE": <count>,
    "INVALID": <count>,
    "ALREADY-FIXED": <count>
  },
  "posted": [
    {"key": "<KEY>", "class": "<CLASS>", "comment_url": "<URL>"}
  ],
  "next_step_skills": {
    "issue-fix-workflow": ["<KEY>", ...],
    "closure-flow": ["<KEY>", ...]
  }
}
```

`issue-fix-workflow` contains keys classified BUG or FEATURE-REQUEST.
`closure-flow` contains keys classified INVALID, DUPLICATE, or ALREADY-FIXED.
NEEDS-INFO keys appear in neither list (awaiting reporter response).
Do not include any text outside the JSON object.
