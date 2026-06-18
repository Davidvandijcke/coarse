"""Quote-fidelity scorer for the multilingual design-A-vs-B experiment.

Reuses the PRODUCTION quote verifier (coarse.quote_verify.verify_quotes_detailed)
so the numbers answer the real question: of the comments a reviewer produced while
writing feedback in language L, how many carry a quote the live pipeline would KEEP
(exact or fuzzy-recovered) vs DROP as unanchored? Quotes stay in the paper's original
(English) text in every condition — design A keeps quotes verbatim and only the
feedback prose changes language — so this isolates whether writing in L degrades
faithful English-quote copying.

The paper text is not committed (it is the author's manuscript); point PAPER_PATH at a
local extraction to re-run. Without it, this script re-prints the committed fidelity.json.

Usage:
    uv run python docs/experiments/score_quote_fidelity.py [path/to/paper.md]
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

DATA = Path(__file__).parent / "data"
LANGS = {
    "en": "English (baseline)",
    "es": "Spanish",
    "zh": "Chinese (Simplified)",
    "ar": "Arabic",
}


def main() -> None:
    paper_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    if paper_path is None or not paper_path.exists():
        print("No paper text given — re-printing committed data/fidelity.json:\n")
        print((DATA / "fidelity.json").read_text(encoding="utf-8"))
        print("\n(Pass a paper-text path to recompute from data/reviews_*.json.)")
        return

    from coarse.quote_verify import verify_quotes_detailed
    from coarse.types import DetailedComment

    paper = paper_path.read_text(encoding="utf-8")
    summary: dict[str, dict] = {}
    for code, name in LANGS.items():
        data = json.loads((DATA / f"reviews_{code}.json").read_text(encoding="utf-8"))
        comments, too_short = [], 0
        for i, item in enumerate(data, 1):
            quote = (item.get("quote") or "").strip()
            if len(quote) < 20:
                too_short += 1
                continue
            comments.append(
                DetailedComment(
                    number=i,
                    title=(item.get("gloss_en") or f"comment {i}")[:120],
                    quote=quote,
                    feedback=item.get("feedback") or "",
                )
            )
        s = verify_quotes_detailed(comments, paper, drop_unverified=True).stats
        n = len(data)
        survived = s["exact"] + s["fuzzy"]
        summary[code] = {
            "name": name,
            "n_comments": n,
            "exact": s["exact"],
            "fuzzy": s["fuzzy"],
            "dropped": s["dropped"],
            "too_short": too_short,
            "survived": survived,
            "fidelity_pct": round(100 * survived / n, 1) if n else 0.0,
            "exact_pct": round(100 * s["exact"] / n, 1) if n else 0.0,
        }
        print(
            f"{code} ({name}): n={n} exact={s['exact']} fuzzy={s['fuzzy']} "
            f"dropped={s['dropped']} too_short={too_short} "
            f"-> fidelity {summary[code]['fidelity_pct']}% (exact {summary[code]['exact_pct']}%)"
        )
    (DATA / "fidelity.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    print("\nwrote data/fidelity.json")


if __name__ == "__main__":
    main()
