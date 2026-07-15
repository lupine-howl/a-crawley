# Sprint 28 — Investment earnings & events skim (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B51  
**Depends on:** B39, B24 helpful  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Bounded **earnings / event calendar skim** for watchlist symbols → Markdown what’s coming / what just printed.

## Demo

1. Run events skim for watchlist window
2. Cite sources
3. No trade recommendations as orders

## Committed

### S28.1 — Earnings & events skim (B51)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B51 |

**Acceptance criteria:**

- [ ] Bounded fetch of earnings/event-like sources for watchlist
- [ ] Markdown table/list of upcoming/recent events + LLM wrap
- [ ] Hard caps; cache where sensible
- [ ] Honest empty state when no events found

---

**Out of scope (sprint):**

- Paid data vendor integration as a product
- Auto trades around earnings
- Automated trading / order placement (Icebox)

## Parking lot

- Link events into Day brief optionally
