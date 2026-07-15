# Sprint 33 — Gmail newsletter & bulk-mail digest (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B56  
**Depends on:** B23, B50  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Detect/cluster **newsletters / bulk mail** in a bounded window and produce one **unsubscribe-minded digest** (summaries + keep/drop suggestions — manual action).

## Demo

1. Run newsletter digest for last N days
2. Grouped by sender
3. Suggestions remain manual

## Committed

### S33.1 — Newsletter clustering digest (B56)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B56 |

**Acceptance criteria:**

- [ ] Heuristic/LLM clustering of bulk/newsletter-like mail in bounded window
- [ ] Markdown digest per sender/group with keep/unsubscribe/archive suggestions
- [ ] No automatic unsubscribe HTTP calls unless confirm-first in a later story
- [ ] Respect VIP rules (do not treat VIP as bulk)

---

**Out of scope (sprint):**

- One-click List-Unsubscribe without confirm
- Delete-all automation
- Automated trading / order placement (Icebox)

## Parking lot

- Confirm-first unsubscribe/archive batch
