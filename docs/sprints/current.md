# Sprint 0 — Bootstrap

## Goal

PO locks product direction and the first delivery plan; architect locks `docs/architecture.md`. No application code until Architect Interview 2 (Sprint 1).

## Sequence

1. PO Interview 1 → brief + roadmap (`S0.1`)
2. PO Interview 2 → backlog + Planned Sprint 1 (`S0.2`)
3. Architect Interview 1 → `docs/architecture.md` (`S0.3`)
4. Archive this file → write Sprint 1 as `docs/sprints/current.md` → Architect Interview 2 implements

## Committed

### S0.1 — PO Interview 1: project brief & roadmap

| Field | Value |
|-------|-------|
| Status | done |
| Owner | Product owner |

**Acceptance criteria:**

- [x] Stakeholder interviewed on problem, users, goals, non-goals, constraints, metrics
- [x] `PRODUCT.md` written as the project brief
- [x] `ROADMAP.md` has Now / Next / Later themes
- [x] Stakeholder confirmed brief + roadmap

**Out of scope:**

- Backlog, Sprint 1 planning, architecture, application code

---

### S0.2 — PO Interview 2: backlog & Planned Sprint 1

| Field | Value |
|-------|-------|
| Status | in_progress |
| Owner | Product owner |
| Depends on | S0.1 done |

**Acceptance criteria:**

- [x] Stakeholder interviewed on near-term priorities and first delivery slice
- [x] `BACKLOG.md` has at least 3 prioritized items with goal, AC, out of scope, dependencies
- [x] **Planned Sprint 1** section below filled (goal + committed stories) — do **not** replace this Sprint 0 file yet
- [ ] Stakeholder confirmed backlog + Planned Sprint 1

**Out of scope:**

- Writing `docs/architecture.md` (Architect Interview 1) — already done
- Application code

**Notes (Interview 2 decisions):**

- Sprint shape: **foundation (B) + lite verticals (A)** for Investment **and** Gmail
- Calendar + other top-tier domains: stubs / Coming soon
- Cadence: **one symbolic week**
- Demo bar: run app → dashboard → investment summary from small scrape/search → email summary from quick inbox scan → stub modules clickable with Coming soon

---

### S0.3 — Architect Interview 1: architecture

| Field | Value |
|-------|-------|
| Status | in_progress |
| Owner | Architect / developer |
| Depends on | S0.2 done (soft: docs drafted against Now themes; archive blocked until Planned Sprint 1 confirmed) |

**Acceptance criteria:**

- [x] Stakeholder interviewed on stack, deploy, data, integrations, constraints
- [x] `docs/architecture.md` written (overview, stack, boundaries, key flows, decisions, risks)
- [ ] Architecture aligned enough to execute Planned Sprint 1 — *pending S0.2 confirm*
- [x] Stakeholder confirmed architecture
- [ ] Sprint 0 archived to `docs/sprints/archive/`; `docs/sprints/current.md` becomes Sprint 1 from the Planned Sprint 1 section — *blocked on S0.2 confirm*

**Notes:**

- Architecture + ADRs 001–005 confirmed 2026-07-15.
- No application code until Architect Interview 2.

**Out of scope:**

- Application code and Sprint 1 implementation (Architect Interview 2)

## Planned Sprint 1

**Duration:** one symbolic week  
**Backlog refs:** B1–B5 (B6 stub only)

### Goal

Ship a runnable Crawley shell on localhost with a modular dashboard: **lite Investment** and **lite Gmail** produce real LLM-backed summaries from bounded fetches; other top-tier modules are clickable **Coming soon** stubs.

### Demo (definition of done for the sprint)

Operator can:

1. Run the app and open the dashboard in a browser
2. Trigger a small investment search/scrape and see a summary/advice panel
3. Complete Gmail read-only OAuth (if needed) and see an inbox skim/summary
4. Open other top-tier modules and see Coming soon (no crashes)

### Committed

#### S1.1 — Project skeleton & local run (B1)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B1 |

**Acceptance criteria:**

- [ ] `uv` project + `python -m crawley` (or equivalent) starts the server on localhost
- [ ] `.env.example` + gitignored secrets path documented
- [ ] Short run instructions for WSL/Linux

---

#### S1.2 — Dashboard shell, contract, registry & stubs (B2, B6 stub)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B2, B6 |

**Acceptance criteria:**

- [ ] FastAPI + Jinja2/HTMX dashboard with module navigation
- [ ] Module contract + explicit registry
- [ ] Top-tier nav: Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative
- [ ] Non-implemented modules (including Calendar & Fitness in this sprint) show Coming soon

---

#### S1.3 — OpenAI LLM provider (B3)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B3 |

**Acceptance criteria:**

- [ ] LLM provider interface + OpenAI implementation via env
- [ ] LocalLlama placeholder only
- [ ] Clear error when API key missing/invalid

---

#### S1.4 — Investment lite (B4)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B4 |

**Acceptance criteria:**

- [ ] Bounded search/scrape → `data/` artifacts + DuckDB rows
- [ ] LLM synthesis shown on Investment panel
- [ ] Simple job/status (busy / done / error)

---

#### S1.5 — Gmail lite read-only (B5)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B5 |

**Acceptance criteria:**

- [ ] OAuth installed-app on WSL/Linux; tokens local/gitignored; read-only scope
- [ ] Bounded inbox scan → email summary on Gmail panel
- [ ] Clear auth/API error states

### Explicitly out of sprint

- Real Calendar fetch (stub only)
- Fitness beyond stub
- Write-back, local LLM, LAN/phone, automated trading
- Deepening investment/mail UX (B7–B8)

## Parking lot

- Calendar read may share Google OAuth with Gmail when B6/B8 are pulled forward
- Exact list of stub labels can be shortened in UI if nav feels crowded
