"""Tests for coarse.agent.workspace."""

from __future__ import annotations

import pytest

from coarse.agent.types import LedgerFinding, PaperAnchor, RefutationVerdict
from coarse.agent.workspace import ReviewWorkspace
from coarse.types import PaperStructure, SectionInfo, SectionType

ABSTRACT = "We study post-selection inference."
SEC_ONE = "Definition 2 says a thing. " * 20
SEC_TWO = "The gradient is wrong here. " * 20


def _structure() -> PaperStructure:
    return PaperStructure(
        title="A Paper",
        domain="statistics/selective_inference",
        taxonomy="academic/research_paper",
        abstract=ABSTRACT,
        sections=[
            SectionInfo(
                number=1,
                title="Introduction",
                text=SEC_ONE,
                section_type=SectionType.INTRODUCTION,
            ),
            SectionInfo(
                number="A.10",
                title="Proof of Proposition 2",
                text=SEC_TWO,
                section_type=SectionType.OTHER,
                math_content=True,
            ),
        ],
    )


def _paper() -> str:
    return f"# A Paper\n\n{ABSTRACT}\n\n# 1 Introduction\n\n{SEC_ONE}\n\n# A.10\n\n{SEC_TWO}\n"


@pytest.fixture
def workspace(tmp_path):
    ws = ReviewWorkspace.create(_paper(), _structure(), root=tmp_path / "ws")
    yield ws
    ws.cleanup()


def test_create_writes_paper_sections_and_outline(workspace):
    assert workspace.paper_path.is_file()
    assert len(workspace.sections) == 2
    for sec in workspace.sections:
        assert sec.path.is_file()
        assert sec.title in sec.path.read_text()
    outline = (workspace.root / "outline.md").read_text()
    assert "Proof of Proposition 2" in outline
    assert ABSTRACT in outline


def test_section_char_start_locates_section_in_paper(workspace):
    paper = workspace.paper_text
    for sec in workspace.sections:
        assert paper[sec.char_start : sec.char_start + 20] in paper
    # Sections are emitted in document order, so offsets must be increasing.
    offsets = [s.char_start for s in workspace.sections]
    assert offsets == sorted(offsets)


def test_section_by_id_accepts_exact_prefix_and_title_fragment(workspace):
    exact = workspace.sections[1].section_id
    assert workspace.section_by_id(exact) is not None
    assert workspace.section_by_id(exact[:5]) is not None
    assert workspace.section_by_id("proposition 2") is not None
    assert workspace.section_by_id("no such section at all") is None


@pytest.mark.parametrize(
    "escape",
    ["../outside.txt", "../../etc/passwd", "notes/../../escape.md"],
)
def test_resolve_in_workspace_refuses_escapes(workspace, escape):
    with pytest.raises(ValueError, match="escapes the workspace"):
        workspace.resolve_in_workspace(escape)


def test_write_note_stays_inside_workspace_even_for_a_traversal_name(workspace):
    path = workspace.write_note("../../pwned.md", "body")
    assert workspace.root in path.parents
    assert path.read_text() == "body"


def test_write_note_truncates_oversized_content(workspace):
    from coarse.agent.workspace import MAX_WRITE_BYTES

    path = workspace.write_note("big.md", "x" * (MAX_WRITE_BYTES + 5_000))
    assert len(path.read_text()) == MAX_WRITE_BYTES


def _finding(fid: str = "t01-f1") -> LedgerFinding:
    return LedgerFinding(
        finding_id=fid,
        target_id="t01",
        title="Sign error",
        location="A.10",
        claim="The displayed gradient has the opposite sign.",
        anchors=[PaperAnchor(section_id="001", quote="The gradient is wrong here.")],
    )


def test_ledger_round_trips_findings_and_verdicts(workspace):
    workspace.write_finding(_finding())
    workspace.write_verdict(
        RefutationVerdict(finding_id="t01-f1", verdict="confirmed", reasoning="Reproduced.")
    )

    findings = workspace.read_findings()
    assert [f.finding_id for f in findings] == ["t01-f1"]
    # The verdict file must not be read back as a finding.
    assert all(not f.finding_id.endswith("verdict") for f in findings)

    verdicts = workspace.read_verdicts()
    assert verdicts["t01-f1"].verdict == "confirmed"


def test_read_findings_skips_corrupt_ledger_entries(workspace):
    workspace.write_finding(_finding())
    (workspace.root / "findings" / "broken.json").write_text("{not json")
    assert len(workspace.read_findings()) == 1


def test_cleanup_removes_only_an_owned_root(tmp_path):
    given = tmp_path / "keep"
    ws = ReviewWorkspace.create(_paper(), _structure(), root=given)
    ws.cleanup()
    assert given.exists(), "a caller-supplied root must survive cleanup"

    owned = ReviewWorkspace.create(_paper(), _structure())
    root = owned.root
    owned.cleanup()
    assert not root.exists()


def test_context_manager_cleans_up_an_owned_root():
    with ReviewWorkspace.create(_paper(), _structure()) as ws:
        root = ws.root
        assert root.exists()
    assert not root.exists()
