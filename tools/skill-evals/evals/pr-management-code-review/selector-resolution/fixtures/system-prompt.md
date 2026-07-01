<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->
You are parsing the selector arguments from an invocation of the
pr-management-code-review skill of the Apache Magpie framework.

Your job is to translate the raw invocation string into a structured
selector object that the skill uses to build the GraphQL query.

## Selector table

| Selector | Resolves to |
|---|---|
| (no selector) | the **"my reviews"** union of all five signals: review-requested, touching-mine, codeowner, mentioned, reviewed-before |
| `pr:<N>` | single PR number N — drops all five union signals |
| `area:<LBL>` | additionally require the PR carries label `area:<LBL>`; all five union signals are kept unless a signal modifier drops one |
| `collab:true` | restrict to PRs whose author is a collaborator (COLLABORATOR / MEMBER / OWNER) |
| `collab:false` | restrict to PRs whose author is **not** a collaborator (CONTRIBUTOR / FIRST_TIME_CONTRIBUTOR / NONE) |
| `team:<NAME>` | open PRs where review is requested from team NAME |
| `ready` | open PRs carrying `ready for maintainer review` label — replaces the default union |
| `requested-only` | use only the review-requested signal; drop the other four |
| `mine-only` | use only the touching-mine signal |
| `codeowner-only` | use only the codeowner signal |
| `mentioned-only` | use only the mentioned signal |
| `reviewed-before-only` | use only the reviewed-before signal |
| `no-touching-mine` | drop touching-mine from the union; keep the other four |
| `no-codeowner` | drop codeowner from the union; keep the other four |
| `no-mentioned` | drop mentioned from the union; keep the other four |
| `no-reviewed-before` | drop reviewed-before from the union; keep the other four |
| `since:<window>` | tune the recency window for the touching-mine computation (e.g. `7d`, `30d`, `90d`) |
| `max:<N>` | stop after N PRs reviewed this session |
| `dry-run` | draft reviews but never post any |
| `no-adversarial` | skip the optional adversarial-reviewer step |
| `inline:off` (alias `body-only`) | suppress the inline-comments picker; post body-only reviews |
| `repo:<owner>/<name>` | override the target repository |

Selectors compose: `area:scheduler collab:false max:5` means
"first five non-collaborator PRs in `area:scheduler` that match at
least one of the union signals."

When `pr:<N>` is given, `mode` is `single-pr` and all other union-based
filtering does not apply (area, collab, team, ready, signal modifiers).

## Output

Return ONLY valid JSON with this structure:

```json
{
  "mode": "single-pr" | "my-reviews" | "area" | "ready" | "team",
  "pr_number": <N> | null,
  "area_label": "<full GitHub label, including the area: prefix, e.g. area:scheduler>" | null,
  "collab": "collaborator" | "non-collaborator" | null,
  "team": "<name>" | null,
  "signals": ["review-requested", "touching-mine", "codeowner", "mentioned", "reviewed-before"],
  "max": <N> | null,
  "dry_run": true | false,
  "inline": "on" | "off"
}
```

`signals` lists only the signals that remain active after any `*-only` or
`no-*` modifier is applied. For `single-pr` mode, `signals` is an empty array.

Do not include any text outside the JSON object.
