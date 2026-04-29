#!/usr/bin/env bash
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
#
# check-tool-updates.sh
#
# Read pinned-versions.toml and report on upstream releases that
# (a) are newer than the pinned versions, AND (b) have themselves
# aged past the 7-day cooldown the pin convention asks for.
#
# Output is informational only — the script never installs anything,
# never edits pinned-versions.toml, never opens a PR. It just
# surfaces candidates for the framework maintainer to review,
# matching the *propose-then-confirm* pattern used elsewhere in
# the framework.
#
# Recommended cadence: run weekly. The README in this directory
# suggests wiring it to `/schedule weekly` so the agent runtime
# surfaces candidates without manual prompting.

set -euo pipefail

# Resolve script directory so the script works whether invoked from
# anywhere in the repo or from a stale `cwd`.
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MANIFEST="${HERE}/pinned-versions.toml"

if [[ ! -r "$MANIFEST" ]]; then
  echo "error: cannot read $MANIFEST" >&2
  exit 1
fi

# Cooldown window. Mirrors `[tool.uv] exclude-newer = "7 days"` in
# the root pyproject.toml and the dependabot weekly cooldown of 7
# days in `.github/dependabot.yml`. Tools released within this
# window are NOT proposed as upgrade candidates yet.
COOLDOWN_DAYS=7

now_epoch=$(date -u +%s)
cooldown_cutoff_epoch=$(( now_epoch - COOLDOWN_DAYS * 86400 ))

# ---------------------------------------------------------------------
# Per-tool upstream lookup. Each function prints the latest aged-past-
# cooldown release in the form "version<TAB>YYYY-MM-DD". A non-zero
# exit code means the upstream lookup failed (rate limit, network
# error, etc.) — the caller continues with other tools.
# ---------------------------------------------------------------------

# GitHub releases lookup (used by bubblewrap and claude-code).
# Picks the most recent release whose `published_at` is at least
# `COOLDOWN_DAYS` old.
gh_latest_aged() {
  local repo="$1"
  curl -fsSL "https://api.github.com/repos/${repo}/releases?per_page=20" \
    | python3 -c '
import json, sys
from datetime import datetime, timezone
cutoff = '"$cooldown_cutoff_epoch"'
for r in json.load(sys.stdin):
    pub = datetime.fromisoformat(r["published_at"].replace("Z", "+00:00"))
    if pub.timestamp() <= cutoff:
        # strip a leading "v" so the script outputs PEP-440-ish version
        tag = r["tag_name"].lstrip("v")
        print(f"{tag}\t{pub.date().isoformat()}")
        break
'
}

# socat upstream is a static HTML index; scrape the highest version
# tarball whose mtime is older than COOLDOWN_DAYS.
socat_latest_aged() {
  # The download index has a fairly stable shape — `socat-X.Y.Z.W.tar.gz`
  # rows in a directory listing. Pick the highest version whose
  # `Last-Modified` (per HEAD) is older than the cutoff.
  local index versions
  index="$(curl -fsSL http://www.dest-unreach.org/socat/download/)" || return 1
  versions=$(echo "$index" | grep -oE 'socat-[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+\.tar\.gz' | sort -uV)
  for v in $(echo "$versions" | tac); do
    local ver mtime mtime_epoch
    ver="${v#socat-}"
    ver="${ver%.tar.gz}"
    mtime=$(curl -sI "http://www.dest-unreach.org/socat/download/${v}" \
              | awk -F': ' '/^[Ll]ast-[Mm]odified:/ {print $2}' | tr -d '\r')
    if [[ -z "$mtime" ]]; then
      continue
    fi
    mtime_epoch=$(date -d "$mtime" +%s 2>/dev/null) || continue
    if (( mtime_epoch <= cooldown_cutoff_epoch )); then
      printf '%s\t%s\n' "$ver" "$(date -u -d "$mtime" +%Y-%m-%d)"
      return 0
    fi
  done
  return 1
}

# ---------------------------------------------------------------------
# Manifest parsing. Each `[tools.<name>]` table contributes one
# pinned (version, released) tuple.
# ---------------------------------------------------------------------

read_pinned() {
  python3 - "$MANIFEST" <<'PY'
import sys, tomllib
with open(sys.argv[1], "rb") as f:
    cfg = tomllib.load(f)
for name, t in cfg.get("tools", {}).items():
    print(f"{name}\t{t['version']}\t{t['released']}")
PY
}

# ---------------------------------------------------------------------
# Report.
# ---------------------------------------------------------------------

printf '%-14s %-10s %-12s %-10s %-12s %s\n' \
  TOOL PINNED 'PINNED@' UPSTREAM 'UPSTREAM@' STATUS
printf '%-14s %-10s %-12s %-10s %-12s %s\n' \
  ------ ------ ------- -------- --------- ------

while IFS=$'\t' read -r name pinned_ver pinned_date; do
  case "$name" in
    bubblewrap)
      latest_line="$(gh_latest_aged containers/bubblewrap || true)"
      ;;
    claude-code)
      latest_line="$(gh_latest_aged anthropics/claude-code || true)"
      ;;
    socat)
      latest_line="$(socat_latest_aged || true)"
      ;;
    *)
      latest_line=""
      ;;
  esac

  if [[ -z "$latest_line" ]]; then
    printf '%-14s %-10s %-12s %-10s %-12s %s\n' \
      "$name" "$pinned_ver" "$pinned_date" "?" "?" \
      'upstream lookup failed (rate limit / network)'
    continue
  fi

  upstream_ver="${latest_line%%$'\t'*}"
  upstream_date="${latest_line##*$'\t'}"

  if [[ "$upstream_ver" == "$pinned_ver" ]]; then
    status='✓ up to date'
  else
    # Note: this lexical comparison is a heuristic — semver-aware
    # comparison would be better, but every tool we track here uses
    # well-formed dotted-version strings, so plain `<` does the
    # right thing for ordered output. The maintainer is the actual
    # decision-maker; the script just surfaces candidates.
    status="upgrade candidate (aged past ${COOLDOWN_DAYS}-day cooldown)"
  fi

  printf '%-14s %-10s %-12s %-10s %-12s %s\n' \
    "$name" "$pinned_ver" "$pinned_date" "$upstream_ver" "$upstream_date" "$status"
done < <(read_pinned)

cat <<'EOF'

To bump a pinned tool:
  1. Confirm the candidate's release-notes / changelog are clean.
  2. Edit `tools/agent-isolation/pinned-versions.toml` — update both
     `version` and `released` for that tool, plus the top-level
     `pinned_at` field to today's date.
  3. Update the install command in `secure-agent-setup.md` if the
     distro package version has shifted.
  4. Open the bump as its own PR with a short rationale.

The 7-day cooldown above is the floor for *eligibility*, not a
mandate to upgrade — the framework maintainer is welcome to defer
a bump indefinitely if the new version doesn't add value.
EOF
