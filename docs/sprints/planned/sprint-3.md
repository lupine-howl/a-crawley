# Sprint 3 — Calendar + Google depth (planned)

**Status:** planned (activates after Sprint 2 closes)  
**Duration:** one symbolic week  
**Backlog refs:** B6, B10, B15  
**Depends on:** Sprint 2 done (Settings, Markdown, home glance preferred)  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer a short `@ux-expert` pass for Calendar panel + shared Google connect states if chrome changes; else follow Sprint 2 patterns

## Goal

Complete the product success metric for **Google life reads**: real **Calendar** skim/summary beside hardened **Gmail**, on a **shared read-only Google OAuth** identity, with Calendar present on home At a glance.

## Demo

Operator can:

1. Connect (or reuse) one Google identity with Gmail **and** Calendar **read-only** scopes
2. Run Calendar → bounded upcoming events → Markdown summary/advice in the panel
3. Run an improved Gmail skim (clearer structure/errors; still bounded)
4. See last Calendar (and existing Gmail) snapshots on dashboard home
5. Revoke/reconnect path documented; no write scopes

## Committed

### S3.1 — Shared Google OAuth (read-only Gmail + Calendar) (B15)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B15 |

**Acceptance criteria:**

- [ ] Single installed-app OAuth flow can grant Gmail readonly + Calendar readonly (documented scopes)
- [ ] Tokens stored locally/gitignored; upgrade/reconsent path if prior Gmail-only token lacks Calendar
- [ ] Settings or Gmail/Calendar panels surface clear “Google connected / reconnect” state (minimal; not a full credentials suite)
- [ ] No write/modify scopes
- [ ] README / architecture notes WSL redirect URI updates if any

---

### S3.2 — Calendar module live (read-only lite) (B6)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B6 |
| Depends on | S3.1 |

**Acceptance criteria:**

- [ ] Calendar leaves Coming soon; panel has Run (or equivalent) for bounded upcoming window
- [ ] Events fetched read-only → optional light normalize into DuckDB/files → LLM Markdown summary
- [ ] Job busy/done/error; empty calendar honest empty state
- [ ] Snapshot on success for home glance (reuse S2.4 store)
- [ ] Errors for missing scope / expired token are actionable

---

### S3.3 — Harden Gmail lite (B10)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B10 |
| Depends on | S3.1 |

**Acceptance criteria:**

- [ ] Clearer inbox summary prompt/structure (e.g. priorities / follow-ups sections in Markdown)
- [ ] Better handling of auth expiry, API quota, and empty inbox
- [ ] Bounded fetch unchanged in spirit (no full-history sync)
- [ ] Continues to use shared Google credentials from S3.1

**Out of scope (sprint):**

- Write-back, labels mutation, multi-account
- Fitness, Investment depth, phone-on-LAN

## Parking lot

- Agenda+inbox combined “day brief” on home → **[Sprint 7](sprint-7.md)**
- Calendar write-back draft flow → design in [Sprint 5](sprint-5.md); implement **[Sprint 8](sprint-8.md)**
