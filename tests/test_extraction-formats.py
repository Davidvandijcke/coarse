"""Tests for coarse.extraction_formats."""

from __future__ import annotations

import builtins
import sys
import types
from pathlib import Path

import pytest

from coarse.extraction_formats import (
    _extract_docx_mammoth,
    _extract_epub,
    _extract_html_markdownify,
    _extract_latex_regex,
)
from coarse.types import ExtractionError


def test_extract_latex_regex_converts_headings_and_strips_preamble(tmp_path: Path) -> None:
    tex = tmp_path / "paper.tex"
    tex.write_text(
        "\\documentclass{article}\n"
        "\\title{Ignored}\n"
        "\\begin{document}\n"
        "\\section{Intro}\n"
        "Body text.\n"
        "\\subsection{Details}\n"
        "More text.\n"
        "\\end{document}\n"
    )

    result = _extract_latex_regex(tex)

    assert "\\documentclass" not in result
    assert "# Intro" in result
    assert "## Details" in result
    assert "Body text." in result


def test_extract_html_markdownify_converts_html(tmp_path: Path, monkeypatch) -> None:
    html = tmp_path / "paper.html"
    html.write_text("<h1>Intro</h1><p>Body</p>", encoding="utf-8")
    markdownify = types.ModuleType("markdownify")
    markdownify.markdownify = lambda text, heading_style="ATX": "# Intro\n\nBody"
    monkeypatch.setitem(sys.modules, "markdownify", markdownify)

    assert _extract_html_markdownify(html) == "# Intro\n\nBody"


def test_extract_html_markdownify_missing_dependency_raises(tmp_path: Path, monkeypatch) -> None:
    html = tmp_path / "paper.html"
    html.write_text("<p>Body</p>", encoding="utf-8")
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "markdownify":
            raise ImportError("missing markdownify")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ExtractionError, match="markdownify"):
        _extract_html_markdownify(html)


def test_extract_docx_mammoth_converts_docx(tmp_path: Path, monkeypatch) -> None:
    docx = tmp_path / "paper.docx"
    docx.write_bytes(b"docx")
    mammoth = types.ModuleType("mammoth")
    mammoth.convert_to_markdown = lambda handle: types.SimpleNamespace(value="# Converted")
    monkeypatch.setitem(sys.modules, "mammoth", mammoth)

    assert _extract_docx_mammoth(docx) == "# Converted"


def test_extract_docx_mammoth_missing_dependency_raises(tmp_path: Path, monkeypatch) -> None:
    docx = tmp_path / "paper.docx"
    docx.write_bytes(b"docx")
    real_import = builtins.__import__

    def fake_import(name, *args, **kwargs):
        if name == "mammoth":
            raise ImportError("missing mammoth")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    with pytest.raises(ExtractionError, match="mammoth"):
        _extract_docx_mammoth(docx)


def test_extract_epub_converts_document_items(tmp_path: Path, monkeypatch) -> None:
    epub_path = tmp_path / "paper.epub"
    epub_path.write_bytes(b"epub")

    class FakeItem:
        def __init__(self, content: str):
            self._content = content

        def get_content(self) -> bytes:
            return self._content.encode("utf-8")

    class FakeBook:
        def get_items_of_type(self, item_type: int):
            assert item_type == 7
            return [FakeItem("<h1>Chapter</h1><p>Body</p>")]

    ebooklib = types.ModuleType("ebooklib")
    ebooklib.ITEM_DOCUMENT = 7
    epub = types.ModuleType("ebooklib.epub")
    epub.read_epub = lambda path: FakeBook()
    ebooklib.epub = epub
    markdownify = types.ModuleType("markdownify")
    markdownify.markdownify = lambda text, heading_style="ATX": "# Chapter\n\nBody"
    monkeypatch.setitem(sys.modules, "ebooklib", ebooklib)
    monkeypatch.setitem(sys.modules, "ebooklib.epub", epub)
    monkeypatch.setitem(sys.modules, "markdownify", markdownify)

    assert _extract_epub(epub_path) == "# Chapter\n\nBody"


def test_extract_epub_raises_when_no_text_content(tmp_path: Path, monkeypatch) -> None:
    epub_path = tmp_path / "paper.epub"
    epub_path.write_bytes(b"epub")

    class FakeBook:
        def get_items_of_type(self, item_type: int):
            return []

    ebooklib = types.ModuleType("ebooklib")
    ebooklib.ITEM_DOCUMENT = 7
    epub = types.ModuleType("ebooklib.epub")
    epub.read_epub = lambda path: FakeBook()
    ebooklib.epub = epub
    markdownify = types.ModuleType("markdownify")
    markdownify.markdownify = lambda text, heading_style="ATX": ""
    monkeypatch.setitem(sys.modules, "ebooklib", ebooklib)
    monkeypatch.setitem(sys.modules, "ebooklib.epub", epub)
    monkeypatch.setitem(sys.modules, "markdownify", markdownify)

    with pytest.raises(ExtractionError, match="No text content found in EPUB"):
        _extract_epub(epub_path)
