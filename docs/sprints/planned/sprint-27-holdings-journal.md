# Sprint 27 — Manual holdings journal (planned)

**Status:** closed — see [`../archive/sprint-26-30-labels-holdings-search-attach-citations.md`](../archive/sprint-26-30-labels-holdings-search-attach-citations.md)
**Duration:** one symbolic week  
**Backlog refs:** B49  
**Depends on:** Sprint 14 paper portfolio; Sprint 23 notebook preferred  
**Primary focus:** asx / investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-27.md`](sprint-27.md) remains a shelved stub if present — prefer this file.

## Goal

Operator-entered **real holdings journal** (distinct from paper simulation) for advice context — not broker truth; no order execution.

## Demo

1. CRUD holdings rows (ticker, qty, cost basis note)
2. Optional include in ASX recommend / notebook prompts (capped)
3. UI states this is operator-entered, not broker-synced; paper portfolio remains separate

## Committed

### S27.1 — Holdings journal (B49)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B49 |

**Acceptance criteria:**

- [ ] Local holdings table/file under data/
- [ ] Panel CRUD; validation for obvious junk rows
- [ ] Optional include in LLM context with hard cap
- [ ] UI states operator-entered, not broker-synced; distinct from paper ledger
- [ ] No order/rebalance execution

## Explicitly out of sprint

- Brokerage OAuth
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
