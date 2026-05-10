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

"""Validate framework skill definitions.

This module validates three aspects of every skill under
.claude/skills/:

1. YAML frontmatter — every SKILL.md must have a valid frontmatter
   block with required keys (name, description, license).
2. Internal link integrity — relative markdown links between skill
   files and docs must point to existing files and anchors.
3. Placeholder convention — skill docs must use <PROJECT>,
   <upstream>, and <tracker> instead of hardcoded project names.

Run from repo root:
    uv run --project tools/skill-validator --group dev pytest
    # or after install:
    skill-validate
"""

from __future__ import annotations

import argparse
import re
import sys
from collections.abc import Iterable
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

SKILLS_DIR = Path(".claude/skills")
DOCS_DIR = Path("docs")
PROJECTS_TEMPLATE_DIR = Path("projects/_template")

REQUIRED_FRONTMATTER_KEYS = {"name", "description", "license"}
OPTIONAL_FRONTMATTER_KEYS = {"when_to_use", "mode"}
ALLOWED_LICENSES = {"Apache-2.0"}
# MISSION mode taxonomy — see docs/modes.md.
# "Auto-merge" deliberately excluded: it is off per MISSION sequencing.
ALLOWED_MODES = {"Triage", "Mentoring", "Drafting", "Pairing"}

# Forbidden hardcoded project references (fixed strings, case-sensitive)
FORBIDDEN_PATTERNS: list[str] = [
    "apache/airflow",
    "airflow-s/airflow-s",
    "Apache Airflow",
    "apache.org/airflow",
]

# Paths that are intentionally allowed to mention the concrete project.
ALLOWLIST_PATHS: tuple[str, ...] = (
    "README.md",
    "AGENTS.md",
    "CONTRIBUTING.md",
    "docs/setup/secure-agent-setup.md",
    "docs/security/how-to-fix-a-security-issue.md",
    "docs/security/new-members-onboarding.md",
    "pyproject.toml",
    "projects/_template/",
    "tools/dev/check-placeholders.sh",
    ".github/",
    ".asf.yaml",
    "NOTICE",
    "LICENSE",
)

# Inline markers that make a line an intentional explanatory mention.
INLINE_ALLOW_MARKERS: tuple[str, ...] = (
    "example:",
    "e.g.",
    "for Airflow",
    "the Airflow",
    "legacy",
    "renamed",
    "future-renamed",
    "originally",
    "vendor>: <product>",
    "apache/airflow-steward",
)

# Placeholders that skills are expected to use instead of hardcoded names.
FRAMEWORK_PLACEHOLDERS: tuple[str, ...] = (
    "<PROJECT>",
    "<upstream>",
    "<tracker>",
    "<project-config>",
    "<viewer>",
    "<base>",
    "<repo>",
)

# Markdown link pattern: [text](url)
LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

# Anchor slug generation — mirrors doctoc/GitHub logic loosely.
ANCHOR_PATTERN = re.compile(r"[^\w\s-]+")
ANCHOR_SPACE_PATTERN = re.compile(r"\s")

# Skill docs use `<token>` placeholders per AGENTS.md (e.g. `<project-config>`).
PLACEHOLDER_TOKEN_PATTERN = re.compile(r"<[A-Za-z][\w\- ]*>")
ELLIPSIS_URLS = {"...", "…"}


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


class Violation:
    """A single validation violation."""

    def __init__(self, path: Path, line: int | None, message: str) -> None:
        self.path = path
        self.line = line
        self.message = message

    def __str__(self) -> str:
        if self.line is not None:
            return f"{self.path}:{self.line}: {self.message}"
        return f"{self.path}: {self.message}"


# ---------------------------------------------------------------------------
# Frontmatter validation
# ---------------------------------------------------------------------------


def parse_frontmatter(text: str) -> dict[str, str] | None:
    """Extract the YAML-like frontmatter block from a markdown file.

    Returns a dict of key→value (all values treated as strings) or
    *None* when no frontmatter block is found.

    We do **not** use an external YAML parser because the frontmatter
    is intentionally simple (scalar keys and string values) and
    keeping the validator stdlib-only makes it cheap to run anywhere.
    """
    if not text.startswith("---\n"):
        return None

    try:
        end = text.index("\n---\n", 3)
    except ValueError:
        return None

    block = text[4:end]
    result: dict[str, str] = {}
    current_key: str | None = None
    current_value_lines: list[str] = []

    for raw_line in block.splitlines():
        # Strip trailing whitespace but keep leading (for folded scalars)
        line = raw_line.rstrip()

        # Empty line ends a folded scalar
        if line == "":
            if current_key is not None:
                result[current_key] = "\n".join(current_value_lines).strip()
                current_key = None
                current_value_lines = []
            continue

        # New top-level key?
        if not line.startswith(" ") and not line.startswith("\t"):
            if ":" in line:
                if current_key is not None:
                    result[current_key] = "\n".join(current_value_lines).strip()
                key, _, value = line.partition(":")
                current_key = key.strip()
                current_value_lines = [value.strip()] if value.strip() else []
                continue
            # Line without colon that is not indented — treat as folded scalar
            if current_key is not None:
                current_value_lines.append(line)
                continue

        # Continuation / folded scalar
        if current_key is not None:
            # Remove the common YAML indent (2 spaces) if present
            if line.startswith("  "):
                line = line[2:]
            current_value_lines.append(line)

    if current_key is not None:
        result[current_key] = "\n".join(current_value_lines).strip()

    return result


