# Sprint 28 — Gmail saved searches (planned)

**Status:** closed — see [`../archive/sprint-26-30-labels-holdings-search-attach-citations.md`](../archive/sprint-26-30-labels-holdings-search-attach-citations.md)
**Duration:** one symbolic week  
**Backlog refs:** B50  
**Depends on:** Sprint 12–15 Sender Inbox  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-28.md`](sprint-28.md) remains a shelved stub if present — prefer this file.

## Goal

Named Gmail / Sender Inbox queries the operator reuses for bounded skims — not a full offline index.

## Demo

1. Save named query; run bounded fetch
2. Results feed Sender Inbox ingest or classic skim path
3. Invalid query / API errors actionable

## Committed

### S28.1 — Named saved searches (B50)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B50 |

**Acceptance criteria:**

- [ ] Persist named queries under data/
- [ ] Panel query builder or advanced string field with examples
- [ ] Run bounded fetch for query; job status
- [ ] Invalid query / API errors actionable

## Explicitly out of sprint

- Full offline index
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
