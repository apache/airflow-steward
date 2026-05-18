## Output format

Return ONLY valid JSON with this structure:

```json
{
  "baselines": [
    {
      "year": <integer>,
      "status": "still-fails | fixed | unknown",
      "source": "<comment-N by <handle> | body>"
    }
  ],
  "baseline_count": <integer matching len(baselines)>
}
```

`baselines` is empty when no maintainer run records are found in the thread.
Do not include any text outside the JSON object.
