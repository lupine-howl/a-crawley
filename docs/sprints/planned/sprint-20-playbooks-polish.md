# Sprint 20 — Dual-desk playbooks + polish (planned)

**Status:** done (delivered in [`../current.md`](../current.md) Sprints 18–20 bundle)  

**Duration:** one symbolic week  
**Backlog refs:** B87, B88  
**Depends on:** Sender Inbox + ASX desks live  
**UX:** Optional short polish pass  

## Goal

Close the 13–20 arc with **operator playbooks** (saved run recipes for Sender Inbox triage and ASX morning scan/recommendations) and a focused **polish** pass on both desks — no Icebox items.

## Demo

1. Save/run playbooks (e.g. “Morning mail triage”, “ASX scan + refresh recs”)  
2. Address PO polish list (density, empty states, caps, errors)  
3. Architecture module maps updated for both desks  

## Committed

### S20.1 — Operator playbooks (B87)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B87 |

**Acceptance criteria:**

- [x] Named playbooks binding desk + scope + prompt/run options
- [x] One-click Run from Gmail/Investment or Settings
- [x] Stored locally under `data/`

### S20.2 — Dual-desk polish pass (B88)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B88 |

**Acceptance criteria:**

- [x] PO polish list recorded in sprint file before implement
- [x] Fixes use existing theme tokens / UX contract
- [x] No new domain modules in this story

**Out of scope:** Live trading, multi-user, public SaaS, full redesign

## Parking lot (post–20)

- Desktop shell wrapper  
- Scheduled overnight Day brief / ASX scan  
- Deeper RAG only if bridge + scale prove need  
- Un-shelve remaining depth items selectively  
