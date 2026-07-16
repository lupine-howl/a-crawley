# ADR-009: Phone Preview UI + Python analytics / daemons

- **Status:** Accepted
- **Date:** 2026-07-16
- **Supersedes (product surface):** ADR-001 “Jinja/HTMX is the product UI”
- **Evolves:** ADR-003 (single process) → API process + explicit worker/daemon entrypoints
- **Related:** ADR-002 (DuckDB/filesystem worker store); ADR-006 (confirm-first mutations stay on analytics host)

## Context

Crawley PoC shipped a capable Python brain (ASX desk, Sender Inbox, Google OAuth, LLM, jobs) behind a FastAPI + Jinja2/HTMX shell. The desired product shape is different:

- **Presentation:** Phone Preview host (`crawley-ui`), packs for desks, local UI persistence (IndexedDB; optional Turso/Duck sync via Phone Preview’s light backend).
- **Analytics:** Python process(es) as semi-autonomous daemons with private scratch stores that **publish** to a presentation surface the UI reads via JSON.

Stakeholder decisions (2026-07-16):

- Install UI via **npm** as `crawley-ui`; consume **published** `@phone-preview/*` packages.
- **Delete** HTMX/Jinja product UI after JSON API covers ASX + Gmail — no permanent `/ops` HTML UI; ops move into `crawley-ui`.
- UI persistence is primarily **IndexedDB** (Phone Preview); Turso/Duck are persistence options for the UI layer, not a replacement for analytics workers.
- **Calendar** and lite life modules (Fitness, Co-parenting, DIY, Work, Finance, Coding) are **out of product surface** for this pivot; Calendar may return later.
- Former Sprint 25-style ASX theme work and depth **31–40** stay shelved until after UI migration.

## Decision

1. **Product UI** = `crawley-ui` on Phone Preview (Vite + published core). Packs: ASX desk, Sender Inbox first; Settings/Connections in UI.
2. **Analytics server** = this repo (`a-crawley` / `crawley` Python package): versioned **JSON API** (`/v1/...`), Google OAuth callbacks, LLM, crawl/ingest workers.
3. **Two storage roles:**
   - **Worker store** — existing `data/` DuckDB/files (raw crawl, ingest, scratch).
   - **Presentation** — stable tables/views or API DTOs the UI consumes; analytics publishes upserts. UI app state (nav, enablement, local notes) lives in Phone Preview persistence (IndexedDB ± sync), not in Python secrets.
4. **UI never** calls Yahoo/Gmail/LLM directly; it starts jobs and reads presentation endpoints.
5. **Secrets** (Google OAuth, OpenAI, Ollama URL) stay on the analytics host only.
6. **HTMX/Jinja** — **removed** in Sprint 35. Thin OAuth HTML at `/modules/gmail/oauth/*` only; no product dashboard.
7. **Daemons** — clear entrypoints (`asx-scanner`, `gmail-ingest`, …) with status via API; threads OK inside a worker.
8. **Quarantine** — Calendar + lite modules under `src/crawley/_quarantine/` (not in registry).

## Consequences

- **Positive:** Correct separation of concerns; Phone Preview UX; analytics can run headlessly; OpenAPI becomes the team contract.
- **Negative:** Two runtimes to operate (Node UI + Python analytics); OAuth “Connect Google” is a cross-app handoff.
- **Neutral:** Repo name stays `a-crawley`; docs call the Python side “Crawley analytics.” Dual HTMX surface ended (Sprint 35).

## Non-goals (this ADR)

- Rebuilding ASX/Gmail logic in TypeScript
- Putting API keys in the Vite app
- Iframe-wrapping HTMX as the “migration”
- Live brokerage / multi-user SaaS
