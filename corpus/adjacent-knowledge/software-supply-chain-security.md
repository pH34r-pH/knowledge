---
title: "Software supply-chain security: inventory, provenance, and policy"
pillar: adjacent-knowledge
method: deep-research
sources: 6
confidence: high
date: 2026-08-07
---

# Software supply-chain security: inventory, provenance, and policy

## What it is

Supply-chain security is evidence-driven artifact delivery: establish what an artifact contains, how it was produced, and whether its delivery path satisfies a policy. These are separate questions. An SBOM inventories components and relationships.[5] Provenance is verifiable information describing where, when, and how an artifact was produced.[2] Treat verification as the policy step that checks attestations, identities, digests, and organizational requirements before promotion or deployment.

Conflating the layers creates bad security claims. An SBOM is not a malware verdict, and a provenance record shifts trust to the identities, build system, and verification policy used to produce and accept it. A SLSA level is not a universal risk score. A recent SoK identifies transparency, validity, and separation as key secure-supply-chain properties.[1]

## When to reach for it

Apply this discipline to release automation, third-party dependencies, containers, internal packages, and high-impact deployment paths. It is especially valuable where a consumer cannot directly inspect the build environment.

It does not replace code review, maintainer security, vulnerability management, incident response, or least privilege. Do not claim a framework would have prevented a particular incident unless its controls are mapped to that incident’s actual attack path.

## How it works

A practical path is source revision → isolated build → artifact digest → signed attestation/provenance → verification at admission or deploy. The provenance binds claims about inputs, build definition, builder identity, and output to a concrete artifact digest. SLSA organizes assurance requirements into levels; in-toto supplies an attestation-oriented framework; SPDX specifies a component/relationship data model for SBOM-style inventory.[2][3][4][5]

The verifier is the enforcement point. It checks that the artifact digest is expected, the provenance/identity chain meets policy, and required inventory evidence exists. Retain the evidence so an incident response can identify affected artifacts and re-evaluate prior promotions. A record that is generated but never verified is audit data, not a delivery control.

## Trade-offs

Trust shifts rather than disappears: to identity issuers, CI builders, signing systems, policy configuration, and metadata accuracy. Adoption is also nontrivial. An analysis of 1,523 SLSA-related GitHub issues found complex implementation and unclear communication as primary challenges, with provenance generation and verification as improvement areas.[6]

Controls add build integration, credential/identity design, verification maintenance, and false-rejection risk. Start with the most consequential artifact boundary and an explicit threat model; demanding complete evidence everywhere before any team can ship often produces bypasses instead of security.

## In practice

Require an immutable artifact digest, an approved builder identity, provenance that names expected source/build inputs, and an SBOM for deployable artifacts. Verify those properties in CI promotion and deployment admission, not only in a release report. Test verifier failures deliberately: wrong digest, untrusted builder, missing provenance, and revoked identity.

Start with one artifact class and one consuming environment. Define who may build it, what source reference and dependency policy are acceptable, where attestations are stored, and which component enforces the decision. Make the verifier’s denial explainable enough that a release engineer can distinguish a missing record from an unexpected identity or an invalid digest. A security control that only experts can diagnose will eventually become a bypass request.

Keep emergency release policy explicit. A break-glass path may be necessary, but it should leave a durable, reviewable exception rather than silently weakening normal verification. That lets post-incident work ask the useful question: which evidence or policy was absent, and how should the standard path change?

Inventory freshness is a separate operating problem. Rebuild or re-attest when source, dependencies, builder configuration, or signing identity changes, and make it clear whether an SBOM describes source intent, a build input set, or the delivered artifact. During an incident, the ability to query that distinction is often more useful than a long component list produced after the fact. Practice revocation and re-verification before the first compromised identity forces a rushed response.

## Further reading

1. Debroy et al. — *SoK: Analysis of Software Supply Chain Security* — https://arxiv.org/abs/2406.10109
2. SLSA — *Provenance* — https://slsa.dev/spec/v1.1/provenance
3. SLSA — *Security levels* — https://slsa.dev/spec/v1.1/levels
4. in-toto — *Documentation and technical specification* — https://in-toto.io/docs/
5. SPDX — *3.0.1 model specification* — https://spdx.github.io/spdx-spec/v3.0.1/model/
6. Tamanna et al. — *Analyzing Challenges in Deployment of the SLSA Framework* — https://arxiv.org/abs/2409.05014
