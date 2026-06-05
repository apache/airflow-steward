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
# claude-term-bg.sh — tint the terminal background while Claude Code is
# waiting on YOU, and keep it calm the rest of the time.
#
# This is a quality-of-life helper, NOT a security control: it makes the
# "Claude is blocked on me" state impossible to miss in a window you've
# tabbed away from. Wire it into five Claude Code hooks (user-scope):
#
#   "Stop"              -> claude-term-bg.sh wait    (turn finished — your turn, tint)
#   "UserPromptSubmit"  -> claude-term-bg.sh reset   (you replied — back to calm)
#   "SessionStart"      -> claude-term-bg.sh reset   (fresh session — clear any stale tint)
#   "PreToolUse"        -> claude-term-bg.sh reset   (actively working — stay calm; also
#                                                     clears an approved-permission tint)
#   "Notification"      -> claude-term-bg.sh notify  (tint for permission prompts only;
#                                                     the plain idle ping stays calm)
#
# Colours are overridable via the environment (e.g. inline in the hook command):
#   CLAUDE_WAIT_BG    background while waiting   (default: #2a1a3a, a muted indigo)
#   CLAUDE_RESET_BG   calm/idle background       (default: unset -> reset to profile default;
#                                                 set e.g. to #000000 for a deterministic black)
#
# Mechanism notes (the two things that make this actually work):
#
#   1. No controlling terminal. Claude Code spawns hook commands detached
#      from the tty, so /dev/tty does not resolve to your terminal window.
#      find_tty_dev() walks up the process tree to the Claude process's pty
#      (e.g. /dev/ttys003) and writes the escape straight to that device.
#
#   2. Set vs. reset asymmetry. iTerm2 honours OSC 11 (set background) but
#      does NOT reliably honour OSC 111 (reset-to-default) through Claude's
#      fullscreen TUI, so a naive reset leaves the tint stuck. The only
#      deterministic reset is an explicit colour via CLAUDE_RESET_BG (OSC 11,
#      the path we know works); without it we emit BOTH OSC 111 and iTerm2's
#      proprietary SetColors=bg=default and let whichever the terminal
#      understands win.
#
# Tested on iTerm2 + macOS. Terminals that ignore OSC 11 entirely simply see
# no change (fail-soft). For a guaranteed reset anywhere, set CLAUDE_RESET_BG.
set -u
WAIT_BG="${CLAUDE_WAIT_BG:-#2a1a3a}"
RESET_BG="${CLAUDE_RESET_BG:-}"
action="${1:-reset}"

find_tty_dev() {
  local pid=${PPID:-$$} t i
  for i in 1 2 3 4 5 6 7 8; do
    [ -z "$pid" ] || [ "$pid" = "0" ] || [ "$pid" = "1" ] && break
    t=$(ps -o tty= -p "$pid" 2>/dev/null | tr -d ' ')
    case "$t" in
      ttys*|tty[0-9]*) echo "/dev/$t"; return 0 ;;
    esac
    pid=$(ps -o ppid= -p "$pid" 2>/dev/null | tr -d ' ')
  done
  return 1
}

tty_dev=$(find_tty_dev || true)
[ -n "${tty_dev:-}" ] && [ -w "$tty_dev" ] || exit 0

set_wait() { printf '\033]11;%s\007' "$WAIT_BG" > "$tty_dev"; }
set_reset() {
  if [ -n "$RESET_BG" ]; then
    printf '\033]11;%s\007' "$RESET_BG" > "$tty_dev"
  else
    printf '\033]111\007' > "$tty_dev"                       # xterm: reset bg
    printf '\033]1337;SetColors=bg=default\007' > "$tty_dev" # iTerm2 proprietary
  fi
}

case "$action" in
  wait|set)  set_wait ;;
  reset|off) set_reset ;;
  notify)
    # Notification fires for permission prompts AND the plain 60s idle ping.
    # Tint only when it's something that genuinely wants the user to act.
    msg=$(cat 2>/dev/null)
    case "$msg" in
      *permission*|*approve*|*"needs your"*) set_wait ;;
      *)                                     set_reset ;;
    esac
    ;;
esac
exit 0
