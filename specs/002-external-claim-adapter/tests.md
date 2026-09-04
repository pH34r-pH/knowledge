# Tests: External Claim Adapter

## Deterministic offline tests

### T-001 Valid fixture resolves offline
Given one `ExternalWork`, one `ExternalClaim`, and one `KnowledgeEvidence` fixture with valid references/hashes and a passed audit, the validator exits zero with networking unavailable.

### T-002 Duplicate IDs fail
Duplicate IDs within or across the adapter namespace must fail closed.

### T-003 Broken work/claim/evidence references fail
- claim references missing work;
- evidence references missing claim;
- supersession references missing object.

All fail.

### T-004 Hash drift fails
If a declared content/support hash does not match locally preserved evidence material, validation fails.

### T-005 Audit gate cannot be bypassed
An evidence record with unresolved source, failed entailment, failed quote-span/paraphrase support, or invalid audit status cannot qualify an external claim as accepted.

### T-006 Offline level is truthful structurally
Only these values are accepted: `OFFLINE_FULL`, `OFFLINE_CLAIM_EVIDENCE`, `METADATA_ONLY`, `ONLINE_REVALIDATION_REQUIRED`. Records claiming `OFFLINE_FULL` must include the locally required preservation metadata defined by the final schema.

### T-007 Real paper / unsupported proposition fails
Use a fixture where work identity is valid but the evidence record is absent or explicitly non-entailing; the attributed claim must not validate.

### T-008 Supersession preserves history
A newer claim/evidence record may supersede an older record, but the old record remains syntactically valid and addressable at its historical commit. Invalid self/cyclic supersession fails where detectable.

## Cross-repository acceptance test

### T-009 Domain-scaling consumer
At a pinned knowledge commit, `domain-scaling-lab` resolves one external-claim ID and expected hash using only a local checkout/copy of the adapter records. No live source fetch is needed.

## Citation-integrity integration test

### T-010 Seed record provenance
For each seeded accepted adapter claim, verify its audit metadata traces to an existing resolved source pool / corpus audit or is freshly run through the same citation-integrity gate before commit.

## Failure policy
Any deterministic integrity failure is a hard failure. Do not downgrade malformed evidence to a warning merely to preserve a downstream claim.