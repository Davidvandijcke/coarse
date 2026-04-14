"""Cache helpers for extracted paper text."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from coarse.types import PaperText

logger = logging.getLogger(__name__)


def _cache_path(pdf_path: Path) -> Path:
    """Return the cache file path for a given extracted document."""
    return pdf_path.with_suffix(".extraction_cache.json")


def _load_cache(pdf_path: Path) -> PaperText | None:
    """Load cached extraction if it exists and is newer than the source file."""
    cache = _cache_path(pdf_path)
    if not cache.exists():
        return None
    if cache.stat().st_mtime < pdf_path.stat().st_mtime:
        logger.info("Cache stale (source modified since cache), re-extracting")
        return None
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        paper_text = PaperText.model_validate(data)
        logger.info("Loaded extraction cache from %s", cache.name)
        return paper_text
    except Exception:
        logger.warning("Cache corrupt, re-extracting")
        return None


def _save_cache(pdf_path: Path, paper_text: PaperText) -> None:
    """Save extraction result to a cache file next to the source document."""
    cache = _cache_path(pdf_path)
    if cache.is_symlink():
        logger.warning("Cache path %s is a symlink, refusing to write", cache)
        return
    payload = paper_text.model_dump_json(indent=None).encode("utf-8")
    try:
        # Create with 0o600 from the start so the file never exists on disk
        # under umask-default permissions. Windows ignores the mode bits, so
        # fall back to a plain write there (no POSIX ACL to worry about).
        if os.name == "nt":
            cache.write_bytes(payload)
        else:
            fd = os.open(cache, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
            try:
                os.fchmod(fd, 0o600)
            except OSError:
                pass
            with os.fdopen(fd, "wb") as f:
                f.write(payload)
            try:
                cache.chmod(0o600)
            except OSError:
                pass
        size_kb = cache.stat().st_size / 1024
        logger.info("Saved extraction cache (%.1f KB) to %s", size_kb, cache.name)
    except Exception:
        logger.warning("Failed to write extraction cache, continuing without cache")
