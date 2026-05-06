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
"""One-shot interactive Vulnogram session-cookie capture.

Walks the operator through:

1. logging into ``https://<host>/users/login`` in their regular
   browser (the ASF-OAuth flow happens normally — username + 2FA);
2. opening DevTools → *Application* / *Storage* → *Cookies* →
   ``<host>``;
3. copying the value of the session cookie (default name
   ``connect.sid``);
4. pasting it back at this script's prompt.

The script then validates the cookie by hitting
``/<section>/new`` and reading the response — ``200 OK`` means the
session is live; a 302 to ``oauth.apache.org`` means the value was
typed wrong (or copied without URL-encoding).

The *long-lived secret* is the cookie value. It is written to
``~/.config/apache-steward/vulnogram-session.json`` (mode 0600,
parent directory 0700) so the file lives outside any project tree
— see the project's *credentials live in $HOME, never in project
tree* convention.
"""

from __future__ import annotations

import argparse
import getpass
import os
import subprocess
import sys
from pathlib import Path

from vulnogram_api.client import probe
from vulnogram_api.credentials import (
    DEFAULT_COOKIE_NAME,
    DEFAULT_CREDENTIALS_PATH,
    DEFAULT_HOST,
    Session,
    write_session_atomic,
)


def detect_from_address() -> str | None:
    if env := os.environ.get("VULNOGRAM_FROM"):
        return env
    try:
        out = subprocess.check_output(
            ["git", "config", "user.email"],
            text=True,
            cwd=Path(__file__).resolve().parent,
            stderr=subprocess.DEVNULL,
        ).strip()
        return out or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description=(__doc__ or "").split("\n\n", 1)[0],
    )
    ap.add_argument(
        "--host",
        default=DEFAULT_HOST,
        help=f"Vulnogram host. Default: {DEFAULT_HOST}.",
    )
    ap.add_argument(
        "--cookie-name",
        default=DEFAULT_COOKIE_NAME,
        help=(
            f"Session cookie name. Default: {DEFAULT_COOKIE_NAME} "
            "(express-session's default; check DevTools → Cookies if a "
            "different name is shown for your Vulnogram instance)."
        ),
    )
    ap.add_argument(
        "--from-address",
        default=detect_from_address(),
        help=(
            "ASF-OAuth account address baked into the session file (informational). "
            "Defaults to $VULNOGRAM_FROM, else `git config user.email`."
        ),
    )
    ap.add_argument(
        "--out",
        default=str(DEFAULT_CREDENTIALS_PATH),
        help=f"Output session-file path. Default: {DEFAULT_CREDENTIALS_PATH}.",
    )
    ap.add_argument(
        "--cookie-value",
        default=None,
        help=(
            "Pass the cookie value directly (skips the interactive prompt). "
            "Mainly useful for tests; production callers should let the "
            "interactive getpass prompt read from the controlling tty."
        ),
    )
    ap.add_argument(
        "--section",
        default="cve5",
        help="Vulnogram section to probe for the validation step. Default: cve5.",
    )
    ap.add_argument(
        "--skip-validate",
        action="store_true",
        help=(
            "Skip the live HTTP probe after capturing the cookie. Use only when "
            "the host is unreachable from the box running setup but the cookie "
            "is known good (e.g. capturing on a remote machine)."
        ),
    )
    return ap.parse_args(argv)


def _print_walkthrough(host: str, cookie_name: str) -> None:
    print(f"Vulnogram session-cookie capture for {host}.")
    print()
    print("Step 1. Open this URL in a regular browser (not curl):")
    print(f"  https://{host}/users/login")
    print()
    print(
        "Step 2. Complete the ASF OAuth login normally (username + 2FA via "
        "oauth.apache.org). After the redirect lands you back on the "
        f"{host} home page, you have a live session cookie."
    )
    print()
    print(
        "Step 3. Open DevTools (Cmd-Option-I / Ctrl-Shift-I), go to:\n"
        "  Application  →  Storage  →  Cookies  →  https://" + host + "\n"
        "(Firefox: Storage → Cookies → https://" + host + ")."
    )
    print()
    print(f"Step 4. Find the cookie named '{cookie_name}' and copy its *Value*.")
    print(
        "  The value typically starts with 's%3A' and is URL-encoded — "
        "copy the value column verbatim, including the leading 's%3A'."
    )
    print()
    print(
        "Step 5. Paste the value at the prompt below. The input is hidden — "
        "the script does not echo or log the cookie value."
    )
    print()


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    _print_walkthrough(args.host, args.cookie_name)

    cookie_value = args.cookie_value
    if not cookie_value:
        cookie_value = getpass.getpass(f"Paste {args.cookie_name} value: ").strip()
    if not cookie_value:
        raise SystemExit("Empty cookie value — aborting; nothing written.")

    out_path = Path(args.out).expanduser()
    write_session_atomic(
        out_path,
        host=args.host,
        cookie_name=args.cookie_name,
        cookie_value=cookie_value,
        from_address=args.from_address,
    )
    print(f"Wrote session to {out_path} (mode 600).")
    if args.from_address:
        print(f"From-address baked in: {args.from_address}")

    if args.skip_validate:
        print("Skipping validation per --skip-validate. Run `vulnogram-api-check` later to test.")
        return 0

    session = Session(
        host=args.host,
        cookie_name=args.cookie_name,
        cookie_value=cookie_value,
        from_address=args.from_address,
    )
    print()
    print(f"Validating session by probing https://{args.host}/{args.section}/new ...")
    result = probe(session, section=args.section)
    if result == "valid":
        print("✓ Session is live. You can now run `vulnogram-api-record-update`.")
        return 0
    if result == "expired":
        print(
            "✗ Vulnogram redirected to the ASF-OAuth login page. The cookie "
            "value was either typed wrong, copied without the leading 's%3A', "
            "or the session has already expired. Re-run setup.",
            file=sys.stderr,
        )
        return 2
    print(f"✗ Probe returned an unexpected result: {result}", file=sys.stderr)
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
