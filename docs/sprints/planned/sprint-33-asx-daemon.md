# Sprint 33 — ASX daemon entrypoint (planned)

**Status:** planned (after Sprint 32 preferred; may overlap after 31)  
**Duration:** one symbolic week  
**Backlog refs:** B96  
**Depends on:** Sprint 31 job API  

## Goal

Promote the ASX scanner into a **clear daemon/worker entrypoint** (separate from “Uvicorn accidentally owns the scan forever”), with status still exposed via `/v1/jobs`.

## Demo

1. Start analytics API; start `asx-scanner` (or documented equivalent entrypoint)  
2. UI or `curl` can observe job progress  
3. Scratch data remains under `data/`; presentation via API unchanged  

## Committed

### S33.1 — asx-scanner entrypoint (B96)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B96 |

**Acceptance criteria:**

- [ ] Documented entrypoint for ASX scan loop (module CLI, second process, or supervisord example)  
- [ ] API can start/pause/reset or attach to that worker without Jinja  
- [ ] Architecture notes process boundaries (evolves ADR-003)  
- [ ] Threads OK inside the worker; no Celery required  

## Explicitly out of sprint

- gmail-ingest daemon (with Sprint 34/35)  
- Kubernetes / multi-host deploy  
