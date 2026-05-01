<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**  *generated with [DocToc](https://github.com/thlorenz/doctoc)*

- [How sandbox isolation works](#how-sandbox-isolation-works)
  - [What `sandbox.enabled` actually does](#what-sandboxenabled-actually-does)
  - [Linux: bubblewrap + user namespaces](#linux-bubblewrap--user-namespaces)
  - [macOS: Seatbelt](#macos-seatbelt)
  - [The blind spot: `Bash(curl *)` and DNS-over-HTTPS](#the-blind-spot-bashcurl--and-dns-over-https)
  - [How the feedback mechanisms layer together](#how-the-feedback-mechanisms-layer-together)
  - [See also](#see-also)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

<!-- SPDX-License-Identifier: Apache-2.0
     https://www.apache.org/licenses/LICENSE-2.0 -->

# How sandbox isolation works

This is the companion to
[`secure-agent-setup.md`](secure-agent-setup.md): the mental
model for *how* the filesystem-sandbox layer (Layer 1 of the
[Three-layer defence](secure-agent-setup.md#three-layer-defence)
table) actually intercepts a Bash call, what the agent's own
tools do that the sandbox does *not* cover, and where each
visible state of a session originates. Optional for adoption —
the setup document is sufficient to install and verify the
secure setup — and worth reading when you want to understand
which layer is doing what, or are debugging why a specific
call did or did not get through.

## What `sandbox.enabled` actually does

`sandbox.enabled: true` is not a flag the agent inspects; it is a
directive to Claude Code's Bash tool to wrap every subprocess in
an OS-level container before launching it. The model itself never
sees the boundary — it just gets a `command not found` /
`No such file or directory` back from a Bash call that tried to
reach outside the allowed paths.

The agent's own Read, Edit, and Write tools are **not** sandboxed.
Those tools call into Claude Code's runtime directly and hit the
host filesystem with whatever privileges the user running
`claude` has. `permissions.deny` (`Read(~/.aws/**)`,
`Read(~/.ssh/**)`, …) is what stops the agent's Read tool from
reading those paths — the sandbox would not.

The two layers are complementary, not redundant. The sandbox stops
a Bash subprocess (an MCP server's child process, a `gh` CLI call,
a `python` snippet the model decided to run) from reading a denied
path. `permissions.deny` stops the agent's Read tool from reading
the same path. A secure setup needs both: the framework's
[`.claude/settings.json`](.claude/settings.json) deny-lists
`Read(~/.config/gh/**)` *and* allow-reads `~/.config/gh/` in the
sandbox, so `gh` can see its token but the agent can never read
the file.

## Linux: bubblewrap + user namespaces

On Linux, Claude Code launches each Bash subprocess inside a
fresh **mount namespace** built by
[`bubblewrap`](https://github.com/containers/bubblewrap). bubblewrap
bind-mounts only the paths listed in `sandbox.filesystem.allowRead`
into the new namespace; everything else from the host is
*literally absent* from the subprocess's view of the filesystem.

The visible result is precise: a `cat ~/.aws/credentials` from
inside the sandbox returns `No such file or directory`, not
`Permission denied`. The path doesn't exist as far as the
subprocess is concerned — there is nothing to deny access to.
That is the same mechanism `flatpak` and `firejail` use.

Network egress is layered on top of the same namespace via
[`socat`](http://www.dest-unreach.org/socat/), which terminates
the outgoing TLS connection, reads the SNI extension, and
forwards only to hosts in `sandbox.network.allowedDomains`.
A connection to a non-allowed host fails at the proxy.

## macOS: Seatbelt

On macOS, bubblewrap and socat are not used — Claude Code wraps
Bash subprocesses in
[`sandbox-exec`](https://developer.apple.com/library/archive/documentation/Security/Conceptual/AppSandboxDesignGuide/AboutAppSandbox/AboutAppSandbox.html)
instead, generating a `.sb` profile that the kernel enforces at
the syscall level. The same `denyRead` / `allowRead` /
`allowedDomains` shape from `settings.json` drives the generated
profile.

The visible result differs slightly: a denied read typically
returns `Operation not permitted` rather than
`No such file or directory`, because Seatbelt rejects the syscall
before the filesystem driver runs. The policy outcome is the
same — denied paths are unreachable from within the subprocess.

No system packages need pinning on macOS — Seatbelt ships with
the OS. The framework's
[`pinned-versions.toml`](tools/agent-isolation/pinned-versions.toml)
only pins `bubblewrap`, `socat`, and `claude-code` itself;
Seatbelt does not appear because its version *is* the OS version.

## The blind spot: `Bash(curl *)` and DNS-over-HTTPS

The SNI proxy filters by the TLS Server Name Indication
extension, which a well-behaved client puts on the wire in
clear text before the TLS handshake completes. A client that
uses DNS-over-HTTPS through an allow-listed CDN (Cloudflare,
Google) can cleanly dodge that inspection — the SNI says
`cloudflare-dns.com`, the actual query is for somewhere else.
That is why the framework's `permissions.deny` list also
contains `Bash(curl *)`, `Bash(wget *)`, and the various cloud
CLIs — defence in depth against an exfiltration path that the
sandbox alone does not close.

## How the feedback mechanisms layer together

| Mechanism | Scope | What it tells you | When it fires |
|---|---|---|---|
| `sandbox.enabled` in settings | per-session | Source of truth — is the sandbox active for this session? | At session start; persists for the session unless `/sandbox` toggles it. |
| [Sandbox-state status line](secure-agent-setup.md#sandbox-state-status-line) | per-session, always-on | Visual confirmation of the source of truth. | Re-rendered on every status-line update. |
| [Sandbox-bypass visibility hook](secure-agent-setup.md#sandbox-bypass-visibility-hook) | per-call | A specific Bash call is asking to step outside the sandbox. | Only when `dangerouslyDisableSandbox: true` is set on the call. |
| Claude Code permission prompt | per-call | The gate — approve or deny the bypass. | Same firing condition as the hook; the hook augments the prompt with a banner the user cannot skim past. |

The settings file is the source of truth; the status line and
the hook surface that truth on two different time scales —
always-on (status line) and per-call (hook). The permission
prompt is the actual gate. Installing all four means a
sandbox-bypass that lands without your noticing has to skim past
two banners and silently approve a prompt — a much higher bar
than skimming a single permission dialog.

## See also

- [`secure-agent-setup.md`](secure-agent-setup.md) — install +
  verify + keep-updated path. The five session screenshots
  demonstrating each layer in action live there too, in
  [What a session looks like](secure-agent-setup.md#what-a-session-looks-like).
- [Sandbox-state status line](secure-agent-setup.md#sandbox-state-status-line)
  and
  [Sandbox-bypass visibility hook](secure-agent-setup.md#sandbox-bypass-visibility-hook)
  — the install instructions for the surfacing pieces this
  document only describes mechanically.
