## Output format

Return ONLY valid JSON with this structure:

```json
{
  "shape": "<one of: A | B | C | D | E-vague | E-precise | F | G | H>",
  "rationale": "<one sentence explaining why this shape was chosen>"
}
```

Shape taxonomy reference:
- **A** — self-contained single-file script that runs as-is (no external fixtures, no framework boilerplate)
- **B** — near-complete but requires minor additions (missing imports, missing `if __name__ == "__main__"`, etc.)
- **C** — framework test method (e.g. `def test_foo(self)`) needing a test class/runner wrapper
- **D** — multi-file project or requires external fixtures
- **E-vague** — code fragment without clear entry point or invocation; vague about how to trigger
- **E-precise** — code fragment with a clear entry point stated in prose but not in the code itself
- **F** — stack trace / error log only, no code
- **G** — configuration or data file (YAML, JSON, SQL) that must be fed to a tool
- **H** — prose-only description; no code or config supplied

Do not include any text outside the JSON object.
