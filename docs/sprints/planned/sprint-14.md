# Sprint 14 — Co-parenting ↔ Calendar sync (confirm-first) (planned)

**Status:** shelved (deferred — Sender Inbox + ASX PoC pivot)  
**Duration:** one symbolic week  
**Backlog refs:** B34  
**Depends on:** B19, B25  
**UX:** Confirm publish of handoff windows; conflict callouts

## Goal

Optional bridge: publish selected co-parenting handoff windows to Google Calendar with **confirm-first** write-back — still sole-operator; no other-parent accounts.

## Demo

1. Select local co-parenting entries → propose Calendar events
2. Confirm insert; Cancel writes nothing
3. Conflicts / duplicates called out honestly
4. Audit log entries

## Committed

### S14.1 — Co-parenting publish to Calendar (B34)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B34 |

**Acceptance criteria:**

- [ ] Operator selects entries to publish; draft list shown
- [ ] Confirm-first Calendar insert reusing Sprint 8 machinery
- [ ] Local schedule remains source of truth unless explicitly published
- [ ] No multi-user sharing; no silent recurring sync loops

**Out of scope:** Family calendar ACLs, court document export
