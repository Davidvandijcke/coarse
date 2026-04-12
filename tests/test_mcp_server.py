"""Tests for deploy/mcp_server.py.

These tests exercise the MCP server's tool functions directly as plain
Python calls (the FastMCP decorator leaves the underlying callable intact).
Extraction + structure parsing are mocked so the tests run offline — we
don't need litellm, Mistral OCR, or a live Supabase instance. The in-memory
``PaperStore`` backend is used throughout.

What we verify here:

- ``upload_paper_url`` save/restores the OpenRouter env var (critical:
  the worker reuses containers across calls, and a leaked key would let
  review N+1 charge review N's wallet).
- ``upload_paper_bytes`` rejects unsupported extensions and oversize files.
- ``get_paper_section`` returns the requested section, including
  ``next_section_id`` / ``has_next`` iteration hints.
- ``get_review_prompt`` returns non-empty ``system``/``user`` strings for
  every stage (overview / section / crossref / critique) and the JSON
  response schema.
- ``verify_quotes`` drops comments whose quote is not a fuzzy substring
  of the stored paper markdown.
- ``finalize_review`` writes a review and returns a stable review URL.
- Paper lookup raises a clear error when ``paper_id`` is unknown.
"""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

import pytest

from coarse.types import (
    DetailedComment,
    OverviewFeedback,
    OverviewIssue,
    PaperStructure,
    PaperText,
    SectionInfo,
    SectionType,
)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "deploy"))

import mcp_server  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_structure() -> PaperStructure:
    """A plausible two-section PaperStructure for verify/finalize tests."""
    return PaperStructure(
        title="A Test Paper on Quote Verification",
        domain="social_sciences/economics",
        taxonomy="academic/research_paper",
        abstract="We study quote verification behavior in reviews.",
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text=(
                    "We introduce a new estimator for the conditional mean. "
                    "The estimator is consistent under mild regularity "
                    "conditions. Our main contribution is a central limit "
                    "theorem that holds without cross-section independence."
                ),
                section_type=SectionType.INTRODUCTION,
            ),
            SectionInfo(
                number=2,
                title="Methodology",
                text=(
                    "The estimator is defined as the solution to a moment "
                    "condition. We assume the moment function is continuously "
                    "differentiable. Theorem 1 establishes asymptotic "
                    "normality under these assumptions."
                ),
                section_type=SectionType.METHODOLOGY,
                math_content=True,
            ),
        ],
    )


