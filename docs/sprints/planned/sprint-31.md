# Sprint 31 — Gmail follow-up tracker (planned)

**Status:** shelved (superseded — active migration Sprint 31 is [`sprint-31-analytics-api.md`](sprint-31-analytics-api.md) · B91–B93) (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B54  
**Depends on:** B44, B46  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Local **follow-up tracker**: pin threads that need a reply/waiting-on; surface in Gmail panel + optional home chip — no silent emails.

## Demo

1. Pin/unpin follow-ups with due note
2. List open follow-ups
3. LLM skim can prefer pinned threads

## Committed

### S31.1 — Follow-up tracker (B54)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B54 |

**Acceptance criteria:**

- [ ] Local follow-up records (thread id, note, due optional, status)
- [ ] Panel list + pin from thread digest
- [ ] Optional boost in priority skim
- [ ] No auto-send reminders off-machine

---

**Out of scope (sprint):**

- SMS/push notifications product
- Shared team CRM
- Automated trading / order placement (Icebox)

## Parking lot

- Confirm-first snooze label via Gmail
