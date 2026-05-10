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

"""Tests for the skill validator."""

from __future__ import annotations

from pathlib import Path

import pytest

from skill_validator import (
    FORBIDDEN_PATTERNS,
    extract_headings,
    find_repo_root,
    parse_frontmatter,
    resolve_link,
    run_validation,
    slugify,
    validate_frontmatter,
    validate_links,
    validate_placeholders,
)

# ---------------------------------------------------------------------------
# Frontmatter parsing
# ---------------------------------------------------------------------------


class TestParseFrontmatter:
    def test_valid_frontmatter(self) -> None:
        text = "---\nname: foo\ndescription: bar\nlicense: Apache-2.0\n---\n# heading\n"
        fm = parse_frontmatter(text)
        assert fm is not None
        assert fm["name"] == "foo"
        assert fm["description"] == "bar"
        assert fm["license"] == "Apache-2.0"

    def test_folded_scalar(self) -> None:
        text = (
            "---\n"
            "name: my-skill\n"
            "description: |\n"
            "  First line of description.\n"
            "  Second line.\n"
            "license: Apache-2.0\n"
            "---\n"
        )
        fm = parse_frontmatter(text)
        assert fm is not None
        assert "First line" in fm["description"]
        assert "Second line" in fm["description"]

    def test_missing_frontmatter(self) -> None:
        assert parse_frontmatter("# no frontmatter\n") is None

    def test_no_closing_delimiter(self) -> None:
        assert parse_frontmatter("---\nname: foo\n") is None


# ---------------------------------------------------------------------------
# Frontmatter validation
# ---------------------------------------------------------------------------


