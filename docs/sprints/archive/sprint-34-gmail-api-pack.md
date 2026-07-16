# Sprint 34 — Gmail ingest daemon + Sender Inbox pack

**Status:** closed (archived)  
**Archived:** 2026-07-16  
**Promoted next:** [`../current.md`](../current.md) (Sprint 35 — HTMX cutover)  
**Duration:** one symbolic week  
**Backlog refs:** B97, B98  
**Depends on:** Sprint 33 ASX daemon patterns; Sender Inbox brain  
**Architecture:** [ADR-009](../../adr/009-phone-preview-analytics.md) · [`../../daemons/gmail-ingest.md`](../../daemons/gmail-ingest.md)  
**Previous:** Migration Sprint 33 closed  
**Planned source:** [`../planned/sprint-34-gmail-api-pack.md`](../planned/sprint-34-gmail-api-pack.md)

## Goal

Restore the former Sender Inbox PoC loop on Phone Preview: **gmail-ingest daemon**, `/v1/gmail/…`, and `senderInboxPack` with ASX-like Start/Stop — scan mail → senders + reports. No new Jinja.

## Demo

1. `CRAWLEY_GMAIL_WORKER=daemon` + `crawley-gmail-ingest watch`  
2. UI Start ingest → `queued` → `busy` on `/v1/jobs/gmail-ingest`  
3. Sender list → detail with profile markdown report  

## Committed

### S34.1 — gmail-ingest daemon (B97)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B97 |

**Acceptance criteria:**

- [x] `crawley.daemons.gmail_ingest` / `crawley-gmail-ingest` + docs  
- [x] `CRAWLEY_GMAIL_WORKER=daemon` queue handoff  
- [x] In-process default; no Celery  

### S34.2 — Sender Inbox JSON API (B97)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B97 |

**Acceptance criteria:**

- [x] `/v1/gmail/senders` + detail/report  
- [x] Ingest start/stop/pause/resume/reset; job `gmail-ingest`  
- [x] Connection + OAuth deep-link  
- [x] OpenAPI / presentation docs + tests  

### S34.3 — senderInboxPack (B98)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B98 |

**Acceptance criteria:**

- [x] Start/Stop + poll like ASX desk  
- [x] Sender list → report + messages  
- [x] Connect Google deep-link; no Vite secrets  

## Explicitly out of sprint

- Labels / send / VIP pack surfaces  
- Calendar pack  
- HTMX deletion (Sprint 35)  
