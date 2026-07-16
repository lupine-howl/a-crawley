# Sprint 18 — Gmail confirm-first send (planned)

**Status:** planned (after Sender Inbox scale preferred)  
**Duration:** one symbolic week  
**Backlog refs:** B84  
**Depends on:** ADR-006; Calendar write-back patterns (Sprint 8); Sender Inbox for reply context  
**UX:** `@ux-expert` for draft/confirm/send danger states  

## Goal

First **Gmail mutation**: draft → explicit confirm → send (or create-draft-only if safer — prefer confirm-then-send with clear irreversible copy). Reuse audit log. No silent automation.

## Demo

1. From Sender Inbox (or Gmail panel), compose/accept an LLM-assisted draft  
2. Review; Cancel = no send; Confirm = send  
3. Audit entry; reconsent path if write scope missing  

## Committed

### S18.1 — Gmail confirm-first send (B84)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B84 |

**Acceptance criteria:**

- [ ] Propose → draft/diff → confirm → send → audit
- [ ] Cancel performs no send
- [ ] Write scope + reconsent when needed; no casual scope creep
- [ ] Audit visible via existing viewer patterns
- [ ] Optional: start from Sender Inbox thread context

**Out of scope:** Bulk send, auto-triage sends, multi-account
