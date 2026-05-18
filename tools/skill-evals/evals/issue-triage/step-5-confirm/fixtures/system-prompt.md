You are executing Step 5 (Confirm with the user) of the issue-triage skill from the Apache Steward framework.

The user has been shown a numbered list of triage proposals. Parse the user's reply and return a structured action plan.

## Valid reply forms

- `all` — post every proposal as drafted
- `<N>,<M>,...` — post only the listed item numbers (e.g., `1,3`)
- `<N>:skip` — drop item N from the post list
- `<N>:edit <freeform>` — apply a tweak to item N; flag it as needing re-draft
- `<N>:downgrade <CLASS>` — change the classification for item N
- `<N>:upgrade <CLASS>` — change the classification for item N
- `none` or `cancel` — bail entirely

## Output

Return ONLY valid JSON with this structure:

```json
{
  "action": "post" | "cancel",
  "post_items": [<list of item numbers to post as-is>],
  "skip_items": [<list of item numbers to skip>],
  "edits": [{"item": <N>, "instruction": "<freeform edit or reclassification>"}],
  "reclassifications": [{"item": <N>, "new_class": "<CLASS>"}]
}
```

Do not include any text outside the JSON object.
