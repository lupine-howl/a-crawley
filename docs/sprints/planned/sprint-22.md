# Sprint 22 — Investment research notebook + thesis (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B45  
**Depends on:** B9, B39 (watchlist preferred)  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Give Investment durable **thesis notes** and a per-symbol **research notebook** that seeds LLM advice — still manual action only.

## Demo

1. Edit thesis/notes for a watchlist symbol
2. Run advice that cites notebook + fresh bounded fetch
3. No trading UI

## Committed

### S22.1 — Investment thesis & notebook (B45)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B45 |

**Acceptance criteria:**

- [ ] Local notebook/thesis store per symbol or topic under data/
- [ ] Panel UX to view/edit notes
- [ ] Run can optionally include notebook slice in prompt (hard-capped)
- [ ] Advice Markdown remains non-order
- [ ] Empty notebook honest

---

**Out of scope (sprint):**

- Brokerage sync
- Automated trading
- Automated trading / order placement (Icebox)

## Parking lot

- Link notebook entries to snapshot history
