# Feature Specification: External Claim Adapter

**Feature Branch**: `002-external-claim-adapter`

**Created**: 2026-09-03

**Status**: Draft

**Input**: issue #2 — provide stable, claim-level external evidence records that downstream research repositories can validate offline from a pinned `pH34r-pH/knowledge` commit.

## User Scenarios & Testing

### User Story 1 — Resolve a stable external claim offline (P1)
A downstream repository pins one knowledge commit plus a stable claim ID and can resolve the attributed work, proposition, support metadata, audit status, and offline-validation level without web access.

**Independent Test**: load a fixture claim from a checked-out pinned commit with networking disabled; validate its work/evidence references and hashes.

### User Story 2 — Fail closed on unsupported attribution (P1)
A paper may be real while a proposition attributed to it is unsupported. The adapter must distinguish source identity from claim entailment.

**Independent Test**: mutate a fixture proposition or support hash and verify validation fails.

### User Story 3 — Preserve epistemic history (P1)
Corrections, staleness, or stronger evidence create a new record linked by supersession; prior records remain addressable at historical commits.

### User Story 4 — Respect offline/copyright boundaries (P1)
Records distinguish `OFFLINE_FULL`, `OFFLINE_CLAIM_EVIDENCE`, `METADATA_ONLY`, and `ONLINE_REVALIDATION_REQUIRED`; no status overstates what can legally and technically be preserved.

## Requirements

- **FR-001**: Define stable IDs for `ExternalWork`, `ExternalClaim`, and `KnowledgeEvidence`.
- **FR-002**: `ExternalWork` MUST carry canonical source identity where available (DOI/arXiv/OpenReview/ISBN/etc.) plus normalized title/authors/date/venue/source metadata.
- **FR-003**: `ExternalClaim` MUST contain one tightly scoped normalized proposition and reference exactly one `ExternalWork`.
- **FR-004**: `KnowledgeEvidence` MUST tie an `ExternalClaim` to support-location/span metadata, content/support hash where possible, ingestion date, citation-integrity audit result, and offline-validation level.
- **FR-005**: Acceptance of an `ExternalClaim` MUST require the existing corpus citation-integrity gate: source resolution, quote-span/paraphrase support, liveness/archival handling, and independent entailment.
- **FR-006**: A valid work alone MUST NOT validate an attributed claim.
- **FR-007**: Records MUST be machine-readable and deterministically validated offline.
- **FR-008**: Stable records MUST be consumable by downstream repositories using `(knowledge commit, object ID, content hash)`; consumers MUST NOT need live URLs for ordinary validation.
- **FR-009**: Historical records MUST NOT be silently rewritten. Corrections/staleness use explicit supersession relations.
- **FR-010**: Full copyrighted text MUST NOT be required or redistributed; metadata plus permitted evidence records are sufficient when full preservation is unavailable.
- **FR-011**: The feature MUST update corpus documentation/ledger as required by repository governance and preserve current citation-integrity standards.

## Key Entities

- **ExternalWork (`KWRK-*`)** — canonical bibliographic/source identity.
- **ExternalClaim (`KCLM-*`)** — exact proposition attributed to a work.
- **KnowledgeEvidence (`KEVD-*`)** — auditable local support record for a claim.

## Success Criteria

- **SC-001**: An offline validator resolves all references and hashes for valid fixture records with no network access.
- **SC-002**: Duplicate IDs, broken references, malformed hashes, unsupported offline status, or claim/evidence mismatch fail closed.
- **SC-003**: A downstream `domain-scaling-lab` snapshot can pin a knowledge commit and claim ID and validate the adapter record offline.
- **SC-004**: No accepted record bypasses the existing citation-integrity gate.

## Boundaries

This feature is an evidence adapter, not a second research corpus and not a replacement for corpus articles. It exposes atomic verified claims from the same evidence discipline. Live web retrieval remains an ingestion/refresh path only.