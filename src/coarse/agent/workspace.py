"""Ephemeral per-review workspace shared by the agent roles (#264).

The workspace is the only medium the roles collaborate through. An
investigator writes a candidate finding as a file; a refuter reads that file
and writes its verdict beside it. No review content is carried by
conversational state between agents, which is what makes the fresh-context
refutation in ``orchestrator`` meaningful.

Everything lives under one temporary directory outside the repository and
outside the user's project, so a tool-enabled agent pointed at this directory
cannot reach either.
"""

from __future__ import annotations

import json
import re
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

from coarse.agent.types import LedgerFinding, RefutationVerdict
from coarse.types import PaperStructure

_SLUG_RE = re.compile(r"[^a-z0-9]+")
# Cap on a single note/finding write. Generous for prose, small enough that a
# runaway agent cannot fill the disk.
MAX_WRITE_BYTES = 256_000


def _slug(text: str, limit: int = 48) -> str:
    out = _SLUG_RE.sub("-", text.lower()).strip("-")
    return (out[:limit].rstrip("-")) or "section"


@dataclass(frozen=True)
class SectionFile:
    """A parsed section as it exists in the workspace."""

    section_id: str
    title: str
    path: Path
    char_start: int
    char_len: int
    math_content: bool


class ReviewWorkspace:
    """Materialize a paper and its sections as files an agent can read.

    Construct with ``create()``; call ``cleanup()`` when done, or use it as a
    context manager.
    """

    def __init__(self, root: Path, sections: list[SectionFile], owns_root: bool) -> None:
        self.root = root
        self.sections = sections
        self._owns_root = owns_root

    # -- construction -----------------------------------------------------

    @classmethod
    def create(
        cls,
        paper_markdown: str,
        structure: PaperStructure,
        *,
        root: Path | None = None,
    ) -> ReviewWorkspace:
        """Write paper.md, one file per section, and outline.md.

        ``root`` is created if given (used by tests for a deterministic path);
        otherwise a temporary directory is allocated and owned by this object.
        """
        owns_root = root is None
        if root is None:
            root = Path(tempfile.mkdtemp(prefix="coarse-review-"))
        root = Path(root)
        (root / "sections").mkdir(parents=True, exist_ok=True)
        (root / "findings").mkdir(parents=True, exist_ok=True)
        (root / "notes").mkdir(parents=True, exist_ok=True)
        (root / "paper.md").write_text(paper_markdown, encoding="utf-8")

        sections: list[SectionFile] = []
        search_from = 0
        for i, sec in enumerate(structure.sections):
            section_id = f"{i:03d}-{_slug(sec.title)}"
            # Locate the section in paper.md so anchors reported by an agent
            # can be mapped back to a global offset. Sections are emitted in
            # document order, so searching forward from the previous hit keeps
            # repeated headings from collapsing onto the same offset.
            char_start = -1
            if sec.text:
                probe = sec.text[:200]
                char_start = paper_markdown.find(probe, search_from)
                if char_start == -1:
                    char_start = paper_markdown.find(probe)
                if char_start >= 0:
                    search_from = char_start + max(1, len(probe) // 2)
            path = root / "sections" / f"{section_id}.md"
            header = (
                f"<!-- section_id: {section_id} | type: {sec.section_type.value} "
                f"| math_content: {sec.math_content} | char_start: {char_start} -->\n"
            )
            path.write_text(f"{header}# {sec.number} {sec.title}\n\n{sec.text}\n", encoding="utf-8")
            sections.append(
                SectionFile(
                    section_id=section_id,
                    title=sec.title,
                    path=path,
                    char_start=max(0, char_start),
                    char_len=len(sec.text),
                    math_content=bool(sec.math_content),
                )
            )

        (root / "outline.md").write_text(cls._render_outline(structure, sections), encoding="utf-8")
        return cls(root, sections, owns_root)

    @staticmethod
    def _render_outline(structure: PaperStructure, sections: list[SectionFile]) -> str:
        lines = [
            f"# {structure.title}",
            "",
            f"Domain: {structure.domain}",
            f"Sections: {len(sections)}",
            "",
            "Every section below is readable in full. `sections/<section_id>.md` holds the",
            "section text; `paper.md` holds the whole paper. Nothing is withheld.",
            "",
            "| section_id | chars | math | title |",
            "|---|---|---|---|",
        ]
        for s in sections:
            lines.append(
                f"| `{s.section_id}` | {s.char_len} | {'yes' if s.math_content else 'no'} "
                f"| {s.title} |"
            )
        lines += ["", "## Abstract", "", structure.abstract or "(none extracted)"]
        return "\n".join(lines) + "\n"

    # -- paths ------------------------------------------------------------

    @property
    def paper_path(self) -> Path:
        return self.root / "paper.md"

    @property
    def paper_text(self) -> str:
        return self.paper_path.read_text(encoding="utf-8")

    def section_by_id(self, section_id: str) -> SectionFile | None:
        for s in self.sections:
            if s.section_id == section_id:
                return s
        # Tolerate an agent passing the bare index or a loose title fragment.
        probe = section_id.strip().lower()
        for s in self.sections:
            if s.section_id.startswith(probe) or probe in s.title.lower():
                return s
        return None

    def resolve_in_workspace(self, relative: str) -> Path:
        """Resolve *relative* under the workspace root, refusing escapes."""
        candidate = (self.root / relative).resolve()
        root = self.root.resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"path escapes the workspace: {relative}")
        return candidate

    # -- ledger -----------------------------------------------------------

    def write_finding(self, finding: LedgerFinding) -> Path:
        path = self.root / "findings" / f"{finding.finding_id}.json"
        path.write_text(finding.model_dump_json(indent=1), encoding="utf-8")
        return path

    def read_findings(self) -> list[LedgerFinding]:
        out: list[LedgerFinding] = []
        for path in sorted((self.root / "findings").glob("*.json")):
            if path.name.endswith(".verdict.json"):
                continue
            try:
                out.append(LedgerFinding.model_validate_json(path.read_text(encoding="utf-8")))
            except Exception:
                continue
        return out

    def write_verdict(self, verdict: RefutationVerdict) -> Path:
        path = self.root / "findings" / f"{verdict.finding_id}.verdict.json"
        path.write_text(verdict.model_dump_json(indent=1), encoding="utf-8")
        return path

    def read_verdicts(self) -> dict[str, RefutationVerdict]:
        out: dict[str, RefutationVerdict] = {}
        for path in sorted((self.root / "findings").glob("*.verdict.json")):
            try:
                v = RefutationVerdict.model_validate_json(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            out[v.finding_id] = v
        return out

    def write_note(self, relative: str, text: str) -> Path:
        path = self.resolve_in_workspace(f"notes/{Path(relative).name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text[:MAX_WRITE_BYTES], encoding="utf-8")
        return path

    def dump_manifest(self, payload: dict) -> Path:
        path = self.root / "run.json"
        path.write_text(json.dumps(payload, indent=1, default=str), encoding="utf-8")
        return path

    # -- lifecycle --------------------------------------------------------

    def cleanup(self) -> None:
        if self._owns_root and self.root.exists():
            shutil.rmtree(self.root, ignore_errors=True)

    def __enter__(self) -> ReviewWorkspace:
        return self

    def __exit__(self, *_exc) -> None:
        self.cleanup()
