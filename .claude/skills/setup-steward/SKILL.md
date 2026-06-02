---
name: setup-steward
description: |
  Transition migration shim for pre-Magpie (apache-steward) adopters.
  This is the ONLY framework artefact that still carries the legacy
  `steward` name, and it exists for exactly one purpose: to migrate a
  repo that adopted the framework before it was renamed to Apache
  Magpie over to the new `magpie-` layout, then delete itself.
  Sub-actions:
    `/setup-steward upgrade` — run the one-time pre-Magpie migration
                               (the only supported sub-action)
when_to_use: |
  Invoke ONLY as the bridge for a pre-Magpie adopter: a repo whose
  committed framework skill is still `.claude/skills/setup-steward/`
  and whose runtime state still uses `.apache-steward*` / un-prefixed
  framework symlinks. A frozen pre-Magpie `/setup-steward upgrade`
  lands here automatically after it refreshes the snapshot and reloads
  the committed skill in-flight. After the migration completes the
  adopter uses `/magpie-setup` for everything; this shim is gone.
argument-hint: "[upgrade]"
capability: capability:setup
license: Apache-2.0
---

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

<!-- Placeholder convention (see ../../../AGENTS.md#placeholder-convention-used-in-skill-files):
     <adopter-skills-dir>  → the dir holding the adopter's skills
                             (`.claude/skills/` or `.github/skills/`,
                             per the project's convention)
     <snapshot-dir>        → the gitignored framework snapshot. Pre-Magpie
                             it is `.apache-steward/`; the migration moves
                             it to `.apache-magpie/`. -->

# setup-steward — pre-Magpie migration shim

> **This skill is a one-shot transition artefact.** The framework was
> renamed from **apache-steward** to **Apache Magpie**, which moved the
> skill source (`​.claude/skills/` → `skills/`), renamed the dotfiles
> (`​.apache-steward*` → `.apache-magpie*`), renamed the bootstrap skill
> (`setup-steward` → committed as `magpie-setup`), and namespaced every
> framework skill under a `magpie-` prefix. A repo that adopted the
> framework **before** that rename has a committed `setup-steward` skill
> frozen on the old layout, and cannot self-upgrade across the change.
> This shim is the bridge.

## How a pre-Magpie adopter reaches this shim

The pre-Magpie `setup-steward/upgrade.md` an adopter committed does, on
every `/setup-steward upgrade`:

1. delete `.apache-steward/` and re-fetch the framework per the
   committed lock (which lands the **new** Magpie framework on disk),
2. overwrite its committed `.claude/skills/setup-steward/` from the
   snapshot's `.apache-steward/.claude/skills/setup-steward/`, and
3. **reload that skill in-flight** (its Golden rule 9).

Because the Magpie framework still ships this shim at the legacy path
`.claude/skills/setup-steward/`, step (2) finds it, step (3) reloads
**this** `upgrade.md`, and the migration below runs in place of the old
upgrade logic — no manual bootstrap required.

> A `/magpie-setup upgrade` on an already-migrated repo never lands
> here (it has no `setup-steward` skill). If a repo is only *partly*
> migrated, `magpie-setup`'s own `upgrade.md` Step 0 detects the
> leftover `.apache-steward*` artefacts and routes back here.

## Sub-actions

| Invocation | Loads | Purpose |
|---|---|---|
| `/setup-steward upgrade` | [`upgrade.md`](upgrade.md) | Run the one-time pre-Magpie → Magpie migration, then hand off to the migrated `magpie-setup`. |
| `/setup-steward` (no args) | [`upgrade.md`](upgrade.md) | Same — the migration is the only thing this shim does. |

Any other sub-action (`adopt`, `verify`, `worktree-init`, `override`,
`unadopt`) is **not** served here: those belong to the migrated
`magpie-setup` skill. If asked for one before migrating, run the
migration first, then invoke it as `/magpie-setup <sub-action>`.

## After the migration

The migration's final step **removes this shim** — it replaces the
committed `.claude/skills/setup-steward/` with `magpie-setup` and drops
the `setup-steward` entry. From then on the adopter uses `/magpie-setup`
for adopt / upgrade / verify / worktree-init / override / unadopt, and
the `steward` name is gone from their repo entirely.
