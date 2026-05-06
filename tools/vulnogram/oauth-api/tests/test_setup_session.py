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

import json

import pytest

from vulnogram_api import setup_session


def test_skip_validate_writes_file(tmp_path, monkeypatch, capsys):
    out = tmp_path / "session.json"
    rc = setup_session.main(
        [
            "--cookie-value",
            "s%3Anew-cookie-value",
            "--out",
            str(out),
            "--from-address",
            "you@apache.org",
            "--skip-validate",
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text())
    assert payload["host"] == "cveprocess.apache.org"
    assert payload["session_cookie_name"] == "connect.sid"
    assert payload["session_cookie_value"] == "s%3Anew-cookie-value"
    assert payload["from_address"] == "you@apache.org"
    assert "Wrote session" in capsys.readouterr().out


def test_validate_valid_returns_0(tmp_path, monkeypatch):
    out = tmp_path / "session.json"
    monkeypatch.setattr(setup_session, "probe", lambda *a, **kw: "valid")
    rc = setup_session.main(
        [
            "--cookie-value",
            "s%3Aabc",
            "--out",
            str(out),
            "--from-address",
            "you@apache.org",
        ]
    )
    assert rc == 0


def test_validate_expired_returns_2(tmp_path, monkeypatch, capsys):
    out = tmp_path / "session.json"
    monkeypatch.setattr(setup_session, "probe", lambda *a, **kw: "expired")
    rc = setup_session.main(
        [
            "--cookie-value",
            "s%3Aold",
            "--out",
            str(out),
            "--from-address",
            "you@apache.org",
        ]
    )
    assert rc == 2
    assert "OAuth login" in capsys.readouterr().err


def test_empty_interactive_cookie_aborts(tmp_path, monkeypatch):
    """When the user pastes nothing at the interactive prompt, the
    script must abort without writing the session file."""
    out = tmp_path / "session.json"
    monkeypatch.setattr(setup_session, "getpass", type("G", (), {"getpass": lambda *_: ""}))
    with pytest.raises(SystemExit) as excinfo:
        setup_session.main(
            [
                "--out",
                str(out),
                "--from-address",
                "you@apache.org",
                "--skip-validate",
            ]
        )
    assert "Empty" in str(excinfo.value)
    # Nothing written.
    assert not out.exists()


def test_custom_host_flag_round_trips(tmp_path, monkeypatch):
    out = tmp_path / "session.json"
    rc = setup_session.main(
        [
            "--host",
            "vuln.example.com",
            "--cookie-name",
            "session.id",
            "--cookie-value",
            "abc",
            "--out",
            str(out),
            "--from-address",
            "you@example.com",
            "--skip-validate",
        ]
    )
    assert rc == 0
    payload = json.loads(out.read_text())
    assert payload["host"] == "vuln.example.com"
    assert payload["session_cookie_name"] == "session.id"
    assert payload["session_cookie_value"] == "abc"
