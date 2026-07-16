# Sprint 32 — crawley-ui + ASX pack (planned)

**Status:** planned (after Sprint 31)  
**Duration:** one symbolic week  
**Backlog refs:** B94, B95  
**Depends on:** Sprint 31 OpenAPI + ASX `/v1`  
**UX:** Prefer `@ux-expert` pass for ASX pack IA against Phone Preview shell  

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
| Status | todo |
| Backlog ref | B94 |

**Acceptance criteria:**

- [ ] Repo or app named `crawley-ui` using published `@phone-preview/*`  
- [ ] README: run instructions, proxy to analytics, pointer to PP setup recipe  
- [ ] UI persistence uses Phone Preview defaults (IndexedDB; Turso/Duck optional per PP)  
- [ ] No analytics secrets in frontend env for browser-exposed keys  

### S32.2 — asxDeskPack (B95)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B95 |

**Acceptance criteria:**

- [ ] Pack lists companies from analytics API  
- [ ] Start (and show status for) ASX scan job  
- [ ] Company detail from `GET /v1/asx/companies/{ticker}` (minimum viable)  
- [ ] Errors/empty states honest; no trade chrome  

## Explicitly out of sprint

- Sender Inbox pack (Sprint 34)  
- Deleting Jinja (Sprint 35)  
- Full paper/recommend UI (Later in migration)  

## Parking lot

- Settings pack for LLM/caps once analytics settings API exists  
