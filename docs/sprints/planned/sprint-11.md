# Sprint 11 — Gmail write-back (draft → confirm → send) (planned)

**Status:** shelved (shelved legacy plan — active Sprint 11 is Settings Update (`sprint-11-update.md`); Sender Inbox is Sprint 12)  
**Duration:** one symbolic week  
**Backlog refs:** B31  
**Depends on:** B18 (ADR-006), B25 (Calendar write-back patterns), B15  
**Architecture:** [`docs/architecture.md`](../architecture.md) + ADR-006  
**UX:** `@ux-expert` for draft/confirm/send danger states (mirror Sprint 8 Calendar)

## Goal

Second live mutation surface: **Gmail draft → explicit confirm → send** (or create draft-only if architect chooses safer first step — product preference is confirm-then-send with clear irreversible copy). Reuse audit log; no silent automation.

## Demo

1. Compose or accept an LLM-assisted reply/compose draft in Gmail panel
2. Review draft; Cancel with zero send; Confirm to send
3. Audit entry recorded; clear success/failure
4. Scope upgrade/reconsent path documented

## Committed

### S11.1 — Gmail confirm-first send (B31)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B31 |

**Acceptance criteria:**

- [ ] Propose → draft/diff → confirm → execute → audit for Gmail send (or documented draft-create-only variant with product note)
- [ ] Cancel performs no send
- [ ] Write scope requested only when needed; reconsent clear
- [ ] Local audit entries; reuse Sprint 8 viewer patterns
- [ ] No label bulk tools / auto-triage sends

**Out of scope:** Silent rules, multi-account, mailing-list managers
