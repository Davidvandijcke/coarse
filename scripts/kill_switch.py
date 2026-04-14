#!/usr/bin/env python3
"""Operator helper for pausing or resuming new coarse submissions."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

REPO_ROOT = Path(__file__).resolve().parents[1]
WEB_ENV_PATH = REPO_ROOT / "web" / ".env.local"
DEFAULT_PAUSE_MESSAGE = (
    "Submissions are temporarily paused. Please try again later or use the CLI: "
    "pip install coarse-ink"
)


@dataclass(frozen=True)
class Config:
    supabase_url: str
    service_key: str


def load_env_file(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :]
        if "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
            value = value[1:-1]
        values[key] = value

    return values


def resolve_config(
    env: dict[str, str] | None = None,
    env_path: Path = WEB_ENV_PATH,
) -> Config:
    current_env = os.environ if env is None else env
    env_url = current_env.get("SUPABASE_URL", "").strip()
    env_key = current_env.get("SUPABASE_SERVICE_KEY", "").strip()

    if env_url or env_key:
        if not env_url or not env_key:
            raise RuntimeError(
                "Set both SUPABASE_URL and SUPABASE_SERVICE_KEY in the shell, "
                "or unset both and use web/.env.local."
            )
        return Config(supabase_url=env_url, service_key=env_key)

    file_values = load_env_file(env_path)
    file_url = file_values.get("NEXT_PUBLIC_SUPABASE_URL", "").strip()
    file_key = file_values.get("SUPABASE_SERVICE_KEY", "").strip()

    if not file_url or not file_key:
        raise RuntimeError(
            f"Could not load NEXT_PUBLIC_SUPABASE_URL and SUPABASE_SERVICE_KEY from {env_path}."
        )

    return Config(supabase_url=file_url, service_key=file_key)


def request_json(
    method: str,
    url: str,
    service_key: str,
    *,
    payload: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body, method=method.upper())
    request.add_header("apikey", service_key)
    request.add_header("Authorization", f"Bearer {service_key}")
    request.add_header("Accept", "application/json")
    if payload is not None:
        request.add_header("Content-Type", "application/json")
        request.add_header("Prefer", "return=representation")

    try:
        with urlopen(request) as response:
            raw = response.read().decode("utf-8")
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase request failed ({exc.code} {exc.reason}): {detail}") from exc
    except URLError as exc:
        raise RuntimeError(f"Supabase request failed: {exc.reason}") from exc

    data = json.loads(raw) if raw else []
    if not isinstance(data, list):
        raise RuntimeError(f"Unexpected response payload: {data!r}")
    return data


def system_status_url(supabase_url: str) -> str:
    return (
        f"{supabase_url.rstrip('/')}/rest/v1/system_status"
        "?id=eq.1&select=accepting_reviews,banner_message,updated_at"
    )


def get_status(config: Config) -> dict[str, Any]:
    rows = request_json("GET", system_status_url(config.supabase_url), config.service_key)
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one system_status row, got {len(rows)}.")
    return rows[0]


def set_paused(
    config: Config,
    *,
    accepting_reviews: bool,
    banner_message: str | None,
) -> dict[str, Any]:
    payload = {
        "accepting_reviews": accepting_reviews,
        "banner_message": banner_message,
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    rows = request_json(
        "PATCH",
        system_status_url(config.supabase_url),
        config.service_key,
        payload=payload,
    )
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one updated row, got {len(rows)}.")
    return rows[0]


def print_status(row: dict[str, Any]) -> None:
    state = "accepting" if row.get("accepting_reviews") else "paused"
    banner = row.get("banner_message") or "(none)"
    updated_at = row.get("updated_at") or "(unknown)"
    print(f"status: {state}")
    print(f"banner: {banner}")
    print(f"updated_at: {updated_at}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    pause_parser = subparsers.add_parser("pause", help="Pause new submissions")
    pause_parser.add_argument(
        "message",
        nargs="?",
        default=DEFAULT_PAUSE_MESSAGE,
        help="Banner message shown to users while paused",
    )
    subparsers.add_parser("resume", help="Resume new submissions")
    subparsers.add_parser("status", help="Show current kill-switch state")

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        config = resolve_config()
        if args.command == "pause":
            row = set_paused(
                config,
                accepting_reviews=False,
                banner_message=args.message,
            )
        elif args.command == "resume":
            row = set_paused(
                config,
                accepting_reviews=True,
                banner_message=None,
            )
        else:
            row = get_status(config)
    except Exception as exc:  # pragma: no cover - exercised via CLI
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print_status(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
