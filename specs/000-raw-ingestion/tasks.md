# Tasks: Raw Research Material Ingestion

**Input**: Design documents from `/specs/000-raw-ingestion/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual file verification and markdown readability checks.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story tag (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `arxiv/`, `reports/`, `scripts/` at repository root

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and spec-kit adoption

- [x] T001 Verify `.specify/` directory exists with templates, scripts, and constitution
- [x] T002 [P] Verify `specs/` directory exists and follows `NNN-feature-name/` convention
- [x] T003 [P] Verify `arxiv/` directory exists for raw PDF storage
- [x] T004 [P] Verify `reports/` directory exists for summary markdown storage

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helper scripts that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 Implement `scripts/ingest_arxiv.py` to accept an arXiv ID, download PDF to `arxiv/{id}.pdf`, and extract metadata to `arxiv/{id}-meta.json`
- [ ] T006 [P] Implement `scripts/summarize_paper.py` to read an arXiv ID, parse metadata and PDF, and write a structured markdown summary to `reports/{id}-summary.md`
- [ ] T007 [P] Add idempotency checks in both scripts — skip existing files unless `--force` is passed
- [ ] T008 Add file integrity validation (non-zero PDF size, valid JSON metadata) in `scripts/ingest_arxiv.py`

**Checkpoint**: Foundation ready — scripts exist, directories are correct, idempotency works

---

## Phase 3: User Story 1 - Source Material Download (Priority: P1) 🎯 MVP

**Goal**: Users can ingest arXiv papers into `arxiv/` with PDF and metadata

**Independent Test**: Run `python3 scripts/ingest_arxiv.py 2605.22794`, verify `arxiv/2605.22794.pdf` and `arxiv/2605.22794-meta.json` exist

### Tests for User Story 1

- [ ] T009 [P] [US1] Manual test: valid arXiv ID downloads PDF in < 30s
- [ ] T010 [P] [US1] Manual test: metadata JSON contains title, authors, date, categories, abstract
- [ ] T011 [P] [US1] Manual test: re-running ingestion skips download and reports existing file

### Implementation for User Story 1

- [ ] T012 [US1] Implement arXiv API query in `scripts/ingest_arxiv.py` using `urllib.request` (stdlib only)
- [ ] T013 [P] [US1] Implement PDF download via `urllib.request` to `arxiv/{id}.pdf`
- [ ] T014 [P] [US1] Implement Atom XML parsing to extract metadata and write `arxiv/{id}-meta.json`
- [ ] T015 [US1] Add error handling for invalid arXiv IDs, network failures, and withdrawn papers

**Checkpoint**: User Story 1 is fully functional and independently testable

---

## Phase 4: User Story 2 - Research Summary Generation (Priority: P1)

**Goal**: Users can generate structured markdown summaries from ingested papers

**Independent Test**: Run `python3 scripts/summarize_paper.py 2605.22794`, verify `reports/2605.22794-summary.md` contains all required sections

### Tests for User Story 2

- [ ] T016 [P] [US2] Manual test: summary markdown contains Title, Authors, Date, Abstract Summary, Key Findings, Methodology, Conclusions, and References sections
- [ ] T017 [P] [US2] Manual test: summary is readable without opening the original PDF
- [ ] T018 [P] [US2] Manual test: re-running summarization reports existing file and does not overwrite

### Implementation for User Story 2

- [ ] T019 [US2] Implement markdown template with all 8 required sections in `scripts/summarize_paper.py`
- [ ] T020 [P] [US2] Implement metadata reader in `scripts/summarize_paper.py` to populate frontmatter
- [ ] T021 [US2] Implement PDF text extraction via `pymupdf` or `pdfplumber` (fallback to metadata-only summary if unavailable)
- [ ] T022 [US2] Add `--force` flag support to allow overwriting existing summaries

**Checkpoint**: User Story 2 is independently functional

---

## Phase 5: User Story 3 - Structured Directory Conventions (Priority: P2)

**Goal**: Repository layout follows predictable spec-kit conventions

**Independent Test**: List repository root and verify all directories conform

### Tests for User Story 3

- [ ] T023 [P] [US3] Manual test: `arxiv/` contains only `.pdf` and `-meta.json` files
- [ ] T024 [P] [US3] Manual test: `reports/` contains only `-summary.md` files
- [ ] T025 [P] [US3] Manual test: `specs/` contains only numbered feature directories with spec.md/plan.md/tasks.md

### Implementation for User Story 3

- [ ] T026 [US3] Document directory conventions in `README.md` at repository root
- [ ] T027 [US3] Add `.gitignore` to ignore any stray files in `arxiv/` or `reports/`
- [ ] T028 [US3] Verify `.specify/` contents were fully copied from upstream project

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T029 [P] Add a master `Makefile` or `justfile` with `ingest ID=` and `summarize ID=` targets
- [ ] T030 [P] Document rate limits and retry logic in `docs/arxiv-api.md`
- [ ] T031 [P] Add BibTeX generation option to `scripts/ingest_arxiv.py`
- [ ] T032 Run end-to-end validation: ingest a paper, summarize it, verify all files exist

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3–5)**: All depend on Foundational phase; can proceed sequentially or in parallel if staffed
- **Polish (Phase 6)**: Depends on all desired user stories

### User Story Dependencies

- **US1 (P1)**: No story dependencies; can start after Phase 2
- **US2 (P1)**: Depends on US1 (needs ingested PDF/metadata); can start immediately after US1
- **US3 (P2)**: Documentation and conventions; can run in parallel with US1/US2

### Within Each User Story

- Directory setup before script implementation
- Download logic before metadata extraction
- Metadata availability before summarization

### Parallel Opportunities

- All directory verification tasks in Phase 1 can run in parallel
- US3 documentation can be written in parallel with US1/US2 implementation
- Polish tasks can be drafted during implementation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
