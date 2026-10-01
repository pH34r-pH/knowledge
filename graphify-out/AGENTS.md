# Graphify output boundary

`graphify-out/` contains intentional derived graph products: reports, manifests,
JSON/HTML navigation, and retained dated snapshots. It is not a disposable trash
directory and must not be removed as a blanket cleanup.

- Source authority remains [`../corpus/`](../corpus/), [`../README.md`](../README.md),
  and the source/evidence records; derived output can be stale.
- Refresh the products with `graphify update .` from the repository root after a
  source or procedure change. Do not hand-edit a report to change source meaning.
- Preserve dated snapshots for historical comparison. Do not treat `cache/` as source
  authority; documentation CI excludes cache/temp/build artifacts explicitly, even
  when they occur below retained or evidence-like roots.
- If a generated file is intentionally retained, keep its relationship to the source
  visible and do not add a parallel hand-maintained inventory here.
