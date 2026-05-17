You are executing the commit/PR title neutrality check from Step 4c of the
security-issue-fix skill from the Apache Steward framework.

Before presenting the implementation plan, the proposed branch name and PR
title must be checked against the neutrality rules in Step 4c.

## Neutrality rules for branch name and PR title

The branch name and PR title must use neutral bug-fix / improvement language.
They must NOT contain any of:

- A CVE identifier (`CVE-YYYY-NNNNN`)
- The words `CVE`, `vulnerability`, `security fix`, `advisory`, or `security`
  as a standalone word (e.g. "security-fix" or "security fix" is forbidden;
  "improves asset security model" is also forbidden because it signals a
  security motivation)
- Any reporter name tied to a security finding
- The word `sensitive` in a context that points at an unmasked-credential bug
- Wording that would allow a reader to reconstruct the attack vector from
  the title alone (e.g. "prevent RCE via pickle.loads in XCom" — "RCE" and
  "exploit path" language reveals the security framing)

Tracker URLs, `<tracker>#NNN`, and bare `#NNN` references ARE allowed —
they are public-safe identifiers. The constraint is on security framing of
the surrounding text, not on the identifier itself.

Good examples (neutral, accurate):
- "Fix asset graph view leaking DAGs outside the user's permissions"
- "Add access_key and connection_string to DEFAULT_SENSITIVE_FIELDS"
- "Improve xcom value handling in extra links API"

Bad examples (reveal security framing):
- "cve-2026-40690-xcom-fix" (contains CVE ID)
- "Fix security vulnerability in connection test endpoint" (contains "security vulnerability")
- "Prevent RCE via XCom pickle deserialization" (attack-vector language)

## Output

Return ONLY valid JSON with these fields:
{
  "branch_name": "<proposed branch name>",
  "pr_title": "<proposed PR title>",
  "branch_name_valid": true | false,
  "pr_title_valid": true | false,
  "forbidden_terms_found": ["<term>"],
  "recommendation": "<one-line fix if invalid, or 'looks good' if valid>"
}

`forbidden_terms_found` lists each specific term or pattern that violated
the rules. Empty array when both are valid.

Do not include any text outside the JSON object.
