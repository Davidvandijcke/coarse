"""Tests for coarse.agent.tools."""

from __future__ import annotations

import pytest

from coarse.agent.tools import MAX_SEARCH_HITS, ToolBox, finding_from_payload, tool_schemas
from coarse.agent.workspace import ReviewWorkspace
from coarse.types import PaperStructure, SectionInfo, SectionType

INTRO = "We introduce stable selection. " * 30
PROOF = "Definition 2 requires a high-probability set. The needle is here. " * 30


def _structure() -> PaperStructure:
    return PaperStructure(
        title="A Paper",
        domain="statistics",
        taxonomy="academic/research_paper",
        abstract="An abstract.",
        sections=[
            SectionInfo(
                number=1, title="Introduction", text=INTRO, section_type=SectionType.INTRODUCTION
            ),
            SectionInfo(
                number="A.10",
                title="Proof of Proposition 2",
                text=PROOF,
                section_type=SectionType.OTHER,
                math_content=True,
            ),
        ],
    )


@pytest.fixture
def box(tmp_path):
    paper = f"# A Paper\n\n# 1 Introduction\n\n{INTRO}\n\n# A.10\n\n{PROOF}\n"
    ws = ReviewWorkspace.create(paper, _structure(), root=tmp_path / "ws")
    yield ToolBox(workspace=ws, max_calls=25)
    ws.cleanup()


def test_schemas_respect_the_role_capability_flags():
    names = {s["function"]["name"] for s in tool_schemas(allow_python=True, allow_write=True)}
    assert {"paper_search", "paper_read", "paper_outline", "python", "note_write"} <= names

    restricted = {
        s["function"]["name"] for s in tool_schemas(allow_python=False, allow_write=False)
    }
    assert "python" not in restricted
    assert "note_write" not in restricted
    assert "paper_search" in restricted


def test_outline_lists_every_section(box):
    out = box.dispatch("paper_outline", {})
    assert "Proof of Proposition 2" in out
    assert "Introduction" in out


def test_search_returns_anchored_hits(box):
    out = box.dispatch("paper_search", {"query": "The needle is here"})
    assert "hit(s)" in out
    assert "char_start=" in out
    assert "Proof of Proposition 2" in out


def test_search_reports_a_miss_without_erroring(box):
    out = box.dispatch("paper_search", {"query": "a phrase that is absent"})
    assert "No match" in out


def test_search_honours_the_hit_cap(box):
    out = box.dispatch("paper_search", {"query": "Definition 2", "max_hits": 999})
    assert out.count("char_start=") <= MAX_SEARCH_HITS


def test_search_rejects_a_bad_regex_as_text_not_an_exception(box):
    out = box.dispatch("paper_search", {"query": "([unclosed", "regex": True})
    assert "TOOL ERROR" in out
    assert "bad regex" in out


def test_read_by_section_id_returns_the_whole_section(box):
    section_id = box.workspace.sections[1].section_id
    out = box.dispatch("paper_read", {"section_id": section_id})
    assert "The needle is here" in out


def test_read_by_offset_returns_a_window(box):
    out = box.dispatch("paper_read", {"char_start": 0, "length": 50})
    assert out.startswith("[paper.md chars 0-50]")


def test_read_an_unknown_section_lists_valid_ids(box):
    out = box.dispatch("paper_read", {"section_id": "nope-not-a-section"})
    assert "TOOL ERROR" in out
    assert "Known ids start" in out


def test_read_without_arguments_explains_what_is_needed(box):
    assert "pass either section_id or char_start" in box.dispatch("paper_read", {})


def test_unknown_tool_is_reported_as_text(box):
    assert "unknown tool" in box.dispatch("not_a_tool", {})


def test_a_disabled_tool_is_refused(tmp_path):
    paper = "# P\n\nbody text that is long enough\n"
    ws = ReviewWorkspace.create(paper, _structure(), root=tmp_path / "ws2")
    box = ToolBox(workspace=ws, allow_python=False, allow_write=False)
    assert "not enabled" in box.dispatch("python", {"code": "print(1)"})
    assert "not enabled" in box.dispatch("note_write", {"name": "a.md", "text": "b"})
    ws.cleanup()


def test_the_tool_budget_stops_further_calls(box):
    box.max_calls = 2
    assert "hit(s)" in box.dispatch("paper_search", {"query": "needle"})
    box.dispatch("paper_outline", {})
    out = box.dispatch("paper_outline", {})
    assert "TOOL BUDGET EXHAUSTED" in out


def test_calls_are_logged_for_the_run_manifest(box):
    box.dispatch("paper_outline", {})
    box.dispatch("paper_search", {"query": "needle"})
    assert [e["tool"] for e in box.log] == ["paper_outline", "paper_search"]
    assert all(e["chars_out"] > 0 for e in box.log)


def test_notes_are_shared_between_agents(box):
    box.dispatch("note_write", {"name": "notation.md", "text": "sigma-hat is the scale estimate"})
    assert "notation.md" in box.dispatch("note_list", {})
    assert "sigma-hat" in box.dispatch("note_read", {"name": "notation.md"})


def test_reading_a_missing_note_is_an_error_message(box):
    assert "TOOL ERROR" in box.dispatch("note_read", {"name": "absent.md"})


def test_a_tool_exception_is_returned_as_text_not_raised(box):
    # A traversal name reaches write_note, which resolves it inside the
    # workspace; a genuinely unresolvable note read must still not raise.
    out = box.dispatch("note_read", {"name": "../../../etc/passwd"})
    assert "TOOL ERROR" in out


def test_python_tool_runs_and_returns_output(box):
    assert "7" in box.dispatch("python", {"code": "print(3 + 4)"})


def test_finding_from_payload_assigns_a_stable_id():
    finding = finding_from_payload(
        {"finding_id": "whatever-the-model-said", "title": "T", "claim": "C"},
        target_id="t03",
        index=2,
    )
    assert finding.finding_id == "t03-f2"
    assert finding.target_id == "t03"