def _fake_paper_text(structure: PaperStructure) -> PaperText:
    md = "\n\n".join(f"# {s.title}\n\n{s.text}" for s in structure.sections)
    return PaperText(full_markdown=md, token_estimate=len(md) // 4)


@pytest.fixture(autouse=True)
def _fresh_store():
    """Reset the module-level in-memory store between tests."""
    original = mcp_server._STORE
    mcp_server._STORE = mcp_server.InMemoryStore()
    try:
        yield mcp_server._STORE
    finally:
        mcp_server._STORE = original


@pytest.fixture
def _mock_extraction(monkeypatch):
    """Replace ``_run_extraction`` with a pre-built structure so tests don't
    need litellm / Mistral OCR / network.
    """
    structure = _fake_structure()
    paper_text = _fake_paper_text(structure)

    def fake_run_extraction(file_path):
        # File must still exist when ingest unlinks it afterward
        assert file_path.exists(), "temp file disappeared before extraction ran"
        return paper_text, structure

    monkeypatch.setattr(mcp_server, "_run_extraction", fake_run_extraction)
    return structure, paper_text


# ---------------------------------------------------------------------------
# scoped_openrouter_key
# ---------------------------------------------------------------------------


def test_scoped_openrouter_key_restores_original(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "original-key")
    with mcp_server.scoped_openrouter_key("user-key"):
        import os

        assert os.environ["OPENROUTER_API_KEY"] == "user-key"
    import os

    assert os.environ["OPENROUTER_API_KEY"] == "original-key"


def test_scoped_openrouter_key_clears_when_no_original(monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    with mcp_server.scoped_openrouter_key("user-key"):
        import os

        assert os.environ["OPENROUTER_API_KEY"] == "user-key"
    import os

    assert "OPENROUTER_API_KEY" not in os.environ


def test_scoped_openrouter_key_restores_on_exception(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "original")
    with pytest.raises(RuntimeError, match="boom"):
        with mcp_server.scoped_openrouter_key("leaky"):
            raise RuntimeError("boom")
    import os

    assert os.environ["OPENROUTER_API_KEY"] == "original"


def test_scoped_openrouter_key_rejects_empty():
    with pytest.raises(ValueError, match="non-empty"):
        with mcp_server.scoped_openrouter_key(""):
            pass
    with pytest.raises(ValueError, match="non-empty"):
        with mcp_server.scoped_openrouter_key("   "):
            pass


# ---------------------------------------------------------------------------
# upload_paper_bytes
# ---------------------------------------------------------------------------


def test_upload_paper_bytes_happy_path(_mock_extraction):
    structure, _ = _mock_extraction
    data_b64 = base64.b64encode(b"%PDF-1.4\nfake pdf bytes").decode()
    result = mcp_server.upload_paper_bytes(
        filename="paper.pdf",
        data_b64=data_b64,
        openrouter_key="sk-or-v1-test",
    )

    assert result["title"] == structure.title
    assert result["section_count"] == 2
    assert len(result["sections"]) == 2
    assert {s["id"] for s in result["sections"]} == {"1", "2"}
    assert result["sections"][1]["math_content"] is True
    assert "next_step" in result

    # Paper should be retrievable by returned paper_id
    row = mcp_server._STORE.get_paper(result["paper_id"])
    assert row is not None
    assert row["title"] == structure.title


def test_upload_paper_bytes_rejects_bad_extension():
    with pytest.raises(ValueError, match="filename must have"):
        mcp_server.upload_paper_bytes(
            filename="paper.exe",
            data_b64=base64.b64encode(b"nope").decode(),
            openrouter_key="sk-or-v1-test",
        )


def test_upload_paper_bytes_rejects_oversize_file():
    big = b"x" * (mcp_server._MAX_PAPER_BYTES + 1)
    with pytest.raises(ValueError, match="cap"):
        mcp_server.upload_paper_bytes(
            filename="paper.pdf",
            data_b64=base64.b64encode(big).decode(),
            openrouter_key="sk-or-v1-test",
        )


def test_upload_paper_bytes_rejects_bad_base64():
    with pytest.raises(ValueError, match="base64"):
        mcp_server.upload_paper_bytes(
            filename="paper.pdf",
            data_b64="not$valid$base64$$",
            openrouter_key="sk-or-v1-test",
        )


def test_upload_paper_bytes_saves_and_restores_env(monkeypatch, _mock_extraction):
    """The user's key must not leak into subsequent calls."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "worker-default")
    data_b64 = base64.b64encode(b"%PDF-1.4\n...").decode()

    mcp_server.upload_paper_bytes(
        filename="paper.pdf",
        data_b64=data_b64,
        openrouter_key="sk-or-v1-user",
    )

    import os

    assert os.environ["OPENROUTER_API_KEY"] == "worker-default"


# ---------------------------------------------------------------------------
# upload_paper_url
# ---------------------------------------------------------------------------


def _make_fake_fetch(_mock_extraction, ext: str = ".pdf"):
    def _fake(url):
        # Create a real temp file so the ingest body's unlink doesn't fail
        import tempfile

        tmp = tempfile.NamedTemporaryFile(suffix=ext, delete=False)
        tmp.write(b"%PDF-1.4\nfake bytes")
        tmp.close()
        return Path(tmp.name)

    return _fake


def test_upload_paper_url_happy_path(monkeypatch, _mock_extraction):
    monkeypatch.setattr(mcp_server, "_fetch_to_tempfile", _make_fake_fetch(_mock_extraction))
    result = mcp_server.upload_paper_url(
        url="https://example.com/paper.pdf",
        openrouter_key="sk-or-v1-test",
    )
    assert result["paper_id"]
    assert result["section_count"] == 2


def test_fetch_to_tempfile_rejects_non_http():
    with pytest.raises(ValueError, match="http"):
        mcp_server._fetch_to_tempfile("ftp://example.com/paper.pdf")


def test_fetch_to_tempfile_rejects_bad_extension():
    with pytest.raises(ValueError, match="one of"):
        mcp_server._fetch_to_tempfile("https://example.com/paper.exe")


# ---------------------------------------------------------------------------
# get_paper_section
# ---------------------------------------------------------------------------


def test_get_paper_section_returns_full_text(_mock_extraction):
    data_b64 = base64.b64encode(b"%PDF-1.4\n").decode()
    upload = mcp_server.upload_paper_bytes(
        filename="paper.pdf", data_b64=data_b64, openrouter_key="sk-or-v1-test"
    )
    paper_id = upload["paper_id"]

    result = mcp_server.get_paper_section(paper_id=paper_id, section_id="1")
    assert result["number"] == 1
    assert result["title"] == "Introduction"
    assert "conditional mean" in result["text"]
    assert result["has_next"] is True
    assert result["next_section_id"] == "2"

    last = mcp_server.get_paper_section(paper_id=paper_id, section_id="2")
    assert last["has_next"] is False
    assert last["next_section_id"] is None
    assert last["math_content"] is True


def test_get_paper_section_unknown_section(_mock_extraction):
    data_b64 = base64.b64encode(b"%PDF-1.4\n").decode()
    upload = mcp_server.upload_paper_bytes(
        filename="paper.pdf", data_b64=data_b64, openrouter_key="sk-or-v1-test"
    )
    with pytest.raises(ValueError, match="section_id"):
        mcp_server.get_paper_section(paper_id=upload["paper_id"], section_id="99")


def test_get_paper_section_unknown_paper_id():
    with pytest.raises(ValueError, match="not found"):
        mcp_server.get_paper_section(
            paper_id="00000000-0000-0000-0000-000000000000", section_id="1"
        )


# ---------------------------------------------------------------------------
# get_review_prompt
# ---------------------------------------------------------------------------


def _ingested_paper(_mock_extraction) -> str:
    data_b64 = base64.b64encode(b"%PDF-1.4\n").decode()
    up = mcp_server.upload_paper_bytes(
        filename="paper.pdf", data_b64=data_b64, openrouter_key="sk-or-v1-test"
    )
    return up["paper_id"]


def test_get_review_prompt_overview(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    result = mcp_server.get_review_prompt(paper_id=paper_id, stage="overview")
    assert result["stage"] == "overview"
    assert len(result["system"]) > 100
    assert len(result["user"]) > 100
    assert "conditional mean" in result["user"]  # full paper content embedded
    assert result["response_schema"]["required"] == ["issues"]


def test_get_review_prompt_section_picks_focus(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)

    # Section 2 is flagged math_content=True → focus=proof
    result = mcp_server.get_review_prompt(paper_id=paper_id, stage="section", section_id="2")
    # Section 2's text must appear in the user prompt
    assert "Theorem 1" in result["user"]
    assert result["response_schema"]["required"] == ["comments"]


def test_get_review_prompt_section_requires_id(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    with pytest.raises(ValueError, match="section_id"):
        mcp_server.get_review_prompt(paper_id=paper_id, stage="section")


def test_get_review_prompt_crossref_and_critique(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    overview = OverviewFeedback(
        issues=[OverviewIssue(title="Gap", body="Some gap in argument.")]
    ).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="Check this equation",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Equation appears correct but lacks justification.",
        ).model_dump()
    ]

    for stage in ("crossref", "critique"):
        result = mcp_server.get_review_prompt(
            paper_id=paper_id,
            stage=stage,
            overview=overview,
            comments=comments,
        )
        assert result["stage"] == stage
        assert "Check this equation" in result["user"]
        assert result["response_schema"]["required"] == ["comments"]


def test_get_review_prompt_crossref_requires_overview_and_comments(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    with pytest.raises(ValueError, match="overview"):
        mcp_server.get_review_prompt(paper_id=paper_id, stage="crossref")
    with pytest.raises(ValueError, match="comments"):
        mcp_server.get_review_prompt(
            paper_id=paper_id,
            stage="crossref",
            overview=OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump(),
        )


def test_get_review_prompt_unknown_stage(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    with pytest.raises(ValueError, match="unknown stage"):
        mcp_server.get_review_prompt(paper_id=paper_id, stage="freeform")


# ---------------------------------------------------------------------------
# verify_quotes
# ---------------------------------------------------------------------------


def test_verify_quotes_keeps_exact_and_drops_hallucinated(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    good_comment = DetailedComment(
        number=1,
        title="Good quote",
        quote="We introduce a new estimator for the conditional mean.",
        feedback="Reasonable motivation.",
    )
    bad_comment = DetailedComment(
        number=2,
        title="Hallucinated quote",
        quote="An entirely fabricated sentence that is not in the paper at all, "
        "with no relation to any actual passage in the text whatsoever.",
        feedback="The paper claims X but it really says Y.",
    )

    result = mcp_server.verify_quotes(
        paper_id=paper_id,
        comments=[good_comment.model_dump(), bad_comment.model_dump()],
    )

    assert result["kept_count"] == 1
    assert result["dropped_count"] == 1
    assert result["verified"][0]["title"] == "Good quote"
    assert result["dropped"][0]["title"] == "Hallucinated quote"
    assert result["dropped"][0]["fuzzy_ratio"] < 0.8


# ---------------------------------------------------------------------------
# finalize_review
# ---------------------------------------------------------------------------


def test_finalize_review_renders_and_persists(_mock_extraction, monkeypatch):
    monkeypatch.setenv("SITE_URL", "https://test.coarse.example")
    paper_id = _ingested_paper(_mock_extraction)

    overview = OverviewFeedback(
        summary="Short outline.",
        assessment="Interesting paper that mostly does what it claims.",
        issues=[OverviewIssue(title="Issue A", body="Body of issue A.")],
        recommendation="minor revision",
        revision_targets=["Clarify Theorem 1 assumptions."],
    )
    comments = [
        DetailedComment(
            number=42,  # intentional wrong number; finalize must renumber
            title="Proof of Theorem 1 is incomplete",
            quote="Theorem 1 establishes asymptotic normality under these assumptions.",
            feedback="The proof step from moment condition to CLT isn't shown.",
        )
    ]

    result = mcp_server.finalize_review(
        paper_id=paper_id,
        overview=overview.model_dump(),
        comments=[c.model_dump() for c in comments],
    )

    assert result["comment_count"] == 1
    assert result["review_url"].startswith("https://test.coarse.example/review/")
    assert "# " in result["markdown"]
    assert "Detailed Comments (1)" in result["markdown"]
    # Comment must have been renumbered to 1
    assert "### 1. Proof of Theorem 1" in result["markdown"]


def test_finalize_review_rejects_bad_overview(_mock_extraction):
    paper_id = _ingested_paper(_mock_extraction)
    with pytest.raises(ValueError, match="OverviewFeedback"):
        mcp_server.finalize_review(
            paper_id=paper_id,
            overview={"totally": "wrong"},
            comments=[],
        )


def test_finalize_review_uses_paper_id_as_review_id(_mock_extraction):
    """Regression: finalize_review must reuse paper_id so the web→MCP handoff
    updates the existing ``reviews`` row instead of orphaning it.
    """
    paper_id = _ingested_paper(_mock_extraction)
    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comment = DetailedComment(
        number=1,
        title="Moment-condition citation needed",
        quote="The estimator is defined as the solution to a moment condition.",
        feedback="Attribute to the GMM literature.",
    ).model_dump()

    result = mcp_server.finalize_review(paper_id=paper_id, overview=overview, comments=[comment])
    assert result["review_id"] == paper_id
    assert result["review_url"].endswith(f"/review/{paper_id}")


# ---------------------------------------------------------------------------
# upload_paper_path
# ---------------------------------------------------------------------------


def test_upload_paper_path_happy_path(_mock_extraction, tmp_path):
    """Reads a real file from disk and must NOT delete it afterwards."""
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"%PDF-1.4\nfake pdf bytes")

    result = mcp_server.upload_paper_path(path=str(paper), openrouter_key="sk-or-v1-test")
    assert result["title"]
    assert result["section_count"] == 2
    # File must still exist after ingest — user owns it
    assert paper.exists()


def test_upload_paper_path_rejects_relative():
    with pytest.raises(ValueError, match="absolute"):
        mcp_server.upload_paper_path(path="paper.pdf", openrouter_key="sk-or-v1-test")


def test_upload_paper_path_rejects_missing_file(tmp_path):
    missing = tmp_path / "nope.pdf"
    with pytest.raises(ValueError, match="not found"):
        mcp_server.upload_paper_path(path=str(missing), openrouter_key="sk-or-v1-test")


def test_upload_paper_path_rejects_bad_extension(tmp_path):
    bad = tmp_path / "paper.exe"
    bad.write_bytes(b"nope")
    with pytest.raises(ValueError, match="unsupported extension"):
        mcp_server.upload_paper_path(path=str(bad), openrouter_key="sk-or-v1-test")


def test_upload_paper_path_rejects_directory(tmp_path):
    with pytest.raises(ValueError, match="not a regular file"):
        mcp_server.upload_paper_path(path=str(tmp_path), openrouter_key="sk-or-v1-test")


def test_upload_paper_path_saves_and_restores_env(_mock_extraction, tmp_path, monkeypatch):
    """The user's key must not leak after upload_paper_path returns."""
    monkeypatch.setenv("OPENROUTER_API_KEY", "worker-default")
    paper = tmp_path / "paper.pdf"
    paper.write_bytes(b"%PDF-1.4\n")

    mcp_server.upload_paper_path(path=str(paper), openrouter_key="sk-or-v1-user")

    import os

    assert os.environ["OPENROUTER_API_KEY"] == "worker-default"


# ---------------------------------------------------------------------------
# load_paper_state (web→MCP handoff ingestion path)
# ---------------------------------------------------------------------------
#
# These tests verify that the capability-handoff ingestion tool used by
# coarse.vercel.app's "Review with my subscription" flow (a) downloads
# the pre-extracted state blob from a signed URL, (b) rehydrates it into
# the MCP server's in-memory store under the caller-supplied paper_id,
# and (c) surfaces clean errors on malformed state, HTTP failures, and
# URL-expiry cases.


def _make_state_blob(paper_id: str = "deadbeef-dead-beef-dead-beefdeadbeef") -> dict:
    """Build a plausible extracted state blob for the load_paper_state tests."""
    structure = _fake_structure()
    return {
        "title": structure.title,
        "domain": structure.domain,
        "taxonomy": structure.taxonomy,
        "abstract": structure.abstract,
        "paper_markdown": _fake_paper_text(structure).full_markdown,
        "structure_json": json.loads(structure.model_dump_json()),
    }


def test_load_paper_state_happy_path(monkeypatch):
    import json as _json

    paper_id = "11111111-2222-3333-4444-555555555555"
    blob = _make_state_blob(paper_id)
    blob_bytes = _json.dumps(blob).encode("utf-8")

    class _FakeResp:
        ok = True
        status_code = 200
        content = blob_bytes

        def json(self):
            return blob

    captured: dict = {}

    def fake_get(url, timeout, headers):
        captured["url"] = url
        captured["timeout"] = timeout
        captured["headers"] = headers
        return _FakeResp()

    import requests as _requests

    monkeypatch.setattr(_requests, "get", fake_get)

    result = mcp_server.load_paper_state(
        signed_state_url="https://sb.example/sign/papers/x.mcp.json?token=abc",
        paper_id=paper_id,
    )
    assert result["paper_id"] == paper_id
    assert result["section_count"] == 2
    assert len(result["sections"]) == 2
    assert result["title"] == blob["title"]
    assert captured["url"].startswith("https://")

    # And the state lives in the store keyed by the caller's paper_id
    row = mcp_server._STORE.get_paper(paper_id)
    assert row is not None
    assert row["title"] == blob["title"]

    # Downstream tools should now work against this paper_id.
    sec = mcp_server.get_paper_section(paper_id=paper_id, section_id="1")
    assert "conditional mean" in sec["text"]


def test_load_paper_state_rejects_non_uuid_paper_id(monkeypatch):
    import requests as _requests

    # Shouldn't even fetch — validation fails first.
    def fail_get(*_a, **_k):
        raise AssertionError("fetch should not happen for bad paper_id")

    monkeypatch.setattr(_requests, "get", fail_get)
    with pytest.raises(ValueError, match="UUID"):
        mcp_server.load_paper_state(
            signed_state_url="https://example.com/x.mcp.json",
            paper_id="not-a-uuid",
        )


def test_load_paper_state_rejects_non_http_url():
    with pytest.raises(ValueError, match="http"):
        mcp_server.load_paper_state(
            signed_state_url="file:///tmp/leak.json",
            paper_id="11111111-2222-3333-4444-555555555555",
        )


def test_load_paper_state_network_error(monkeypatch):
    import requests as _requests

    def fake_get(*_a, **_k):
        raise _requests.ConnectionError("dns failure")

    monkeypatch.setattr(_requests, "get", fake_get)
    with pytest.raises(RuntimeError, match="Failed to GET"):
        mcp_server.load_paper_state(
            signed_state_url="https://sb.example/x.mcp.json",
            paper_id="11111111-2222-3333-4444-555555555555",
        )


def test_load_paper_state_http_error(monkeypatch):
    class _FakeResp:
        ok = False
        status_code = 410
        text = "expired"

    import requests as _requests

    monkeypatch.setattr(_requests, "get", lambda *a, **k: _FakeResp())
    with pytest.raises(RuntimeError, match="HTTP 410"):
        mcp_server.load_paper_state(
            signed_state_url="https://sb.example/x.mcp.json",
            paper_id="11111111-2222-3333-4444-555555555555",
        )


def test_load_paper_state_malformed_blob(monkeypatch):
    import json as _json

    bad_blob = {"title": "only a title", "paper_markdown": "something"}
    bad_bytes = _json.dumps(bad_blob).encode()

    class _FakeResp:
        ok = True
        status_code = 200
        content = bad_bytes

        def json(self):
            return bad_blob

    import requests as _requests

    monkeypatch.setattr(_requests, "get", lambda *a, **k: _FakeResp())

    with pytest.raises(ValueError, match="missing required fields"):
        mcp_server.load_paper_state(
            signed_state_url="https://sb.example/x.mcp.json",
            paper_id="11111111-2222-3333-4444-555555555555",
        )


# ---------------------------------------------------------------------------
# finalize_review — callback mode (capability handoff to Next.js backend)
# ---------------------------------------------------------------------------
#
# These tests verify that when the host LLM passes ``finalize_token`` +
# ``callback_url`` to ``finalize_review``, the MCP server POSTs the
# rendered review to the supplied URL and returns whatever ``review_url``
# the callback responded with. The point is that the MCP server must
# NEVER touch Supabase directly — all persistence flows through the
# Next.js /api/mcp-finalize route, which holds the real service key.


def test_finalize_review_in_memory_mode_still_works(_mock_extraction, monkeypatch):
    """Without finalize_token + callback_url, falls back to in-memory store."""
    monkeypatch.setenv("SITE_URL", "https://in-memory.test")
    paper_id = _ingested_paper(_mock_extraction)

    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="In-memory path",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Cite GMM.",
        ).model_dump()
    ]

    result = mcp_server.finalize_review(
        paper_id=paper_id,
        overview=overview,
        comments=comments,
    )
    assert result["review_id"] == paper_id
    assert result["review_url"] == f"https://in-memory.test/review/{paper_id}"
    # The in-memory store should now have the review.
    store_reviews = getattr(mcp_server._STORE, "_reviews", None)
    assert store_reviews is not None and paper_id in store_reviews


