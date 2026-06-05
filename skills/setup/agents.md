<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

# agents — the agent-target registry (where framework-skill symlinks land)

Framework skills are **vendor-neutral content**: every supported
agent reads the *same* `SKILL.md` (the open Agent Skills format —
plain Markdown + a small YAML frontmatter). The skill body is
byte-identical no matter which agent loads it; there is **no
per-agent compile, adapter, or content transform**. The only thing
that genuinely differs between agents is **where on disk each one
looks for skills**. This file is the registry of those locations —
the single source of truth `adopt`, `upgrade`, `verify`,
`unadopt`, and `worktree-init` consult to decide *which directories*
to wire, refresh, health-check, and tear down.

It is the magpie analogue of a package manager's per-agent path
table: keep all vendor-specific knowledge here as *"where files
go"*, never as *"what files contain"*.

## The registry

| Target id | Project skills dir | Kind | Reads it |
|---|---|---|---|
| `universal` | `.agents/skills/` | universal | Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode, Cline, Zed, Warp, Amp, and the rest of the cluster that converged on the shared path |
| `claude-code` | `.claude/skills/` | native | Claude Code (layout variants A/B/C/D — see [`conventions.md`](conventions.md)) |
| `github` | `.github/skills/` | native | GitHub's skill loader (paired with `claude-code` under conventions Pattern B / D) |
| `windsurf` | `.windsurf/skills/` | native | Windsurf |
| `goose` | `.goose/skills/` | native | Goose |

The table is **extensible**: a new agent that wants framework
skills is one new row (`id`, project dir, kind), nothing else —
the same way a path-registry-driven installer adds an agent. Do
not invent per-agent *content*; if an agent needs a different
directory, add a row, never a forked skill.

## The universal directory — `.agents/skills/`

The load-bearing move for neutrality is that a large cluster of
agents (Codex, Cursor, Gemini CLI, GitHub Copilot, OpenCode,
Cline, Zed, Warp, …) all read **`.agents/skills/`** as their
project-scope skills path. Wiring `magpie-<skill>` once into
`.agents/skills/` covers that whole cluster in a **single
placement**:

```text
.agents/skills/magpie-pr-management-triage   →  one symlink
   ├─ Codex      picks it up
   ├─ Cursor     picks it up
   ├─ Gemini CLI picks it up
   └─ Copilot …  picks it up
```

Only agents with a **bespoke** folder (`claude-code` →
`.claude/skills/`, `github` → `.github/skills/`, `windsurf`,
`goose`, …) need their own symlink in addition. This pushes the
adopter repo toward de facto convergence on one neutral location
while still bridging the holdouts.

(Global / per-user skill paths diverge across agents — e.g.
`~/.cursor/skills/`, `~/.codex/skills/`, `~/.gemini/skills/`. The
framework's adoption is **project-scope** — it writes inside the
adopter repo — so it only ever cares about the project columns
above. Global installs are the operator's concern, out of scope
for `setup`.)

## Active-target selection — which dirs `adopt` wires

On every `adopt` / `upgrade` / `worktree-init`, the **active
target set** is computed as the union of:

1. **The always-on neutral targets** — `universal`
   (`.agents/skills/`) **plus** the `claude-code` + `github`
   pair, wired per the adopter's detected
   [skills-dir convention](conventions.md) (A/B/C/D). These three
   are wired unconditionally; they are cheap relative symlinks
   into the gitignored snapshot, harmless to an agent that never
   reads them, and dropping them is not a supported configuration.
2. **Any other registry target already present in the repo** —
   if `.windsurf/skills/` or `.goose/skills/` (etc.) already
   exists as a real directory, it is added to the active set so
   that agent sees the framework skills too.
