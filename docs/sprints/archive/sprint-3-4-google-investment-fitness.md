# Sprint 3–4 — Google life reads + Investment/Fitness depth (bundled)

**Status:** done (delivered as one implementation bundle)  
**Duration:** one symbolic compound sprint  
**Backlog refs:** B6, B9, B10, B11, B15, B16  
**Depends on:** Sprint 2 (Settings, Markdown, home glance)  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-2-themes-settings-glance.md`](archive/sprint-2-themes-settings-glance.md)  
**Planned sources:** [`planned/sprint-3.md`](planned/sprint-3.md), [`planned/sprint-4.md`](planned/sprint-4.md)

## Goal

Finish **Google life reads** (shared read-only OAuth, Calendar live, hardened Gmail), deepen **Investment**, land **Fitness** lite (non-clinical), and extend home **At a glance** for Calendar + Fitness.

## Demo

Operator can:

1. Connect one Google identity with Gmail **and** Calendar read-only scopes (reconnect if Gmail-only token)
2. Run Calendar → bounded upcoming events → Markdown summary; snapshot on home
3. Run improved Gmail skim (Priorities / Follow-ups; clearer auth/quota/empty)
4. Run Investment with cache + richer Markdown advice; use-cache control
5. Run Fitness with a goal → introductory plan + medical disclaimer; snapshot on home
6. See Investment / Gmail / Calendar / Fitness slots on dashboard home

## Committed

### S3.1 — Shared Google OAuth (B15)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B15 |

**Acceptance criteria:**

- [x] Single installed-app OAuth grants Gmail readonly + Calendar readonly
- [x] Tokens under `data/secrets/` (`google_token.json`; legacy `gmail_token.json` still read/synced); reconsent when Calendar missing
- [x] Gmail/Calendar panels surface connected / reconnect state
- [x] No write/modify scopes
- [x] README notes redirect URI + enable both APIs

---

### S3.2 — Calendar module live (B6)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B6 |

**Acceptance criteria:**

- [x] Calendar leaves Coming soon; Run for bounded upcoming window
- [x] Events → files/DuckDB → LLM Markdown summary
- [x] Job busy/done/error; honest empty calendar
- [x] Snapshot on success for home glance
- [x] Actionable missing-scope / auth errors

---

### S3.3 — Harden Gmail lite (B10)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B10 |

**Acceptance criteria:**

- [x] Clearer inbox summary prompt (Priorities / Follow-ups)
- [x] Better auth expiry, quota, empty inbox handling
- [x] Bounded fetch unchanged in spirit
- [x] Shared Google credentials from S3.1

---

### S4.1 — Harden Investment crawl & advice (B9)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B9 |

**Acceptance criteria:**

- [x] Query cache under `data/investment/cache/` (1h TTL) + “Use cache” checkbox
- [x] Slightly richer bounded sources (5 items + publisher/pubDate metadata)
- [x] Advice Markdown template: what’s moving / risks / watch list
- [x] Error taxonomy: network, parse, empty, LLM
- [x] Panel shows sources this run + summary
- [x] No trading UI

---

### S4.2 — Fitness module lite (B11)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B11 |

**Acceptance criteria:**

- [x] Fitness leaves Coming soon
- [x] Goal form + last goal persisted locally
- [x] LLM Markdown introductory plan
- [x] Explicit not-medical-advice disclaimer
- [x] Job + Markdown + success snapshot
- [x] No wearables required

---

### S4.3 — Home glance slots (B16)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B16 |

**Acceptance criteria:**

- [x] Home shows Investment, Gmail, Calendar, Fitness last runs
- [x] Truncated summary bodies; no stub filler cards
- [x] Architecture documents glance participants

## Out of scope (this bundle)

- Write-back, multi-account Google
- Wearables, brokerage APIs
- Phone-on-LAN / Work lite (Sprint 5)
- Co-parenting / DIY / Finance live modules

## Parking lot

- Agenda+inbox combined “day brief”
- Investment watchlist symbols file
- Fitness data import (Strava/etc.)
