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

from oauth_draft.credentials import Credentials, locate_credentials


def write_creds(path, **overrides):
    data = {
        "client_id": "id-123",
        "client_secret": "secret-456",
        "refresh_token": "refresh-789",
        "from_address": "you@example.com",
    }
    data.update(overrides)
    path.write_text(json.dumps(data))
    return path


def test_load_full_record(tmp_path):
    p = write_creds(tmp_path / "c.json")
    creds = Credentials.load(p)
    assert creds.client_id == "id-123"
    assert creds.client_secret == "secret-456"
    assert creds.refresh_token == "refresh-789"
    assert creds.from_address == "you@example.com"


def test_load_missing_required_field(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"client_id": "x", "client_secret": "y"}))
    with pytest.raises(SystemExit) as excinfo:
        Credentials.load(p)
    assert "refresh_token" in str(excinfo.value)
    assert "from_address" in str(excinfo.value)


def test_load_without_from_address_when_not_required(tmp_path):
    p = tmp_path / "c.json"
    p.write_text(json.dumps({"client_id": "x", "client_secret": "y", "refresh_token": "z"}))
    creds = Credentials.load(p, require_from_address=False)
    assert creds.from_address is None


def test_load_empty_value_treated_as_missing(tmp_path):
    p = write_creds(tmp_path / "c.json", refresh_token="")
    with pytest.raises(SystemExit) as excinfo:
        Credentials.load(p)
    assert "refresh_token" in str(excinfo.value)


def test_locate_explicit_wins(tmp_path, monkeypatch):
    explicit = tmp_path / "explicit.json"
    explicit.write_text("{}")
    other = tmp_path / "other.json"
    other.write_text("{}")
    monkeypatch.setenv("GMAIL_OAUTH_CREDENTIALS", str(other))
    assert locate_credentials(str(explicit)) == explicit


def test_locate_falls_back_to_env(tmp_path, monkeypatch):
    env_path = tmp_path / "env.json"
    env_path.write_text("{}")
    monkeypatch.setenv("GMAIL_OAUTH_CREDENTIALS", str(env_path))
    assert locate_credentials(None) == env_path


def test_locate_raises_when_nothing_exists(tmp_path, monkeypatch):
    monkeypatch.delenv("GMAIL_OAUTH_CREDENTIALS", raising=False)
    monkeypatch.setattr(
        "oauth_draft.credentials.DEFAULT_CREDENTIALS_PATH",
        tmp_path / "does-not-exist.json",
    )
    with pytest.raises(SystemExit) as excinfo:
        locate_credentials(None)
    assert "No Gmail OAuth credentials found" in str(excinfo.value)
