# Sprint 15 — Snapshot history + deeper shared memory (planned)

**Status:** done (legacy shelved plan; delivered with Sprint 14 in [`../current.md`](../current.md) — **not** pivot Sprint 15)  
**Pivot Sprint 15:** [`sprint-15-sender-inbox-scale.md`](sprint-15-sender-inbox-scale.md)  

**Duration:** one symbolic week  
**Backlog refs:** B35, B36  
**Depends on:** B14, B29  

## Goal

Thicken local organisation: **searchable / browsable snapshot history** and a richer shared-context pack for prompts — still hard-capped; not a vector-DB product unless architect justifies a thin local embed option in ADR.

## Demo

1. Browse recent past summaries per module (bounded retention)
2. Search titles/snippets locally
3. Shared context can pull selected history items (opt-in)
4. Retention/prune policy documented

## Committed

### S15.1 — Snapshot history browser (B35)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B35 |

**Acceptance criteria:**

- [x] Persist more than “last success” (bounded N per module)
- [x] Simple history UI; open body safely (escaped pre)
- [x] Prune/retention documented

### S15.2 — Shared context depth (B36)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B36 |
| Depends on | S15.1, B29 |

**Acceptance criteria:**

- [x] Operator can pin/select history items into shared context
- [x] Hard caps; secrets never injected
- [x] ADR/architecture update: history vs seed standing notes

**Out of scope:** Cloud sync of memory, multi-user knowledge base
