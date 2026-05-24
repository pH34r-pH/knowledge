# Feature Specification: Raw Research Material Ingestion

**Feature Branch**: `000-raw-ingestion`

**Created**: 2026-05-24

**Status**: Draft

**Input**: User description: "Create a structured process for using the /arxiv and /research skills to download source academic material into source-named directories and generate summary reports in a standard format."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Source Material Download (Priority: P1)

Users must be able to ingest raw research papers from arXiv into a local, organized directory structure for offline access and archival.

**Why this priority**: establishes the foundational data layer. No summarization or synthesis can occur without first acquiring the primary source.

**Independent Test**: Can be fully tested by providing an arXiv URL, verifying the PDF and metadata land in `arxiv/`, and confirming file integrity.

**Acceptance Scenarios**:
1. **Given** a valid arXiv URL (e.g., `https://arxiv.org/abs/2605.22794`), **When** the ingestion command runs, **Then** the PDF is downloaded to `arxiv/2605.22794.pdf`
2. **Given** a valid arXiv URL, **When** the ingestion command runs, **Then** paper metadata (title, authors, published date, categories, abstract) is extracted and saved to `arxiv/2605.22794-meta.json`
3. **Given** a duplicate arXiv ID, **When** ingestion is triggered again, **Then** the system skips the download and reports the existing file path

### User Story 2 - Research Summary Generation (Priority: P1)

Users must be able to generate a structured markdown summary of an ingested paper and save it to the `reports/` directory.

**Why this priority**: transforms raw source material into readable, shareable intelligence. The summary is the primary artifact consumed by downstream features.

**Independent Test**: Can be fully tested by running the summarization command on an ingested paper and verifying the markdown file in `reports/` contains all required sections.

**Acceptance Scenarios**:
1. **Given** a paper has been ingested into `arxiv/`, **When** the summarization command runs, **Then** a markdown file is created at `reports/{arxiv-id}-summary.md`
2. **Given** a summary is generated, **When** the file is inspected, **Then** it contains sections: Title, Authors, Date, Abstract Summary, Key Findings, Methodology, Conclusions, and References
3. **Given** a summary already exists, **When** summarization is triggered again, **Then** the system reports the existing file and does not overwrite without a force flag

### User Story 3 - Structured Directory Conventions (Priority: P2)

The system must enforce a clear, predictable directory layout so that source material and outputs are always discoverable.

**Why this priority**: without a convention, the repository becomes unmaintainable as the volume of ingested material grows.

**Independent Test**: Can be fully tested by listing the repository root and verifying all top-level directories conform to the spec.

**Acceptance Scenarios**:
1. **Given** the repository root, **When** inspected, **Then** there exists an `arxiv/` directory containing only raw PDFs and metadata JSON
2. **Given** the repository root, **When** inspected, **Then** there exists a `reports/` directory containing only markdown summaries
3. **Given** the repository root, **When** inspected, **Then** there exists a `specs/` directory containing feature specifications in the spec-kit format
4. **Given** the repository root, **When** inspected, **Then** there exists a `.specify/` directory containing the spec-kit tooling and templates

### Edge Cases

- What happens when the arXiv API is unreachable or returns a 500 error during ingestion?
- What happens when a paper is withdrawn after initial ingestion — how is the metadata updated?
- How does the system handle an arXiv ID that does not exist?
- What happens if the PDF download is interrupted mid-stream?
- How are versioned arXiv papers handled (e.g., `2605.22794v1` vs `2605.22794v2`)?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST accept an arXiv URL or ID as input for ingestion
- **FR-002**: System MUST download the PDF to `arxiv/{id}.pdf`
- **FR-003**: System MUST extract and save metadata to `arxiv/{id}-meta.json`
- **FR-004**: System MUST generate a markdown summary to `reports/{id}-summary.md`
- **FR-005**: System MUST skip existing files on re-ingestion unless a `--force` flag is provided
- **FR-006**: System MUST verify downloaded PDF file size is non-zero and report corruption
- **FR-007**: System MUST use the spec-kit conventions for all feature documentation in `specs/`
- **FR-008**: System MUST include the arXiv skill helper scripts under `.specify/scripts/`

### Key Entities *(include if feature involves data)*
- **Source Paper**: Raw PDF and metadata representing a single academic publication
- **Ingestion Record**: Metadata JSON tracking download status, timestamp, and file paths
- **Summary Report**: Markdown artifact synthesizing the paper's contents for human consumption

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Ingestion of a valid arXiv paper completes end-to-end in under 30 seconds on a standard internet connection
- **SC-002**: Summaries contain all 8 required sections and are readable without reference to the original PDF
- **SC-003**: 100% of ingested papers have both a PDF and a metadata file in `arxiv/`
- **SC-004**: No duplicate downloads occur on repeated ingestion of the same ID

## Assumptions
- Users have `curl` and `python3` available on their system
- Internet connectivity is available during ingestion (summarization may be done offline once PDF is local)
- The arXiv API and PDF endpoints remain stable and publicly accessible
- The user has write permissions to `~/repos/knowledge/`
- Markdown is the preferred summary format for downstream consumption
