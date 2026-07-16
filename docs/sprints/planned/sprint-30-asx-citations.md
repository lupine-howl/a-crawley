# Sprint 30 — ASX citations + source quality (planned)

**Status:** closed — see [`../archive/sprint-26-30-labels-holdings-search-attach-citations.md`](../archive/sprint-26-30-labels-holdings-search-attach-citations.md)
**Duration:** one symbolic week  
**Backlog refs:** B53  
**Depends on:** Sprint 13–25 ASX desk + clustering  
**Primary focus:** asx / investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-30.md`](sprint-30.md) remains a shelved stub if present — prefer this file.

## Goal

Structured citations and domain mute/quality tags for ASX scan/profile/recommend — close the 21–30 depth band with evidence hygiene.

## Demo

1. Advice/profile Markdown includes citations section from structured source records
2. Mute/exclude domains for future runs
3. Simple quality rubric documented

## Committed

### S30.1 — Citations & source quality (B53)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B53 |

**Acceptance criteria:**

- [ ] Structured source records in DuckDB/files (url, title, retrieved_at, quality tag)
- [ ] Profile/recommend Markdown includes citations section
- [ ] Operator can mute/exclude domains for future runs
- [ ] Document quality rubric simply in architecture or module notes

## Explicitly out of sprint

- Paywall bypass product
- Automated trading
- Full redesign

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
