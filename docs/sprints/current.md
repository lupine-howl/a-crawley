# Sprint 32 — crawley-ui + ASX pack

**Status:** blocked (awaiting Phone Preview consume path)  
**Duration:** one symbolic week  
**Backlog refs:** B94, B95  
**Depends on:** Sprint 31 OpenAPI + ASX `/v1` ([archive](archive/sprint-31-analytics-api.md))  
**Architecture:** [ADR-009](../adr/009-phone-preview-analytics.md) · [`../migration-phone-preview.md`](../migration-phone-preview.md)  
**API contract:** [`../api/presentation-v1.md`](../api/presentation-v1.md) · [`../api/openapi-v1.json`](../api/openapi-v1.json)  
**UX:** Prefer `@ux-expert` pass for ASX pack IA against Phone Preview shell  
**Previous:** Migration Sprint 31 closed  
**Planned source:** [`planned/sprint-32-crawley-ui-asx-pack.md`](planned/sprint-32-crawley-ui-asx-pack.md)

## Goal

Scaffold **`crawley-ui`** from **published** Phone Preview packages and ship an **`asxDeskPack`** that lists companies and starts a scan via the analytics API (Vite proxy in dev).

## Demo

1. `npm` install / run `crawley-ui`  
2. ASX pack shows company list from `/v1/asx/companies`  
3. Start scan from UI; job progress visible  
4. No secrets in the Vite app; Google OAuth not required for this ASX-only slice  

## Blocker (2026-07-16)

Published `@phone-preview/core@0.6.0` is a **monorepo re-export stub** (`export … from "../../../web/src/…"`). It does not contain Shell/pack runtime when installed from npm; `create-phone-preview@0.4.0` also imports `starterPacks`, which is **not** exported from core@0.6.0 (`withoutEducationFeatures` is). `lupine-howl/phone-preview` is not readable from this agent.

**Need from stakeholder / PP team before S32.1:** consume path for a custom host (see questions on the story).

## Committed

Implement **in order** (S32.1 → S32.2).

### S32.1 — crawley-ui scaffold (B94)

| Field | Value |
|-------|-------|
| Status | blocked |
| Backlog ref | B94 |

**Acceptance criteria:**

- [ ] Repo or app named `crawley-ui` using published `@phone-preview/*`  
- [ ] README: run instructions, proxy to analytics, pointer to PP setup recipe  
- [ ] UI persistence uses Phone Preview defaults (IndexedDB; Turso/Duck optional per PP)  
- [ ] No analytics secrets in frontend env for browser-exposed keys  

**Blocker questions:**

1. How should we consume PP today — (a) app inside phone-preview monorepo (`apps/crawley`), (b) wait for a real published `@phone-preview/core` tarball, (c) git/file dependency to a checkout, or (d) other?  
2. Where should `crawley-ui` live — subdirectory of `a-crawley`, separate repo, or PP `apps/`?  

### S32.2 — asxDeskPack (B95)

| Field | Value |
|-------|-------|
| Status | blocked |
| Backlog ref | B95 |

**Acceptance criteria:**

- [ ] Pack lists companies from analytics API  
- [ ] Start (and show status for) ASX scan job  
- [ ] Company detail from `GET /v1/asx/companies/{ticker}` (minimum viable)  
- [ ] Errors/empty states honest; no trade chrome  

**Open (pack composition — answer when unblocked):**

3. Pack set for MVP: `starterPacks()` + `asxDeskPack`, or `withoutEducationFeatures()` + `asxDeskPack` only?  
4. Dev proxy: `/api/analytics` → `:8000` with path rewrite (UI calls `/api/analytics/v1/…`), or proxy `/v1` + `/health` directly?  
5. Is demo login (`admin@demo.local` / `demo123`) required for Sprint 32, or can ASX pack work before PP auth/Connections are configured?  

## Explicitly out of sprint

- Sender Inbox pack (Sprint 34)  
- Deleting Jinja (Sprint 35)  
- Full paper/recommend UI (Later in migration)  

## Parking lot

- Settings pack for LLM/caps once analytics settings API exists  
