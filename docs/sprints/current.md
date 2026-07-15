# Sprint 1 — Local shell + lite Investment & Gmail

**Duration:** one symbolic week  
**Backlog refs:** B1–B5 (B6 stub only)  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-0-bootstrap.md`](archive/sprint-0-bootstrap.md)

## Goal

Ship a runnable Crawley shell on localhost with a modular dashboard: **lite Investment** and **lite Gmail** produce real LLM-backed summaries from bounded fetches; other top-tier modules are clickable **Coming soon** stubs.

## Demo (definition of done for the sprint)

Operator can:

1. Run the app and open the dashboard in a browser
2. Trigger a small investment search/scrape and see a summary/advice panel
3. Complete Gmail read-only OAuth (if needed) and see an inbox skim/summary
4. Open other top-tier modules and see Coming soon (no crashes)

## Committed

Implement **in order** (S1.1 → S1.5) unless dependencies already satisfied.

### S1.1 — Project skeleton & local run (B1)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B1 |

**Acceptance criteria:**

- [ ] `uv` project + `python -m crawley` (or equivalent) starts the server on localhost
- [ ] `.env.example` + gitignored secrets path documented
- [ ] Short run instructions for WSL/Linux

---

### S1.2 — Dashboard shell, contract, registry & stubs (B2, B6 stub)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B2, B6 |
| Depends on | S1.1 |

**Acceptance criteria:**

- [ ] FastAPI + Jinja2/HTMX dashboard with module navigation
- [ ] Module contract + explicit registry
- [ ] Top-tier nav: Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative
- [ ] Non-implemented modules (including Calendar & Fitness in this sprint) show Coming soon

---

### S1.3 — OpenAI LLM provider (B3)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B3 |
| Depends on | S1.1 |

**Acceptance criteria:**

- [ ] LLM provider interface + OpenAI implementation via env
- [ ] LocalLlama placeholder only
- [ ] Clear error when API key missing/invalid

---

### S1.4 — Investment lite (B4)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B4 |
| Depends on | S1.2, S1.3 |

**Acceptance criteria:**

- [ ] Bounded search/scrape → `data/` artifacts + DuckDB rows
- [ ] LLM synthesis shown on Investment panel
- [ ] Simple job/status (busy / done / error)

---

### S1.5 — Gmail lite read-only (B5)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B5 |
| Depends on | S1.2, S1.3 |

**Acceptance criteria:**

- [ ] OAuth installed-app on WSL/Linux; tokens local/gitignored; read-only scope
- [ ] Bounded inbox scan → email summary on Gmail panel
- [ ] Clear auth/API error states

## Explicitly out of sprint

- Real Calendar fetch (stub only)
- Fitness beyond stub
- Write-back, local LLM, LAN/phone, automated trading
- Deepening investment/mail UX (B7–B8)

## Parking lot

- Calendar read may share Google OAuth with Gmail when B6/B8 are pulled forward
- Exact list of stub labels can be shortened in UI if nav feels crowded
