# SPDX-License-Identifier: Apache-2.0
# https://www.apache.org/licenses/LICENSE-2.0

"""Python reference implementation of the issue-reassess-stats dashboard.

Status: stub. Parity implementation welcome.

The Groovy reference at reference.groovy is the working implementation.
A Python parity implementation should:

1. Accept the same CLI shape: <campaign-dir> [--output <file>]
2. Read verdict.json files from <campaign-dir>/<KEY>/verdict.json
3. Compute aggregates per .claude/skills/issue-reassess-stats/aggregate.md
4. Emit self-contained HTML per .claude/skills/issue-reassess-stats/render.md
5. Match the Groovy reference's section ordering and threshold values
6. Use only stdlib (no external dependencies)

Contributions welcome via PR against apache/airflow-steward.
"""

import sys

print(
    "Python reference is a stub. Use reference.groovy for now.\n"
    "Parity implementation welcome via PR.",
    file=sys.stderr,
)
sys.exit(2)
