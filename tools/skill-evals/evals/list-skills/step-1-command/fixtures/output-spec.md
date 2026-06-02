## Output format

Return ONLY valid JSON with this structure:

```json
{
  "command": "<full bash command to run, including any flags>",
  "verbose": true | false
}
```

`verbose` is `true` when the user asked for detailed or long descriptions; `false` for the default one-line-per-skill layout.
Do not include any text outside the JSON object.
