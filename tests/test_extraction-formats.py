"""Tests for coarse.extraction_formats."""

from __future__ import annotations

from pathlib import Path

from coarse.extraction_formats import _extract_latex_regex


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
