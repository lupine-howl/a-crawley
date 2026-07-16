# Sprint 33 — ASX daemon entrypoint

**Status:** closed (archived)  
**Archived:** 2026-07-16  
**Promoted next:** [`../current.md`](../current.md) (Sprint 34 — Sender Inbox API + pack)  
**Ops:** [`../../daemons/asx-scanner.md`](../../daemons/asx-scanner.md)  
**Duration:** one symbolic week  
**Backlog refs:** B96  
**Depends on:** Sprint 31 job API; Sprint 32 UI optional  
**Architecture:** [ADR-003](../../adr/003-single-process-threads.md) (evolved) · [ADR-009](../../adr/009-phone-preview-analytics.md) · [`../../daemons/asx-scanner.md`](../../daemons/asx-scanner.md)  
**Previous:** Migration Sprint 32 closed  
**Planned source:** [`../planned/sprint-33-asx-daemon.md`](../planned/sprint-33-asx-daemon.md)

## Goal

Promote the ASX scanner into a **clear daemon/worker entrypoint** (separate from “Uvicorn accidentally owns the scan forever”), with status still exposed via `/v1/jobs`.

## Demo

1. Start analytics API with `CRAWLEY_ASX_WORKER=daemon`; start `asx-scanner watch`  
2. `curl` / UI start scan; observe `queued` → `busy` on `/v1/jobs/asx-scan`  
3. Scratch data remains under `data/`; presentation via API unchanged  

## Committed

### S33.1 — asx-scanner entrypoint (B96)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B96 |

**Acceptance criteria:**

- [x] Documented entrypoint: `python -m crawley.daemons.asx_scanner` / `crawley-asx-scanner` + [`docs/daemons/asx-scanner.md`](../../daemons/asx-scanner.md) (supervisord example)  
- [x] API can start/pause/stop/reset or queue for daemon without Jinja (`CRAWLEY_ASX_WORKER=daemon`)  
- [x] Architecture / ADR-003 notes process boundaries  
- [x] Threads OK inside the worker; no Celery required  

## Explicitly out of sprint

- gmail-ingest daemon (with Sprint 34/35)  
- Kubernetes / multi-host deploy  
