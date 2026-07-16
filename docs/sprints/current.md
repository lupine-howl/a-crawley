# Sprint 31 — Analytics JSON API (ASX + jobs)

**Status:** ready (Migration band — hard pivot)  
**Duration:** one symbolic week  
**Backlog refs:** B91, B92, B93  
**Depends on:** Shipped ASX desk (Sprints 13–30 brain)  
**Architecture:** [ADR-009](../adr/009-phone-preview-analytics.md) · [`../migration-phone-preview.md`](../migration-phone-preview.md)  
**Previous:** Depth band 21–30 complete (no open HTMX feature sprint)  
**Planned source:** [`planned/sprint-31-analytics-api.md`](planned/sprint-31-analytics-api.md)

## Goal

Make **Crawley analytics** callable without the Jinja product UI: versioned JSON API for ASX companies + job control, documented presentation DTOs, and OpenAPI. Freeze HTMX feature work (bugfixes only until Sprint 35 deletion).

## Demo

1. `GET /health` and `GET /v1/asx/companies` return JSON  
2. `POST /v1/asx/scan/start` (or equivalent) starts enrichment; `GET /v1/jobs/{id}` shows progress  
3. OpenAPI (or equivalent schema file) checked in and matches handlers  
4. No new Jinja product features landed  

## Committed

Implement **in order** (S31.1 → S31.2 → S31.3).

### S31.1 — Pivot docs lock + freeze HTMX features (B91)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B91 |

**Acceptance criteria:**

- [x] PRODUCT / ROADMAP / ADR-009 / migration doc describe the pivot (this PR)  
- [ ] Architect confirms no new Jinja product features; HTMX routes may remain until Sprint 35 but are non-product  
- [ ] Architecture overview diagram updated to analytics + UI split  

### S31.2 — ASX + jobs JSON API (B92)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B92 |

**Acceptance criteria:**

- [ ] `GET /health` → `{ ok, … }`  
- [ ] `GET /v1/asx/companies` and `GET /v1/asx/companies/{ticker}` (or equivalent) return presentation JSON from existing ASX data  
- [ ] Job control: start/pause/reset scan (or document mapping to existing controls) + `GET /v1/jobs/{id}` (or list)  
- [ ] Automated tests for happy-path JSON (no browser)  
- [ ] OAuth remains on analytics host (no change required beyond noting redirect stays here)  

### S31.3 — Presentation DTOs + OpenAPI (B93)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B93 |

**Acceptance criteria:**

- [ ] Documented presentation fields for company list, company detail, job status  
- [ ] OpenAPI 3 (or JSON Schema) checked in under `docs/` or served at `/openapi.json`  
- [ ] Field docs note worker store vs presentation; UI must not read raw scratch paths  

## Explicitly out of sprint

- `crawley-ui` scaffold (Sprint 32)  
- Gmail JSON API (Sprint 34)  
- Deleting Jinja (Sprint 35)  
- Turso / IndexedDB work (UI repo)  
- Calendar / lite modules  

## Parking lot

- Day brief as later composition pack  
- Bridge / themes / paper endpoints once ASX list+scan is stable  
