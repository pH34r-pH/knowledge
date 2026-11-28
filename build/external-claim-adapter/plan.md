---
artifact: implementation-plan
revision: 1
acceptance: candidate-review
---

# External claim adapter implementation plan

This plan owns the technical choices for the adapter's offline registry integrity. Behavior and acceptance live in the feature specification; requirements are referenced by ID. The earlier plan in `specs/002-external-claim-adapter/plan.md` stays as history.

## Implementation targets and direct path

**Component and consumers.** `tools/validate_external_claim_adapter.py` implements ECA-FR-001 through ECA-FR-012 over the registries in `references/external/` and `governance/source-reviews.jsonl`. The real consumers are the `offline-integrity` job of `.github/workflows/external-claim-adapter.yml`; Fleet, which qualifies a pinned Knowledge commit from that job's result; the domain-scaling-lab validator, which runs the command and reads records at a pinned commit; and maintainers.

**Current and target implementation.** The implementation is a single Python module that uses only the standard library and runs on Python 3.12 in CI. This is the accepted implementation decision; no port is planned.

**Reuse.** `json` with an object-pairs hook rejects duplicate fields; `hashlib` supplies SHA-256 and `hmac.compare_digest` the constant-time identity comparison used by the source report; `pathlib` resolves and confines paths. The module imports `source_admission` and `source_readback`, which belong to unspecified areas.

**Direct path and state.** The command takes one in-memory snapshot of the four registry files, validates the three adapter registries in a single pass that collects every error, and only if there are none applies the governance source-review checks. It keeps no state beyond that snapshot and writes nothing. The repository root is the only runtime input. Identity patterns, offline levels and audit values are fixed at build time.

**Layer dispositions.**

| Layer | Disposition | Duty |
| --- | --- | --- |
| Registry snapshot and confinement | Retain | Consistent reads inside the root (ECA-FR-001, ECA-FR-011). |
| Strict JSONL loader | Retain | Duplicate-field and shape rejection (ECA-FR-002). |
| Row validation | Retain | Identity, references, supersession, offline levels, local evidence and the acceptance gate (ECA-FR-003 to ECA-FR-008). |
| Source-review application | Retain, unspecified | Governance policy checks applied after row validation (ECA-FR-009). |
| Source report and live readback | Preserve as an external boundary | Separate, unspecified modes selected by `--source-report`. |

**Objective and preserved acceptance.** Preserve every requirement. A relaxed check or a downgraded error is never acceptable: any deterministic integrity failure is a hard failure.

**Unresolved decisions and local discretion.** Local discretion covers private helper names and error ordering within a message group. Whether the content hash that consumers pin should be computed by the adapter is undecided; today each consumer computes it.

## Public interface

Other code relies on these names, paths and formats.

- **Command.** `python tools/validate_external_claim_adapter.py --root PATH`, `--registry-sha256`, and the source-report options (`--source-report`, `--expected-registry-sha256`, `--as-of`, `--check-live`), which are outside this specification. Exit codes: 0 valid, 1 integrity errors, 2 input errors. Output formats: `OK: external claim adapter integrity valid` on standard output; `ERROR: MESSAGE` lines and `FAILED: N adapter error(s)` on standard error.
- **Error messages.** Each starts with the record ID and a colon. Formats that tests and logs rely on: `duplicate adapter id: ID`; `invalid work supersedes target 'X'` (and `claim`, `evidence`); `broken work_id 'X'`; `broken claim_id 'X'`; `cyclic work supersession: A -> B -> A` (and `claim`, `evidence`); `invalid offline_validation 'X'`; `OFFLINE_FULL requires local_path`; `LEVEL requires support_text` and `requires support_text_sha256`; `support_text_sha256 mismatch`; `local evidence file missing: PATH`; `local_path requires local_content_sha256`; `local evidence hash mismatch: PATH`; `local_path escapes repository root`; `ACCEPTED claim lacks ACCEPTED evidence with a fully passed citation audit`.
- **Registries.** `references/external/works.jsonl`, `claims.jsonl` and `evidence.jsonl`, and `governance/source-reviews.jsonl`. A work carries `id`, `type` and optional `supersedes`; a claim `id`, `type`, `work_id`, `status` and optional `supersedes`; an evidence record `id`, `type`, `claim_id`, `status`, `offline_validation`, `audit` with `resolution`, `support_span`, `liveness` and `entailment`, optional `support_text`, `support_text_sha256`, `local_path`, `local_content_sha256` and `supersedes`. Other fields are descriptive and not validated here.
- **Module exports.** `validate_adapter(root) -> list[str]`, `registry_fingerprint(snapshot) -> str`, `REGISTRY_FILES`, `SOURCE_REVIEWS`, `load_jsonl(path)` and `main(argv)`.
- **Qualification by Fleet.** Fleet requires the push run of workflow `external-claim-adapter.yml` and its job `offline-integrity` to succeed on the exact pinned SHA, and hashes `references/external/**`, `tools/validate_external_claim_adapter.py`, `tools/test_external_claim_adapter.py` and `specs/002-external-claim-adapter/**`. This plan keeps that workflow unchanged.
- **Consumer-defined record hash.** domain-scaling-lab pins `(repository, commit, object_id, content_sha256, offline_validation)` and computes `content_sha256` as the SHA-256 of the record serialized as UTF-8 JSON with sorted keys, compact separators and non-ASCII characters preserved. The adapter does not compute it, so a change to how records are serialized or ordered within a line is not detected here.

## Prior-art decisions

Strict JSON object parsing with duplicate-field rejection avoids the ambiguity of last-value-wins. Collecting every error in one pass, rather than stopping at the first, lets a maintainer fix a registry in one round. Detecting cycles with a per-kind path walk is linear in the number of records. No code is copied.
