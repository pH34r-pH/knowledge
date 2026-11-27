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

Obtain the registry SHA-256 from an independently reviewed checkout using
`python tools/validate_external_claim_adapter.py --registry-sha256`. The value
binds the raw Work, Claim, Evidence, and review files together. Use that exact identity
and an explicit review date to check an input snapshot.

```bash
python tools/validate_external_claim_adapter.py --source-report \
  --expected-registry-sha256 <reviewed-registry-sha256> --as-of 2026-11-26
```

The report checks retained PDF identities and identifies affected claims,
evidence, and corpus articles with matching arXiv citations. Old dispositions
remain in the registry. Expiry and reported source changes require renewed
review. Passage text and source notes remain evidence. Publication, model
augmentation, and training have separate approval paths.

For a current UTC report, replace `--as-of <date>` with `--check-live`. A live
check uses the same registry pin and existing metadata permissions. It compares
the primary arXiv identity, current version, withdrawal notice, and exact PDF
digest against the retained review. A failed or unconfirmed check suppresses
the use map and lists the affected claims, evidence, and corpus articles.

The public workflow saves a readback report on pushes, pull requests, and
weekly. Its registry hash identifies the scanned checkout. Consumers supply
their own admitted registry pin before relying on the use decisions.
