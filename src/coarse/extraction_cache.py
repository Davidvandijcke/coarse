"""Cache helpers for extracted paper text."""

from __future__ import annotations

import json
import logging
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
    try:
        cache.write_text(
            paper_text.model_dump_json(indent=None),
            encoding="utf-8",
        )
        cache.chmod(0o600)
        size_kb = cache.stat().st_size / 1024
        logger.info("Saved extraction cache (%.1f KB) to %s", size_kb, cache.name)
    except Exception:
        logger.warning("Failed to write extraction cache, continuing without cache")
