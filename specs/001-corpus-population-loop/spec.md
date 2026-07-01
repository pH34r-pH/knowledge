# Feature Specification: Corpus Population Research Loop

**Feature Branch**: `001-corpus-population-loop`

**Created**: 2026-07-01

**Status**: Draft

**Input**: User description: "Act as a researcher systematically building this corpus to encapsulate key software engineering design patterns, machine learning techniques, and any knowledge with evidence of being high-value for an ambitious, knowledge-hungry mid-career software engineer. Generate a reproducible loop that populates this repo, incorporates vault context where necessary, and uses the STORM and deep-research skills as research harnesses. Encode the loop itself in the repo as a re-referenceable protocol."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Topic-Driven Article Synthesis (Priority: P1)

A researcher (human or agent) must be able to select one high-value, uncovered topic and produce a sourced, structured article without re-deriving the process from scratch each time.

**Why this priority**: this is the core loop. Without a repeatable synthesis step, every invocation reinvents structure, tone, and rigor, and the corpus becomes inconsistent.

**Independent Test**: invoke the loop once, verify a new file lands under `corpus/<pillar>/` with required frontmatter and all required body sections, and that every non-obvious claim carries a source.

**Acceptance Scenarios**:
1. **Given** an unchecked topic in `TOPICS.md`, **When** the loop runs, **Then** a markdown article is created at `corpus/<pillar>/<slug>.md` with frontmatter (`title`, `pillar`, `method`, `date`, `sources`, `confidence`)
2. **Given** an article has been written, **When** it is inspected, **Then** it contains sections: What it is, When to reach for it, How it works, Trade-offs, In practice, Further reading
3. **Given** a topic has already been marked done in `TOPICS.md`, **When** the loop is asked to run again, **Then** it skips that topic and selects the next unchecked one

### User Story 2 - Harness-Appropriate Research Method Selection (Priority: P1)

The loop must choose among three research paths (vault reuse, `deep-research`, `storm`) based on the topic's nature, rather than always defaulting to the heaviest or the cheapest option.

**Why this priority**: mismatched harness weight either wastes a full multi-perspective research pipeline on a settled technical fact, or under-serves a genuinely contested topic with a single unsourced pass.

**Independent Test**: for a topic already covered by a mature vault page, verify the loop reuses it (`method: vault-adapt`) without invoking web research; for a contested topic, verify it invokes `storm` and the article's trade-offs section reflects multiple perspectives.

**Acceptance Scenarios**:
1. **Given** a topic with an existing, mature `experience`-tier page in `~/brain/wiki/`, **When** the loop selects a harness, **Then** it adapts that page (`method: vault-adapt`) instead of running fresh research
2. **Given** a topic with a converged, single-throughline technical exposition, **When** the loop selects a harness, **Then** it invokes the built-in `deep-research` skill (`method: deep-research`)
3. **Given** a topic where practitioners genuinely disagree, **When** the loop selects a harness, **Then** it invokes the `storm` skill (`method: storm`) and the resulting article's Trade-offs section reflects the contradiction map
4. **Given** a topic that is both mechanism-rich and genuinely contested, **When** the loop selects a harness, **Then** it runs both `deep-research` and `storm` (`method: deep-research + storm`), deriving How-it-works from the former and the Trade-offs contradiction map from the latter, with source lists deduped across both
5. **Given** any fresh-research path, **When** the loop starts, **Then** it first checks `corpus/LEDGER.md` and the vault's `research-log.md` for a reusable prior run

### User Story 3 - Deduplication and Backlog Management (Priority: P2)

The loop must not silently duplicate work, and must keep its own backlog alive across many invocations spanning an unknown time horizon.

**Why this priority**: without a durable backlog and ledger, a loop re-invoked weeks or months apart has no memory of prior runs and re-researches or duplicates topics.

**Independent Test**: run the loop twice; verify the second run picks a different topic and the ledger has two distinct entries. Empty a pillar's backlog; verify the loop proposes new candidates rather than stalling.

