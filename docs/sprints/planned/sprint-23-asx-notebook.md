# Sprint 23 — ASX research notebook + thesis (planned)

**Status:** closed — see [`../archive/sprint-21-24-oauth-digests-notebook-vip.md`](../archive/sprint-21-24-oauth-digests-notebook-vip.md)  
**Duration:** one symbolic week  
**Backlog refs:** B45  
**Depends on:** Sprint 13–14 ASX desk + paper  
**Primary focus:** asx / investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-23.md`](sprint-23.md) remains a shelved stub if present — prefer this file.

## Goal

Give the ASX desk durable **thesis notes** and a per-ticker **research notebook** that seeds profile/recommendation LLM runs — still manual action only; not a broker product.

## Demo

1. Edit thesis/notes for an ASX ticker on the company profile
2. Regenerate profile/recommendations that optionally cite notebook (hard-capped)
3. No trading UI / live orders

## Committed

### S23.1 — ASX thesis & notebook (B45)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B45 |

**Acceptance criteria:**

- [ ] Local notebook/thesis store per ticker under data/
- [ ] Panel UX to view/edit notes on ASX company profile
- [ ] Scan/profile/recommend can optionally include notebook slice (hard-capped)
- [ ] Advice/recommendation Markdown remains non-order
- [ ] Empty notebook honest

## Explicitly out of sprint

- Brokerage sync
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
