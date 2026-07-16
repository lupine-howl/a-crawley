# Sprint 26 — Gmail labels confirm-first (planned)

**Status:** closed — see [`../archive/sprint-26-30-labels-holdings-search-attach-citations.md`](../archive/sprint-26-30-labels-holdings-search-attach-citations.md)
**Duration:** one symbolic week  
**Backlog refs:** B48  
**Depends on:** ADR-006; Sprint 18 Gmail send patterns  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-26.md`](sprint-26.md) remains a shelved stub if present — prefer this file.

## Goal

Read Gmail labels; confirm-first apply/remove with local audit — second mutation surface after send.

## Demo

1. See labels on a message/thread in Sender Inbox
2. Propose apply/remove → confirm → execute → audit
3. Cancel leaves no remote change; reconsent if modify scope missing

## Committed

### S26.1 — Labels confirm-first (B48)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B48 |

**Acceptance criteria:**

- [ ] Read and display labels for messages/threads in panel
- [ ] Propose apply/remove → draft → confirm → execute → audit
- [ ] Reconsent if modify scope missing
- [ ] No bulk silent labeling; no auto-rules engine yet

## Explicitly out of sprint

- Silent auto-label loops
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
