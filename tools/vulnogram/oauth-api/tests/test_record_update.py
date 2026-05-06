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

from vulnogram_api import record_update


def _write_session(path):
    path.write_text(
        json.dumps(
            {
                "host": "cveprocess.apache.org",
                "session_cookie_name": "connect.sid",
                "session_cookie_value": "s%3Atest",
                "from_address": "you@apache.org",
            }
        )
    )
    return path


def test_invalid_cve_id_rejected(tmp_path, monkeypatch, capsys):
    creds = _write_session(tmp_path / "session.json")
    body = tmp_path / "body.json"
    body.write_text("{}")
    monkeypatch.setenv("VULNOGRAM_SESSION", str(creds))
    with pytest.raises(SystemExit) as excinfo:
        record_update.main(
            ["--cve-id", "not-a-cve", "--json-file", str(body)],
        )
    assert "CVE-YYYY-NNNN" in str(excinfo.value)


def test_missing_json_file_errors(tmp_path, monkeypatch):
    _write_session(tmp_path / "session.json")
    monkeypatch.setenv("VULNOGRAM_SESSION", str(tmp_path / "session.json"))
    with pytest.raises(SystemExit) as excinfo:
        record_update.main(
            ["--cve-id", "CVE-2026-12345", "--json-file", str(tmp_path / "missing.json")],
        )
    assert "not found" in str(excinfo.value)


def test_non_object_json_rejected(tmp_path, monkeypatch):
    _write_session(tmp_path / "session.json")
    body = tmp_path / "body.json"
    body.write_text(json.dumps([1, 2, 3]))
    monkeypatch.setenv("VULNOGRAM_SESSION", str(tmp_path / "session.json"))
    with pytest.raises(SystemExit) as excinfo:
        record_update.main(
            ["--cve-id", "CVE-2026-12345", "--json-file", str(body)],
        )
    assert "not a JSON object" in str(excinfo.value)


def test_session_expired_returns_2(tmp_path, monkeypatch, capsys):
    _write_session(tmp_path / "session.json")
    body = tmp_path / "body.json"
    body.write_text(json.dumps({"x": 1}))
    monkeypatch.setenv("VULNOGRAM_SESSION", str(tmp_path / "session.json"))

    def _raise_expired(*a, **kw):
        from vulnogram_api.client import SessionExpired

        raise SessionExpired("session expired")

    monkeypatch.setattr(record_update, "update_record", _raise_expired)
    rc = record_update.main(["--cve-id", "CVE-2026-12345", "--json-file", str(body)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "session expired" in err


def test_save_failed_returns_5(tmp_path, monkeypatch, capsys):
    _write_session(tmp_path / "session.json")
    body = tmp_path / "body.json"
    body.write_text(json.dumps({"x": 1}))
    monkeypatch.setenv("VULNOGRAM_SESSION", str(tmp_path / "session.json"))

    def _raise_save_failed(*a, **kw):
        from vulnogram_api.client import RecordSaveFailed

        raise RecordSaveFailed("validation: missing field")

    monkeypatch.setattr(record_update, "update_record", _raise_save_failed)
    rc = record_update.main(["--cve-id", "CVE-2026-12345", "--json-file", str(body)])
    assert rc == 5
    err = capsys.readouterr().err
    assert "missing field" in err


def test_happy_path_returns_0(tmp_path, monkeypatch, capsys):
    _write_session(tmp_path / "session.json")
    body = tmp_path / "body.json"
    body.write_text(json.dumps({"x": 1}))
    monkeypatch.setenv("VULNOGRAM_SESSION", str(tmp_path / "session.json"))
    monkeypatch.setattr(
        record_update,
        "update_record",
        lambda *a, **kw: {"type": "saved"},
    )
    rc = record_update.main(["--cve-id", "CVE-2026-12345", "--json-file", str(body)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "saved" in out
    assert "CVE-2026-12345" in out
