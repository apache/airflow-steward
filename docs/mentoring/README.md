<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [Mentoring skill family](#mentoring-skill-family)
  - [Status](#status)
  - [Adopter contract (proposed)](#adopter-contract-proposed)
  - [Cross-references](#cross-references)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# Mentoring skill family

**Status: proposed.** No skill ships yet. The framework lands the
spec — tone guide, hand-off protocol, adopter contract — ahead
of any skill code so the project's tone choices are reviewable
independently of runtime behaviour. See
[`MISSION.md` § Mentoring](../../MISSION.md#technical-scope) for
the *why*.

Why a framework skill family? Mentoring is named in
[`MISSION.md`](../../MISSION.md) as the highest-value mode and
the one off-the-shelf agent tooling skips. Lifting it into the
framework lets every adopter pick up the tone work and the
hand-off rules without re-deriving them, and lets the
framework's contributor-sentiment evaluation cover all adopters
at once.

## Status

Mentoring is **proposed**. No SKILL.md exists yet. This directory
currently contains:

- [**`spec.md`**](spec.md) — what the future skill should do:
  scope, triggers, tone, hand-off, adopter knobs.

A prototype skill (`pr-management-mentor`, working name) lands
in a follow-up PR after this spec is reviewed. The skill ships
flagged `mode: Mentoring` + `experimental` per the
[mode lifecycle](../modes.md#mode-lifecycle).

## Adopter contract (proposed)

The future skill resolves project-specific content from the
adopter's `<project-config>/mentoring-config.md` — see the
template at
[`projects/_template/mentoring-config.md`](../../projects/_template/mentoring-config.md).

## Cross-references

- [`MISSION.md` § Mentoring](../../MISSION.md#technical-scope) —
  mode definition, RAI empowerment framing.
- [`docs/modes.md` § Mentoring](../modes.md#mentoring) —
  implementation status.
- [`spec.md`](spec.md) — full spec.
