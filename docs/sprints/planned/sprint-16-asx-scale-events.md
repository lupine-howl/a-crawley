# Sprint 16 — ASX scale + earnings/events skim (planned)

**Status:** done (delivered in [`../current.md`](../current.md) Sprints 15–17 bundle)  

**Duration:** one symbolic week  
**Backlog refs:** B81, B82  
**Depends on:** Sprint 13 ASX desk; Sprint 14 paper/recommendations preferred  

## Goal

Scale ASX desk beyond the 20-company PoC slice and add a bounded **earnings/events skim** for the active set — still polite background scan, no live trading.

## Demo

1. Expand/select a larger active scan set (e.g. 50) with progress  
2. Run earnings/events skim for the active set → Markdown + structured rows  
3. Profiles remain regenerable; rate limits respected  

## Committed

### S16.1 — ASX active-set scale (B81)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B81 |

**Acceptance criteria:**

- [x] Operator can enlarge active scan set beyond 20 within a documented hard ceiling
- [x] Scanner/progress UI handles larger N; pause/resume preserved
- [x] Universe list still the source; provenance unchanged

### S16.2 — Earnings & events skim (B82)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B82 |

**Acceptance criteria:**

- [x] Bounded fetch of earnings/event-like signals for active set
- [x] Markdown/table of upcoming/recent events + optional LLM wrap
- [x] Hard caps; honest empty; non-advice copy

**Out of scope:** Paid data terminals; auto trades around earnings
