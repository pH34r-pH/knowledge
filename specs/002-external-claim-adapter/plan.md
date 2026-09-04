# Implementation Plan: External Claim Adapter

## Objective
Add a small machine-readable evidence adapter to `pH34r-pH/knowledge` without weakening or duplicating the existing corpus citation-integrity process.

## Design

### Storage
Use a dedicated adapter tree under `references/` (final exact path may be adjusted if existing repo conventions require it):

```text
references/
  works.jsonl
  claims.jsonl
  evidence.jsonl
  schema/
    work.schema.json
    claim.schema.json
    evidence.schema.json
```

Records are append/supersede oriented. Stable IDs are repository-global within each prefix.

### Identity
- `KWRK-000001` — work identity
- `KCLM-000001` — normalized external proposition
- `KEVD-000001` — supporting evidence/audit record

Downstream identity is `(repository=pH34r-pH/knowledge, commit SHA, object ID, content SHA-256)`.

### Validation
Implement a dependency-light deterministic validator that:
1. parses every JSONL record;
2. enforces unique IDs and schemas;
3. resolves `claim -> work` and `evidence -> claim` references;
4. verifies declared content/support hashes when local material is present;
5. enforces valid offline-validation levels;
6. fails accepted claims lacking a passed citation-integrity audit;
7. detects invalid supersession links/cycles where practical;
8. runs without network access.

The validator does **not** redo live DOI/arXiv resolution offline. It verifies the durable result of the ingestion audit. Online ingestion remains responsible for source resolution/liveness/entailment.

### Consumer contract
`domain-scaling-lab` may store only:
- pinned knowledge commit;
- adapter object ID;
- optional expected content SHA-256;
- offline-validation level cached for display.

Bibliographic truth remains owned by this repository.

### Ingestion integration
The corpus research workflow should be extended later so a verified source pool can optionally emit atomic work/claim/evidence records. Phase 1 may seed records manually from already-audited corpus material, but records cannot be marked accepted unless their evidence meets the existing citation gate.

## Phases

1. **Schema + fixtures** — record formats, IDs, offline levels, valid/invalid fixtures.
2. **Offline validator** — deterministic integrity checks and tests.
3. **Seed claims** — a small set needed by `domain-scaling-lab` independent-convergence records.
4. **Corpus integration** — update README/ledger/process docs and optionally the populate-corpus skill to emit adapter records.
5. **Cross-repo acceptance** — pin a knowledge commit from `domain-scaling-lab` and validate one claim offline.

## Non-goals
- mirroring the entire web;
- redistributing restricted full text;
- replacing prose corpus articles;
- assigning truth to a scientific proposition beyond what the cited source/evidence actually entails;
- allowing downstream consumers to mutate canonical work metadata.