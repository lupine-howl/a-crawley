# Sprint 8 — Confirm-first Calendar write-back (planned)

**Status:** shelved (deferred — Sender Inbox + ASX PoC pivot)  
**Duration:** one symbolic week  
**Backlog refs:** B25, B26  
**Depends on:** Sprint 5 write-back design (B18); Sprint 3 shared Google + Calendar read (B15, B6)  
**Architecture:** [`docs/architecture.md`](../architecture.md) + Sprint 5 write-back ADR  
**UX:** **Schedule `@ux-expert`** for propose → confirm → result states (draft/diff clarity, danger of accidental writes); bind to ADR stages

## Goal

Ship the first **real** mutation: Calendar event insert with explicit user confirmation, draft-first UX, and a local audit trail — proving the Sprint 5 design without opening Gmail send or silent automation.

## Demo

Operator can:

1. Propose a Calendar event (manual fields and/or LLM-assisted draft)
2. Review draft/diff and **Cancel** with zero remote write, or **Confirm** to insert
3. See clear success/failure; reconnect/reconsent if write scope missing
4. Skim a bounded recent audit log of write attempts
5. Still cannot send Gmail from Crawley

## Committed

### S8.1 — Calendar write-back confirm-first (B25)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B25 |
| Depends on | B18, B6, B15 |

**Acceptance criteria:**

- [ ] Propose → show draft/diff → confirm → execute → audit stages implemented for Calendar insert
- [ ] Cancel path performs no remote write
- [ ] Google write scope requested only when needed; reconsent documented; Gmail send scope not added casually
- [ ] Success/failure UI states; primary calendar target documented if multi-calendar exists
- [ ] Local audit record under `data/` for each attempt
- [ ] Aligns with accepted Sprint 5 ADR (no silent automation)

---

### S8.2 — Write-back audit log viewer lite (B26)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B26 |
| Depends on | S8.1 |

**Acceptance criteria:**

- [ ] Settings or Calendar surfaces recent audit entries (bounded, newest first)
- [ ] Fields: timestamp, module, action summary, success/failure
- [ ] Read-only this sprint (no replay/edit required)

**Out of scope (sprint):**

- Gmail send / label mutation
- Bulk calendar sync tools, recurring-series advanced editor
- LocalLlama hosting, desktop wrapper

## Parking lot

- Gmail draft-then-send (separate backlog after Calendar soak)
- Undo/delete last inserted event from audit row
