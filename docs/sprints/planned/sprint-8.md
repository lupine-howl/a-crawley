# Sprint 8 — Confirm-first Calendar write-back (planned)

**Status:** proposed (architect) — activates after Sprint 7 closes; requires Sprint 5 ADR soak  
**Duration:** one symbolic week  
**Backlog refs:** B25, B26  
**Depends on:** ADR-006 + Sprint 5 write-back dry-run (B18); Sprint 3 shared Google + Calendar read (B15, B6)  
**Architecture:** [`docs/architecture.md`](../architecture.md) + [`docs/adr/006-write-back-confirm.md`](../adr/006-write-back-confirm.md)  
**UX:** **Schedule `@ux-expert`** for propose → confirm → result states (draft/diff clarity; accidental-write risk)

## Goal

Ship the first **real** mutation: Calendar event insert with explicit user confirmation, draft-first UX, and a local audit trail — proving ADR-006 without opening Gmail send or silent automation.

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
- [ ] Google **Calendar write** scope requested only when needed; reconsent documented; **Gmail send scope not added**
- [ ] Success/failure UI states; primary calendar target documented if multi-calendar exists
- [ ] Local audit record under `data/` for each attempt (extend `writeback_audit.jsonl` or successor)
- [ ] Aligns with ADR-006 (no silent automation); `WriteBackCapability` flips from dry-run-only for Calendar insert path

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

## Architect notes

- Keep OAuth scope additive and **narrow**: Calendar events write only; leave Gmail readonly. Document reconsent and token file impact.
- Prefer a session-scoped draft token (UUID) so Confirm always binds to a specific propose result — prevents double-submit against a stale form.
- Update ADR-006 status note or add ADR-007 if execute-path trade-offs need a separate decision (e.g. primary calendar selection).

## Parking lot

- Gmail draft-then-send (separate backlog after Calendar soak)
- Undo/delete last inserted event from audit row
