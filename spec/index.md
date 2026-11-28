---
schema_version: 1
document_id: knowledge/overview
role: overview
revision: 1
target_status: mature-complete-product
approval_status: proposed
artifact_acceptance: unspecified
delivery_status: designed-only
delivery_evidence: []
qualifiers: [living-spec-paradigm, spec-kit-mapped]
---

# Knowledge

Knowledge is a structured research corpus with a citation-integrity gate and an external claim adapter that lets downstream repositories pin and validate evidence records offline. Its behavior is described feature by feature in `specs/`, which stays in place as retained history and as the home of unmapped features.

This living specification is onboarded one area at a time. The [external claim adapter's offline registry integrity](features/external-claim-adapter/index.md) is the first specified area. Every other area, including raw ingestion, the corpus population loop, live source readback and freshness, source admission, the bibliography crosswalk and documentation hygiene, is explicitly unspecified here until it is onboarded; its authority remains the matching `specs/<NNN-feature>/` package.
