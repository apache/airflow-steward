## Output format

Return ONLY valid JSON with this structure:

```json
{
  "high_confidence_count": 0,
  "broad_candidate_count": 0,
  "broad_candidates_marked_false_positive_prone": true | false,
  "security_overclaim": true | false,
  "recommended_language": "ci-risk" | "security-vulnerability" | "unclear",
  "include_command_and_scope": true | false,
  "reason": "<short rationale>"
}
```

`high_confidence_count` counts retired runner hits plus setup-action architecture mismatches.
`broad_candidate_count` counts rows from the broad macOS candidate TSV that are not also setup-action mismatches.
`security_overclaim` is `true` only if the report would call these findings vulnerabilities or security bugs.
Do not include any text outside the JSON object.
