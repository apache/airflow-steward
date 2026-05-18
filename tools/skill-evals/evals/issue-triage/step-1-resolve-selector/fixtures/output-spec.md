## Output format

Return ONLY valid JSON with this structure:

```json
{
  "issues": ["<KEY>", ...],
  "selector_type": "default | explicit-key | component | updated-since | reporter",
  "error": "<string describing validation error>" | null
}
```

`issues` is an empty array when `error` is non-null.
Do not include any text outside the JSON object.
