# Implementation Plan: Corpus Population Research Loop

**Branch**: `001-corpus-population-loop` | **Date**: 2026-07-01 | **Spec**: [spec.md](./spec.md)

**Note**: This template is filled in by the `__SPECKIT_COMMAND_PLAN__` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implement a repeatable research loop that grows this repository into a general knowledge corpus (software engineering design patterns, ML techniques, adjacent high-value engineering knowledge), distinct from the paper-citation-graph pipeline in `000-raw-ingestion`. The loop is encoded as a Claude Code skill (`.claude/skills/populate-corpus/SKILL.md`) so it is re-invocable without chat context, selects a research harness per topic (vault reuse, the built-in `deep-research` skill, or the vault's `storm` skill) via an explicit decision rule, and checkpoints itself through a backlog (`TOPICS.md`) and a ledger (`corpus/LEDGER.md`) modeled on the vault's own `research-log.md` discipline.

## Technical Context

**Language/Version**: Markdown, YAML frontmatter, Bash (git only)

**Primary Dependencies**: Claude Code Skill tool; built-in `deep-research` skill; the vault's `storm` skill at `~/Users/haidmoham/brain/agent-config/skills/storm/SKILL.md` (invoked by path, not by relying on the `~/.claude/skills/storm` symlink, which was found dangling during this feature's design — see Notes)

**Storage**: Local filesystem — `TOPICS.md` (backlog), `corpus/<pillar>/` (articles), `corpus/LEDGER.md` (run ledger), `README.md` (index)

**Testing**: Manual verification of file existence, frontmatter completeness, source citation, and ledger/backlog consistency (same manual-verification posture as `000-raw-ingestion`; no automated test harness exists in this repo)

**Target Platform**: Any machine running Claude Code with the vault (`~/brain`) mounted; degrades gracefully (vault cross-linking skipped) if the vault is absent

**Project Type**: local-tooling (research corpus, distinct feature from the arXiv ingestion pipeline)

**Performance Goals**: Not latency-sensitive; a single loop iteration is expected to take minutes (research-bound), not seconds

**Constraints**: Write access to the canonical repo granted 2026-07-01 — every run commits and pushes to `origin` (`pH34r-pH/knowledge`), pulling `--rebase --autostash` first since the repo is now shared with another collaborator; a personal `backup` remote (`github.com/haidmoham/knowledge-backup`) is kept as a secondary mirror; no writes to `~/brain` under any circumstance; no PII; commits scoped by explicit pathspec, never a broad `git add`

**Scale/Scope**: Personal-to-small-team research corpus; expected concurrent invocation < 1 (single operator, sequential runs)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

The `.specify/memory/constitution.md` in this repo is the Blue Swallow Society constitution, copied in wholesale from a prior, unrelated web-security project (per `000-raw-ingestion/plan.md`). It is security/anonymity-focused and does not bind a static-markdown research corpus in the way it would a live web application. Assessed against what genuinely applies:

| Principle | Assessment | Notes |
|-----------|------------|-------|
| Security-First | PASS (N/A scope) | No user input, no network-facing surface; only file writes and outbound research reads |
| Privacy/Anonymity | PASS | No PII collected or transmitted; articles are generalized, never tied to an individual project or person |
| Defense in Depth | PASS (N/A scope) | Single-writer local filesystem; no attack surface to layer defenses on |
| Secure Defaults | PASS | Never writes to the vault by default; pulls --rebase before pushing to the shared canonical repo; pathspec-scoped commits by default (never a broad `git add` in a shared tree) |
| Continuous Monitoring | N/A | No running service; nothing to monitor between invocations |

No constitution violation blocks this feature. The mismatch between this feature's actual risk profile (a markdown-writing research loop) and the constitution's actual scope (a security/anonymity web app) is itself worth flagging to the repo owner as a candidate to write a corpus-specific constitution later, rather than silently ignoring the gate.

## Project Structure

### Documentation (this feature)

```text
specs/001-corpus-population-loop/
├── spec.md              # Feature specification
├── plan.md              # This file
└── tasks.md             # Phase 2 output
```

No `research.md`, `data-model.md`, or `contracts/` — this feature has no external API surface or schema beyond the frontmatter already specified in `spec.md`'s Key Entities section.

### Source Code (repository root)

```text
~/projects/knowledge/
├── .claude/
│   └── skills/
│       └── populate-corpus/
│           └── SKILL.md     # The reproducible protocol itself
├── specs/
│   ├── 000-raw-ingestion/   # Existing: arXiv paper ingestion pipeline (separate feature)
│   └── 001-corpus-population-loop/
├── TOPICS.md                 # Prioritized topic backlog, 3 pillars
├── corpus/                   # New: general-knowledge articles
│   ├── LEDGER.md              # Run ledger (research-log.md-style)
│   ├── design-patterns/
│   ├── ml-techniques/
│   └── adjacent-knowledge/
├── arxiv/                     # Existing: raw papers (000-raw-ingestion)
└── reports/                   # Existing: paper summaries (000-raw-ingestion)
```

**Structure Decision**: `corpus/` is deliberately separate from `arxiv/`/`reports/` — those are keyed by arXiv ID and hold paper-derived material; `corpus/` is keyed by topic slug within a pillar and holds synthesized, general-purpose articles that may cite papers, vault pages, or web sources interchangeably. Pillar subdirectories are flat (no further nesting) to keep navigation trivial, matching the flat-by-ID convention `000-raw-ingestion` already established for `arxiv/`/`reports/`.

## Complexity Tracking

> No constitution violations or unjustified complexity detected. The feature stays within markdown-file scope with no new external dependencies; the only cross-repo dependency is read-only reference to `~/brain`, which degrades gracefully to a no-op if absent.

## Notes

- During design, the personal skill-loading symlinks at `~/.claude/skills/*` (which are meant to expose vault skills like `storm` as top-level slash commands) were found dangling — they point at a `claude-config` path that was renamed to `agent-config` at some point. This does not block this feature, since the skill in this repo references `storm` by its full filesystem path rather than depending on the symlink, but it is a pre-existing issue in the operator's personal environment worth fixing separately.
