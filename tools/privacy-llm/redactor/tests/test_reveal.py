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
"""Tests for ``redactor.reveal`` — the ``pii-reveal`` CLI."""

from __future__ import annotations

import io
import pathlib
from collections.abc import Iterator

import pytest

from redactor import redact, reveal
from redactor.mapping import load_mapping


@pytest.fixture()
def seeded_mapping(tmp_path: pathlib.Path, monkeypatch) -> Iterator[pathlib.Path]:
    """Run a redact pass to seed a mapping, then yield its path."""
    path = tmp_path / "pii-mapping.json"
    monkeypatch.setenv("PII_MAPPING_PATH", str(path))
    # Seed with one reporter and one email.
    monkeypatch.setattr("sys.stdin", io.StringIO("Jane Smith jane@example.com"))
    monkeypatch.setattr("sys.stdout", io.StringIO())
    redact.main(["--field", "reporter:Jane Smith", "--field", "email:jane@example.com"])
    yield path


def _reveal(monkeypatch, stdin_text: str) -> tuple[str, int]:
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    monkeypatch.setattr("sys.stdin", stdin)
    monkeypatch.setattr("sys.stdout", stdout)
    rc = reveal.main([])
    return stdout.getvalue(), rc


# -- core round-trip ----------------------------------------------------


def test_reveal_substitutes_known_identifiers(seeded_mapping, monkeypatch):
    mapping = load_mapping(seeded_mapping)
    reporter = next(e for e in mapping.values() if e.type == "reporter")
    email = next(e for e in mapping.values() if e.type == "email")
    text = f"Hi {reporter.identifier}, your email {email.identifier} was confirmed."
    out, rc = _reveal(monkeypatch, text)
    assert rc == 0
    assert "Jane Smith" in out
    assert "jane@example.com" in out
    assert reporter.identifier not in out
    assert email.identifier not in out


def test_reveal_leaves_unknown_identifiers_intact(seeded_mapping, monkeypatch):
    """An identifier shape that is NOT in the mapping is passed through.

    This is the cross-machine / lost-mapping case — we have no
    way to reverse it, so we leave the bytes alone.
    """
    text = "Reply to R-deadbeef please."
    out, _ = _reveal(monkeypatch, text)
    assert out == text


def test_reveal_does_not_match_arbitrary_uppercase_dash_hex(seeded_mapping, monkeypatch):
    """``HTTP-200`` should pass through unchanged — wrong prefix, wrong hex shape."""
    text = "Got HTTP-200 OK back."
    out, _ = _reveal(monkeypatch, text)
    assert out == text


def test_reveal_handles_identifier_inside_punctuation(seeded_mapping, monkeypatch):
    """Identifiers next to punctuation should still be revealed."""
    mapping = load_mapping(seeded_mapping)
    reporter = next(e for e in mapping.values() if e.type == "reporter")
    text = f"({reporter.identifier})"
    out, _ = _reveal(monkeypatch, text)
    assert out == "(Jane Smith)"


def test_reveal_empty_mapping_passes_through(tmp_path: pathlib.Path, monkeypatch):
    """No mapping file → identifier-shaped tokens are left as-is."""
    monkeypatch.setenv("PII_MAPPING_PATH", str(tmp_path / "missing.json"))
    text = "Hi R-abcdef, your email E-deadbe was confirmed."
    out, rc = _reveal(monkeypatch, text)
    assert rc == 0
    assert out == text


def test_reveal_round_trip_with_redact(tmp_path: pathlib.Path, monkeypatch):
    """``pii-redact`` then ``pii-reveal`` should be a no-op on the text."""
    monkeypatch.setenv("PII_MAPPING_PATH", str(tmp_path / "rt.json"))
    body = "Hi I am Jane Smith and my email is jane@example.com."
    # Redact pass.
    monkeypatch.setattr("sys.stdin", io.StringIO(body))
    redacted_buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", redacted_buf)
    redact.main(["--field", "reporter:Jane Smith", "--field", "email:jane@example.com"])
    # Reveal pass.
    monkeypatch.setattr("sys.stdin", io.StringIO(redacted_buf.getvalue()))
    revealed_buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", revealed_buf)
    reveal.main([])
    assert revealed_buf.getvalue() == body


# -- internals ----------------------------------------------------------


def test_reveal_function_directly():
    """Smoke-test the pure function without going through stdin."""
    from redactor.mapping import Entry

    mapping = {
        "R-abcdef": Entry(identifier="R-abcdef", type="reporter", value="Jane Smith"),
    }
    assert reveal.reveal("Hello R-abcdef.", mapping) == "Hello Jane Smith."


def test_reveal_returns_2_on_malformed_mapping_file(tmp_path: pathlib.Path, monkeypatch):
    path = tmp_path / "pii.json"
    path.write_text("not json at all")
    monkeypatch.setenv("PII_MAPPING_PATH", str(path))
    monkeypatch.setattr("sys.stdin", io.StringIO("ignored"))
    monkeypatch.setattr("sys.stdout", io.StringIO())
    monkeypatch.setattr("sys.stderr", io.StringIO())
    rc = reveal.main([])
    assert rc == 2


@pytest.mark.parametrize("type_code", ["IP"])
def test_reveal_handles_two_char_prefix(tmp_path: pathlib.Path, monkeypatch, type_code: str):
    """Two-character prefixes (e.g. ``IP-``) round-trip correctly."""
    monkeypatch.setenv("PII_MAPPING_PATH", str(tmp_path / "ip.json"))
    body = "I tested from 192.0.2.42."
    # Redact.
    monkeypatch.setattr("sys.stdin", io.StringIO(body))
    monkeypatch.setattr("sys.stdout", io.StringIO())
    redact.main(["--field", "ip:192.0.2.42"])
    # Read mapping to grab identifier.
    mapping = load_mapping(tmp_path / "ip.json")
    [entry] = mapping.values()
    assert entry.identifier.startswith("IP-")
    # Reveal.
    monkeypatch.setattr("sys.stdin", io.StringIO(f"see {entry.identifier} please"))
    out_buf = io.StringIO()
    monkeypatch.setattr("sys.stdout", out_buf)
    reveal.main([])
    assert out_buf.getvalue() == "see 192.0.2.42 please"
