# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
from __future__ import annotations

from oauth_draft.mark_threads_read import parse_args


def test_default_action_is_remove_unread():
    args = parse_args(["--query", "in:inbox"])
    assert args.add_label == []
    assert args.remove_label == ["UNREAD"]
    assert args.execute is False
    assert args.max is None


def test_explicit_add_label_does_not_inject_unread_default():
    args = parse_args(["--query", "in:inbox", "--add-label", "STARRED"])
    assert args.add_label == ["STARRED"]
    assert args.remove_label == []


def test_explicit_remove_label_does_not_inject_unread_default():
    args = parse_args(["--query", "in:inbox", "--remove-label", "INBOX"])
    assert args.add_label == []
    assert args.remove_label == ["INBOX"]


def test_repeat_label_flags_accumulate():
    args = parse_args(
        [
            "--query",
            "in:inbox",
            "--add-label",
            "A",
            "--add-label",
            "B",
            "--remove-label",
            "C",
        ]
    )
    assert args.add_label == ["A", "B"]
    assert args.remove_label == ["C"]


def test_execute_and_max_flags():
    args = parse_args(["--query", "x", "--execute", "--max", "5"])
    assert args.execute is True
    assert args.max == 5
