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
