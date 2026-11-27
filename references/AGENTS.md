# Reference and evidence boundary

`references/external/` is the machine-readable provenance boundary for resolved works,
claims, evidence, schemas, and scoped formal imports. It feeds citation audits and
adapter validation; it is not a second article index.

- Change the registry or schema when the external-source contract changes.
- Preserve exact source IDs, canonical URLs, quoted evidence, dates, and audit scope.
- Keep dated `*-audit-*.json` records and `*.md` source notes as history. A later audit
  can narrow or correct a claim only with an explicit scope; it must not erase the
  earlier record.
- Put explanatory knowledge in [`../corpus/`](../corpus/) and research procedure in
  [`../BUILDING.md`](../BUILDING.md) or the relevant skill.

Validate from the repository root with:

```bash
python tools/test_external_claim_adapter.py
python tools/validate_external_claim_adapter.py --root .
git diff --check
```

## Reviewed source metadata

Record each reviewed use in [the governance review file](../governance/source-reviews.jsonl)
under its canonical Work ID. The initial profile covers public primary
arXiv sources and binds the exact versioned source URL, retained PDF SHA-256,
review and expiry dates, current review status, and independently stated
metadata index and search decisions. Older Work records remain historical
identities and require review for use. Unconfirmed, inaccessible, revised, or
retracted sources have an empty use map.

Crossref reviews use schema version 2 and the
`crossref-bibliographic-metadata` source kind. They bind the exact DOI, deposit
timestamp, and SHA-256 of the retained bibliographic JSON under
`governance/source-evidence/`. The checked fields are the title, authors,
publication date and venue recorded by the Work. This profile covers those
metadata fields for approved index or search use.

Use `crossref-journal-bibliographic-metadata` when the Work's venue is a
formatted journal reference. The snapshot retains the publisher's journal title
and its exact volume, optional issue, and page range or article number. The Work
venue must match those components in the supported citation forms, including
optional issue and publication year. The match allows an omitted leading
`The` and equivalent hyphen and en dash typography. The DOI, title, ordered
authors and date must also match. Live verification pins the snapshot and treats any
locator change or editorial notice as requiring review. [Crossref metadata fields](https://github.com/CrossRef/rest-api-doc/blob/master/api_format.md#work)

arXiv metadata reviews use schema version 2 and the
`arxiv-bibliographic-metadata` source kind. Retain a canonical JSON snapshot
of the title, ordered authors, publication date, venue, and exact arXiv
revision under `governance/source-evidence/`. Match the registered identity,
title, ordered authors, publication date, and any version pinned by the Work
or explicitly cited in the corpus before adding a review. A Work with an
omitted venue can use the publisher snapshot's arXiv preprint venue. The
original venue field remains part of the historical Work record.

Live readback batches canonical modern and historical arXiv identifiers
through the publisher's Atom API and reports withdrawals, revised versions,
and metadata changes. This profile supports approved bibliographic indexing
and search. [arXiv identifiers](https://info.arxiv.org/help/arxiv_identifier.html) · [arXiv API terms](https://info.arxiv.org/help/api/tou.html)

Obtain the registry SHA-256 from an independently reviewed checkout using
`python tools/validate_external_claim_adapter.py --registry-sha256`. The value
binds the raw Work, Claim, Evidence, and review files together. Use that exact identity
and an explicit review date to check an input snapshot.

```bash
python tools/validate_external_claim_adapter.py --source-report \
  --expected-registry-sha256 <reviewed-registry-sha256> --as-of 2026-11-26
```

The report checks retained source identities and identifies affected claims,
evidence, and corpus articles with matching arXiv and DOI citations. Old dispositions
remain in the registry. Expiry and reported source changes require renewed
review. Passage text and source notes remain evidence. Publication, model
augmentation, and training have separate approval paths.

`citation_coverage` lists explicit arXiv and DOI links in current corpus
articles by normalized identifier. Each row includes the citing paths and
registered Work IDs. Review links with no Work, only historical matches, or
more than one active match before using them. An active Work match establishes
registry coverage. Consult the separate Work decision for source review,
version, and permitted uses.

For a current UTC report, replace `--as-of <date>` with `--check-live`. A live
check uses the same registry pin and existing metadata permissions. It compares
the arXiv identity, version, withdrawal notice, and exact PDF digest, or the
Crossref deposit, bibliographic fields, and editorial notices. A failed or unconfirmed check suppresses
the use map and lists the affected claims, evidence, and corpus articles.

The public workflow saves a readback report on pushes, pull requests, and
weekly. Its registry hash identifies the scanned checkout. Consumers supply
their own admitted registry pin before relying on the use decisions.
