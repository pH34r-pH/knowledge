# Implementation Plan: Raw Research Material Ingestion

**Branch**: `000-raw-ingestion` | **Date**: 2026-05-24 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/000-raw-ingestion/spec.md`

**Note**: This template is filled in by the `__SPECKIT_COMMAND_PLAN__` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement a structured ingestion pipeline for academic research papers sourced from arXiv. The feature provides: (1) automated download of PDFs and metadata into `arxiv/`, (2) generation of structured markdown summaries in `reports/`, and (3) enforcement of directory conventions aligned with spec-kit standards. The primary interface is the command line using curl, Python stdlib, and the Hermes arxiv skill.

## Technical Context

**Language/Version**: Bash, Python 3, Markdown, JSON

**Primary Dependencies**: `curl`, `python3` (stdlib only), arXiv REST API, Semantic Scholar API (optional)

**Storage**: Local filesystem — `arxiv/` for raw PDFs and JSON metadata, `reports/` for markdown summaries

**Testing**: Manual verification of file existence, size checks, and markdown readability

**Target Platform**: Linux (Jetson Orin Nano 8GB), headless / CLI-first

**Project Type**: local-tooling (research data pipeline)

**Performance Goals**: Ingestion < 30s per paper, summary generation < 10s after PDF is cached

**Constraints**: No external Python dependencies (pip install prohibited on target platform); no PII; all operations must be idempotent

**Scale/Scope**: Personal research vault; expected concurrent ingestion < 1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Assessment | Notes |
|-----------|------------|-------|
| Security-First | PASS | No execution of downloaded content; only curl and file writes |
| Privacy/Anonymity | PASS | No user identity transmitted to arXiv; read-only public API access |
| Defense in Depth | PASS | File size validation; read-only filesystem where possible |
| Secure Defaults | PASS | Skips re-download by default; no overwrite without force |
| Continuous Monitoring | N/A at this phase | Integrity checks via file size exist |

## Project Structure

### Documentation (this feature)

```text
specs/000-raw-ingestion/
├── spec.md              # Feature specification
├── plan.md              # This file
├── research.md          # Phase 0 output (arxiv API quirks, rate limits)
├── data-model.md        # Phase 1 output (metadata JSON schema, summary markdown schema)
├── contracts/           # Phase 1 output (API request/response shapes)
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
~/repos/knowledge/
├── .specify/            # Spec-kit tooling and templates (copied from blue-swallow-society)
├── specs/               # Feature specifications
│   └── 000-raw-ingestion/
├── arxiv/               # Ingested PDFs and metadata JSON
├── reports/             # Generated markdown summaries
└── scripts/             # Helper scripts for ingestion and summarization
    ├── ingest_arxiv.py
    └── summarize_paper.py
```

**Structure Decision**: Single-directory research vault. `arxiv/` and `reports/` are flat (no subdirectories) keyed by arXiv ID to keep the navigation model trivial.

## Complexity Tracking

> No constitution violations or unjustified complexity detected. Feature stays within single-directory filesystem scope with stdlib-only tooling.
