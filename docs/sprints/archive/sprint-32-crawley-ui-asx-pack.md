# Sprint 32 — crawley-ui + ASX pack

**Status:** closed (archived)  
**Archived:** 2026-07-16  
**Promoted next:** [`../current.md`](../current.md) (Sprint 33 — ASX daemon)  
**Duration:** one symbolic week  
**Backlog refs:** B94, B95  
**Depends on:** Sprint 31 OpenAPI + ASX `/v1`  
**Architecture:** [ADR-009](../../adr/009-phone-preview-analytics.md) · [`../../migration-phone-preview.md`](../../migration-phone-preview.md)  
**Consume recipe:** [`../../build/consuming-published-core.md`](../../build/consuming-published-core.md)  
**Previous:** Migration Sprint 31 closed  
**Planned source:** [`../planned/sprint-32-crawley-ui-asx-pack.md`](../planned/sprint-32-crawley-ui-asx-pack.md)

## Goal

Scaffold **`crawley-ui`** from **published** Phone Preview packages and ship an **`asxDeskPack`** that lists companies and starts a scan via the analytics API (Vite proxy in dev).

## Demo

1. `npm` install / run `crawley-ui`  
2. ASX pack shows company list from `/v1/asx/companies`  
3. Start scan from UI; job progress visible  
4. No secrets in the Vite app; Google OAuth not required for this ASX-only slice  

## Committed

### S32.1 — crawley-ui scaffold (B94)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B94 |

**Acceptance criteria:**

- [x] App named `crawley-ui` using published `@phone-preview/core` ≥ 0.6.1  
- [x] README: run instructions, proxy to analytics, pointer to consume recipe  
- [x] UI persistence uses Phone Preview defaults (IndexedDB; Turso/Duck optional per PP)  
- [x] No analytics secrets in frontend env for browser-exposed keys  

### S32.2 — asxDeskPack (B95)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B95 |

**Acceptance criteria:**

- [x] Pack lists companies from analytics API  
- [x] Start (and show status for) ASX scan job  
- [x] Company detail from `GET /v1/asx/companies/{ticker}` (minimum viable)  
- [x] Errors/empty states honest; no trade chrome  

## Notes

- Host: `starterPacks()` + app-private `asxDeskPack` (no education packs, no `--with-api` analytics).  
- Proxy: `/api/analytics` → `:8000` with path rewrite.  
- Smoke: Vite proxy `/api/analytics/health` and `/v1/asx/companies` verified against running analytics.  
