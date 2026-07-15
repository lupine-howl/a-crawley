# Sprint 34 — Investment theme & sector baskets (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B57  
**Depends on:** B39, B47  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Operator-defined **theme/sector baskets** (e.g. AI infra, UK income) that scope fetches and advice beyond a flat watchlist.

## Demo

1. Create basket of symbols/topics
2. Run scoped to basket
3. Notebook can attach to basket

## Committed

### S34.1 — Theme/sector baskets (B57)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B57 |

**Acceptance criteria:**

- [ ] Local basket CRUD under data/
- [ ] Investment Run target: watchlist | basket | ad-hoc
- [ ] Cluster/advice paths accept basket scope
- [ ] No ETF auto-trading

---

**Out of scope (sprint):**

- Auto-rebalancing
- Index replication product
- Automated trading / order placement (Icebox)

## Parking lot

- Basket vs basket compare
