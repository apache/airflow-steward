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

"""
Automated eval runner — calls Claude for each case and diffs against expected.json.

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    python3 -m skill_evals.eval_runner tools/skill-evals/evals/security-issue-sync/step-2c-next-step/fixtures/
    python3 -m skill_evals.eval_runner tools/skill-evals/evals/          # all suites

Options:
    --model MODEL   Model to use (default: claude-haiku-4-5-20251001)
    --filter GLOB   Only run cases whose path matches GLOB
    --fail-fast     Stop on first failure
    --strict        Fail if the model returns keys not present in expected.json
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import anthropic

from skill_evals.runner import find_cases, load_case, load_step_config, build_corpus_text, build_roster_text

# ---------------------------------------------------------------------------
# JSON extraction
# ---------------------------------------------------------------------------

def extract_json(text: str) -> dict:
    """Extract the first JSON object from a model response."""
    # Strip a single outermost markdown code fence if present.
    # Use re.DOTALL but NOT re.MULTILINE so ^ and $ match only the very
    # start/end of the string — internal fences inside JSON string values
    # are left intact.
    text = text.strip()
    text = re.sub(r"^```(?:json)?\s*\n?(.*?)\n?```\s*$", r"\1", text, flags=re.DOTALL)
    text = text.strip()

    # Try parsing the whole thing first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Find first {...} block
    start = text.find("{")
    if start == -1:
        raise ValueError(f"No JSON object found in response:\n{text[:300]}")
    depth = 0
    for i, ch in enumerate(text[start:], start):
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError(f"Unclosed JSON object in response:\n{text[:300]}")


# ---------------------------------------------------------------------------
# Comparison
# ---------------------------------------------------------------------------

def compare(expected: dict, actual: dict, strict: bool = False) -> tuple[bool, list[str]]:
    """
    Compare expected vs actual JSON.

    For boolean fields: assert equal.
    For integer/string fields: assert equal.
    For list fields: assert equal (exact match).
    With strict=True, any key in actual that is not in expected is also a failure.
    Returns (passed, list_of_failure_messages).
    """
    failures = []
    for key, exp_val in expected.items():
        if key not in actual:
            failures.append(f"  missing key '{key}' (expected {exp_val!r})")
            continue
        act_val = actual[key]
        if exp_val != act_val:
            failures.append(f"  '{key}': expected {exp_val!r}, got {act_val!r}")
    if strict:
        for key in actual:
            if key not in expected:
                failures.append(f"  unexpected key '{key}' in response (strict mode)")
    return len(failures) == 0, failures


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Call Claude for each eval case and compare against expected.json."
    )
    parser.add_argument("path", type=Path, help="Case dir, fixtures dir, or suite root.")
    parser.add_argument(
        "--model", default="claude-haiku-4-5-20251001",
        help="Model to call (default: claude-haiku-4-5-20251001)"
    )
    parser.add_argument("--fail-fast", action="store_true", help="Stop on first failure.")
    parser.add_argument("--strict", action="store_true",
                        help="Fail if the model returns keys not present in expected.json.")
    parser.add_argument("--filter", default=None, metavar="SUBSTR",
                        help="Only run cases whose path contains SUBSTR.")
    args = parser.parse_args()

    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY from env

    cases = find_cases(args.path)
    if not cases:
        print(f"No eval cases found under {args.path}", file=sys.stderr)
        sys.exit(1)

    if args.filter:
        cases = [(c, f) for c, f in cases if args.filter in str(c)]

    _step_config_cache: dict[Path, tuple[str, str]] = {}

    passed = 0
    failed = 0
    errors = 0
    failures_detail: list[str] = []

    for case_dir, fixtures_dir in cases:
        if fixtures_dir not in _step_config_cache:
            _step_config_cache[fixtures_dir] = load_step_config(fixtures_dir)
        system_prompt, user_prompt_template = _step_config_cache[fixtures_dir]

        corpus, roster, report, expected = load_case(case_dir)
        try:
            user_prompt = user_prompt_template.format(
                corpus=build_corpus_text(corpus),
                roster=build_roster_text(roster),
                report=report,
            )
        except (KeyError, ValueError) as exc:
            raise type(exc)(
                f"user-prompt-template.md in {fixtures_dir} has a format error: {exc}. "
                "Available slots: {{corpus}}, {{roster}}, {{report}}. "
                "Literal braces that are not slots must be doubled ({{ and }})."
            ) from exc

        step_label = fixtures_dir.parent.name
        label = f"{step_label}/{case_dir.name}"
        print(f"  {label} ... ", end="", flush=True)

        try:
            response = client.messages.create(
                model=args.model,
                max_tokens=1024,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text
            actual = extract_json(raw)
            ok, diffs = compare(expected, actual, strict=args.strict)
            if ok:
                print("PASS")
                passed += 1
            else:
                print("FAIL")
                failed += 1
                detail = f"FAIL  {label}\n" + "\n".join(diffs)
                failures_detail.append(detail)
                if args.fail_fast:
                    break
        except Exception as exc:
            print(f"ERROR ({exc})")
            errors += 1
            failures_detail.append(f"ERROR {label}: {exc}")
            if args.fail_fast:
                break

        # Tiny sleep to avoid rate-limit bursts
        time.sleep(0.3)


    total = passed + failed + errors
    print()
    print(f"{'=' * 60}")
    print(f"Results: {passed}/{total} passed, {failed} failed, {errors} errors")
    if failures_detail:
        print()
        for d in failures_detail:
            print(d)
    sys.exit(0 if failed == 0 and errors == 0 else 1)


if __name__ == "__main__":
    main()
