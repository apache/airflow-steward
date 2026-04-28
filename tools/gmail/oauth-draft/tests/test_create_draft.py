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

import email
import email.policy
from email.message import EmailMessage

from oauth_draft.create_draft import build_mime, headers_from_thread, parse_args


def parse_built_message(raw: bytes) -> EmailMessage:
    msg = email.message_from_bytes(raw, policy=email.policy.default)
    assert isinstance(msg, EmailMessage)
    return msg


def test_build_mime_sets_basic_headers():
    raw = build_mime(
        from_addr="me@example.com",
        to=["a@example.com"],
        cc=[],
        bcc=[],
        subject="Hello",
        body="Body content.",
        in_reply_to=None,
        references=None,
    )
    msg = parse_built_message(raw)
    assert msg["From"] == "me@example.com"
    assert msg["To"] == "a@example.com"
    assert msg["Subject"] == "Hello"
    assert msg["Cc"] is None
    assert msg["Bcc"] is None
    assert msg["In-Reply-To"] is None
    assert msg["References"] is None
    assert msg.get_content().rstrip() == "Body content."


def test_build_mime_joins_multiple_recipients():
    raw = build_mime(
        from_addr="me@example.com",
        to=["a@example.com", "b@example.com"],
        cc=["cc1@example.com", "cc2@example.com"],
        bcc=["bcc@example.com"],
        subject="Multi",
        body="x",
        in_reply_to=None,
        references=None,
    )
    msg = parse_built_message(raw)
    assert msg["To"] == "a@example.com, b@example.com"
    assert msg["Cc"] == "cc1@example.com, cc2@example.com"
    assert msg["Bcc"] == "bcc@example.com"


def test_build_mime_sets_reply_headers_when_provided():
    raw = build_mime(
        from_addr="me@example.com",
        to=["a@example.com"],
        cc=[],
        bcc=[],
        subject="Re: Thing",
        body="reply",
        in_reply_to="<msg-1@example.com>",
        references="<root@example.com> <msg-1@example.com>",
    )
    msg = parse_built_message(raw)
    assert msg["In-Reply-To"] == "<msg-1@example.com>"
    assert msg["References"] == "<root@example.com> <msg-1@example.com>"


def test_headers_from_thread_empty_returns_none_pair():
    assert headers_from_thread({}) == (None, None)
    assert headers_from_thread({"messages": []}) == (None, None)


def test_headers_from_thread_no_message_id_returns_none_pair():
    thread = {"messages": [{"payload": {"headers": [{"name": "Subject", "value": "x"}]}}]}
    assert headers_from_thread(thread) == (None, None)


def test_headers_from_thread_seeds_references_when_absent():
    thread = {
        "messages": [
            {
                "payload": {
                    "headers": [
                        {"name": "Message-ID", "value": "<a@example.com>"},
                    ]
                }
            }
        ]
    }
    assert headers_from_thread(thread) == ("<a@example.com>", "<a@example.com>")


def test_headers_from_thread_appends_to_existing_references():
    thread = {
        "messages": [
            {
                "payload": {
                    "headers": [
                        {"name": "Message-ID", "value": "<root@example.com>"},
                    ]
                }
            },
            {
                "payload": {
                    "headers": [
                        {"name": "Message-ID", "value": "<reply@example.com>"},
                        {"name": "References", "value": "<root@example.com>"},
                    ]
                }
            },
        ]
    }
    in_reply_to, references = headers_from_thread(thread)
    assert in_reply_to == "<reply@example.com>"
    assert references == "<root@example.com> <reply@example.com>"


def test_headers_from_thread_is_case_insensitive_on_header_name():
    thread = {
        "messages": [
            {
                "payload": {
                    "headers": [
                        {"name": "message-id", "value": "<lower@example.com>"},
                    ]
                }
            }
        ]
    }
    assert headers_from_thread(thread)[0] == "<lower@example.com>"


def test_parse_args_defaults():
    args = parse_args(["--to", "x@example.com", "--subject", "S"])
    assert args.to == ["x@example.com"]
    assert args.cc == []
    assert args.bcc == []
    assert args.body_file == "-"
    assert args.thread_id is None
    assert args.no_reply_headers is False


def test_parse_args_repeats():
    args = parse_args(
        [
            "--to",
            "a@example.com",
            "--to",
            "b@example.com",
            "--cc",
            "c@example.com",
            "--subject",
            "S",
        ]
    )
    assert args.to == ["a@example.com", "b@example.com"]
    assert args.cc == ["c@example.com"]
