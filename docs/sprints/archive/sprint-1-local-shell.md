# Sprint 1 — Local shell + lite Investment & Gmail (archived)

**Archived:** 2026-07-15  
**Status:** closed (PO review)  
**Promoted to:** [`docs/sprints/current.md`](../current.md) (Sprint 2)  
**Architecture:** [`docs/architecture.md`](../../architecture.md)  
**Previous:** [`sprint-0-bootstrap.md`](sprint-0-bootstrap.md)

## Goal

Ship a runnable Crawley shell on localhost with a modular dashboard: **lite Investment** and **lite Gmail** produce real LLM-backed summaries from bounded fetches; other top-tier modules are clickable **Coming soon** stubs.

## Demo (definition of done for the sprint)

Operator can:

1. Run the app and open the dashboard in a browser
2. Trigger a small investment search/scrape and see a summary/advice panel
3. Complete Gmail read-only OAuth (if needed) and see an inbox skim/summary
4. Open other top-tier modules and see Coming soon (no crashes)

## Close-out notes (2026-07-15)

- S1.1–S1.5 acceptance criteria met in code; automated tests green (21 passed at close).
- Styling shipped as **custom CSS variables** in the shell template (not Tailwind CDN). Themable polish deferred to Sprint 2 (B7).
- Residual operational risk: live Gmail OAuth on stakeholder WSL (documented; not E2E-automated).

## Committed

### S1.1 — Project skeleton & local run (B1)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B1 |

**Acceptance criteria:**

- [x] `uv` project + `python -m crawley` (or equivalent) starts the server on localhost
- [x] `.env.example` + gitignored secrets path documented
- [x] Short run instructions for WSL/Linux

---

### S1.2 — Dashboard shell, contract, registry & stubs (B2, B6 stub)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B2, B6 |
| Depends on | S1.1 |

**Acceptance criteria:**

- [x] FastAPI + Jinja2/HTMX dashboard with module navigation
- [x] Module contract + explicit registry
- [x] Top-tier nav: Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative
- [x] Non-implemented modules (including Calendar & Fitness in this sprint) show Coming soon

---

### S1.3 — OpenAI LLM provider (B3)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B3 |
| Depends on | S1.1 |

**Acceptance criteria:**

- [x] LLM provider interface + OpenAI implementation via env
- [x] LocalLlama placeholder only
- [x] Clear error when API key missing/invalid

---

### S1.4 — Investment lite (B4)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B4 |
| Depends on | S1.2, S1.3 |

**Acceptance criteria:**

- [x] Bounded search/scrape → `data/` artifacts + DuckDB rows
- [x] LLM synthesis shown on Investment panel
- [x] Simple job/status (busy / done / error)

---

### S1.5 — Gmail lite read-only (B5)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B5 |
| Depends on | S1.2, S1.3 |

**Acceptance criteria:**

- [x] OAuth installed-app on WSL/Linux; tokens local/gitignored; read-only scope
- [x] Bounded inbox scan → email summary on Gmail panel
- [x] Clear auth/API error states

## Explicitly out of sprint (carried forward)

- Real Calendar fetch (stub only) — B6 later AC / B10
- Fitness beyond stub — B11
- Write-back, local LLM, LAN/phone, automated trading
- Design system / themable palette — **B7 → Sprint 2**
- LLM settings UI & connection test — **B8 → Sprint 2**
- Deepening investment/mail UX — B9–B10

## Parking lot (at close)

- Calendar read may share Google OAuth with Gmail when B6/B10 are pulled forward
- Exact list of stub labels can be shortened in UI if nav feels crowded
- Sprint 1 UI: custom CSS tokens in `base.html` — evolve into themes in B7
