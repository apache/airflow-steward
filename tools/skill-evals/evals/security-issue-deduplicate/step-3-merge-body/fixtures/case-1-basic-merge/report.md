Drop tracker fields (issue #67):

The issue description: The /api/v1/connections/test endpoint follows HTTP
redirects to RFC-1918 addresses, bypassing the basic host check. An
authenticated API user can exploit this to reach metadata services
(e.g. 169.254.169.254) via a redirect chain.

Short public summary for publish: SSRF via redirect follow in connection
test allows authenticated users to reach cloud metadata endpoints.

Affected versions: >= 2.8.0, < 2.10.3

Security mailing list thread: Bob Researcher (redirect-chain vector):
https://lists.apache.org/thread/xyz789

Public advisory URL: _No response_

Reporter credited as: Bob Researcher

PR with the fix: _No response_

CWE: CWE-918

Severity: Unknown

CVE tool link: _No response_
