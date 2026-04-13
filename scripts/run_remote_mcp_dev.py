#!/usr/bin/env python3
"""Launch local Next.js dev against a remote coarse MCP endpoint.

This is the dev topology we need before production:

1. The coarse web app runs locally (`npm run dev` in `web/`).
2. A public tunnel points at that local web app, so a remote MCP worker can
   reach `/api/mcp-finalize`.
3. The MCP server itself runs remotely (Modal or another public host).

This helper validates the two public URLs, probes the remote MCP endpoint,
sets the right `NEXT_PUBLIC_*` environment variables, starts the local web
server, and optionally waits for the public tunnel URL to become reachable.
"""

from __future__ import annotations

import argparse
import ipaddress
import os
import signal
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import ParseResult, urlparse, urlunparse

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = REPO_ROOT / "web"


class ConfigError(ValueError):
    """Raised when the requested remote-dev topology is invalid."""


def is_public_host(host: str) -> bool:
    """Return True only for publicly reachable hosts.

    Reject localhost, private IPs, link-local IPs, and obvious local-only
    hostnames. This is intentionally conservative: the whole point of this
    setup is that a *remote* MCP worker must be able to call back into the
    local web app through a public tunnel.
    """

    lowered = host.strip().lower()
    if not lowered:
        return False
    if lowered in {"localhost", "127.0.0.1", "::1"}:
        return False
    if lowered.endswith(".local") or lowered.endswith(".internal"):
        return False

    try:
        addr = ipaddress.ip_address(lowered)
    except ValueError:
        return "." in lowered

    return not (
        addr.is_private
        or addr.is_loopback
        or addr.is_link_local
        or addr.is_reserved
        or addr.is_multicast
        or addr.is_unspecified
    )


def _validate_base_url(raw: str, *, name: str, require_public: bool) -> ParseResult:
    parsed = urlparse(raw.strip())
    if parsed.scheme not in {"http", "https"}:
        raise ConfigError(f"{name} must start with http:// or https://")
    if not parsed.netloc:
        raise ConfigError(f"{name} must be an absolute URL")
    if parsed.params or parsed.query or parsed.fragment:
        raise ConfigError(f"{name} must not include params, query strings, or fragments")
    if not parsed.hostname:
        raise ConfigError(f"{name} is missing a host")
    if require_public and not is_public_host(parsed.hostname):
        raise ConfigError(
            f"{name} must use a public host. "
            "For local web dev, expose localhost with a tunnel first."
        )
    if require_public and parsed.scheme != "https":
        raise ConfigError(f"{name} must use https when testing against a remote MCP worker")
    return parsed


def normalize_site_url(raw: str) -> str:
    """Normalize the public site origin the remote MCP worker will call back into."""

    parsed = _validate_base_url(raw, name="site URL", require_public=True)
    if parsed.path not in {"", "/"}:
        raise ConfigError("site URL must point at the site origin only, not a subpath")
    return urlunparse((parsed.scheme, parsed.netloc, "", "", "", "")).rstrip("/")


def normalize_mcp_url(raw: str) -> str:
    """Normalize a remote MCP endpoint to the canonical `/mcp/` URL."""

    parsed = _validate_base_url(raw, name="MCP URL", require_public=True)
    if parsed.path in {"", "/"}:
        path = "/mcp/"
    elif parsed.path in {"/mcp", "/mcp/"}:
        path = "/mcp/"
    else:
        raise ConfigError("MCP URL must point at the server root or the /mcp path")
    return urlunparse((parsed.scheme, parsed.netloc, path, "", "", ""))


def build_web_env(site_url: str, mcp_url: str) -> dict[str, str]:
    """Build the env overrides needed for local-web + remote-MCP dev."""

    return {
        "NEXT_PUBLIC_SITE_URL": site_url,
        "NEXT_PUBLIC_MCP_SERVER_URL": mcp_url,
    }


def probe_remote_mcp(mcp_url: str, *, timeout_seconds: float = 10.0) -> dict[str, object]:
    """GET the public MCP endpoint and confirm it looks like the coarse server."""

    response = requests.get(
        mcp_url,
        headers={"Accept": "application/json"},
        timeout=timeout_seconds,
    )
    response.raise_for_status()
    payload: dict[str, object]
    try:
        payload = response.json()
    except ValueError:
        payload = {}
    return {
        "status_code": response.status_code,
        "payload": payload,
    }


