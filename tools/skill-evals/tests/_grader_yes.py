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
"""Mock batched grader: returns match=true for every Field: path in stdin.

Used by tests as a stand-in for ``claude -p --model haiku``. Reads the runner's
batched rubric prompt on stdin, extracts every ``Field: <path>`` line, and
emits a one-line JSON object mapping each path to ``{"match": true, ...}``.
"""
from __future__ import annotations

import json
import re
import sys


def main() -> None:
    paths = re.findall(r"^Field: (\S+)$", sys.stdin.read(), flags=re.MULTILINE)
    print(json.dumps({p: {"match": True, "reason": "ok"} for p in paths}))


if __name__ == "__main__":
    main()
