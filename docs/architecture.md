# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley  
**Status:** Sprint 1 closed 2026-07-15; aligned to Sprint 2  
**Host (Now):** WSL2 / Linux personal machine, localhost by default  
**Active sprint:** [`docs/sprints/current.md`](sprints/current.md) (Sprint 2 — themes & LLM settings)  
**Prior sprint:** [`docs/sprints/archive/sprint-1-local-shell.md`](sprints/archive/sprint-1-local-shell.md)

## Overview

Crawley is a **local-first personal assistant**: one Python process serves a browser UI, runs pluggable life modules, fetches from configured sources, and synthesizes advice via an LLM provider.

```
┌─────────────────────────────────────────────────────────┐
│  Browser (localhost)  ← HTMX / HTML                     │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│  Shell (FastAPI + Jinja2/HTMX)                          │
│  · dashboard navigation  · module panels  · jobs/status │
└──────────────┬─────────────────────────────┬────────────┘
               │                             │
┌──────────────▼──────────────┐   ┌──────────▼────────────┐
│  Module registry + contract  │   │  LLM provider          │
│  investment, gmail, stubs…  │   │  OpenAI → LocalLlama   │
└──────────────┬──────────────┘   └───────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│  Data plane                                               │
│  DuckDB (analytical) · filesystem raw/cache · .env/tokens │
└───────────────────────────────────────────────────────────┘
```

**Shape:** shared core + modules behind a stable contract (read paths first; write-back reserved).  
**Shipped (Sprint 1):** runnable shell + contract/registry + OpenAI provider + **lite Investment** + **lite Gmail**; Calendar and other top-tier domains are **Coming soon** stubs; shell UI uses **custom CSS variables** (no Tailwind CDN).  
**Sprint 2 slice:** themable palette (B7) + LLM settings & connection test (B8) + Markdown summaries (B13) + **home At a glance with persisted last runs (B14)**.  
**UX:** [`docs/ux.md`](ux.md) is the Sprint 2 design contract (S2.1–S2.2); S2.3–S2.4 detailed in the sprint file.  
**Not in PoC yet:** public hosting, multi-user, local LLM ops, native desktop shell, automated trading, write-back, real Calendar fetch.

## Sprint delivery maps

### Sprint 1 (closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S1.1** Project skeleton & local run | `uv`, `python -m crawley`, FastAPI/Uvicorn localhost, `.env.example`, gitignored `data/` / secrets paths |
| **S1.2** Dashboard, contract, registry & stubs | Shell nav + panels; module Protocol/ABC; explicit registry; Coming soon for non-lite modules (incl. Calendar, Fitness) |
| **S1.3** OpenAI LLM provider | Provider interface + OpenAI via env; LocalLlama placeholder; clear errors if key missing/invalid |
| **S1.4** Investment lite | Threaded bounded fetch → `data/` artifacts + DuckDB rows → LLM synthesis on Investment panel; busy/done/error status |
| **S1.5** Gmail lite (read-only) | Installed-app OAuth (Gmail read-only scope only); bounded inbox scan → panel summary; local tokens |

### Sprint 2 (active)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S2.1** Themable UI | Centralize theme tokens; four named themes; Settings Appearance picker; persist choice; document CSS approach |
| **S2.2** LLM settings & test | Settings surface; persist model/provider PoC settings; test-connection action; hot-reload vs restart policy |
| **S2.3** Markdown summaries | Python MD→HTML for panel summaries; sanitize; tokenized `.summary` styles |
| **S2.4** Home At a glance | Persist last successful Investment/Gmail summaries; status chips on `/`; reuse MD renderer |

Implement Sprint 2 stories **in order** (S2.1 → S2.2 → S2.3 → S2.4) unless dependencies already met.

## Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.12+ | Hard requirement for core, modules, crawl, analysis, LLM calls |
| Packaging / run | `uv` | `uv run python -m crawley` (or equivalent entrypoint) |
| HTTP / UI | FastAPI + Jinja2 + HTMX | Server-rendered local browser UI; optional native wrapper Later |
| UI styling | Custom CSS variables + `data-theme` | Four themes (`paper`/`slate`/`ink`/`moss`); no Node/Tailwind build |
| Operator settings | `data/secrets/settings.json` | Theme + LLM provider/model/key; gitignored |
| Theme persistence | Cookie `crawley_theme` + settings file | Cookie wins for immediate apply / first paint |
| LLM config precedence | Settings key overrides `.env` when set | Blank Settings key keeps `OPENAI_API_KEY`; hot-reload per request |
| Markdown | `markdown-it-py` + `bleach` | Safe subset for summaries / home glance |
| Snapshots | `data/snapshots.json` | Last successful Investment/Gmail summaries for home |
| Process | Single process | Uvicorn hosts the app; I/O concurrency via threads |
| Crawl / fetch | `ThreadPoolExecutor` (or equivalent) | Multi-thread for I/O-bound work; no separate worker service in Sprint 1 |
| Analytical store | DuckDB | Local file DB under `data/`; sorting, joins, ML feature pulls |
| Raw / cache | Filesystem under `data/` | Crawl dumps, mail caches, artifacts |
| Large batches | Parquet via DuckDB / Polars | When tabular volume grows (optional in Sprint 1 if DuckDB rows suffice) |
| Dataframe / ML | Polars (preferred) / pandas, numpy, scikit-learn as needed | Keep heavy models behind module/provider boundaries; Sprint 1 may stay light |
| LLM | Provider interface | `OpenAI` for Sprint 1; `LocalLlama` placeholder only |
| Google | OAuth installed-app | **Sprint 1:** Gmail **read-only** only; Calendar real scopes deferred (nav stub). Write scopes later. |
| Secrets | Local files | `.env` for API keys; Google tokens under gitignored local config/data |