3. **Explicit opt-in** via the `agents:<list>` flag (see
   [`SKILL.md` Inputs](SKILL.md#inputs)) — a comma-separated list
   of registry ids. When passed it **replaces** the auto-detected
   set (1)+(2) for that run; `universal` is always retained even
   if omitted, because dropping it defeats neutrality.

The flow **never** removes or rewrites an adopter's own
non-`magpie-` skill content in any target dir. It only adds /
repairs `magpie-*` symlinks.

## How the framework's rules generalise across targets

Every existing adoption rule is "per active target", not
"for `.claude` and `.github`":

- **`magpie-` prefix** ([`SKILL.md` Golden rule 6](SKILL.md#golden-rules))
  — unchanged. Every framework skill is `magpie-<skill>` in
  *every* active target dir, so it never collides with an
  adopter's own skills regardless of agent.
- **`.gitignore`** — one block per active target dir:
  `/<dir>/magpie-*` plus `!/<dir>/magpie-setup`. The negation
  keeps the one committed bootstrap (`magpie-setup`) tracked; the
  glob ignores the rest (their targets are the gitignored
  snapshot, so they would dangle on a fresh clone). See
  [`adopt.md` Step 7](adopt.md#step-7--gitignore-entries-fresh-only).
- **Symlink wiring** — flat (one `magpie-<n>` → snapshot per
  skill), exactly like conventions Pattern A, for `universal`,
  `windsurf`, `goose`, and any other native dir. The
  `claude-code` + `github` pair is the **one** special case: its
  inter-directory relationship (double-symlink B, single-dir
  symlink D, flat A) is described in [`conventions.md`](conventions.md)
  and detected per repo. See
  [`adopt.md` Step 8](adopt.md#step-8--wire-up-the-framework-skill-symlinks).
- **Local self-adoption** (framework checkout) — committed
  symlinks into `../../skills/<skill>/` in *every* active target
  dir, not just two. See
  [`adopt.md` → Local self-adoption](adopt.md#local-self-adoption-methodlocal).
- **`unadopt` / `worktree-init`** — every active target dir is
  torn down / propagated uniformly. Removing only `.claude` +
  `.github` would orphan the `.agents/skills/magpie-*` links.

## SKILL.md format portability

The same `SKILL.md` is valid in every target with no
per-agent edit:

| Frontmatter field | Cross-agent behaviour |
|---|---|
| `name`, `description` | Universal — discovery works everywhere. |
| `when_to_use` | Claude-family routing hint; other agents may ignore it → discovery still works off `description`, only routing precision degrades. |
| `argument-hint`, `capability` | magpie / Claude extensions; non-supporting agents silently ignore them. |
| `license` | Inert metadata. |

Unknown frontmatter is ignored by each agent (graceful
degradation), so there is **no compile step and no per-agent
file**. The gitignored snapshot stays the single source of truth;
every target dir is a symlink into it.

## The Claude-Code-only layer (not wired for other targets)

Some of what `adopt` installs is **genuinely Claude-Code-specific
and is wired only when the `claude-code` target is active**:

- `.claude/settings.json` — the sandbox (`network.allowedDomains`
  allowlist, `filesystem.denyRead`), the MCP-tool permission
  allowlist, and the hooks. Schema:
  `claude-code-settings.json`.
- `.claude/settings.local.json` — per-machine sandbox-allowlist
  entries.
- The `setup-isolated-setup-*` skill family — sandbox / pinned-
  tools / hooks installer.

Other agents adopt the **skills** (the neutral content) **without**
this layer.

> **Security caveat — this layer is a control, not cosmetics.**
> For a security framework the sandbox is a *confidentiality
> control* (it blocks exfiltration of non-public vulnerability
> data and reading `~/`). Running a security-class skill on an
> agent that lacks an equivalent control is a **policy decision**,
> not graceful degradation. Adopting the skills onto a non-Claude
> agent is supported; *executing confidential workflows there*
> requires the project to either declare that agent unsupported
> for those workflows or provide an equivalent control. `adopt`
> itself only places files — it does not grant that approval.

## Relationship to `conventions.md`

[`conventions.md`](conventions.md) describes the **`.claude/` ↔
`.github/` layout** (patterns A/B/C/D) — i.e. the internal shape
of the `claude-code` + `github` rows of this registry, which are
coupled because some adopters mirror one into the other. This file
is the **wider** picture: the full set of agent targets, of which
that pair is one coupled entry and `universal` (`.agents/skills/`)
is another. When `adopt` wires symlinks it consults **both**: this
file for *which targets*, `conventions.md` for *how the
`.claude/`/`.github/` pair is laid out* in this particular repo.