def test_finalize_review_rejects_partial_callback_args(_mock_extraction):
    """Token + url must come as a pair — passing only one is a caller bug."""
    paper_id = _ingested_paper(_mock_extraction)
    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="Partial args",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Half a handoff is a bug.",
        ).model_dump()
    ]
    with pytest.raises(ValueError, match="requires both finalize_token"):
        mcp_server.finalize_review(
            paper_id=paper_id,
            overview=overview,
            comments=comments,
            finalize_token="deadbeef",
            # callback_url intentionally omitted
        )
    with pytest.raises(ValueError, match="requires both finalize_token"):
        mcp_server.finalize_review(
            paper_id=paper_id,
            overview=overview,
            comments=comments,
            # finalize_token intentionally omitted
            callback_url="https://example.test/api/mcp-finalize",
        )


def test_finalize_review_callback_mode_posts_to_url(_mock_extraction, monkeypatch):
    """The callback mode POSTs the right payload and returns review_url from the response."""
    paper_id = _ingested_paper(_mock_extraction)

    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="Callback mode",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Fine.",
        ).model_dump()
    ]

    captured: dict = {}

    class _FakeResp:
        ok = True
        status_code = 200

        def json(self):
            return {
                "review_id": paper_id,
                "review_url": f"https://callback.test/review/{paper_id}",
            }

    def fake_post(url, json, timeout, headers):
        captured["url"] = url
        captured["json"] = json
        captured["timeout"] = timeout
        captured["headers"] = headers
        return _FakeResp()

    import requests as _requests

    monkeypatch.setattr(_requests, "post", fake_post)

    result = mcp_server.finalize_review(
        paper_id=paper_id,
        overview=overview,
        comments=comments,
        finalize_token="tok-deadbeef",
        callback_url="https://callback.test/api/mcp-finalize",
    )

    assert result["review_url"] == f"https://callback.test/review/{paper_id}"
    assert result["review_id"] == paper_id
    assert result["comment_count"] == 1
    # Payload sanity checks
    assert captured["url"] == "https://callback.test/api/mcp-finalize"
    assert captured["json"]["token"] == "tok-deadbeef"
    assert captured["json"]["paper_id"] == paper_id
    assert "Callback mode" in captured["json"]["markdown"]
    assert captured["json"]["paper_title"]


