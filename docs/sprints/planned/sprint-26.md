# Sprint 26 — Investment holdings journal (manual) (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B49  
**Depends on:** B45 preferred, B39  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Manual **holdings journal** (positions the operator types or pastes) for context in advice — not a brokerage link, not orders.

## Demo

1. Enter/edit holdings (symbol, qty/notes, optional cost basis note)
2. Investment Run can cite holdings context
3. Disclaimer: not brokerage truth

## Committed

### S26.1 — Manual holdings journal (B49)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B49 |

**Acceptance criteria:**

- [ ] Local holdings table/file under data/
- [ ] Panel CRUD; validation for obvious junk rows
- [ ] Optional include in LLM context with hard cap
- [ ] UI states this is operator-entered, not broker-synced
- [ ] No order/rebalance execution

---

**Out of scope (sprint):**

- Brokerage OAuth
- Automated trading
- Tax lot accounting product
- Automated trading / order placement (Icebox)

## Parking lot

- CSV import of holdings (align with Finance import patterns)
