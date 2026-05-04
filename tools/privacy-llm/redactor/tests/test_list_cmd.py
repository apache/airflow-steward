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
"""Tests for ``redactor.list_cmd`` — the ``pii-list`` CLI."""

from __future__ import annotations

import io
import json
import pathlib

from redactor import list_cmd
from redactor.mapping import Entry, save_mapping_atomic


def _seed(path: pathlib.Path) -> None:
    save_mapping_atomic(
        path,
        {
            "N-abcdef": Entry(identifier="N-abcdef", type="name", value="Jane Smith"),
            "E-fedcba": Entry(identifier="E-fedcba", type="email", value="jane@example.com"),
        },
    )


def _run(monkeypatch, argv: list[str]) -> tuple[str, int]:
    stdout = io.StringIO()
    monkeypatch.setattr("sys.stdout", stdout)
    rc = list_cmd.main(argv)
    return stdout.getvalue(), rc


def test_list_text_format(tmp_path: pathlib.Path, monkeypatch):
    _seed(tmp_path / "pii.json")
    out, rc = _run(monkeypatch, ["--mapping-path", str(tmp_path / "pii.json")])
    assert rc == 0
    # Sorted by identifier; tab-separated columns.
    lines = out.strip().splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("E-fedcba\t")
    assert "Jane Smith" in lines[1]


def test_list_json_format(tmp_path: pathlib.Path, monkeypatch):
    _seed(tmp_path / "pii.json")
    out, rc = _run(
        monkeypatch,
        ["--mapping-path", str(tmp_path / "pii.json"), "--format", "json"],
    )
    assert rc == 0
    payload = json.loads(out)
    assert payload["version"] == 1
    assert "N-abcdef" in payload["entries"]
    assert payload["entries"]["N-abcdef"]["value"] == "Jane Smith"


def test_list_empty_text(tmp_path: pathlib.Path, monkeypatch):
    out, rc = _run(monkeypatch, ["--mapping-path", str(tmp_path / "missing.json")])
    assert rc == 0
    assert "empty" in out.lower()


def test_list_empty_json(tmp_path: pathlib.Path, monkeypatch):
    out, rc = _run(
        monkeypatch,
        ["--mapping-path", str(tmp_path / "missing.json"), "--format", "json"],
    )
    assert rc == 0
    payload = json.loads(out)
    assert payload["entries"] == {}
