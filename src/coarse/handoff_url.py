"""Parse subscription handoff URLs copied through chat applications."""

from __future__ import annotations

import argparse
import re
from urllib.parse import urlsplit


def normalize_handoff_url(value: str) -> str:
    """Remove chat presentation wrappers without changing the URL destination."""
    url = value.strip()
    if url.startswith("`") and url.endswith("`"):
        url = url[1:-1].strip()
    link = re.fullmatch(r"\[[^\]\r\n]*\]\((https?://[^\s<>]+|<https?://[^\s<>]+>)\)", url)
    if link:
        url = link.group(1)
    if url.startswith("<") and url.endswith(">"):
        url = url[1:-1]
    if "://" not in url:
        url = f"https://{url}"
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme in ("http", "https")
            and bool(parsed.hostname)
            and not any(c.isspace() or c in "<>`\\" for c in url)
            and not any(c in parsed.netloc for c in "()")
        )
        # Accessing port also validates malformed/non-numeric port strings.
        parsed.port
    except ValueError:
        valid = False
    if not valid:
        # Never echo the input: preview URLs can contain access credentials.
        raise ValueError("--handoff requires a valid HTTP(S) URL or a Markdown link to one")
    return url


def handoff_url_argument(value: str) -> str:
    """Expose validation to argparse without echoing credentials in its error."""
    try:
        return normalize_handoff_url(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc
