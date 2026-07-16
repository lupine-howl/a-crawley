# Sprint 25 — ASX news theme clustering (planned)

**Status:** promoted to [`../current.md`](../current.md) (ready — next delivery)  
**Duration:** one symbolic week  
**Backlog refs:** B47  
**Depends on:** Sprint 13–16 ASX desk + events skim  
**Primary focus:** asx / investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-25.md`](sprint-25.md) remains a shelved stub if present — prefer this file.

## Goal

Cluster bounded news/headlines across the active ASX set into cited **themes** — research aid, not trade signals.

## Demo

1. Run theme cluster for active set → themes with source lists
2. Hard caps preserved; empty/error honest
3. No trade buttons

## Committed

### S25.1 — Active-set news clustering (B47)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B47 |

**Acceptance criteria:**

- [ ] Bounded fetch/reuse of headlines across active ASX set
- [ ] LLM or heuristic clustering into themes with source lists
- [ ] Panel shows clusters + summary; hard caps preserved
- [ ] No trade buttons; clear empty/error taxonomy

## Explicitly out of sprint

- Streaming quotes product
- Order tickets
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