## Boundaries

| Component | Owns | Does not own |
|-----------|------|--------------|
| **Shell** | App lifecycle, HTTP routes, dashboard chrome, job/status UX, wiring modules ↔ LLM ↔ data | Domain logic, provider SDKs called ad hoc from templates |
| **Module contract** | Lifecycle, config/credential hooks, inputs/outputs, optional write-back hooks (unused in Sprint 1) | Storage engine details, which LLM vendor is active |
| **Modules** (in-repo packages) | Domain fetch, normalize, analyze, panel content | Global auth UI, choosing DuckDB schema for unrelated modules |
| **LLM provider** | Chat/completions (and later local model) behind one interface | Source fetching, persistence format |
| **Data plane** | Paths, DuckDB access helpers, cache conventions | Product copy, module-specific ranking rules |
| **Secrets** | Load keys/tokens from local files; never commit | Cloud secret managers (out of scope) |

### Module loading (Sprint 1)

- In-repo Python packages  
- Explicit **registry** in the core (list/dict of module implementations)  
- Entry-point / plugin discovery deferred until multiple external packages justify it  
- **Top-tier nav (all registered):** Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative  
- **Live in Sprint 1:** Investment, Gmail  
- **Coming soon stubs:** Calendar, Fitness, and the rest of the top-tier list  

### Proposed package layout (indicative)

```
src/crawley/
  __main__.py          # python -m crawley
  app.py               # FastAPI app factory
  shell/               # routes, templates, static (S1.2+)
  modules/             # contract, registry, domains (S1.2+)
  llm/                 # provider interface (S1.3+)
  data/                # DuckDB helpers (S1.4+)
data/                  # runtime, gitignored
docs/
```

Sprint 1 uses a `src/` layout via `uv`/`hatchling`. Boundaries above stay; subpackages land with later stories.

## Key flows

1. **Start & open dashboard (S1.1–S1.2)**  
   Operator runs the entrypoint → single process listens on localhost → browser shows module nav; Investment and Gmail panels are live paths; other top-tier entries show Coming soon.

2. **Investment lite (S1.4)**  
   User triggers a **bounded** search/scrape → threaded fetch → raw artifacts on disk → structured rows in DuckDB → LLM provider synthesizes short summary/advice → Investment panel updates (HTMX partial or full render) with busy/done/error status.

3. **Gmail lite read-only (S1.5)**  
   First-time OAuth in browser (Gmail read-only scope) → tokens stored locally → **bounded** inbox scan → summary via LLM (or structured skim) on Gmail panel. Clear auth/API errors. No write-back. No Calendar API in this flow.

4. **Stub module click (S1.2)**  
   User opens Calendar (or any non-lite module) → Coming soon panel; no crash, no fake data.

5. **Add a domain module (ongoing)**  
   Implement contract → register → nav/panel → reuse data + LLM helpers. Core shell should not need a rewrite.

6. **Swap LLM (Later — not Sprint 1)**  
   Configure `LocalLlama` behind the same provider interface; modules keep calling the interface, not OpenAI APIs directly.

## Decisions (ADR log)

Use `docs/adr/` for full write-ups when a choice has lasting impact. Summarize here:

| ID | Decision | Date | Status |
|----|----------|------|--------|
| [ADR-001](adr/001-fastapi-htmx.md) | FastAPI + Jinja2/HTMX for local UI | 2026-07-15 | Accepted |
| [ADR-002](adr/002-duckdb-filesystem.md) | DuckDB + filesystem (+ Parquet) data plane | 2026-07-15 | Accepted |
| [ADR-003](adr/003-single-process-threads.md) | Single process; threads for crawl I/O | 2026-07-15 | Accepted |
| [ADR-004](adr/004-module-contract-registry.md) | Module Protocol + explicit in-repo registry | 2026-07-15 | Accepted |
| [ADR-005](adr/005-llm-provider-interface.md) | LLM provider interface; OpenAI first | 2026-07-15 | Accepted |

## Risks & open questions

| Item | Notes |
|------|-------|
| **Google OAuth on WSL** | Happy path documented in README; residual risk for Windows browser → WSL port forwarding. Manual verify recommended; no live E2E test. |
| **OpenAI cost / rate limits** | Bound fetches and prompt size (B3/B4/B5); no silent unbounded crawl→LLM loops. Sprint 2 settings (B8) must not remove bounds. |
| **DuckDB + threads** | Write lock in data helpers; keep ownership rules clear as modules grow. |
| **Nav density** | Nine top-tier stubs may feel crowded; shortening labels is OK without dropping registry entries. |
| **Calendar / shared Google auth** | Real Calendar read may later share OAuth with Gmail; do not request Calendar scopes until B6/B10 commit them. |
| **Theme persistence** | Cookie `crawley_theme` + `settings.json` (documented). |
| **LLM settings vs `.env`** | Settings API key overrides env when non-empty; blank Keep/env fallback; hot-reload per request. |
| **HTMX UX ceiling** | Fine for Now; SPA migration Later if needed — not a second UI stack. |
| **Write-back** | Contract reserves hooks; no write scopes or mutations until a later sprint commits them. |
| **LAN / phone access** | Out of Now; if enabled later, bind/auth defaults must stay intrusion-minded. |
