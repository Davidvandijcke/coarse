# CLI Reference Manual

Comprehensive command-line interface guide for `coarse-ink`.

## Table of Contents

- [CLI Reference Manual](#cli-reference-manual)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [CLI Commands](#cli-commands)
    - [`coarse review`](#coarse-review)
    - [`coarse review-parallel`](#coarse-review-parallel)
    - [`coarse-review`](#coarse-review-1)
    - [`coarse attach`](#coarse-attach)
  - [Configuration](#configuration)
    - [Configuration File (`~/.coarse/config.toml`)](#configuration-file-coarseconfigtoml)
    - [Environment Variables](#environment-variables)
  - [Headless & Handoff Mode](#headless--handoff-mode)

---

## Overview

`coarse-ink` provides command-line interfaces for reviewing academic papers locally or headlessly. The primary entry point is `coarse`, with specialized executables for serverless handoff environments.

---

## CLI Commands

### `coarse review`

Main interactive review command.

```bash
coarse review paper.pdf [OPTIONS]
```

#### Options

- `--model TEXT`: Primary LLM model ID override (defaults to `DEFAULT_MODEL` in `models.py`).
- `--output PATH`: Path to write rendered Markdown review (defaults to `paper_review.md`).
- `--language TEXT`: Output language code (e.g. `en`, `es`, `fr`, `de`).
- `--yes`, `-y`: Skip cost approval prompt.
- `--no-cache`: Bypass extraction cache.
- `--attach`: Run in background attach mode with PID file monitoring.

### `coarse review-parallel`

Extract a paper once, then review it with several models in parallel. Each
review runs in its own worker subprocess; the parent shows one live table and
stops every worker on Ctrl-C.

```bash
coarse review-parallel paper.pdf --model anthropic/claude-sonnet-5 --model openai/gpt-4o --yes
```

#### Options

- `--model TEXT`, `-m TEXT` (required, repeatable): model to review with; repeat once per parallel review. Repeating the same model runs it independently again.
- `--output-dir PATH`: parent for a new, unique run directory (default: `./coarse-output/`, the same default as `coarse-review`).
- `--env-file PATH`: load credentials from a dotenv file, overriding existing environment values.
- `--language TEXT`, `-l TEXT`: review language for every model.
- `--no-qa`: disable PDF extraction QA, including the automatic check triggered by garbled text.
- `--yes`, `-y`: skip the single run confirmation. Required when stdin is not a terminal.

Reviews always skip the interactive cost gate; the confirmation lists the models and warns that no combined estimate is available.

#### Run directory

Each invocation creates `coarse-output/<paper>-<UTC timestamp>-<suffix>/`:

```text
extracted.md            shared extraction (QA-corrected when QA ran)
extraction.log          extraction worker output
01-<model>.md           review by the first --model
01-<model>.log          that worker's output
02-<model>.md ...
*.job.json              worker specs (paths and options only)
summary.json            statuses, stages, elapsed time, reported costs
```

Costs in the table and summary are the amounts coarse reports per worker; OCR charges from a cold extraction cache are not itemised.

#### Exit codes

`0` every review succeeded · `1` a job or the run failed · `2` invalid options · `130` interrupted (Ctrl-C/SIGTERM). An extraction failure prevents reviews from starting; one review failing leaves the others running. macOS and Linux only.

### `coarse-review`

Standalone headless CLI entry point designed for non-interactive execution, scripts, and Modal worker subprocesses.

```bash
coarse-review paper.pdf --output review.md
```

### `coarse attach`

Attaches terminal output to a running background review job.

```bash
coarse attach --pid-file /path/to/pidfile
```

---

## Configuration

### Configuration File (`~/.coarse/config.toml`)

`coarse` automatically loads configuration options from `~/.coarse/config.toml`.

```toml
[keys]
openrouter = "sk-or-v1-..."
perplexity = "pplx-..."
openai = "sk-..."
anthropic = "sk-ant-..."

[defaults]
model = "qwen/qwen3.7-plus"
language = "en"
```

### Environment Variables

Environment variables override configuration file entries:

- `OPENROUTER_API_KEY`: API key for OpenRouter models and OCR file-parser.
- `PERPLEXITY_API_KEY`: API key for Perplexity Sonar literature search.
- `OPENAI_API_KEY`: API key for OpenAI fallback models.
- `ANTHROPIC_API_KEY`: API key for Anthropic models.
- `GEMINI_API_KEY`: API key for Google Gemini models.

---

## Headless & Handoff Mode

When executed in headless mode (`coarse-review` or `cli_attach.py`), progress events are emitted as JSON lines to stdout or log files, enabling integration with web frontends and cloud workers.