def test_finalize_review_callback_propagates_http_error(_mock_extraction, monkeypatch):
    """A non-2xx from the callback must raise so the host sees the failure."""
    paper_id = _ingested_paper(_mock_extraction)
    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="HTTP error",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Server returned 401.",
        ).model_dump()
    ]

    class _FakeResp:
        ok = False
        status_code = 401
        text = '{"error":"Token expired"}'

        def json(self):
            return {"error": "Token expired"}

    def fake_post(url, json, timeout, headers):
        return _FakeResp()

    import requests as _requests

    monkeypatch.setattr(_requests, "post", fake_post)

    with pytest.raises(RuntimeError, match="HTTP 401.*Token expired"):
        mcp_server.finalize_review(
            paper_id=paper_id,
            overview=overview,
            comments=comments,
            finalize_token="tok-dead",
            callback_url="https://callback.test/api/mcp-finalize",
        )


def test_finalize_review_callback_propagates_network_error(_mock_extraction, monkeypatch):
    """Network errors during POST must raise with a clear message."""
    paper_id = _ingested_paper(_mock_extraction)
    overview = OverviewFeedback(issues=[OverviewIssue(title="x", body="y")]).model_dump()
    comments = [
        DetailedComment(
            number=1,
            title="Network error",
            quote="The estimator is defined as the solution to a moment condition.",
            feedback="Network said no.",
        ).model_dump()
    ]

    import requests as _requests

    def fake_post(url, json, timeout, headers):
        raise _requests.ConnectionError("dns failure")

    monkeypatch.setattr(_requests, "post", fake_post)

    with pytest.raises(RuntimeError, match="network layer"):
        mcp_server.finalize_review(
            paper_id=paper_id,
            overview=overview,
            comments=comments,
            finalize_token="tok-dead",
            callback_url="https://callback.test/api/mcp-finalize",
        )


# ---------------------------------------------------------------------------
# Module wiring
# ---------------------------------------------------------------------------


def test_mcp_tools_registered():
    """All 8 tools should be discoverable via the FastMCP server.

    The ``upload_paper_from_id`` tool was deliberately removed when the
    server moved to a capability-based auth model: web→MCP handoffs now
    flow through /api/mcp-handoff → signed URL → load_paper_state, so
    the server never needs a Supabase service key.

    Direct-drive tools (upload_paper_url / _bytes / _path) remain for
    CLI and Claude-Code users who drive the server without the web
    form in front of them.
    """
    import asyncio

    tools = asyncio.run(mcp_server.mcp.list_tools())
    names = {t.name for t in tools}
    assert names == {
        "upload_paper_url",
        "upload_paper_bytes",
        "upload_paper_path",
        "load_paper_state",
        "get_paper_section",
        "get_review_prompt",
        "verify_quotes",
        "finalize_review",
    }
    assert "upload_paper_from_id" not in names
