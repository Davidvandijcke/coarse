# System Architecture & Component Guide

Welcome to the architectural documentation for `coarse-ink` (import name `coarse`). This document provides a high-level overview of system components, execution pipelines, data transformations, and subsystem interactions.

## Table of Contents

- [System Architecture & Component Guide](#system-architecture--component-guide)
  - [Table of Contents](#table-of-contents)
  - [High-Level Architecture](#high-level-architecture)
  - [Subsystem Architecture](#subsystem-architecture)
    - [1. Core Orchestration Engine](#1-core-orchestration-engine)
    - [2. Multi-Agent Review Subsystem](#2-multi-agent-review-subsystem)
    - [3. Document Ingestion & Extraction](#3-document-ingestion--extraction)
    - [4. Quote Integrity & Verification](#4-quote-integrity--verification)
    - [5. LLM Transport & Model Registry](#5-llm-transport--model-registry)
    - [6. Quality & Recall Evaluation Framework](#6-quality--recall-evaluation-framework)
    - [7. CLI & Headless Handoff Interfaces](#7-cli--headless-handoff-interfaces)
    - [8. Deployment Infrastructure](#8-deployment-infrastructure)
  - [Data Models & Schema Contracts](#data-models--schema-contracts)
  - [Review Pipeline Execution Flow](#review-pipeline-execution-flow)

---

## High-Level Architecture

`coarse` is an automated AI academic paper reviewer designed as an open-source alternative to proprietary services. The framework takes paper documents, parses structural sections, executes domain calibration and literature retrieval in parallel, orchestrates section-specific review agents, verifies verbatim quotes against original text, and renders structured Markdown output.

---

## Subsystem Architecture

### 1. Core Orchestration Engine

The core orchestration layer manages document transformation, pipeline state, stage timing, and cost estimation.

```mermaid
graph TD
    Core["Core Orchestration"] --> Pipeline["pipeline.py (Orchestrator)"]
    Core --> Struct["structure.py (Heading & Math Parse)"]
    Core --> Spec["pipeline_spec.py (Stage Manifest)"]
    Core --> Stages["review_stages.py (Stage Helpers)"]
```

- `src/coarse/pipeline.py`: Main entry point exposing `review_paper()`. Manages stage progression and exception boundaries.
- `src/coarse/structure.py`: Analyzes `PaperText`, extracts table of contents, detects mathematical rigor, and builds `PaperStructure`.
- `src/coarse/pipeline_spec.py`: Defines pipeline stages, dependencies, and token multipliers for runtime planning and cost estimation.
- `src/coarse/review_stages.py`: Isolated stage execution helpers used by `pipeline.py`.

### 2. Multi-Agent Review Subsystem

All LLM agents inherit from `ReviewAgent` in `src/coarse/agents/base.py`. Agents output strongly typed Pydantic objects using Instructor.

```mermaid
graph TD
    Agents["Specialized Agents"] --> Overview["overview.py (Macro Feedback)"]
    Agents --> Section["section.py (Per-Section Comments)"]
    Agents --> Complete["completeness.py (Gap Detection)"]
    Agents --> Lit["literature.py (Search Engine)"]
    Agents --> Cross["cross_section.py (Synthesis)"]
    Agents --> Edit["editorial.py (Filter & Dedup)"]
    Agents --> Verify["verify.py (Proof Checker)"]
```

- `overview.py`: Generates 4 to 6 macro-level structural critiques of the paper.
- `section.py`: Executes section-by-section detailed comments with verbatim quote extraction.
- `completeness.py`: Identifies missing methodology, missing baseline comparisons, or omitted proofs.
- `literature.py`: Queries literature engines (Perplexity Sonar Pro, arXiv fallback) to verify novel contributions.
- `verify.py`: Performs adversarial mathematical verification on technical sections containing proof assertions.
- `editorial.py`: Filters duplicates, resolves contradictory statements, orders feedback, and enforces quality bars.

### 3. Document Ingestion & Extraction

Supports multiple input file types and OCR paths.

```mermaid
graph TD
    Ingest["Ingestion & QA"] --> Extr["extraction.py (Format Loader)"]
    Ingest --> ExtrOR["extraction_openrouter.py (OCR Transport)"]
    Ingest --> ExtrQA["extraction_qa.py (Vision QA)"]
    Ingest --> Garble["garble.py (Garble Detection)"]
```

- `src/coarse/extraction.py`: Primary router for document parsing.
- `src/coarse/extraction_openrouter.py`: Transport handler for OpenRouter file-parser plugin requests.
- `src/coarse/extraction_formats.py`: Fallback parsers for non-PDF file formats.
- `src/coarse/extraction_qa.py`: Uses vision LLMs to inspect visual quality when text garbling ratio exceeds threshold.
- `src/coarse/garble.py`: Detects text corruption, character replacement anomalies, and garbled output.

### 4. Quote Integrity & Verification

Guarantees that quotes cited in review comments exist in the source document.

```mermaid
graph TD
    Quote["Quote Engine"] --> Verify["quote_verify.py (Fuzzy Matcher)"]
    Quote --> Repair["agents/quote_repair.py (Context Repair)"]
```

- `src/coarse/quote_verify.py`: Performs multi-tiered fuzzy string matching (exact, normalized, substring, whitespace-agnostic).
- `src/coarse/agents/quote_repair.py`: Batched LLM re-anchoring pass for near-miss quotes prior to final verification.

### 5. LLM Transport & Model Registry

Unified abstraction layer over LiteLLM and Instructor.

```mermaid
graph TD
    LLM["LLM Layer"] --> Client["llm.py (LiteLLM + Instructor)"]
    LLM --> Models["models.py (Source of Truth)"]
    LLM --> Reg["model_registry.py (Catalog)"]
```

- `src/coarse/models.py`: Single source of truth for all LLM model identifier strings across the system.
- `src/coarse/llm.py`: Wraps API client initialization, retry strategies, cost tracking, and structured output parsing.
- `src/coarse/model_registry.py`: Catalog of LiteLLM context windows and pricing overrides.

### 6. Quality & Recall Evaluation Framework

The evaluation infrastructure benchmarks generated reviews against ground-truth expert human reviews.

```mermaid
graph TD
    Eval["Evaluation Framework"] --> Quality["quality.py (Judge Accuracy & Depth)"]
    Eval --> Recall["recall.py (Coverage & Recall Ratio)"]
    Eval --> Lang["lang_eval.py (Multilingual Consistency)"]
    Eval --> Scripts["scripts/run_eval.py (Batch Runner)"]
```

- `src/coarse/quality.py`: Scores accuracy, depth, quote precision, and clarity using single-judge or multi-judge panels.
- `src/coarse/recall.py`: Maps generated comments to ground-truth human comments to measure discovery rate.
- `src/coarse/lang_eval.py`: Evaluates consistency across supported languages to ensure identical technical rigor.

### 7. CLI & Headless Handoff Interfaces

Provides command-line interfaces for local interactive execution and remote handoff workflows.

```mermaid
graph TD
    CLI["Execution Interfaces"] --> RichCLI["cli.py (Interactive)"]
    CLI --> HeadlessCLI["cli_review.py (Headless)"]
    CLI --> Attach["cli_attach.py (Signal Watcher)"]
```

- `src/coarse/cli.py`: Typer-based interactive CLI with live Rich progress indicators.
- `src/coarse/cli_review.py`: Standalone CLI executable for headless local runs.
- `src/coarse/cli_attach.py`: Signal watcher for long-running headless background tasks.
- `src/coarse/headless_review.py`: Shared orchestration logic for headless execution.

### 8. Deployment Infrastructure

Serverless backend and web interface setup.

```mermaid
graph TD
    Infra["Cloud Infrastructure"] --> Modal["deploy/modal_worker.py (Queue)"]
    Infra --> DB["deploy/supabase_schema.sql (DB)"]
    Infra --> Web["web/ (Next.js Frontend)"]
```

- `deploy/modal_worker.py`: Serverless task queue implementation deployed on Modal.
- `deploy/supabase_schema.sql`: Database schema definition for review states, user tokens, and rate limits.
- `web/`: Next.js web application frontend.

---

## Data Models & Schema Contracts

Core data structures are defined in `src/coarse/types.py`:

- `PaperText`: Raw extracted text, token estimate, and garble ratio.
- `PaperStructure`: Parsed hierarchy, title, domain, sections, and math flag.
- `OverviewFeedback`: Macro issues including titles, bodies, and statuses.
- `DetailedComment`: Section comment containing verbatim quote and remediation feedback.
- `Review`: Complete output structure combining overall feedback and detailed comments.
- `CostEstimate`: Breakdown of expected token costs prior to pipeline execution.

---

## Review Pipeline Execution Flow

This flowchart illustrates the end-to-end data transformation from raw document ingestion through parallel agent review and final Markdown synthesis.

```mermaid
flowchart TD
    InputDoc["Input Document (PDF, TXT, MD, TeX, DOCX, HTML, EPUB)"] --> Extraction["extraction.py (Parse Document)"]
    Extraction --> QACheck{"Garble Detected?"}
    QACheck -- Yes --> VisionQA["extraction_qa.py (Vision LLM Check)"]
    QACheck -- No --> Structure["structure.py (Parse Headings & Math)"]
    VisionQA --> Structure

    Structure --> ParallelStage1["Parallel Execution Stage"]
    ParallelStage1 --> Calibrate["Domain Calibration"]
    ParallelStage1 --> LitSearch["agents/literature.py (Perplexity & arXiv)"]

    Calibrate --> OverviewPass["agents/overview.py (Macro Overview)"]
    LitSearch --> OverviewPass
    OverviewPass --> CompletenessPass["agents/completeness.py (Structural Gaps)"]

    CompletenessPass --> ParallelStage2["Parallel Section Review"]
    ParallelStage2 --> SectionAgents["agents/section.py (Per-Section Reviewers)"]
    ParallelStage2 --> ProofVerify["agents/verify.py (Proof Verification)"]

    SectionAgents --> CrossSection["agents/cross_section.py (Results vs Discussion)"]
    ProofVerify --> CrossSection

    CrossSection --> EditorialFilter["agents/editorial.py (Dedup & Quality Filter)"]

    EditorialFilter --> QuoteVerification1["quote_verify.py (Programmatic Match)"]
    QuoteVerification1 --> QuoteRepairPass["agents/quote_repair.py (LLM Repair)"]
    QuoteRepairPass --> QuoteVerification2["quote_verify.py (Final Re-Check)"]

    QuoteVerification2 --> Synthesis["synthesis.py (Render Markdown)"]
    Synthesis --> OutputMarkdown["Final Markdown Review (refine.ink format)"]
```
