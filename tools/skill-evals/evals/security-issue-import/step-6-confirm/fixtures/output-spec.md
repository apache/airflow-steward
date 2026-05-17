## Eval output format

You are executing Step 6 (user confirmation) in isolation. The proposal list
and the user's confirmation reply are provided in the user turn as mock data.
Parse the reply and return ONLY valid JSON with these fields:

```json
{
  "action": "import" | "cancel" | "ambiguous",
  "import_items": [<int>, ...],
  "skip_items": [<int>, ...],
  "reject_with_canned": [{"item": <int>, "canned_name": "<string>"}],
  "edits": [{"item": <int>, "instruction": "<string>"}],
  "ambiguous_tokens": ["<token>", ...]
}
```

`import_items` lists every candidate that will have a tracker created.
When `action` is `"cancel"`, all lists are empty.
`ambiguous_tokens` is empty unless `action` is `"ambiguous"`.

Do not include any text outside the JSON object.
