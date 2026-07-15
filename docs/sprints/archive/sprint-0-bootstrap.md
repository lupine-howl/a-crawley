# Sprint 0 — Bootstrap (archived)

**Archived:** 2026-07-15  
**Promoted to:** [`docs/sprints/current.md`](../current.md) (Sprint 1)

## Goal

PO locks product direction and the first delivery plan; architect locks `docs/architecture.md`. No application code until Architect Interview 2 (Sprint 1).

## Sequence

1. PO Interview 1 → brief + roadmap (`S0.1`) — done
2. PO Interview 2 → backlog + Planned Sprint 1 (`S0.2`) — content filled; Planned Sprint 1 promoted on S0.3 close-out
3. Architect Interview 1 → `docs/architecture.md` (`S0.3`) — done
4. Archive this file → write Sprint 1 as `docs/sprints/current.md` → Architect Interview 2 implements — done (archive + promote)

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
| Status | done |
| Owner | Product owner |
| Depends on | S0.1 done |

**Acceptance criteria:**

- [x] Stakeholder interviewed on near-term priorities and first delivery slice
- [x] `BACKLOG.md` has at least 3 prioritized items with goal, AC, out of scope, dependencies
- [x] **Planned Sprint 1** section filled (goal + committed stories)
- [x] Stakeholder confirmed backlog + Planned Sprint 1 — *close-out treated Planned Sprint 1 as authoritative for promotion (2026-07-15)*

**Out of scope:**

- Writing `docs/architecture.md` (Architect Interview 1)
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
| Status | done |
| Owner | Architect / developer |
| Depends on | S0.2 / Planned Sprint 1 |

**Acceptance criteria:**

- [x] Stakeholder interviewed on stack, deploy, data, integrations, constraints
- [x] `docs/architecture.md` written (overview, stack, boundaries, key flows, decisions, risks)
- [x] Architecture aligned enough to execute Planned Sprint 1
- [x] Stakeholder confirmed architecture
- [x] Sprint 0 archived to `docs/sprints/archive/`; `docs/sprints/current.md` becomes Sprint 1 from the Planned Sprint 1 section

**Notes:**

- Architecture + ADRs 001–005 confirmed 2026-07-15; aligned to Sprint 1 on S0.3 close-out.
- No application code in S0.3 (Architect Interview 2 implements Sprint 1).

**Out of scope:**

- Application code and Sprint 1 implementation (Architect Interview 2)

## Planned Sprint 1 (snapshot at archive)

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

- S1.1 — Project skeleton & local run (B1)
- S1.2 — Dashboard shell, contract, registry & stubs (B2, B6 stub)
- S1.3 — OpenAI LLM provider (B3)
- S1.4 — Investment lite (B4)
- S1.5 — Gmail lite read-only (B5)

### Explicitly out of sprint

- Real Calendar fetch (stub only)
- Fitness beyond stub
- Write-back, local LLM, LAN/phone, automated trading
- Deepening investment/mail UX (B7–B8)

## Parking lot (at archive)

- Calendar read may share Google OAuth with Gmail when B6/B8 are pulled forward
- Exact list of stub labels can be shortened in UI if nav feels crowded
