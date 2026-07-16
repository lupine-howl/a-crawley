# Sprint 31 — Analytics JSON API (ASX + jobs)

**Status:** closed (archived)  
**Archived:** 2026-07-16  
**Promoted next:** [`../current.md`](../current.md) (Sprint 32 — crawley-ui + ASX pack)  
**Duration:** one symbolic week  
**Backlog refs:** B91, B92, B93  
**Depends on:** Shipped ASX desk (Sprints 13–30 brain)  
**Architecture:** [ADR-009](../../adr/009-phone-preview-analytics.md) · [`../../migration-phone-preview.md`](../../migration-phone-preview.md)  
**Previous:** Depth band 21–30 complete  
**Planned source:** [`../planned/sprint-31-analytics-api.md`](../planned/sprint-31-analytics-api.md)

## Goal

Make **Crawley analytics** callable without the Jinja product UI: versioned JSON API for ASX companies + job control, documented presentation DTOs, and OpenAPI. Freeze HTMX feature work (bugfixes only until Sprint 35 deletion).

## Demo

1. `GET /health` and `GET /v1/asx/companies` return JSON  
2. `POST /v1/asx/scan/start` starts enrichment; `GET /v1/jobs/asx-scan` shows progress  
3. OpenAPI checked in (`docs/api/openapi-v1.json`) and served at `/openapi.json`  
4. No new Jinja product features landed  

## Committed

### S31.1 — Pivot docs lock + freeze HTMX features (B91)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B91 |

**Acceptance criteria:**

- [x] PRODUCT / ROADMAP / ADR-009 / migration doc describe the pivot  
- [x] Architect confirms no new Jinja product features; HTMX routes may remain until Sprint 35 but are non-product  
- [x] Architecture overview diagram updated to analytics + UI split  

### S31.2 — ASX + jobs JSON API (B92)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B92 |

**Acceptance criteria:**

- [x] `GET /health` → `{ ok, … }`  
- [x] `GET /v1/asx/companies` and `GET /v1/asx/companies/{ticker}` return presentation JSON  
- [x] Job control: start/pause/resume/reset + `GET /v1/jobs/{id}` (`asx-scan`)  
- [x] Automated tests for happy-path JSON (no browser)  
- [x] OAuth remains on analytics host  

### S31.3 — Presentation DTOs + OpenAPI (B93)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B93 |

**Acceptance criteria:**

- [x] Documented presentation fields (`docs/api/presentation-v1.md`)  
- [x] OpenAPI 3 checked in (`docs/api/openapi-v1.json`) + runtime `/openapi.json`  
- [x] Field docs note worker store vs presentation  

## Explicitly out of sprint

- `crawley-ui` scaffold (Sprint 32)  
- Gmail JSON API (Sprint 34)  
- Deleting Jinja (Sprint 35)  
- Turso / IndexedDB work (UI repo)  
- Calendar / lite modules  
