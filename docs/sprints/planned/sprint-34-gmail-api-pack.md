# Sprint 34 — Sender Inbox API + pack (planned)

**Status:** planned (after Sprints 31–32)  
**Duration:** one symbolic week  
**Backlog refs:** B97, B98  
**Depends on:** Sprint 12+ Sender Inbox brain; Sprint 32 UI host  

## Goal

Expose **Sender Inbox** presentation over `/v1/gmail/…` and ship **`senderInboxPack`** in `crawley-ui`. Google OAuth remains on the analytics host; UI deep-links “Connect Google.”

## Demo

1. Connect Google via analytics OAuth URL opened from UI  
2. Start ingest; see senders / todos from JSON  
3. No Gmail secrets in Vite  

## Committed

### S34.1 — Gmail / Sender Inbox JSON API (B97)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B97 |

**Acceptance criteria:**

- [ ] Endpoints for senders list, sender detail (messages/todos/profile as available), ingest job control  
- [ ] OpenAPI updated  
- [ ] Tests for JSON happy path without browser  
- [ ] OAuth callback paths unchanged on analytics host  

### S34.2 — senderInboxPack (B98)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B98 |

**Acceptance criteria:**

- [ ] Pack: sender list → detail; start/stop ingest; show progress  
- [ ] “Connect Google” opens analytics OAuth URL (documented)  
- [ ] Theme/Phone Preview patterns; no auto-send from todos  

## Explicitly out of sprint

- Full Gmail send/labels packs (Later; APIs may stub or defer)  
- Calendar pack  
