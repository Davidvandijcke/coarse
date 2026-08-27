"""Tests for coarse.extraction_cache."""

from __future__ import annotations

import os
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


def test_save_and_load_versioned_pdf_cache_roundtrip(tmp_path: Path) -> None:
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-1.4")
    cached = PaperText(full_markdown="# Paper", token_estimate=2, garble_ratio=0.0)

    _save_cache(source, cached)

    assert _load_cache(source) == cached


def test_load_cache_returns_none_when_source_is_newer(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")
    cached = PaperText(full_markdown="# Paper", token_estimate=2, garble_ratio=0.0)

    _save_cache(source, cached)
    cache = source.with_suffix(".extraction_cache.json")
    newer = cache.stat().st_mtime + 10
    os.utime(source, (newer, newer))

    assert _load_cache(source) is None


def test_load_cache_returns_none_for_corrupt_json(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")
    source.with_suffix(".extraction_cache.json").write_text("{not json", encoding="utf-8")

    assert _load_cache(source) is None


def test_load_cache_invalidates_legacy_unversioned_pdf(tmp_path: Path) -> None:
    """Caches that may contain blind QA corrections must be rebuilt once."""
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-1.4")
    source.with_suffix(".extraction_cache.json").write_text(
        '{"full_markdown":"# Paper","token_estimate":2,"garble_ratio":0.0}',
        encoding="utf-8",
    )

    assert _load_cache(source) is None


def test_load_cache_keeps_legacy_unversioned_non_pdf(tmp_path: Path) -> None:
    """The blind-QA path was PDF-only, so local-format caches stay reusable."""
    source = tmp_path / "paper.md"
    source.write_text("# Paper", encoding="utf-8")
    source.with_suffix(".extraction_cache.json").write_text(
        '{"full_markdown":"# Paper","token_estimate":2,"garble_ratio":0.0}',
        encoding="utf-8",
    )

    assert _load_cache(source) == PaperText(
        full_markdown="# Paper",
        token_estimate=2,
        garble_ratio=0.0,
    )


def test_load_cache_returns_none_for_empty_markdown(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")
    source.with_suffix(".extraction_cache.json").write_text(
        '{"full_markdown":"","token_estimate":0,"garble_ratio":0.0}',
        encoding="utf-8",
    )

    assert _load_cache(source) is None


def test_save_cache_skips_blank_extraction(tmp_path: Path) -> None:
    """#189: blank/whitespace extractions are never persisted — symmetric with
    the _load_cache empty-payload guard."""
    source = tmp_path / "paper.pdf"
    source.write_bytes(b"%PDF-1.4")

    _save_cache(source, PaperText(full_markdown="   \n\t", token_estimate=0, garble_ratio=0.0))

    assert not source.with_suffix(".extraction_cache.json").exists()


def test_save_cache_skips_symlink_path(tmp_path: Path) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")
    target = tmp_path / "target.json"
    target.write_text("original", encoding="utf-8")
    cache = source.with_suffix(".extraction_cache.json")
    cache.symlink_to(target)

    _save_cache(
        source,
        PaperText(full_markdown="# Paper", token_estimate=2, garble_ratio=0.0),
    )

    assert target.read_text(encoding="utf-8") == "original"


def test_save_cache_write_failure_is_swallowed(tmp_path: Path, monkeypatch) -> None:
    source = tmp_path / "paper.txt"
    source.write_text("hello")

    def boom(self: Path, *args, **kwargs) -> str:
        raise OSError("disk full")

    monkeypatch.setattr(Path, "write_text", boom)

    _save_cache(
        source,
        PaperText(full_markdown="# Paper", token_estimate=2, garble_ratio=0.0),
    )
