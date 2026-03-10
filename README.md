# coarse

[![CI](https://github.com/Davidvandijcke/coarse/actions/workflows/ci.yml/badge.svg)](https://github.com/Davidvandijcke/coarse/actions/workflows/ci.yml)
[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/github/license/Davidvandijcke/coarse)](LICENSE)

Free, open-source AI academic paper reviewer that outperforms popular paid AI reviewers.

You provide your own API key and pay the LLM provider directly — typically **under $1 per review**.

Don't want to run it locally? Use the [web interface](https://coarse.vercel.app/) instead.

## Quickstart

Get an API key from [OpenRouter](https://openrouter.ai/keys) (free to sign up), then:

```bash
uvx coarse review paper.pdf --api-key sk-or-v1-YOUR_KEY
```

That's it. The review is written to `paper_review.md` in the current directory.

### Prerequisites

coarse requires Python 3.12+. If you don't have `uvx`, install [uv](https://docs.astral.sh/uv/) first:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

`uvx` runs coarse in a temporary environment with no permanent install. To install permanently:

```bash
uv tool install coarse    # or: pip install coarse
```

### Save your API key

To avoid passing `--api-key` every time, create a `.env` file in your working directory:

```
OPENROUTER_API_KEY=sk-or-v1-YOUR_KEY
```

Or run `coarse setup` to store keys in `~/.coarse/config.toml`.

## How it works

```
paper.pdf
  -> Mistral OCR (Docling fallback)      Extract text as markdown
  -> Vision LLM spot-check               Optional quality check
  -> Structure analysis                   Parse sections, classify domain
  -> Overview + section agents            Run in parallel: 4-6 macro issues + 15-25 detailed comments
  -> Cross-reference agent                Deduplicate, validate consistency
  -> Quote verification                   Fuzzy-match quotes against paper text
  -> Self-critique agent                  Quality gate, revise weak comments
  -> Quote re-verification               Fix any quotes garbled during critique
  -> Synthesis                            Render final paper_review.md
```

The pipeline extracts text via OCR, classifies the paper's domain and structure, then runs
multiple review agents in parallel. A cross-reference pass deduplicates comments and a
self-critique agent acts as a quality gate. All quotes are programmatically verified against
the source text.

## Model selection

Pass any litellm-compatible model string with `--model`:

```bash
coarse review paper.pdf --model openai/gpt-4o
coarse review paper.pdf --model anthropic/claude-3-5-sonnet-20241022
coarse review paper.pdf --model gemini/gemini-3-flash
```

The default model is `qwen/qwen3.5-plus-02-15` routed via [OpenRouter](https://openrouter.ai).
Any model supported by [litellm](https://docs.litellm.ai/docs/providers) works.
With only `OPENROUTER_API_KEY` set, all models (including vision QA) route through OpenRouter automatically.

## API keys

Only `OPENROUTER_API_KEY` is needed. For step-by-step setup instructions, see the
[API key guide](https://coarse.vercel.app/setup). For direct provider access (lower latency),
set the provider-specific key instead:

| Provider   | Environment variable   |
|------------|------------------------|
| OpenRouter | `OPENROUTER_API_KEY`   |
| OpenAI     | `OPENAI_API_KEY`       |
| Anthropic  | `ANTHROPIC_API_KEY`    |
| Google     | `GEMINI_API_KEY`       |
| Mistral    | `MISTRAL_API_KEY`      |
| Groq       | `GROQ_API_KEY`         |
| Together   | `TOGETHER_API_KEY`     |
| Cohere     | `COHERE_API_KEY`       |
| Azure      | `AZURE_API_KEY`        |

## Cost

coarse estimates cost before running and asks for confirmation.

| Paper length    | Typical cost  |
|-----------------|---------------|
| Short (< 20pp)  | $0.25 - $0.50 |
| Long (30+ pp)   | $0.50 - $1    |

The default spending cap is **$10 per review** (`max_cost_usd` in config). Use `--yes` to skip the
confirmation prompt. Use `--no-qa` to skip the post-extraction quality check (vision LLM).
Scanned PDFs are supported via Docling's built-in OCR (`pip install coarse[docling]`).

## Output format

The review is written as a structured markdown file:

```
# Paper Title

**Date**: MM/DD/YYYY
**Domain**: social_sciences/economics
**Taxonomy**: academic/research_paper
**Filter**: Active comments

---

## Overall Feedback

4-6 macro issues with titles and body paragraphs.

---

## Detailed Comments (N)

20+ numbered comments, each with a verbatim quote from the paper and
actionable feedback.
```

## Python API

```python
from coarse import review_paper
from pathlib import Path

review, markdown, paper_text = review_paper(
    pdf_path=Path("paper.pdf"),
    model="openai/gpt-4o",   # optional; uses config default if omitted
)

print(markdown)                         # full review as markdown string
print(review.detailed_comments[0].feedback)  # access structured fields
```

`review_paper` returns a `(Review, str, PaperText)` tuple: the structured `Review` model,
rendered markdown, and the extracted paper text (useful for quality evaluation).

## Configuration

Settings are stored in `~/.coarse/config.toml`:

```toml
default_model = "qwen/qwen3.5-plus-02-15"
vision_model = "gemini/gemini-3-flash-preview"
extraction_qa = true
max_cost_usd = 10.0

[api_keys]
openai = "sk-..."
anthropic = "sk-ant-..."
```

Run `coarse setup` for an interactive prompt that writes this file.

## Development

```bash
git clone https://github.com/Davidvandijcke/coarse.git
cd coarse
uv sync --extra dev
uv run pytest tests/ -v
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, project structure, and guidelines.

## Version

1.0.0

## License

MIT
