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
import subprocess
from unittest.mock import MagicMock, patch

import pytest

from oauth_draft.setup_creds import detect_from_address, main, parse_args

# --- detect_from_address ---------------------------------------------------


def test_detect_from_address_uses_env_var(monkeypatch):
    monkeypatch.setenv("GMAIL_FROM", "env@example.com")
    assert detect_from_address() == "env@example.com"


def test_detect_from_address_falls_back_to_git_config(monkeypatch):
    monkeypatch.delenv("GMAIL_FROM", raising=False)
    with patch(
        "oauth_draft.setup_creds.subprocess.check_output",
        return_value="git@example.com\n",
    ):
        assert detect_from_address() == "git@example.com"


def test_detect_from_address_returns_none_when_git_missing(monkeypatch):
    monkeypatch.delenv("GMAIL_FROM", raising=False)
    with patch(
        "oauth_draft.setup_creds.subprocess.check_output",
        side_effect=FileNotFoundError,
    ):
        assert detect_from_address() is None


def test_detect_from_address_returns_none_when_git_errors(monkeypatch):
    monkeypatch.delenv("GMAIL_FROM", raising=False)
    with patch(
        "oauth_draft.setup_creds.subprocess.check_output",
        side_effect=subprocess.CalledProcessError(1, "git"),
    ):
        assert detect_from_address() is None


def test_detect_from_address_returns_none_when_git_returns_empty(monkeypatch):
    monkeypatch.delenv("GMAIL_FROM", raising=False)
    with patch(
        "oauth_draft.setup_creds.subprocess.check_output",
        return_value="\n",
    ):
        assert detect_from_address() is None


# --- parse_args ------------------------------------------------------------


def test_parse_args_minimal(monkeypatch):
    # Avoid relying on the host's environment / git config: stub
    # detect_from_address out of the parser default.
    monkeypatch.setenv("GMAIL_FROM", "default@example.com")
    args = parse_args(["client.json"])
    assert args.client_secrets == "client.json"
    assert args.from_address == "default@example.com"
    assert args.out.endswith("/.config/apache-steward/gmail-oauth.json")
    assert args.rm_client_secrets is False


def test_parse_args_overrides(monkeypatch):
    monkeypatch.setenv("GMAIL_FROM", "default@example.com")
    args = parse_args(
        [
            "client.json",
            "--from-address",
            "override@example.com",
            "--out",
            "/custom/path.json",
            "--rm-client-secrets",
        ]
    )
    assert args.from_address == "override@example.com"
    assert args.out == "/custom/path.json"
    assert args.rm_client_secrets is True


# --- main ------------------------------------------------------------------


def _client_secrets(tmp_path):
    p = tmp_path / "client_secrets.json"
    p.write_text(
        json.dumps(
            {
                "installed": {
                    "client_id": "cid",
                    "client_secret": "secret",
                }
            }
        )
    )
    return p


def _flow_creds(refresh_token="rt-1"):
    creds = MagicMock()
    creds.refresh_token = refresh_token
    creds.scopes = ["https://mail.google.com/"]
    return creds


def test_main_errors_when_no_from_address(tmp_path, monkeypatch):
    monkeypatch.delenv("GMAIL_FROM", raising=False)
    secrets = _client_secrets(tmp_path)
    out = tmp_path / "out.json"
    with patch(
        "oauth_draft.setup_creds.subprocess.check_output",
        side_effect=FileNotFoundError,
    ):
        with pytest.raises(SystemExit) as excinfo:
            main([str(secrets), "--out", str(out)])
    assert "Could not determine --from-address" in str(excinfo.value)


def test_main_errors_when_client_secrets_missing(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_FROM", "me@example.com")
    out = tmp_path / "out.json"
    with pytest.raises(SystemExit) as excinfo:
        main([str(tmp_path / "does-not-exist.json"), "--out", str(out)])
    assert "client_secrets not found" in str(excinfo.value)


def test_main_errors_when_flow_returns_no_refresh_token(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_FROM", "me@example.com")
    secrets = _client_secrets(tmp_path)
    out = tmp_path / "out.json"
    flow = MagicMock()
    flow.run_local_server.return_value = _flow_creds(refresh_token=None)
    with patch(
        "oauth_draft.setup_creds.InstalledAppFlow.from_client_secrets_file",
        return_value=flow,
    ):
        with pytest.raises(SystemExit) as excinfo:
            main([str(secrets), "--out", str(out)])
    assert "no refresh_token" in str(excinfo.value)


def test_main_writes_credentials_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GMAIL_FROM", "me@example.com")
    secrets = _client_secrets(tmp_path)
    out_dir = tmp_path / "creds-dir"
    out = out_dir / "gmail-oauth.json"
    flow = MagicMock()
    flow.run_local_server.return_value = _flow_creds()
    with patch(
        "oauth_draft.setup_creds.InstalledAppFlow.from_client_secrets_file",
        return_value=flow,
    ):
        rc = main([str(secrets), "--out", str(out)])
    assert rc == 0
    written = json.loads(out.read_text())
    assert written == {
        "client_id": "cid",
        "client_secret": "secret",
        "refresh_token": "rt-1",
        "from_address": "me@example.com",
    }
    # Mode should be 600 (owner-rw only) per the atomic-write path.
    assert (out.stat().st_mode & 0o777) == 0o600
    # Parent dir should be 700.
    assert (out_dir.stat().st_mode & 0o777) == 0o700
    # Original client_secrets is left in place by default.
    assert secrets.exists()
    # The startup banner logs the path of the client_secrets file (NOT
    # its content). Asserts the variable rename
    # (`client_secrets` → `client_secrets_path`) didn't break the
    # log message that addresses CodeQL `py/clear-text-logging-
    # sensitive-data` finding #3 on PR #6.
    out_text = capsys.readouterr().out
    assert f"Running OAuth flow against {secrets.resolve()}" in out_text


def test_main_with_rm_client_secrets_deletes_input(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("GMAIL_FROM", "me@example.com")
    secrets = _client_secrets(tmp_path)
    out = tmp_path / "creds-dir" / "creds.json"
    flow = MagicMock()
    flow.run_local_server.return_value = _flow_creds()
    with patch(
        "oauth_draft.setup_creds.InstalledAppFlow.from_client_secrets_file",
        return_value=flow,
    ):
        main([str(secrets), "--out", str(out), "--rm-client-secrets"])
    assert not secrets.exists()
    # The "Removed <path>" log line — covers the second CodeQL
    # `py/clear-text-logging-sensitive-data` site on the renamed
    # `client_secrets_path` variable.
    out_text = capsys.readouterr().out
    assert f"Removed {secrets.resolve()}" in out_text


def test_main_handles_web_shaped_client_secrets(tmp_path, monkeypatch):
    monkeypatch.setenv("GMAIL_FROM", "me@example.com")
    secrets = tmp_path / "client.json"
    secrets.write_text(json.dumps({"web": {"client_id": "wcid", "client_secret": "wsecret"}}))
    out = tmp_path / "creds-dir" / "creds.json"
    flow = MagicMock()
    flow.run_local_server.return_value = _flow_creds()
    with patch(
        "oauth_draft.setup_creds.InstalledAppFlow.from_client_secrets_file",
        return_value=flow,
    ):
        main([str(secrets), "--out", str(out)])
    written = json.loads(out.read_text())
    assert written["client_id"] == "wcid"
    assert written["client_secret"] == "wsecret"
