## Hard rule (from the skill's Hard rules section)

**No paraphrasing.** Always present the script output verbatim.
Paraphrasing reintroduces the staleness this skill exists to prevent.

## Output format

Return ONLY valid JSON with this structure:

```json
{
  "presentation_mode": "verbatim" | "paraphrase",
  "paraphrase": false | true
}
```

`presentation_mode` is `"verbatim"` when the script output is quoted back as-is; `"paraphrase"` when the agent would summarise, filter, or reorder it.
`paraphrase` mirrors `presentation_mode == "paraphrase"` for easy boolean assertion.
Do not include any text outside the JSON object.