class TestValidateFrontmatter:
    def test_valid(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\nname: foo\ndescription: bar\nlicense: Apache-2.0\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert violations == []

    def test_missing_name(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\ndescription: bar\nlicense: Apache-2.0\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert len(violations) == 1
        assert "name" in violations[0].message

    def test_missing_multiple_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\n---\n"
        violations = list(validate_frontmatter(path, text))
        messages = {v.message for v in violations}
        assert any("name" in m for m in messages)
        assert any("description" in m for m in messages)
        assert any("license" in m for m in messages)

    def test_empty_value(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\nname: \ndescription: bar\nlicense: Apache-2.0\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert any("name' is empty" in v.message for v in violations)

    def test_invalid_license(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\nname: foo\ndescription: bar\nlicense: MIT\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert any("MIT" in v.message for v in violations)

    def test_valid_mode(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        for mode in ("Triage", "Mentoring", "Drafting", "Pairing"):
            text = f"---\nname: foo\ndescription: bar\nlicense: Apache-2.0\nmode: {mode}\n---\n"
            violations = list(validate_frontmatter(path, text))
            assert violations == [], f"mode '{mode}' should be valid"

    def test_invalid_mode(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "---\nname: foo\ndescription: bar\nlicense: Apache-2.0\nmode: Auto-merge\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert any("mode" in v.message and "'Auto-merge'" in v.message for v in violations)

    def test_mode_optional(self, tmp_path: Path) -> None:
        # Skills without a mode (e.g. setup-* infrastructure) must not fail.
        path = tmp_path / "SKILL.md"
        text = "---\nname: foo\ndescription: bar\nlicense: Apache-2.0\n---\n"
        violations = list(validate_frontmatter(path, text))
        assert violations == []


# ---------------------------------------------------------------------------
# Heading / anchor helpers
# ---------------------------------------------------------------------------


class TestSlugify:
    def test_basic(self) -> None:
        assert slugify("Hello World") == "hello-world"

    def test_punctuation(self) -> None:
        assert slugify("What's new?") == "whats-new"

    def test_multiple_spaces(self) -> None:
        # GitHub's anchor algorithm replaces each whitespace character with
        # a dash one-for-one rather than collapsing runs. Doctoc and the
        # GitHub renderer agree on this; the canonical case is em-dash
        # headings, which strip to "" and leave two adjacent spaces.
        assert slugify("A  B   C") == "a--b---c"

    def test_em_dash_in_heading(self) -> None:
        assert slugify("Mentoring") == "mentoring"


class TestExtractHeadings:
    def test_basic(self) -> None:
        text = "# Foo\n## Bar Baz\n### Qux\n"
        slugs = extract_headings(text)
        assert slugs == {"foo", "bar-baz", "qux"}

    def test_with_links(self) -> None:
        text = "# [Foo](url)\n"
        slugs = extract_headings(text)
        assert "foo" in slugs


# ---------------------------------------------------------------------------
# Link resolution
# ---------------------------------------------------------------------------


class TestResolveLink:
    def test_external_http(self, tmp_path: Path) -> None:
        assert resolve_link(tmp_path / "SKILL.md", "http://example.com", set(), set()) is None

    def test_external_https(self, tmp_path: Path) -> None:
        assert resolve_link(tmp_path / "SKILL.md", "https://example.com", set(), set()) is None

    def test_mailto(self, tmp_path: Path) -> None:
        assert resolve_link(tmp_path / "SKILL.md", "mailto:a@b.com", set(), set()) is None

    def test_same_file_anchor(self, tmp_path: Path) -> None:
        source = tmp_path / "SKILL.md"
        result = resolve_link(source, "#anchor", set(), set())
        assert result == source


# ---------------------------------------------------------------------------
# Link validation
# ---------------------------------------------------------------------------


class TestValidateLinks:
    def test_valid_same_file_anchor(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "# Foo\n[link](#foo)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_invalid_same_file_anchor(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "# Foo\n[link](#bar)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert len(violations) == 1
        assert "#bar" in violations[0].message

    def test_valid_cross_file(self, tmp_path: Path) -> None:
        base = tmp_path
        source = base / "SKILL.md"
        target = base / "other.md"
        target.write_text("# Other\n", encoding="utf-8")
        text = "[link](other.md)\n"
        violations = list(validate_links(source, text, {base}, set()))
        assert violations == []

    def test_missing_cross_file(self, tmp_path: Path) -> None:
        base = tmp_path
        source = base / "SKILL.md"
        text = "[link](missing.md)\n"
        violations = list(validate_links(source, text, {base}, set()))
        assert len(violations) == 1
        assert "missing.md" in violations[0].message

    def test_valid_cross_file_anchor(self, tmp_path: Path) -> None:
        base = tmp_path
        source = base / "SKILL.md"
        target = base / "other.md"
        target.write_text("# Other\n## Sub Section\n", encoding="utf-8")
        text = "[link](other.md#sub-section)\n"
        violations = list(validate_links(source, text, {base}, set()))
        assert violations == []

    def test_invalid_cross_file_anchor(self, tmp_path: Path) -> None:
        base = tmp_path
        source = base / "SKILL.md"
        target = base / "other.md"
        target.write_text("# Other\n", encoding="utf-8")
        text = "[link](other.md#nonexistent)\n"
        violations = list(validate_links(source, text, {base}, set()))
        assert len(violations) == 1
        assert "#nonexistent" in violations[0].message

    def test_external_link_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "[link](https://example.com)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_framework_placeholder_url_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "[doc](<project-config>/project.md)\n[doc2](../../../<project-config>/release-trains.md)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_template_token_url_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "[a](<doc_url>)\n[b](<URL into the public source>)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_anchor_with_placeholder_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "[link](#issuecomment-<id>)\n[link2](other.md#issuecomment-<id>)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_ellipsis_url_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "[continues](...)\n[continues](…)\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_link_inside_inline_code_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "Use ``[text](url)`` form for emails.\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_link_inside_single_backtick_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "Write `[text](missing.md)` literally.\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_link_inside_fenced_code_ignored(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "```\nsee [doc](missing.md) here\n```\n"
        violations = list(validate_links(path, text, set(), set()))
        assert violations == []

    def test_duplicate_heading_anchor_resolves(self, tmp_path: Path) -> None:
        base = tmp_path
        source = base / "SKILL.md"
        target = base / "other.md"
        target.write_text("# Setup\n# Setup\n# Setup\n", encoding="utf-8")
        text = "[a](other.md#setup)\n[b](other.md#setup-1)\n[c](other.md#setup-2)\n"
        violations = list(validate_links(source, text, {base}, set()))
        assert violations == []


# ---------------------------------------------------------------------------
# Placeholder validation
# ---------------------------------------------------------------------------


class TestValidatePlaceholders:
    def test_clean_line(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "Use <PROJECT> and <upstream> here.\n"
        violations = list(validate_placeholders(path, text))
        assert violations == []

    def test_forbidden_pattern(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "See apache/airflow for details.\n"
        violations = list(validate_placeholders(path, text))
        assert len(violations) == 1
        assert "apache/airflow" in violations[0].message

    def test_allowlisted_path(self, tmp_path: Path) -> None:
        # Simulate a path inside projects/_template/
        path = tmp_path / "projects" / "_template" / "foo.md"
        path.parent.mkdir(parents=True)
        text = "This mentions apache/airflow intentionally.\n"
        violations = list(validate_placeholders(path, text))
        assert violations == []

    def test_inline_marker(self, tmp_path: Path) -> None:
        path = tmp_path / "SKILL.md"
        text = "For example: apache/airflow is the upstream.\n"
        violations = list(validate_placeholders(path, text))
        assert violations == []


# ---------------------------------------------------------------------------
# Repo-root detection
# ---------------------------------------------------------------------------


class TestFindRepoRoot:
    def test_locates_root_from_validator_subtree(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Regression: the silent-pass bug fired only when CWD was inside the validator subtree.
        repo = Path(__file__).resolve().parents[3]
        assert (repo / ".claude" / "skills").is_dir(), "test setup precondition"
        monkeypatch.chdir(repo / "tools" / "skill-validator")
        assert find_repo_root() == repo

    def test_explicit_start_outside_repo(self, tmp_path: Path) -> None:
        assert find_repo_root(tmp_path) == tmp_path.resolve()


# ---------------------------------------------------------------------------
# End-to-end: real repo
# ---------------------------------------------------------------------------


class TestRunValidation:
    def test_no_duplicate_errors_with_check_placeholders(self) -> None:
        """Ensure our placeholder checks don't add noise beyond check-placeholders.sh.

        Both tools share the same forbidden-pattern list, so any line
        that check-placeholders.sh would catch we should also catch.
        This test verifies that the two validators stay in sync.
        """
        assert set(FORBIDDEN_PATTERNS) == {
            "apache/airflow",
            "airflow-s/airflow-s",
            "Apache Airflow",
            "apache.org/airflow",
        }

    def test_real_repo_passes(self) -> None:
        """Run the full validation suite against the actual repo.

        This is the primary integration test: it exercises every
        SKILL.md, every supporting file, and every internal link.
        """
        violations = run_validation()
        if violations:
            # Pretty-print the first few failures so pytest output is useful
            lines = [str(v) for v in violations[:10]]
            pytest.fail(f"{len(violations)} validation violation(s) found:\n" + "\n".join(lines))
