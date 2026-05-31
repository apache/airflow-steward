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
from permission_audit.audit import audit_settings


def test_empty_allow_only_misses_recommended():
    result = audit_settings(allow_list=[], families=["security"])
    assert result.forbidden == []
    # lychee (default family "") + 10 security family = 11
    assert len(result.missing_recommended) == 11


def test_forbidden_python_wildcard_flagged_with_pointer():
    allow = [
        "Bash(git status *)",
        "Bash(python3 *)",  # forbidden
        "Bash(uv run *)",  # forbidden
        "mcp__claude_ai_Gmail__get_thread",
    ]
    result = audit_settings(allow_list=allow, families=["security"])
    forbidden_pointers = {f.pattern: f.json_pointer for f in result.forbidden}
    assert forbidden_pointers == {
        "Bash(python3 *)": ".permissions.allow[1]",
        "Bash(uv run *)": ".permissions.allow[2]",
    }


def test_family_scoping_excludes_other_families():
    # Adopter only opted into the default "" family — security MCPs
    # must not appear as gaps.
    result = audit_settings(allow_list=[], families=[])
    patterns = {f.pattern for f in result.missing_recommended}
    assert "Bash(lychee *)" in patterns
    # No security-family entries surfaced.
    assert "mcp__claude_ai_Gmail__get_thread" not in patterns


def test_recommended_present_is_not_flagged_missing():
    allow = ["Bash(lychee *)", "mcp__claude_ai_Gmail__get_thread"]
    result = audit_settings(allow_list=allow, families=["security"])
    missing = {f.pattern for f in result.missing_recommended}
    assert "Bash(lychee *)" not in missing
    assert "mcp__claude_ai_Gmail__get_thread" not in missing


def test_duplicate_forbidden_entries_get_distinct_pointers():
    allow = ["Bash(uv run *)", "Bash(uv run *)"]
    result = audit_settings(allow_list=allow, families=[])
    pointers = [f.json_pointer for f in result.forbidden]
    assert pointers == [".permissions.allow[0]", ".permissions.allow[1]"]


def test_default_family_always_included_even_when_not_requested():
    result = audit_settings(allow_list=[], families=["security"])
    patterns = {f.pattern for f in result.missing_recommended}
    assert "Bash(lychee *)" in patterns
