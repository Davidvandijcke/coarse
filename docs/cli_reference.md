# CLI Reference Manual

Comprehensive command-line interface guide for `coarse-ink`.

## Table of Contents

- [CLI Reference Manual](#cli-reference-manual)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [CLI Commands](#cli-commands)
    - [`coarse review`](#coarse-review)
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
