<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/legal/release-policy.html -->

<!-- Adopter template — copy this file into <project-config>/privacy-llm.md
     and customise per the recipes in
     ../../docs/setup/privacy-llm.md.

     The default below (Variant 1 — Claude Code only) is the
     starting state for a fresh adoption. Adopting projects that
     wire in additional LLMs (Ollama, Bedrock, Anthropic direct,
     etc.) replace the *Currently configured LLM stack* section
     and populate *Approved third-party endpoints* per the recipe
     for that variant. -->

# Privacy-LLM configuration

This file declares which LLM endpoints this project's framework
skills are allowed to route private data through, and which
mailing lists count as private.

The contract behind these declarations lives in the framework at
[`tools/privacy-llm/models.md`](../../tools/privacy-llm/models.md);
the per-variant setup recipes are at
[`docs/setup/privacy-llm.md`](../../docs/setup/privacy-llm.md).

## Currently configured LLM stack

- Claude Code (the agent running framework skills)

<!-- Add additional LLMs here, one per line, with the endpoint URL
     or provider name and the model name in parentheses. Example:

       - Local Ollama at http://127.0.0.1:11434/  (model: llama3.1:8b)

     For a Claude-Code-only deployment (Variant 1), leave this
     section as-is.  -->

## Approved third-party endpoints (opt-in)

(none — Claude Code is the only LLM)

<!-- Populate this section when adding any LLM that is NOT in
     the framework's default-approved set
     (Claude Code itself / *.apache.org / 127.0.0.1 or localhost
     local inference). Each entry needs:

       - Endpoint URL or provider product name
       - Data-residency contract: <link or short identifier>
       - Approved-by: <PMC-member-initials> <YYYY-MM-DD>

     A `<project-config>/privacy-llm.md` that lists an opt-in
     endpoint without the Approved-by line will be flagged as
     incomplete by the privacy-llm-check helper. -->

## Private mailing lists for this project

- `<private-list>`

<!-- List every PMC-private foundation list this project's
     security team reads. The framework's privacy-llm gate
     refuses to fetch from these lists unless the active LLM
     stack above is fully approved.

     `<security-list>` (the project's security@ list) is **not**
     listed here — its body is treated as non-private; only the
     reporter PII inside it is redacted (per
     ../../tools/privacy-llm/pii.md). -->
