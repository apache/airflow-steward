## Eval output format

You are executing Step 4 (extract template fields) in isolation. The
classified email is provided in the user turn as mock data. Extract the
fields and return ONLY valid JSON with these fields:

```json
{
  "title": "<string>",
  "affected_versions": "<string or _No response_>",
  "reporter_credited_as": "<string>",
  "severity": "Unknown",
  "rationale": "<one paragraph explaining each extraction decision>"
}
```

Do not include any text outside the JSON object.
