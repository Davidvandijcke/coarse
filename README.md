# coarse

Free, open-source AI academic paper reviewer. The rough alternative to refine.ink.

You provide your own API key and pay the LLM provider directly — typically **$2-5 per review**
vs refine.ink's ~$50.

## Install

```bash
pip install coarse
```

```bash
pipx install coarse
```

```bash
uvx coarse paper.pdf
```

## Quickstart

Configure your API key once:

```bash
coarse setup
```

Review a paper:

```bash
coarse review paper.pdf
```

The review is written to `paper_review.md` in the current directory.

## Model selection

Pass any litellm-compatible model string with `--model`:

```bash
coarse review paper.pdf --model openai/gpt-4o
coarse review paper.pdf --model anthropic/claude-3-5-sonnet-20241022
coarse review paper.pdf --model gemini/gemini-3-flash
```

The default model is `qwen/qwen3.5-plus-02-15` (via OpenRouter). Any model supported by
[litellm](https://docs.litellm.ai/docs/providers) works here.

## API keys

Set the environment variable for your provider before running:

| Provider  | Environment variable  |
|-----------|-----------------------|
| OpenAI    | `OPENAI_API_KEY`      |
| Anthropic | `ANTHROPIC_API_KEY`   |
| Google    | `GEMINI_API_KEY`      |
| Google    | `GOOGLE_API_KEY`      |
| Cohere    | `COHERE_API_KEY`      |
| Mistral   | `MISTRAL_API_KEY`     |
| Groq      | `GROQ_API_KEY`        |
| Together  | `TOGETHER_API_KEY`    |
| Azure     | `AZURE_API_KEY`       |

Alternatively, run `coarse setup` to store keys in `~/.coarse/config.toml`.

## Agentic mode

For deeper analysis of proof-heavy, methodology, or results sections, enable coding agents:

```bash
coarse review paper.pdf --agentic
```

Coding agents use the [OpenHands SDK](https://github.com/All-Hands-AI/openhands) to autonomously
read the full paper, cross-reference sections, and run Python to verify math. Adds ~$2-3 and takes
3-10 minutes (vs ~30s for standard mode). Falls back to standard LLM agents on failure.

## Cost

coarse estimates cost before running and asks for confirmation.

| Paper length    | Typical cost  |
|-----------------|---------------|
| Short (< 20pp)  | $1 - $2       |
| Long (30+ pp)   | $2 - $5       |

The default spending cap is **$10 per review** (`max_cost_usd` in config). Use `--yes` to skip the
confirmation prompt. Use `--no-qa` to skip the post-extraction quality check (vision LLM).
Scanned PDFs are supported via Docling's built-in OCR.

## Output format

The review is written as a markdown file matching the refine.ink format:

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

review, markdown = review_paper(
    pdf_path=Path("paper.pdf"),
    model="openai/gpt-4o",   # optional; uses config default if omitted
)

print(markdown)                         # full review as markdown string
print(review.detailed_comments[0].feedback)  # access structured fields
```

`review_paper` returns a `(Review, str)` tuple where the first element is the structured
`Review` Pydantic model and the second is the rendered markdown.

## Configuration

Settings are stored in `~/.coarse/config.toml`:

```toml
default_model = "qwen/qwen3.5-plus-02-15"
vision_model = "gemini/gemini-3-flash"
extraction_qa = true
max_cost_usd = 10.0

[api_keys]
openai = "sk-..."
anthropic = "sk-ant-..."
```

Run `coarse setup` for an interactive prompt that writes this file.

## Version

0.1.0

## License

MIT
