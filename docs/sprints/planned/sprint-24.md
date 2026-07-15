# Sprint 24 — Investment watchlist news clusters (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B47  
**Depends on:** B39, B9  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Cluster and synthesize **news/sources per watchlist** into theme clusters (what’s moving / contested narratives) with citations.

## Demo

1. Run watchlist-scoped fetch → cluster Markdown
2. Each cluster lists sources
3. Cache/TTL respected

## Committed

### S24.1 — Watchlist news clustering (B47)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B47 |

**Acceptance criteria:**

- [ ] Bounded fetch across watchlist symbols/topics
- [ ] LLM or heuristic clustering into themes with source lists
- [ ] Panel shows clusters + summary; hard caps preserved
- [ ] No trade buttons; clear empty/error taxonomy

---

**Out of scope (sprint):**

- Real-time streaming quotes product
- Order tickets
- Automated trading / order placement (Icebox)

## Parking lot

- Cluster → thesis notebook append suggestion
