"""Tests for the standalone coarse-review handoff wrapper."""

from __future__ import annotations

from unittest.mock import patch

from coarse.cli_review import _infer_handoff_extension, main
from coarse.types import OverviewFeedback, OverviewIssue, PaperText, Review


def _make_review() -> Review:
    return Review(
        title="Targeting Interventions in Networks",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        date="04/12/2026",
        overall_feedback=OverviewFeedback(
            issues=[OverviewIssue(title=f"Issue {i}", body=f"Body {i}.") for i in range(1, 5)]
        ),
        detailed_comments=[],
    )


def test_infer_handoff_extension_prefers_supported_title_suffix() -> None:
    assert (
        _infer_handoff_extension(
            paper_title="paper.md",
            signed_url="https://example.test/storage/papers/123.pdf?token=abc",
            content_type="application/pdf",
        )
        == ".md"
    )


def test_infer_handoff_extension_uses_content_type_fallback() -> None:
    assert (
        _infer_handoff_extension(
            paper_title="paper",
            signed_url="https://example.test/download/no-extension",
            content_type="text/markdown; charset=utf-8",
        )
        == ".md"
    )


def test_main_handoff_supports_markdown_source(tmp_path) -> None:
    """Handoff mode should preserve non-PDF extensions for direct extraction."""
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }
    captured: dict[str, object] = {}

    def fake_run_headless_review(paper_path, **kwargs):
        captured["paper_path"] = paper_path
        captured["kwargs"] = kwargs
        return _make_review(), "# Review\n", PaperText(full_markdown="# Paper\n", token_estimate=2)

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch("coarse.headless_review.run_headless_review", side_effect=fake_run_headless_review),
        patch(
            "coarse.cli_review._post_finalize",
            return_value={"review_url": "https://example.test/review/123"},
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--model",
                "gpt-5.4",
                "--effort",
                "high",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    assert captured["paper_path"] == source
    assert captured["kwargs"] == {
        "host": "codex",
        "model": "gpt-5.4",
        "effort": "high",
        "pre_extracted": None,
    }
    assert (out_dir / "paper_review.md").read_text(encoding="utf-8") == "# Review\n"


def test_main_handoff_success_prints_absolute_local_and_view_lines(tmp_path, capsys) -> None:
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(
                _make_review(),
                "# Review\n",
                PaperText(full_markdown="# Paper\n", token_estimate=2),
            ),
        ),
        patch(
            "coarse.cli_review._post_finalize",
            return_value={"review_url": "https://example.test/review/123"},
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    stdout = capsys.readouterr().out
    assert "PUBLISHED TO COARSE WEB" in stdout
    assert "  view:     https://example.test/review/123" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout
    assert "REVIEW COMPLETE" in stdout


def test_main_handoff_callback_failure_still_prints_local_footer(tmp_path, capsys) -> None:
    source = tmp_path / "paper.md"
    source.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"
    handoff_bundle = {
        "paper_id": "12345678-1234-1234-1234-123456789abc",
        "signed_download_url": "https://example.test/papers/123.md?token=abc",
        "finalize_token": "tok-123",
        "callback_url": "https://example.test/api/mcp-finalize",
        "paper_title": "paper.md",
        "domain": "",
        "taxonomy": "",
    }

    with (
        patch("coarse.cli_review._fetch_handoff", return_value=handoff_bundle),
        patch("coarse.cli_review._download_handoff_source", return_value=source),
        patch(
            "coarse.headless_review.run_headless_review",
            return_value=(
                _make_review(),
                "# Review\n",
                PaperText(full_markdown="# Paper\n", token_estimate=2),
            ),
        ),
        patch(
            "coarse.cli_review._post_finalize",
            side_effect=RuntimeError("Callback to https://example.test/api failed: HTTP 500"),
        ),
    ):
        rc = main(
            [
                "--handoff",
                "https://example.test/h/token",
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 7
    stdout = capsys.readouterr().out
    assert "WEB CALLBACK FAILED" in stdout
    assert "  view:     unavailable" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout
    assert "REVIEW COMPLETE" in stdout


def test_main_local_mode_prints_absolute_local_footer(tmp_path, capsys) -> None:
    paper = tmp_path / "paper.md"
    paper.write_text("# Paper\n", encoding="utf-8")
    out_dir = tmp_path / "out"

    with patch(
        "coarse.headless_review.run_headless_review",
        return_value=(
            _make_review(),
            "# Review\n",
            PaperText(full_markdown="# Paper\n", token_estimate=2),
        ),
    ):
        rc = main(
            [
                str(paper),
                "--host",
                "codex",
                "--output-dir",
                str(out_dir),
            ]
        )

    assert rc == 0
    stdout = capsys.readouterr().out
    assert "REVIEW COMPLETE" in stdout
    assert f"  local:    {(out_dir / 'paper_review.md').resolve()}" in stdout
