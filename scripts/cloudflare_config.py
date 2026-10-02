"""Reconcile the Cloudflare Pages project against the state this repo declares.

The blog's Cloudflare setup is not reproducible from `wrangler.toml`: that file only
describes what a *build* would need, and this project is never built by Cloudflare.
Everything that actually shapes the live site (the compatibility date, Smart
Placement, the build image) lives server-side in the project's `deployment_configs`
and is invisible to anyone reading the repository. This module makes that state
explicit, diffable and re-applicable.

Three modes:

    python scripts/cloudflare_config.py --check    # diff live against DESIRED, exit 1 on drift
    python scripts/cloudflare_config.py --apply    # PATCH live to match DESIRED
    python scripts/cloudflare_config.py --dump     # print the live state, secrets redacted

Credentials are resolved in this order, so the same command works in CI and on a
laptop without a token ever being passed on a command line:

    1. `CLOUDFLARE_API_TOKEN` from the environment (what CI uses).
    2. The OAuth token `wrangler login` stores locally.

The account is resolved from `CLOUDFLARE_ACCOUNT_ID` when set, otherwise from
`GET /accounts` when the credential can see exactly one. No identifier is hardcoded:
this repository is public and account IDs do not belong in it.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any

import tomllib

API_ROOT = "https://api.cloudflare.com/client/v4"
PROJECT = "kevin-deldycke-blog"

WRANGLER_CONFIG = (
    pathlib.Path.home() / "Library/Preferences/.wrangler/config/default.toml"
)

# Response keys whose values must never be printed.
SECRET_KEYS = frozenset({"oauth_token", "refresh_token", "api_token", "secret"})


@dataclass(frozen=True)
class Setting:
    """One server-side setting, with enough context to justify its value.

    `default` is what a stock Cloudflare Pages project reports for this key. Where
    that value is quoted from Cloudflare's documentation, `verified` is True. Where
    it is inferred from how the product behaves, it is False and the diff labels it
    as such: an unverified default is a reasonable guess, not a fact, and this file
    should not launder one into the other.
    """

    path: tuple[str, ...]
    desired: Any
    default: Any
    why: str
    verified: bool = False
    managed: bool = True


# Settings applied identically to both environments. Pages supports only `production`
# and `preview`, so the two are enumerated rather than globbed.
_PER_ENVIRONMENT = (
    Setting(
        path=("compatibility_date",),
        desired="2026-06-16",
        default="<project creation date>",
        why=(
            "Pins the Workers runtime for Pages Functions. Inert today because this "
            "project has no Functions, but it is the value that would suddenly start "
            "mattering the moment one is added, so it is pinned rather than drifting."
        ),
        verified=False,
    ),
    Setting(
        path=("placement", "mode"),
        desired="smart",
        default="off",
        why=(
            "Smart Placement moves execution close to the origin. For a fully static "
            "site it changes nothing measurable, and it costs nothing. Recorded "
            "because it is switched on and would otherwise look like an accident."
        ),
        verified=False,
    ),
    Setting(
        path=("build_image_major_version",),
        desired=3,
        default=3,
        why=(
            "v1 auto-migrates to v3 on 2026-09-15 and v2 on 2027-02-23, after which "
            "Cloudflare states there will be no further build image versions. Already "
            "on 3, so this asserts a floor rather than requesting a change."
        ),
        verified=True,
    ),
)

DESIRED: tuple[Setting, ...] = tuple(
    Setting(
        path=("deployment_configs", environment, *setting.path),
        desired=setting.desired,
        default=setting.default,
        why=setting.why,
        verified=setting.verified,
    )
    for environment in ("production", "preview")
    for setting in _PER_ENVIRONMENT
)

# Settings that are read and reported but never written, because the API path is not
# a simple PATCH or because getting them wrong breaks publishing. They still belong
# in the diff: an unmanaged setting that changes is exactly the kind of drift that
# goes unnoticed for a year.
OBSERVED: tuple[Setting, ...] = (
    Setting(
        path=("source",),
        desired=None,
        default="a `github` source block",
        why=(
            "This project is Direct Upload only: .github/workflows/deploy.yaml builds "
            "the site and uploads it pre-rendered, and Cloudflare must never build it. "
            "Anything other than null here means a source repository got attached, "
            "which risks Cloudflare publishing a build of its own over a real upload."
        ),
        verified=False,
        managed=False,
    ),
    Setting(
        path=("build_config", "build_command"),
        desired="",
        default="",
        why=(
            "Empty because Cloudflare never builds this project. A build command "
            "appearing here means something is trying to make it build one."
        ),
        verified=False,
        managed=False,
    ),
)


def _token() -> str:
    token = os.environ.get("CLOUDFLARE_API_TOKEN")
    if token:
        return token
    if WRANGLER_CONFIG.is_file():
        stored = tomllib.loads(WRANGLER_CONFIG.read_text()).get("oauth_token")
        if stored:
            return str(stored)
    raise SystemExit(
        "No credential. Set CLOUDFLARE_API_TOKEN, or run `wrangler login` locally."
    )


def _call(path: str, token: str, method: str = "GET", body: dict | None = None) -> Any:
    request = urllib.request.Request(
        f"{API_ROOT}{path}",
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        data=None if body is None else json.dumps(body).encode(),
    )
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as error:
        detail = error.read().decode(errors="replace")[:400]
        if error.code == 403 and path == "/accounts":
            detail += (
                "\n\nA minimum-scope Pages token cannot enumerate accounts, which is "
                "only used to guess the target when CLOUDFLARE_ACCOUNT_ID is unset. "
                "Set CLOUDFLARE_ACCOUNT_ID and this call goes away."
            )
        raise SystemExit(f"{method} {path} failed: HTTP {error.code}\n{detail}")
    if not payload.get("success", True):
        raise SystemExit(f"{method} {path} returned errors: {payload.get('errors')}")
    return payload["result"]


def _account(token: str) -> str:
    account = os.environ.get("CLOUDFLARE_ACCOUNT_ID")
    if account:
        return account
    accounts = _call("/accounts", token)
    if len(accounts) != 1:
        names = ", ".join(a["name"] for a in accounts) or "none"
        raise SystemExit(
            f"Set CLOUDFLARE_ACCOUNT_ID: the credential sees {len(accounts)} "
            f"accounts ({names}), so the target is ambiguous."
        )
    return str(accounts[0]["id"])


def _dig(node: Any, path: tuple[str, ...]) -> Any:
    for key in path:
        if not isinstance(node, dict) or key not in node:
            return KeyError
        node = node[key]
    return node


def _nest(path: tuple[str, ...], value: Any) -> dict:
    *parents, leaf = path
    nested: dict = {leaf: value}
    for key in reversed(parents):
        nested = {key: nested}
    return nested


def _merge(into: dict, other: dict) -> dict:
    for key, value in other.items():
        if isinstance(value, dict) and isinstance(into.get(key), dict):
            _merge(into[key], value)
        else:
            into[key] = value
    return into


def _redact(node: Any) -> Any:
    if isinstance(node, dict):
        return {
            k: ("<redacted>" if k in SECRET_KEYS else _redact(v))
            for k, v in node.items()
        }
    if isinstance(node, list):
        return [_redact(v) for v in node]
    return node


def _diff(project: dict) -> tuple[list[Setting], list[tuple[Setting, Any]]]:
    """Return (settings matching DESIRED, settings that drifted with their live value)."""
    matched: list[Setting] = []
    drifted: list[tuple[Setting, Any]] = []
    for setting in (*DESIRED, *OBSERVED):
        live = _dig(project, setting.path)
        # Cloudflare reports "this is unset" as either a null value or a missing key
        # depending on the field, and both mean the same thing to a setting we want
        # gone. Without this, whichever form it is not currently using reads as drift.
        if setting.desired is None and live is KeyError:
            live = None
        if live == setting.desired:
            matched.append(setting)
        else:
            drifted.append((setting, live))
    return matched, drifted


def _describe(setting: Setting) -> str:
    dotted = ".".join(setting.path)
    stock = "documented" if setting.verified else "inferred, unverified"
    scope = "managed" if setting.managed else "read-only"
    return f"{dotted}  [{scope}, stock default {setting.default!r}: {stock}]"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument(
        "--check", action="store_true", help="report drift, exit 1 if any"
    )
    mode.add_argument(
        "--apply", action="store_true", help="write DESIRED to Cloudflare"
    )
    mode.add_argument("--dump", action="store_true", help="print live state, redacted")
    arguments = parser.parse_args()

    token = _token()
    account = _account(token)
    endpoint = f"/accounts/{account}/pages/projects/{PROJECT}"
    project = _call(endpoint, token)

    if arguments.dump:
        print(json.dumps(_redact(project), indent=2, sort_keys=True))
        return 0

    matched, drifted = _diff(project)

    for setting in matched:
        print(f"ok    {_describe(setting)} = {setting.desired!r}")
    for setting, live in drifted:
        shown = "<absent>" if live is KeyError else repr(live)
        print(
            f"DRIFT {_describe(setting)}\n        live={shown} want={setting.desired!r}"
        )
        print(f"        {setting.why}")

    if not drifted:
        print("\nNo drift. Cloudflare matches what this repository declares.")
        return 0

    writable = [(s, v) for s, v in drifted if s.managed]
    readonly = [(s, v) for s, v in drifted if not s.managed]

    if readonly:
        print(
            f"\n{len(readonly)} drifted setting(s) are read-only here and must be "
            "changed in the dashboard. See docs/infrastructure.md."
        )

    if arguments.check:
        print(f"\n{len(drifted)} drifted setting(s).")
        return 1

    if not writable:
        print("\nNothing to apply: every drifted setting is read-only.")
        return 1

    body: dict = {}
    for setting, _ in writable:
        _merge(body, _nest(setting.path, setting.desired))
    _call(endpoint, token, method="PATCH", body=body)
    print(f"\nApplied {len(writable)} setting(s).")
    return 1 if readonly else 0


if __name__ == "__main__":
    sys.exit(main())
