# Development Backlog

Components are built in order. Each row becomes a PR.

| # | Component | Status | File(s) | Deps | Description |
|---|-----------|--------|---------|------|-------------|
| 1 | Project setup | done | pyproject.toml, .gitignore, LICENSE | — | Verify project structure, add missing scaffolding, initial commit |
| 2 | Types | done | src/coarse/types.py | — | Pydantic models: PaperText, PaperStructure, Review, DetailedComment, CostEstimate, etc. |
| 3 | Config | done | src/coarse/config.py | 2 | Settings: ~/.coarse/config.toml, API key resolution, model defaults |
| 4 | LLM client | done | src/coarse/llm.py | 2,3 | litellm + instructor wrapper, cost tracking, structured output |
| 5 | Cost estimator | pending | src/coarse/cost.py | 4 | Pre-flight cost estimate, fetch pricing from litellm, user approval display |
| 6 | Extraction | pending | src/coarse/extraction.py | 2 | PDF → PaperText via pymupdf4llm (text mode) + pymupdf (vision mode) |
| 7 | Prompts | pending | src/coarse/prompts.py | 2 | All prompt templates for structure, overview, section, crossref, critique |
| 8 | Structure analysis | pending | src/coarse/structure.py | 4,7 | PaperText → PaperStructure via LLM call |
| 9 | Agent base | pending | src/coarse/agents/base.py, src/coarse/agents/__init__.py | 4 | ReviewAgent ABC with run() method |
| 10 | Overview agent | pending | src/coarse/agents/overview.py | 7,9 | Macro-level review producing 4-6 OverviewIssues |
| 11 | Section agent | pending | src/coarse/agents/section.py | 7,9 | Per-section review producing DetailedComments (runs parallel) |
| 12 | Crossref agent | pending | src/coarse/agents/crossref.py | 7,9 | Dedup comments, validate quotes against paper text, check consistency |
| 13 | Critique agent | pending | src/coarse/agents/critique.py | 7,9 | Self-critique quality gate: revise weak comments, drop low-value ones |
| 14 | Synthesis | pending | src/coarse/synthesis.py | 2 | Review → refine.ink-format markdown string |
| 15 | Pipeline | pending | src/coarse/pipeline.py | 6,8,10-14 | review_paper() orchestrator: extract → structure → agents → synthesize |
| 16 | CLI | pending | src/coarse/cli.py, src/coarse/__init__.py, src/coarse/__main__.py | 3,5,15 | Typer CLI with progress display, interactive setup, cost approval |
| 17 | Quality eval | pending | src/coarse/quality.py | 4,14 | Compare review against reference using LLM judge (dev/eval only) |
| 18 | README + packaging | pending | README.md, CHANGELOG.md | 16 | User-facing docs, verify pip/pipx/uvx install works |
