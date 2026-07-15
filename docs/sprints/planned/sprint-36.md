# Sprint 36 — Investment local in-panel alerts (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B59  
**Depends on:** B39, B13 scheduler patterns preferred  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Local **in-panel alerts** for watchlist (price/news keywords) evaluated when Crawley runs — no brokerage, no off-machine push required.

## Demo

1. Define alert rules locally
2. On Run or scheduled check, surface triggered alerts in panel/home
3. No order placement

## Committed

### S36.1 — Local investment alerts (B59)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B59 |

**Acceptance criteria:**

- [ ] Alert rule CRUD (symbol/topic, condition type: keyword / manual threshold note)
- [ ] Evaluation on Run and/or opt-in schedule (reuse job patterns; default off)
- [ ] Triggered alerts list in Investment panel; optional home chip
- [ ] Explicit: alerts are informational; no trades

---

**Out of scope (sprint):**

- SMS/email push off-machine
- Broker webhooks
- Automated trading
- Automated trading / order placement (Icebox)

## Parking lot

- Alert → open notebook stub
