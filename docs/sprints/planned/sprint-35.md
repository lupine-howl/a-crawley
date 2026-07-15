# Sprint 35 — Gmail confirm-first archive/trash batch (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B58  
**Depends on:** B25, B31, B33 helpful  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Mailbox hygiene: **multi-select confirm-first archive/trash** with draft list + audit — ADR-006 discipline.

## Demo

1. Select messages/threads from skim/digest
2. Confirm archive or trash
3. Cancel writes nothing; audit

## Committed

### S35.1 — Archive/trash batch confirm-first (B58)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B58 |

**Acceptance criteria:**

- [ ] Multi-select from recent skim/search results
- [ ] Propose archive or trash → confirm → execute → audit
- [ ] Clear irreversible copy for trash
- [ ] Caps on batch size

---

**Out of scope (sprint):**

- Auto-delete rules without confirm
- Spam-as-a-service
- Automated trading / order placement (Icebox)

## Parking lot

- Undo last batch via Gmail API if available
