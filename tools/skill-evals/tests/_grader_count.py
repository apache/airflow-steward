#!/usr/bin/env python3
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
"""Mock batched grader that records its invocation count to a file.

Tests set ``GRADER_COUNTER_FILE`` to a temp path, then assert that exactly one
batched grader call was made per case regardless of how many prose-field
mismatches it contained.
"""
from __future__ import annotations

import json
import os
import re
import sys


def main() -> None:
    counter = os.environ["GRADER_COUNTER_FILE"]
    with open(counter, "a") as f:
        f.write("1\n")
    paths = re.findall(r"^Field: (\S+)$", sys.stdin.read(), flags=re.MULTILINE)
    print(json.dumps({p: {"match": True, "reason": "ok"} for p in paths}))


if __name__ == "__main__":
    main()