def wait_for_public_site(
    site_url: str,
    *,
    timeout_seconds: float = 75.0,
    interval_seconds: float = 2.0,
    session: requests.Session | requests.api = requests,
    process: subprocess.Popen[bytes] | subprocess.Popen[str] | None = None,
) -> int:
    """Poll the public tunnel URL until it reaches the local Next.js server."""

    deadline = time.monotonic() + timeout_seconds
    last_error = "no response yet"
    while time.monotonic() < deadline:
        if process is not None and process.poll() is not None:
            raise RuntimeError(
                f"Next.js dev server exited before the public site came up "
                f"(exit code {process.returncode})"
            )
        try:
            response = session.get(site_url, timeout=5.0)
            # 2xx/3xx/4xx all prove the tunnel reaches the app. 5xx usually
            # means the tunnel exists but the local app is not ready yet.
            if response.status_code < 500:
                return response.status_code
            last_error = f"HTTP {response.status_code}"
        except requests.RequestException as exc:
            last_error = str(exc)
        time.sleep(interval_seconds)
    raise RuntimeError(
        f"Public site URL did not become reachable within {timeout_seconds:.0f}s: {last_error}"
    )


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run local coarse web dev against a remote MCP server."
    )
    parser.add_argument(
        "--site-url",
        required=True,
        help="Public tunnel URL pointing at the local Next.js app (for example https://abc.trycloudflare.com)",
    )
    parser.add_argument(
        "--mcp-url",
        required=True,
        help="Remote coarse MCP URL (root or /mcp path).",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Validate/probe the URLs and print the env overrides without starting npm run dev.",
    )
    parser.add_argument(
        "--skip-site-probe",
        action="store_true",
        help="Do not wait for the public site URL after starting npm run dev.",
    )
    parser.add_argument(
        "--site-timeout",
        type=float,
        default=75.0,
        help="Seconds to wait for the public site URL to come up after starting npm run dev.",
    )
    parser.add_argument(
        "--mcp-timeout",
        type=float,
        default=10.0,
        help="Seconds to wait for the remote MCP probe request.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)

    try:
        site_url = normalize_site_url(args.site_url)
        mcp_url = normalize_mcp_url(args.mcp_url)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    try:
        mcp_probe = probe_remote_mcp(mcp_url, timeout_seconds=args.mcp_timeout)
    except requests.RequestException as exc:
        print(f"Remote MCP probe failed for {mcp_url}: {exc}", file=sys.stderr)
        return 1

    env_overrides = build_web_env(site_url, mcp_url)
    print("Remote MCP probe succeeded.")
    print(f"  MCP URL:  {mcp_url}")
    print(f"  Site URL: {site_url}")
    print(f"  Probe:    HTTP {mcp_probe['status_code']}")
    payload = mcp_probe.get("payload")
    if isinstance(payload, dict) and payload:
        server = payload.get("server")
        transport = payload.get("transport")
        if server or transport:
            print(f"  Server:   {server or 'unknown'} ({transport or 'unknown transport'})")

    print("\nEnv overrides:")
    for key, value in env_overrides.items():
        print(f"  {key}={value}")

    if args.check_only:
        print("\nDry run only. Launch the web app with:")
        print("  cd web && " + " ".join(f"{key}={value}" for key, value in env_overrides.items()))
        print("  npm run dev")
        return 0

    env = os.environ.copy()
    env.update(env_overrides)
    print(f"\nStarting Next.js dev server in {WEB_DIR} ...")
    proc = subprocess.Popen(["npm", "run", "dev"], cwd=WEB_DIR, env=env)

    try:
        if not args.skip_site_probe:
            status = wait_for_public_site(
                site_url,
                timeout_seconds=args.site_timeout,
                process=proc,
            )
            print(f"Public site URL is reachable (HTTP {status}).")
            print("You can now upload a paper locally and hand it off to the remote MCP.")
        return proc.wait()
    except KeyboardInterrupt:
        proc.send_signal(signal.SIGINT)
        return proc.wait()
    except Exception as exc:
        print(f"Startup verification failed: {exc}", file=sys.stderr)
        proc.send_signal(signal.SIGINT)
        return proc.wait()


if __name__ == "__main__":
    raise SystemExit(main())
