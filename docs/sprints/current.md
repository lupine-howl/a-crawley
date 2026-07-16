# Current sprint — 34: Sender Inbox API + pack

**Theme:** Roadmap Theme 3 — Gmail path via JSON API + Phone Preview pack  
**Dates:** —  
**Goal:** Expose Sender Inbox as `/v1/gmail/…` presentation + ingest job control, and ship `senderInboxPack` in `crawley-ui`. OAuth stays on analytics; UI deep-links Connect Google. **No new Jinja/HTMX product UI.**

**Prerequisites:** Sprint 33 ASX daemon (closed). Follow [migration plan](../migration-phone-preview.md) Phase 4 and [ADR-009](../adr/009-phone-preview-analytics.md).

**Out of scope:** HTMX cutover (Sprint 35); Calendar pack; multi-account Gmail.

---

## Stories

### S34.1 — Sender Inbox JSON API (B97)

**Points:** 5  
**Status:** Todo  
**BACKLOG:** B97  

**Acceptance criteria:**

- [ ] Senders + detail + ingest job endpoints under `/v1/gmail/…` (or documented `/v1/sender-inbox/…`)
- [ ] OpenAPI + `presentation-v1.md` updated; structured JSON errors
- [ ] Automated tests for handlers (mock Gmail client) without browser

---

### S34.2 — senderInboxPack (B98)

**Points:** 5  
**Status:** Todo  
**BACKLOG:** B98  

**Acceptance criteria:**

- [ ] Sender list → detail; ingest start/stop (or equivalent) in `crawley-ui`
- [ ] OAuth Connect Google deep-link to analytics host documented
- [ ] No secrets in Vite; analytics JSON only

---

## Parking lot

- Multi-account Gmail
- Push / watch notifications
- Calendar pack (post–Sprint 35)

---

## Sprint review checklist

- [ ] All stories Done or explicitly deferred with reason
- [ ] `uv run pytest` green
- [ ] OpenAPI + architecture updated
- [ ] Archive this file → `archive/sprint-34-gmail-api-pack.md`; promote Sprint 35