def validate_frontmatter(path: Path, text: str) -> Iterable[Violation]:
    """Validate the YAML frontmatter of a SKILL.md file."""
    fm = parse_frontmatter(text)
    if fm is None:
        yield Violation(path, 1, "missing YAML frontmatter block (expected '---' at start)")
        return

    missing = REQUIRED_FRONTMATTER_KEYS - set(fm.keys())
    for key in sorted(missing):
        yield Violation(path, 1, f"missing required frontmatter key: '{key}'")

    for key, value in fm.items():
        if not value:
            yield Violation(path, 1, f"frontmatter key '{key}' is empty")

    if "license" in fm and fm["license"] not in ALLOWED_LICENSES:
        yield Violation(path, 1, f"frontmatter license '{fm['license']}' not in {ALLOWED_LICENSES}")

    if "mode" in fm and fm["mode"] not in ALLOWED_MODES:
        yield Violation(
            path,
            1,
            f"frontmatter mode '{fm['mode']}' not in {sorted(ALLOWED_MODES)} (see docs/modes.md)",
        )


# ---------------------------------------------------------------------------
# Link validation
# ---------------------------------------------------------------------------


def slugify(text: str) -> str:
    """Generate a GitHub-style anchor slug from a heading."""
    text = text.lower().strip()
    text = ANCHOR_PATTERN.sub("", text)
    text = ANCHOR_SPACE_PATTERN.sub("-", text)
    return text.strip("-")


def extract_headings(text: str) -> set[str]:
    """Return anchor slugs for every heading; duplicates get GitHub-style ``-N`` suffixes."""
    slugs: set[str] = set()
    seen: dict[str, int] = {}
    for match in re.finditer(r"^(#{1,6})\s+(.+)$", text, re.MULTILINE):
        heading_text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", match.group(2).strip())
        base = slugify(heading_text)
        count = seen.get(base, 0)
        slugs.add(base if count == 0 else f"{base}-{count}")
        seen[base] = count + 1
    return slugs


_FENCED_CODE_RE = re.compile(r"^```[\s\S]*?^```", re.MULTILINE)
_DOUBLE_BACKTICK_RE = re.compile(r"``[\s\S]+?``")
_SINGLE_BACKTICK_RE = re.compile(r"`[^`\n]+`")


def _code_spans(text: str) -> list[tuple[int, int]]:
    """Return ``(start, end)`` ranges covering every code span in *text*."""
    spans: list[tuple[int, int]] = []
    for pattern in (_FENCED_CODE_RE, _DOUBLE_BACKTICK_RE):
        spans.extend(m.span() for m in pattern.finditer(text))
    for m in _SINGLE_BACKTICK_RE.finditer(text):
        s, e = m.span()
        if not any(os <= s < oe for os, oe in spans):
            spans.append((s, e))
    return spans


def resolve_link(
    source: Path,
    url: str,
    skill_dirs: set[Path],
    doc_files: set[Path],
) -> Path | None:
    """Resolve a relative markdown link URL to an absolute Path.

    Returns *None* when the URL is external (http/https/mailto) or
    when it cannot be resolved to a filesystem path inside the repo.
    """
    if url.startswith(("http://", "https://", "mailto:")):
        return None

    # Strip anchor
    bare = url.split("#")[0]
    if not bare:
        return source  # same-file anchor

    # Resolve relative to the source file's directory
    target = (source.parent / bare).resolve()

    return target


def is_placeholder_url(url: str) -> bool:
    """Return True when *url* is a `<token>` placeholder or an ellipsis stand-in."""
    if url in ELLIPSIS_URLS:
        return True
    return bool(PLACEHOLDER_TOKEN_PATTERN.search(url))


