# Sprint 25 — Gmail labels (read + confirm-first mutate) (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B48  
**Depends on:** B31, B18, B15  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Read Gmail labels and support **confirm-first** label apply/remove (ADR-006) with audit — deeper mailbox hygiene without automation loops.

## Demo

1. List labels; propose label change on a message/thread
2. Confirm applies; Cancel no-ops
3. Audit entry

## Committed

### S25.1 — Gmail labels confirm-first (B48)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B48 |

**Acceptance criteria:**

- [ ] Read and display labels for messages/threads in panel
- [ ] Propose apply/remove → draft → confirm → execute → audit
- [ ] Reconsent if modify scope missing
- [ ] No bulk silent labeling; no auto-rules engine yet

---

**Out of scope (sprint):**

- Server-side Google Apps Script product
- Auto-label on every fetch
- Automated trading / order placement (Icebox)

## Parking lot

- Bulk label with multi-select confirm