**Acceptance Scenarios**:
1. **Given** `TOPICS.md` has one topic per pillar, **When** the loop runs three times, **Then** three distinct articles exist and `corpus/LEDGER.md` has three entries
2. **Given** a pillar's backlog is exhausted, **When** the loop selects a topic for that pillar, **Then** it proposes and appends 3-5 new candidates with justification before picking one
3. **Given** `corpus/LEDGER.md` already has a current entry for a topic, **When** asked to research that same topic again, **Then** the loop reports it as already covered rather than duplicating the file

### User Story 4 - Reproducible Re-Invocation as a Repo-Native Protocol (Priority: P1)

The loop's definition must live in the repository itself, not only in a chat transcript, so any future session (or collaborator, once granted access) can run it identically.

**Why this priority**: a prompt that only exists in one conversation is not a protocol — it can't be re-run, audited, or handed to someone else without loss.

**Independent Test**: open a fresh session with only the repository checked out, invoke the skill by name, and confirm it reproduces the same steps described here without additional chat-provided context.

**Acceptance Scenarios**:
1. **Given** a fresh Claude Code session with this repo as the working directory, **When** `populate-corpus` is invoked, **Then** the skill's own file (`.claude/skills/populate-corpus/SKILL.md`) fully specifies the workflow with no missing steps
2. **Given** the repo's existing spec-kit convention (`specs/NNN-feature-name/`), **When** this feature is inspected, **Then** it follows the same `spec.md` / `plan.md` / `tasks.md` structure as `000-raw-ingestion`

### Edge Cases

