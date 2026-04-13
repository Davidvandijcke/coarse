"""Tests for coarse.extraction_cache."""

from __future__ import annotations

from pathlib import Path

from coarse.extraction_cache import _load_cache, _save_cache
from coarse.types import PaperText


def test_save_and_load_cache_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")
    cached = PaperText(full_markdown="# Paper", token_estimate=2, garble_ratio=0.0)

    _save_cache(source, cached)
    loaded = _load_cache(source)

    assert loaded == cached
