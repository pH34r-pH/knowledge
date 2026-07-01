# Tasks: Corpus Population Research Loop

**Input**: Design documents from `/specs/001-corpus-population-loop/`

**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: Manual file/content verification, same posture as `000-raw-ingestion`.

**Organization**: Tasks are grouped by user story. Unlike `000-raw-ingestion`, this feature's later phases are an ongoing operating loop, not a one-time build — Phase 5 tasks recur every invocation rather than being checked off once.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel
- **[Story]**: User story tag (US1-US4)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Scaffolding the loop needs before any topic can be researched

- [x] T001 Create `TOPICS.md` with the three-pillar backlog (design patterns, ML techniques, adjacent knowledge), seeded with real candidates and harness hints
- [x] T002 [P] Create `corpus/LEDGER.md` with the ledger template, empty entries section
- [x] T003 [P] Verify `.claude/skills/` directory convention is followed for a repo-scoped, re-invocable skill

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: The protocol artifact itself — MUST exist before any user story can be exercised

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T004 Write `.claude/skills/populate-corpus/SKILL.md` covering: boundaries, state loading, topic selection, harness selection, article writing, index/ledger update, commit discipline
- [x] T005 [P] Cross-reference the vault's `storm` skill by absolute path (`/Users/haidmoham/brain/agent-config/skills/storm/SKILL.md`) rather than relying on the (found-dangling) `~/.claude/skills/storm` symlink
- [x] T006 [P] Document the vault-read/never-vault-write boundary explicitly in the skill, matching the vault's own client-work confidentiality pattern (generalize-don't-copy) applied in the opposite direction

**Checkpoint**: Foundation ready — the skill fully specifies the loop with no missing steps

---

## Phase 3: User Story 1 - Topic-Driven Article Synthesis (Priority: P1) 🎯 MVP

**Goal**: One invocation produces one correctly-structured, sourced article

**Independent Test**: Run `populate-corpus` once against a real `TOPICS.md` entry; verify the resulting file's frontmatter and section structure

### Implementation for User Story 1

- [ ] T007 [US1] First live invocation: select a topic, write the article, verify against the frontmatter/section contract in spec.md
- [ ] T008 [P] [US1] Manual test: confirm every non-obvious claim in the first article traces to a listed source
- [ ] T009 [P] [US1] Manual test: confirm re-running the loop skips the now-done topic and selects a different one

**Checkpoint**: User Story 1 is functional after one real run

---

## Phase 4: User Story 2 - Harness-Appropriate Research Method Selection (Priority: P1)

**Goal**: The loop demonstrably chooses different harnesses for different topic shapes

**Independent Test**: Run the loop against one vault-coverable topic, one converged-technical topic, and one contested topic; verify three different `method` values in the resulting frontmatter

### Implementation for User Story 2

- [ ] T010 [US2] Run against a topic with existing vault coverage (e.g. `graceful-degradation`, `secrets-at-point-of-use`); verify `method: vault-adapt` and no fresh web research performed
- [ ] T011 [US2] Run against a converged-technical topic (e.g. backpropagation); verify `method: deep-research`
- [ ] T012 [US2] Run against a contested topic (e.g. CQRS/event sourcing); verify `method: storm` and a populated Trade-offs section reflecting multiple perspectives
- [ ] T013 [P] [US2] Manual test: confirm each run checks `corpus/LEDGER.md` and the vault's `research-log.md` before starting fresh research

**Checkpoint**: User Story 2 is independently verified across all three harness paths

---

## Phase 5: User Story 3 - Deduplication and Backlog Management (Priority: P2)

**Goal**: The loop sustains itself across many invocations without duplicating work or stalling

**Independent Test**: Run the loop repeatedly until a pillar's seed backlog is exhausted; verify new candidates get proposed rather than the loop stalling or repeating

### Implementation for User Story 3 (recurring — not a one-time checklist)

- [ ] T014 [US3] Manual test: run the loop N+1 times where N is a pillar's seed topic count; verify new candidates are proposed and appended before the (N+1)th topic is picked
- [ ] T015 [P] [US3] Manual test: attempt to re-target an already-`done` topic; verify the loop reports it as covered instead of duplicating the article
- [ ] T016 [P] [US3] Periodically audit `corpus/LEDGER.md` for entries that should be marked stale (the underlying technique moved, not the write being wrong)

**Checkpoint**: Backlog and ledger remain internally consistent after repeated, non-contiguous invocations

---

## Phase 6: User Story 4 - Reproducible Re-Invocation (Priority: P1)

**Goal**: The protocol survives outside this conversation

**Independent Test**: In a fresh session with only this repository checked out, invoke `populate-corpus` with no other chat context and confirm it runs the same workflow

### Implementation for User Story 4

- [ ] T017 [US4] Verify a fresh Claude Code session in this repo surfaces `populate-corpus` as an invocable skill
- [ ] T018 [P] [US4] Confirm `specs/001-corpus-population-loop/` follows the same three-file spec-kit structure as `000-raw-ingestion`
- [ ] T019 [P] [US4] Cross-link `SKILL.md` → `spec.md` and `spec.md`'s Input section back to the originating request, so the provenance of the protocol is auditable later

**Checkpoint**: The protocol is repo-native and does not depend on this conversation's memory

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect the loop as a whole, not one user story

- [ ] T020 [P] Fix the dangling `~/.claude/skills/*` symlinks in the operator's personal environment (found during T005; out of scope for this repo, flagged separately)
- [x] T021 [P] Once collaborator (push) access is granted by the repo owner, confirm the same local clone pushes cleanly with no remote reconfiguration needed — done 2026-07-01: access granted, 5 local commits fast-forwarded to `origin/main` cleanly, upstream repointed to `origin`
- [ ] T022 Consider a repo-specific constitution once the corpus grows past the seed set, given `.specify/memory/constitution.md` is inherited from an unrelated project (see plan.md Constitution Check)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies
- **Foundational (Phase 2)**: Depends on Setup; BLOCKS all user stories
- **User Stories (Phase 3-6)**: All depend on Foundational; US1/US2/US4 should be exercised together on the first real run, US3 only becomes testable across multiple runs over time
- **Polish (Phase 7)**: Depends on at least one successful loop iteration existing

### Within Each User Story

- Backlog/ledger existence before topic selection
- Harness selection before article writing
- Article writing before index/ledger update
- Index/ledger update before commit

## Notes

- [P] tasks touch different files/checks and have no ordering dependency
- Unlike `000-raw-ingestion`, Phases 3-6 are not "build once, done forever" — they describe how to *verify* the loop, which then runs indefinitely as new topics are invoked
- Commit after each topic (Step 6 of the skill), never batch multiple topics into one commit
- This repository has no push access yet; every commit here is local until the owner grants collaborator access
