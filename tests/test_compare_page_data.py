import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
COMPARE_PAGE = ROOT / "web" / "src" / "components" / "ComparePage.tsx"
COMPARE_DATA = ROOT / "web" / "src" / "data" / "compare.ts"
REFINE_EXAMPLES = ROOT / "data" / "refine_examples"
ESCAPED_UNICODE_RE = re.compile(r"\\u[0-9a-fA-F]{4}")


def test_compare_overview_table_derives_from_loaded_papers() -> None:
    content = COMPARE_PAGE.read_text(encoding="utf-8")
    assert "function ScoresOverviewTable({ papers }" in content
    assert "const SCORE_DATA =" not in content
    assert "OVERVIEW_MODEL_ORDER" in content


def test_compare_loader_normalizes_json_escaped_unicode() -> None:
    content = COMPARE_DATA.read_text(encoding="utf-8")
    assert "function normalizeEscapedUnicode" in content
    assert "readFile(filePath: string): string" in content
    assert "tryReadFile(filePath: string): string | null" in content


def test_new_gpt54_artifacts_are_clean_for_compare_page() -> None:
    artifact_paths = sorted(REFINE_EXAMPLES.glob("*/review_gpt54_20260412_quoterepair.md"))
    artifact_paths += sorted(REFINE_EXAMPLES.glob("*/quality_gpt54_20260412_vs_*_gemini31pro.md"))

    assert artifact_paths, "Expected GPT-5.4 benchmark artifacts to be present"

    for path in artifact_paths:
        text = path.read_text(encoding="utf-8")
        assert not ESCAPED_UNICODE_RE.search(text), f"Unexpected escaped unicode sequence in {path}"
        assert "**Reference**: /Users/" not in text, f"Unexpected absolute path leak in {path}"
