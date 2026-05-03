<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# upgrade — refresh the gitignored snapshot + reconcile overrides

Refresh `<repo-root>/.apache-steward/` to a newer framework
version, surface what changed, and reconcile any agentic
overrides against the new framework structure.

## Inputs

- `from:<git-ref>` — bring the snapshot to a specific framework
  ref (default: latest `main`).
- `dry-run` — show what would change without modifying anything.

## Step 0 — Pre-flight

1. Read `<repo-root>/.apache-steward.lock` for the current
   pinned commit SHA. If missing, the repo isn't adopted —
   suggest `/setup-steward adopt` and stop.
2. Read `<repo-root>/.apache-steward/` to confirm the snapshot
   is on disk. If missing (gitignored, fresh clone),
   re-download to the locked SHA first — that's the
   recover-snapshot path, not an upgrade. Then continue.

## Step 1 — Compare locked vs upstream

Fetch upstream's latest SHA for the configured ref:

```bash
git ls-remote https://github.com/apache/airflow-steward.git \
  refs/heads/main
```

If the locked SHA matches upstream, surface that and stop —
the snapshot is up to date. The user can re-invoke later.

Otherwise, list the commits between locked and upstream
(shallow log via the GitHub API or by re-cloning into a temp
dir; both work).

## Step 2 — Surface what changed

Show the user:

- The commit list (`git log --oneline <locked>..<upstream>`).
- Files touched in the framework `.claude/skills/` directory,
  grouped by skill family. Call out any change to a skill the
  adopter has an override for (overrides may need
  reconciliation — see Step 4).
- Any change to the `setup-steward` skill itself in the
  framework — that means the adopter's *committed* copy may
  have drifted. Surface as an extra note; the adopter chooses
  whether to re-copy.

Ask for explicit confirmation before refreshing.

## Step 3 — Refresh the snapshot

Replace `<repo-root>/.apache-steward/` with a fresh
`--depth=1` clone at the new ref:

```bash
rm -rf .apache-steward
git clone --depth=1 \
  --branch <ref> \
  https://github.com/apache/airflow-steward.git \
  .apache-steward
```

Update `.apache-steward.lock` with the new SHA + date.

If the user is on a UNIX system with hardlink-aware tools, an
optimization is to clone alongside and `mv` — but a simple
nuke-and-clone is the canonical path and is what the skill
defaults to. The snapshot is gitignored anyway, so destroying
it loses no committed work.

## Step 4 — Reconcile overrides

For each file in `<repo-root>/.apache-steward-overrides/`:

1. Check the corresponding framework skill exists in the new
   snapshot. If not (skill renamed or removed), surface as a
   conflict — the override may now apply to nothing. The user
   either updates the override's target skill name or removes
   the override.
2. If the framework skill's structure changed in a way the
   override anchors against (e.g. the override invalidates
   "Step 5 — Land the valid/invalid consensus" but the
   framework renumbered or restructured steps), surface as a
   conflict. The user re-anchors the override against the new
   structure.

The skill **does not** auto-rewrite overrides. It surfaces
conflicts and lets the user decide; agentic interpretation
means the right call is human judgement, not pattern-matching.

## Step 5 — Re-create symlinks

Walk `<adopter-skills-dir>` looking for stale symlinks that
point at framework skills no longer in the new snapshot
(rename, removal). For each, ask the user to either:

- Remove the stale symlink (renamed-away skill is gone), or
- Re-symlink to the new name (if the framework documented a
  rename).

Then walk the new snapshot for any new framework skills in
the families the adopter previously picked, and offer to
symlink them in.

## Step 6 — Sanity check

Run [`verify.md`](verify.md)'s checklist as a final step.

## Output to the user

```text
Snapshot refreshed: <old-SHA> → <new-SHA>
  X commits pulled (see list above)
  Y framework skills changed
  Z framework skills added
  W framework skills renamed/removed (see Step 5)

Overrides reconciled:
  ✓ <list of overrides whose target skill is unchanged>
  ⚠ <list of overrides flagged for re-anchoring>

.apache-steward.lock updated. Symlinks refreshed.

Recommended follow-ups:
  - Run /setup-isolated-setup-update if the secure-setup blast
    radius (settings.json, agent-isolation/, pinned-versions.toml)
    appears in the diff.
  - For each ⚠ override, open the file and re-anchor against the
    new framework structure.
```

## Failure modes

- **`.apache-steward.lock` missing** → repo not adopted yet;
  suggest `/setup-steward adopt`.
- **Network failure** → stop, surface error, user retries.
- **Conflict during reconcile** → not a failure per se; the
  skill surfaces the conflict and finishes the upgrade up to
  the conflict. The user's next step is editing the override
  files.
