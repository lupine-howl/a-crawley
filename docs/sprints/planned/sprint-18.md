# Sprint 18 — Investment watchlist (planned)

**Status:** planned (activates after Sprint 4 Investment harden)  
**Duration:** one symbolic week  
**Backlog refs:** B39  
**Depends on:** B9  

## Goal

Operator-maintained **watchlist** of symbols/topics for bounded Investment refresh — still manual action advice only; no orders.

## Demo

1. Save a small watchlist locally
2. Run Investment scoped to watchlist with cache caps
3. No trade / order affordances

## Committed

### S18.1 — Investment watchlist (B39)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B39 |

**Acceptance criteria:**

- [ ] Local watchlist edit/save under `data/`
- [ ] Run can target watchlist with existing hard caps
- [ ] Advice Markdown remains non-order; no brokerage hooks
- [ ] Empty watchlist honest empty state

**Out of scope:** Automated trading, alerts pushed off-machine, portfolio PnL product