- What happens when `TOPICS.md` or `corpus/LEDGER.md` doesn't exist yet (first-ever run)? The loop creates them if missing, seeded per the templates in this spec.
- What happens when the vault (`~/brain`) is unreachable or absent (e.g. a different machine)? Fall back to `deep-research`/`storm` only, and note in the article that vault cross-linking was skipped.
- What happens when both `storm` and `deep-research` would apply reasonably well? If the topic has a substantial mechanism to explain *and* a genuine practitioner debate, use the dual-harness reconcile mode (run both, deep-research for the mechanism and STORM for the contradiction map, merged into one article). If only the debate carries value and the mechanism is thin, use `storm` alone; if there is a mechanism but no real camps, use `deep-research` alone (cheaper). Do not run both on a clearly-converged topic — STORM will manufacture perspectives that don't exist.
- What happens when a topic turns out to be too thin or already well covered elsewhere in the corpus mid-research? Abandon it, log why in the run's output, and select the next topic rather than force a low-value entry.
- How are stale `done` topics handled if the underlying technique gets superseded? Note the staleness in the ledger entry rather than silently rewriting history (same discipline as the vault's "don't silently overwrite a fact that changed" convention).

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST maintain a prioritized, human-readable topic backlog at `TOPICS.md`, grouped into exactly three pillars: design patterns, ML techniques, adjacent high-value knowledge
- **FR-002**: System MUST select one topic per invocation and mark it done in `TOPICS.md` only after the corresponding article and ledger entry exist
- **FR-003**: System MUST choose a research method per topic from four options — vault-adapt, `deep-research`, `storm`, or dual-harness reconcile (`deep-research` AND `storm`) — using the selection rule in Step 3 of the skill. The dual mode is reserved for topics that are both mechanism-rich and genuinely contested; deep-research supplies the mechanism, STORM the contradiction map, reconciled into one article
- **FR-004**: System MUST check both `corpus/LEDGER.md` and the vault's `wiki/meta/research-log.md` before any fresh-research invocation, to avoid re-paying for existing coverage
- **FR-005**: System MUST write each article to `corpus/<pillar>/<slug>.md` with the frontmatter and body sections defined in the skill
- **FR-006**: System MUST cite a source for every non-obvious claim; STORM-sourced and deep-research-sourced articles carry a numbered Further Reading section
- **FR-007**: System MUST append one entry to `corpus/LEDGER.md` per completed article, and update `README.md`'s corpus index
- **FR-008**: System MUST commit only the files it changed, by explicit pathspec, and MUST push to the canonical remote (`origin` → `pH34r-pH/knowledge`, write access granted 2026-07-01) as the defined end of every run — this is a durable, extensible knowledge base, so a run is not complete until it is backed up. Because the repo is now shared with another collaborator, it MUST `git pull --rebase --autostash origin main` before pushing, and MUST report a rejected push plainly rather than dropping it silently
- **FR-009**: System MUST NOT write to `~/brain` under any circumstance; vault interaction is read-only
- **FR-010**: System MUST encode this entire workflow in a repo-native, re-invocable artifact (`.claude/skills/populate-corpus/SKILL.md`), not only as ephemeral chat instructions
- **FR-011**: System MUST follow this repository's existing spec-kit conventions for feature documentation, per the precedent set by `000-raw-ingestion`
- **FR-012**: System MUST run a citation-integrity gate (Step 5) before an article counts as done, applying, in order: (a) deterministic reference resolution (DOI via CrossRef, arXiv id, or title via OpenAlex/Semantic Scholar) that drops any reference resolving to nothing or to a *different* work; (b) quote-span matching of each cited claim against the fetched source; (c) URL liveness (live 200 or Wayback, else block); (d) entailment checking by a verifier that is NOT the writer, answered factored (without the draft in context). Zero unresolved references and zero dead URLs are hard commit blocks. Evidence base: `.claude/skills/populate-corpus/references/citation-integrity.md`
- **FR-013**: System MUST constrain the writer to cite only from the pre-resolved source pool the research stage produced — a citation to any source the pipeline has not already resolved is a failure — and MUST record the citation-audit tally (references resolved/unresolved, URLs live/dead, entailment result) in the `corpus/LEDGER.md` entry on commit

### Key Entities *(include if feature involves data)*
- **Topic Backlog Entry**: one line in `TOPICS.md` — topic, one-line justification, suggested harness, done/unchecked status
- **Corpus Article**: a markdown file under `corpus/<pillar>/` with frontmatter (title, pillar, method, date, sources, confidence, optional vault-links) and the six required body sections
- **Ledger Entry**: one record in `corpus/LEDGER.md` capturing what was researched, how, at what confidence, and what it cross-links to — the audit trail that makes re-invocation safe
- **Research Harness**: one of vault-adapt (reuse), `deep-research` (built-in skill), `storm` (vault skill at `~/brain/agent-config/skills/storm/`), or a dual-harness reconcile that runs `deep-research` and `storm` together and merges their outputs into one article

## Success Criteria *(mandatory)*

### Measurable Outcomes
- **SC-001**: Each `populate-corpus` invocation produces exactly one new article, one new ledger entry, and one updated `TOPICS.md` checkbox, or explicitly reports why it produced none
- **SC-002**: Zero duplicate articles exist for the same topic across repeated invocations, verified against `corpus/LEDGER.md`
- **SC-003**: 100% of articles carry a `method` field and, for `deep-research`/`storm` methods, a non-empty Further Reading section with real, checkable sources
- **SC-004**: A fresh session with no chat history can invoke the skill and reproduce the same workflow, verified by inspecting `.claude/skills/populate-corpus/SKILL.md` in isolation
- **SC-005**: 100% of citations in committed articles resolve to a real, correct source and carry a live (or archived) URL; the citation-audit tally in each ledger entry shows zero unresolved references and zero dead URLs, or the article was not committed

## Assumptions
- The operator has read access to this repository and to `~/brain`; write/push access to this repository is pending a collaborator invite from its owner
- Claude Code (or an equivalent agent runtime with Skill support, subagent fan-out, and the built-in `deep-research` skill) is the execution environment
- The vault at `~/brain` remains the source of already-tested (`experience`-tier) knowledge; this corpus is a separate, generalized artifact and never writes back to it
- `TOPICS.md`'s seed backlog is a starting point, not a ceiling — the loop is expected to extend it over many invocations
