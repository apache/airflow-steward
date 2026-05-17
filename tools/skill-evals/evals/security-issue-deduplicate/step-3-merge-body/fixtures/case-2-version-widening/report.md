Drop tracker fields (issue #71):

The issue description: XCom pickle deserialization is present from 2.7.0
onwards — the fix in the kept tracker's targeted version is incomplete
because the vulnerable code path also exists in the Celery worker context
from 2.7.0.

Affected versions: >= 2.7.0, < 2.10.3

Security mailing list thread: Dave Security (wider range): https://lists.apache.org/thread/bbb222

Reporter credited as: Dave Security

CWE: CWE-502

Severity: Unknown

CVE tool link: _No response_
