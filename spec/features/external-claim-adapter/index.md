---
schema_version: 1
document_id: knowledge/external-claim-adapter
role: feature
feature_id: external-claim-adapter
revision: 1
target_status: mature-complete-product
approval_status: proposed
artifact_acceptance: candidate-review
delivery_status: designed-only
delivery_evidence: []
qualifiers: [living-spec-paradigm, brownfield-characterized, spec-kit-mapped]
---

# External claim adapter: offline registry integrity

This feature is the living form of the integrity core of `specs/002-external-claim-adapter/`, which stays in place as retained history. It characterizes what the offline registry validator checks and reports today. Live source readback, reviewed-source freshness, source admission, the public bibliography crosswalk and documentation hygiene are outside this specification.

## Product description

The adapter gives downstream repositories stable, claim-level external evidence records that they can validate offline from a pinned `pH34r-pH/knowledge` commit. Three registries hold the records: external works (`KWRK-`), external claims (`KCLM-`) and knowledge evidence (`KEVD-`). A validator checks the registries' integrity without network access and fails closed on any violation.

A real work does not validate a proposition attributed to it. A claim is accepted only when evidence for it carries a fully passed citation audit. Corrections create new records linked by supersession, and records are never silently rewritten. Evidence states honestly how much can be validated offline.

## Actors and acceptance scenarios

| Story | Actor and outcome | Independent acceptance scenarios |
| --- | --- | --- |
| ECA-US1 | A downstream repository or CI validates the registries offline | AS1: valid registries, including empty ones, validate with no network access and a zero exit. AS2: any integrity violation produces a nonzero exit and names the offending records. AS3: the exact registry state has a stable identity that can be pinned and compared. |
| ECA-US2 | A maintainer is protected from unsupported attribution | AS1: a claim marked accepted without accepted evidence whose citation audit fully passed fails validation, even when its work is real. AS2: evidence whose entailment failed never qualifies a claim. |
| ECA-US3 | A maintainer corrects records without rewriting history | AS1: a record may supersede another record of the same kind and the superseded record stays valid. AS2: a self-reference, a missing target or a cycle fails. |
| ECA-US4 | A consumer trusts the stated offline level | AS1: only the four defined levels are accepted. AS2: full and claim-evidence levels require support text bound to its hash, and full offline evidence requires a local file bound to its hash. |

## Functional requirements

| ID | Required observable behavior |
| --- | --- |
| ECA-FR-001 | The canonical registries are `references/external/works.jsonl`, `claims.jsonl` and `evidence.jsonl`, plus the governance source-review file `governance/source-reviews.jsonl`, which reads as empty when absent. Each must be a regular file inside the repository root; a symbolic link, or a path that resolves outside the root, is refused. A missing registry file is an input error. |
| ECA-FR-002 | Each non-blank line of a registry is one UTF-8 JSON object with no duplicate field names. A line that is not valid JSON, is not an object, or repeats a field is an input error that names the file and line. A set of empty registries is valid. |
| ECA-FR-003 | Every record has a string `id` and a matching `type`: works are `KWRK-` followed by six digits with type `ExternalWork`, claims are `KCLM-` followed by six digits with type `ExternalClaim`, and evidence is `KEVD-` followed by six digits with type `KnowledgeEvidence`. An ID is unique across all three registries; each occurrence after the first is reported as a duplicate. |
| ECA-FR-004 | A claim's `work_id` names an existing work and an evidence record's `claim_id` names an existing claim. A broken reference is an error. |
| ECA-FR-005 | A record's optional `supersedes` names an existing record of the same kind other than itself, and supersession within a kind has no cycle. A cycle is reported once, starting from its smallest ID. Superseded records remain valid. |
| ECA-FR-006 | An evidence record's `offline_validation` is exactly one of `OFFLINE_FULL`, `OFFLINE_CLAIM_EVIDENCE`, `METADATA_ONLY` or `ONLINE_REVALIDATION_REQUIRED`. `OFFLINE_FULL` and `OFFLINE_CLAIM_EVIDENCE` require non-blank `support_text` and a lowercase hexadecimal SHA-256 `support_text_sha256` equal to the SHA-256 of the support text encoded as UTF-8. `OFFLINE_FULL` also requires a string `local_path`. |
| ECA-FR-007 | A present `local_path` is a non-blank string naming a regular file inside the repository root, and `local_content_sha256` is a lowercase hexadecimal SHA-256 equal to the SHA-256 of that file. A path that leaves the root, a missing file, and an absent, malformed or mismatched hash are each errors. |
| ECA-FR-008 | A claim with status `ACCEPTED` requires at least one evidence record for it with status `ACCEPTED` whose audit has `resolution` and `support_span` and `entailment` all `PASSED` and `liveness` either `PASSED` or `ARCHIVED`. Evidence with any other audit result, an absent audit, or another status does not qualify the claim. |
| ECA-FR-009 | A work record carries no `source_review` or `permitted_uses`; source policy lives only in the governance source-review file, whose own rules are outside this specification. Validation also applies those governance checks. |
| ECA-FR-010 | `python tools/validate_external_claim_adapter.py --root PATH` validates the registries under `PATH`, which defaults to the current directory. A valid set prints `OK: external claim adapter integrity valid` and exits 0. Integrity errors print one `ERROR: ...` line each on standard error, then `FAILED: N adapter error(s)`, and exit 1; all errors found in the three registries are reported in one run. An input error prints `ERROR: ...` and exits 2. |
| ECA-FR-011 | `--registry-sha256` prints the registry identity and exits 0 without validating the records. The identity is the SHA-256 over, for each of the four registry files in the order works, claims, evidence, source reviews, its relative path, a NUL byte and the raw SHA-256 digest of its bytes, with an absent source-review file counting as empty. |
| ECA-FR-012 | Validation in its default mode makes no network request. |

## Success criteria

| ID | Observable measure |
| --- | --- |
| ECA-SC-001 | Every independent case in the external-claim-adapter test contract passes. |

## Boundaries

The validator checks the audit results recorded on evidence records; it does not re-run the citation-integrity pipeline that produced them. This feature is an evidence adapter, not a second research corpus. It does not specify the live source readback, the reviewed-source freshness gate, source admission and review policy, the public bibliography crosswalk, the documentation hygiene checks or the corpus citation-integrity pipeline. It does not compute the content hash that downstream repositories pin for a record; each consumer defines that hash, and the plan records the definition domain-scaling-lab uses.
