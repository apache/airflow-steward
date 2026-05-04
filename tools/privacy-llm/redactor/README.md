<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [redactor](#redactor)
  - [Run](#run)
  - [Mapping file](#mapping-file)
  - [Test](#test)
  - [Lint / type-check](#lint--type-check)
  - [Referenced by](#referenced-by)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- Licensed to the Apache Software Foundation (ASF) under one
     or more contributor license agreements.  See the NOTICE file
     distributed with this work for additional information
     regarding copyright ownership.  The ASF licenses this file
     to you under the Apache License, Version 2.0 (the
     "License"); you may not use this file except in compliance
     with the License.  You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

     Unless required by applicable law or agreed to in writing,
     software distributed under the License is distributed on an
     "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
     KIND, either express or implied.  See the License for the
     specific language governing permissions and limitations
     under the License. -->

# redactor

Stdlib-only Python project implementing the PII redactor for
the apache-steward privacy-llm tool. Three console scripts:

| Console script | Purpose |
|---|---|
| `pii-redact` | Replace declared PII values in stdin with hash-prefixed identifiers; persist new mappings to the local file. |
| `pii-reveal` | Replace identifiers in stdin with stored real values from the local mapping. |
| `pii-list` | Print the current mapping for debugging (text or JSON). |

The behavioural contract — which fields count as PII, the
identifier format, the redact-then-reveal lifecycle — lives in
[`../pii.md`](../pii.md). This README covers local-setup and
day-to-day invocation.

## Run

From the framework's root (this repository when running standalone;
the snapshot path inside an adopting tracker repo):

```bash
# Redact: pass --field <type>:<value> for each PII value to swap.
echo "Hi I am Jane Smith, jane@example.com" | \
  uv run --project tools/privacy-llm/redactor pii-redact \
    --field reporter:"Jane Smith" \
    --field email:"jane@example.com"
# →  Hi I am R-<hex>, E-<hex>

# Reveal: identifiers in stdin → real values from the local map.
echo "Reply to R-<hex>" | \
  uv run --project tools/privacy-llm/redactor pii-reveal
# →  Reply to Jane Smith

# List the current map (text or JSON):
uv run --project tools/privacy-llm/redactor pii-list
uv run --project tools/privacy-llm/redactor pii-list --format json
```

Skill files reference the same invocation via the `<framework>`
placeholder so the path resolves in either context:

```bash
uv run --project <framework>/tools/privacy-llm/redactor pii-redact ...
```

`<framework>` substitutes to the snapshot path inside an adopting
project (typically `.apache-steward/apache-steward/`) and to `.`
when running standalone — see the placeholder convention in
[`AGENTS.md`](../../../AGENTS.md#placeholder-convention-used-in-skill-files).

Field types accepted by `--field`:

| Friendly name | Code | Use for |
|---|---|---|
| `reporter` | `R` | Reporter / external party natural-person name. |
| `email` | `E` | Any email address. |
| `phone` | `P` | Phone number in any format. |
| `ip` | `IP` | IPv4 or IPv6 address self-disclosed by the reporter. |
| `handle` | `H` | Personal social handle (GitHub, Twitter, IRC nick, …). |
| `address` | `A` | Postal / employer address. |

## Mapping file

The mapping is stored at:

```text
~/.config/apache-steward/pii-mapping.json     (default)
$PII_MAPPING_PATH                             (env override)
--mapping-path <path>                         (per-call override)
```

The file is written with mode `0o600`, atomically (`tempfile +
os.replace`). It is per-machine, never committed. The
identifier-from-value derivation is deterministic, so two
developers redacting the same value get the same identifier
without sharing the file.

## Test

```bash
# Run the test suite:
uv run --project tools/privacy-llm/redactor --group dev pytest

# With coverage (if you add coverage.py to the dev group locally):
uv run --project tools/privacy-llm/redactor --group dev pytest --cov=redactor
```

## Lint / type-check

```bash
uv run --project tools/privacy-llm/redactor --group dev ruff check src tests
uv run --project tools/privacy-llm/redactor --group dev ruff format --check src tests
uv run --project tools/privacy-llm/redactor --group dev mypy
```

## Referenced by

- [`tools/privacy-llm/tool.md`](../tool.md) — tool overview.
- [`tools/privacy-llm/pii.md`](../pii.md) — PII redaction contract.
- [`docs/setup/privacy-llm.md`](../../../docs/setup/privacy-llm.md) — setup recipes for adopters.
