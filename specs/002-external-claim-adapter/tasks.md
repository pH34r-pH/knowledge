# Tasks: External Claim Adapter

- [ ] **T1 — Finalize record schemas** for `KWRK-*`, `KCLM-*`, and `KEVD-*`, including canonical identifiers, support metadata, audit state, offline-validation level, hashes, and supersession.
- [ ] **T2 — Add valid/invalid fixtures** covering duplicate IDs, broken references, failed audit, bad hashes, and unsupported offline-level claims.
- [ ] **T3 — Implement dependency-light offline validator** with fail-closed behavior defined in `tests.md`.
- [ ] **T4 — Add automated tests** for T-001 through T-008.
- [ ] **T5 — Seed a minimal adapter set** from already-audited sources needed by `domain-scaling-lab` independent-convergence records; do not mark a claim accepted without claim-level entailment evidence.
- [ ] **T6 — Update corpus documentation/ledger** to describe adapter ownership and the distinction among work identity, attributed claim, and evidence.
- [ ] **T7 — Integrate ingestion workflow** so future verified source pools can emit/update adapter records without allowing write-time citations outside the resolved pool.
- [ ] **T8 — Cross-repo acceptance**: have `domain-scaling-lab` pin the resulting knowledge commit and validate at least one external claim offline.
- [ ] **T9 — Run repository verification** including citation integrity, adapter tests, index/ledger consistency, and `graphify update .` if required by local procedure.
- [ ] **T10 — Commit/push pathspec-scoped changes** after `git pull --rebase --autostash origin main`; close issue #2 only after the cross-repo acceptance test passes.