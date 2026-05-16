You are executing Step 4 (extract template fields) of the security-issue-import
skill from the Apache Steward framework.

Your task: given a classified Report or ASF-security-relay email, extract the
fields needed to create a tracking issue. Return ONLY valid JSON.

Field extraction rules:

  title
    Construct from the email subject. Strip leading Re:, Fwd:, [SECURITY],
    and similar prefixes. Prefer the reporter's original subject when it is
    descriptive; otherwise paraphrase as "<Component>: <short description>".

  affected_versions
    Extract version strings mentioned in the body (e.g. "Airflow 2.9.1",
    ">= 2.7.0, < 2.10.3", "3.1.5"). If none mentioned, use "_No response_".

  reporter_credited_as
    For a plain Report: the display name from the From: header
    (e.g. "Alice Example" from '"Alice Example" <alice@example.com>').
    For an ASF-security-relay (sender is security@apache.org): use the
    name from the "Credit:" line at the end of the forwarded body instead.
    Never use "security@apache.org" as the credited name.

  severity
    Always "Unknown". The security team scores independently; reporter-supplied
    CVSS or severity labels are informational only and must not be used here.

Return ONLY valid JSON with exactly these fields:
{
  "title": "<string>",
  "affected_versions": "<string or _No response_>",
  "reporter_credited_as": "<string>",
  "severity": "Unknown",
  "rationale": "<one paragraph explaining each extraction decision>"
}

Do not include any text outside the JSON object.
