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
import json
from pathlib import Path

import pytest

from permission_audit.edit import apply_changes


def _write_settings(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def test_add_appends_new_entry_in_order(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(p, {"permissions": {"allow": ["Bash(git status *)"]}})
    outcome = apply_changes(p, additions=["Bash(lychee *)"], removals=[])
    assert outcome.added == ["Bash(lychee *)"]
    assert outcome.removed == []
    final = json.loads(p.read_text())["permissions"]["allow"]
    assert final == ["Bash(git status *)", "Bash(lychee *)"]


def test_add_existing_entry_is_noop(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(p, {"permissions": {"allow": ["Bash(lychee *)"]}})
    outcome = apply_changes(p, additions=["Bash(lychee *)"], removals=[])
    assert outcome.added == []
    final = json.loads(p.read_text())["permissions"]["allow"]
    assert final == ["Bash(lychee *)"]


def test_remove_drops_first_and_subsequent_duplicates(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(
        p,
        {"permissions": {"allow": ["Bash(uv run *)", "Bash(git status *)", "Bash(uv run *)"]}},
    )
    outcome = apply_changes(p, additions=[], removals=["Bash(uv run *)"])
    # Both duplicates removed.
    assert outcome.removed == ["Bash(uv run *)", "Bash(uv run *)"]
    final = json.loads(p.read_text())["permissions"]["allow"]
    assert final == ["Bash(git status *)"]


def test_remove_absent_entry_is_noop(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(p, {"permissions": {"allow": ["Bash(git status *)"]}})
    outcome = apply_changes(p, additions=[], removals=["Bash(uv run *)"])
    assert outcome.removed == []
    assert outcome.added == []
    # File untouched.
    final = json.loads(p.read_text())["permissions"]["allow"]
    assert final == ["Bash(git status *)"]


def test_unrelated_keys_preserved(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(
        p,
        {
            "extraKnownMarketplaces": {"foo": "bar"},
            "permissions": {"allow": ["Bash(uv run *)"], "deny": ["Bash(rm -rf /)"]},
            "hooks": {"PostToolUse": [{"matcher": "X", "hooks": []}]},
        },
    )
    apply_changes(p, additions=["Bash(lychee *)"], removals=["Bash(uv run *)"])
    final = json.loads(p.read_text())
    assert final["extraKnownMarketplaces"] == {"foo": "bar"}
    assert final["permissions"]["deny"] == ["Bash(rm -rf /)"]
    assert final["hooks"] == {"PostToolUse": [{"matcher": "X", "hooks": []}]}
    assert final["permissions"]["allow"] == ["Bash(lychee *)"]


def test_missing_file_raises_unless_create(tmp_path):
    p = tmp_path / "absent.json"
    with pytest.raises(FileNotFoundError):
        apply_changes(p, additions=["x"], removals=[])
    outcome = apply_changes(p, additions=["x"], removals=[], create_if_missing=True)
    assert outcome.file_was_created is True
    assert outcome.added == ["x"]


def test_invalid_json_raises_value_error(tmp_path):
    p = tmp_path / "settings.local.json"
    p.write_text("{not json", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        apply_changes(p, additions=["x"], removals=[])


def test_non_object_top_level_raises(tmp_path):
    p = tmp_path / "settings.local.json"
    p.write_text("[]", encoding="utf-8")
    with pytest.raises(ValueError, match="not an object"):
        apply_changes(p, additions=["x"], removals=[])


def test_allow_not_a_list_raises(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(p, {"permissions": {"allow": "not-a-list"}})
    with pytest.raises(ValueError, match="not a list"):
        apply_changes(p, additions=["x"], removals=[])


def test_no_changes_does_not_rewrite_file(tmp_path):
    p = tmp_path / "settings.local.json"
    _write_settings(p, {"permissions": {"allow": ["Bash(lychee *)"]}})
    mtime_before = p.stat().st_mtime_ns
    outcome = apply_changes(p, additions=["Bash(lychee *)"], removals=[])
    assert outcome.added == []
    assert outcome.removed == []
    # File should not have been rewritten — same mtime.
    assert p.stat().st_mtime_ns == mtime_before
