# Sprint 25 — ASX news theme clustering

**Status:** ready (next delivery; Sprints 26–30 archived out-of-order)  
**Duration:** one symbolic week  
**Backlog refs:** B47  
**Depends on:** Sprint 13–16 ASX desk + events skim; Sprint 23 notebook helpful  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** ASX desk / themes panel — no trade chrome  
**Previous:** [`archive/sprint-21-24-oauth-digests-notebook-vip.md`](archive/sprint-21-24-oauth-digests-notebook-vip.md)  
**Also closed (out-of-order):** [`archive/sprint-26-30-labels-holdings-search-attach-citations.md`](archive/sprint-26-30-labels-holdings-search-attach-citations.md)  
**Planned source:** [`planned/sprint-25-asx-news-clusters.md`](planned/sprint-25-asx-news-clusters.md)

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
- Re-opening closed 26–30 items

## Parking lot

- Tie-ins to playbooks / notebook / citations when useful
