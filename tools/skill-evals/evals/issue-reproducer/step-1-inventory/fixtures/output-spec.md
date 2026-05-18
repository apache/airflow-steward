## Output format

Return ONLY valid JSON with this structure:

```json
{
  "blocks": [
    {
      "location": "body | comment-<N> | attachment-<filename>",
      "language": "python | java | bash | sql | yaml | other | unknown",
      "line_count": <integer>
    }
  ],
  "reporter_env": {
    "runtime_version": "<version string or null>",
    "os": "<OS string or null>",
    "notes": "<any other environment details or null>"
  },
  "block_count": <integer matching len(blocks)>
}
```

Do not include any text outside the JSON object.