def validate_links(
    path: Path,
    text: str,
    skill_dirs: set[Path],
    doc_files: set[Path],
) -> Iterable[Violation]:
    """Validate all internal markdown links in a skill file."""
    headings = extract_headings(text)
    code_spans = _code_spans(text)

    for match in LINK_PATTERN.finditer(text):
        url = match.group(2)
        start = match.start()
        line_no = text[:start].count("\n") + 1

        if any(s <= start < e for s, e in code_spans):
            continue
        if url.startswith(("http://", "https://", "mailto:")):
            continue
        if is_placeholder_url(url):
            continue

        target = resolve_link(path, url, skill_dirs, doc_files)
        if target is None:
            continue

        # Same-file anchor?
        if url.startswith("#"):
            anchor = url[1:]
            if anchor and slugify(anchor) not in headings:
                yield Violation(path, line_no, f"anchor '#{anchor}' not found in {path.name}")
            continue

        # Cross-file link
        if not target.exists():
            yield Violation(path, line_no, f"linked file does not exist: {target}")
            continue

        # Anchor in cross-file link?
        if "#" in url:
            anchor = url.split("#", 1)[1]
            try:
                target_text = target.read_text(encoding="utf-8")
            except OSError:
                continue
            target_headings = extract_headings(target_text)
            if slugify(anchor) not in target_headings:
                yield Violation(
                    path,
                    line_no,
                    f"anchor '#{anchor}' not found in {target}",
                )


# ---------------------------------------------------------------------------
# Placeholder validation (complement to check-placeholders.sh)
# ---------------------------------------------------------------------------


def is_path_allowlisted(file_path: Path) -> bool:
    """Check whether a file path is in the allowlist."""
    # Try relative path first, then absolute
    for path in (file_path, file_path.resolve()):
        str_path = str(path)
        for prefix in ALLOWLIST_PATHS:
            if str_path.startswith(prefix):
                return True
            if str_path.startswith("./" + prefix):
                return True
            # Also match when the path contains the prefix as a component
            if "/" + prefix in str_path or "\\" + prefix in str_path:
                return True
    return False


def line_has_inline_allow_marker(line: str) -> bool:
    """Check whether a line contains an allowlist marker."""
    return any(marker in line for marker in INLINE_ALLOW_MARKERS)


def validate_placeholders(path: Path, text: str) -> Iterable[Violation]:
    """Validate that no hardcoded project references appear in skill docs.

    This is a structured reimplementation of the logic in
    tools/dev/check-placeholders.sh, producing Violation objects that
    can be aggregated with frontmatter and link violations.
    """
    if is_path_allowlisted(path):
        return

    lines = text.splitlines()
    for line_no, line in enumerate(lines, start=1):
        if line_has_inline_allow_marker(line):
            continue
        for pattern in FORBIDDEN_PATTERNS:
            if pattern in line:
                yield Violation(
                    path,
                    line_no,
                    f"hardcoded project reference '{pattern}' — use placeholders",
                )


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------


def find_repo_root(start: Path | None = None) -> Path:
    """Walk up from *start* (or CWD) until ``.claude/skills/`` is found.

    Defense in depth: lets the validator work even when the entry point
    runs from inside a subtree (e.g. ``uv run --directory``), which
    historically caused the suite to silently scan an empty path.
    """
    cur = (start or Path.cwd()).resolve()
    for candidate in (cur, *cur.parents):
        if (candidate / SKILLS_DIR).is_dir():
            return candidate
    return cur


def collect_files_to_check(root: Path | None = None) -> list[Path]:
    """Return every .md file under .claude/skills/ that should be validated."""
    base = (root or find_repo_root()) / SKILLS_DIR
    if not base.exists():
        return []
    return list(base.rglob("*.md"))


def collect_skill_dirs(root: Path | None = None) -> set[Path]:
    """Return the set of skill directories (immediate children of .claude/skills)."""
    base = (root or find_repo_root()) / SKILLS_DIR
    if not base.exists():
        return set()
    return {p.resolve() for p in base.iterdir() if p.is_dir()}


def collect_doc_files(root: Path | None = None) -> set[Path]:
    """Return every .md file under docs/ and projects/_template/."""
    repo_root = root or find_repo_root()
    files: set[Path] = set()
    for rel in (DOCS_DIR, PROJECTS_TEMPLATE_DIR):
        base = repo_root / rel
        if base.exists():
            files.update(p.resolve() for p in base.rglob("*.md"))
    return files


def run_validation(root: Path | None = None) -> list[Violation]:
    """Run the full validation suite and return all violations."""
    repo_root = root or find_repo_root()
    violations: list[Violation] = []
    files = collect_files_to_check(repo_root)
    skill_dirs = collect_skill_dirs(repo_root)
    doc_files = collect_doc_files(repo_root)

    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            violations.append(Violation(path, None, f"cannot read file: {exc}"))
            continue

        # Only SKILL.md files get frontmatter validation
        if path.name == "SKILL.md":
            violations.extend(validate_frontmatter(path, text))

        # All skill files get link + placeholder validation
        violations.extend(validate_links(path, text, skill_dirs, doc_files))
        violations.extend(validate_placeholders(path, text))

    return violations


def main(argv: list[str] | None = None) -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate framework skill definitions.",
    )
    parser.parse_args(argv)

    violations = run_validation()

    if not violations:
        print("skill-validator: OK (no violations)")
        return 0

    print(f"skill-validator: {len(violations)} violation(s) found\n")
    for v in violations:
        print(v)
    return 1


if __name__ == "__main__":
    sys.exit(main())
