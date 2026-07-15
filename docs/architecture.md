# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley  
**Status:** Interview 1 confirmed (2026-07-15)  

**Host (Now):** WSL2 / Linux personal machine, localhost by default

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
│  investment, gmail, …       │   │  OpenAI → LocalLlama   │
└──────────────┬──────────────┘   └───────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│  Data plane                                               │
│  DuckDB (analytical) · filesystem raw/cache · .env/tokens │
└───────────────────────────────────────────────────────────┘
```

**Shape:** shared core + modules behind a stable contract (read paths first; write-back reserved).  
**Not in PoC:** public hosting, multi-user, local LLM ops, native desktop shell, automated trading.

## Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.12+ | Hard requirement for core, modules, crawl, analysis, LLM calls |
| Packaging / run | `uv` | `uv run python -m crawley` (or equivalent entrypoint) |
| HTTP / UI | FastAPI + Jinja2 + HTMX | Server-rendered local browser UI; optional native wrapper Later |
| Process | Single process | Uvicorn hosts the app; I/O concurrency via threads |
| Crawl / fetch | `ThreadPoolExecutor` (or equivalent) | Multi-thread for I/O-bound work; no separate worker service in PoC |
| Analytical store | DuckDB | Local file DB under `data/`; sorting, joins, ML feature pulls |
| Raw / cache | Filesystem under `data/` | Crawl dumps, mail caches, artifacts |
| Large batches | Parquet via DuckDB / Polars | When tabular volume grows |
| Dataframe / ML | Polars (preferred) / pandas, numpy, scikit-learn as needed | Keep heavy models behind module/provider boundaries |
| LLM | Provider interface | `OpenAI` implementation for PoC; `LocalLlama` later |
| Google | OAuth installed-app | Read-only Gmail + Calendar scopes for PoC; write scopes later |
| Secrets | Local files | `.env` for API keys; tokens under gitignored local config/data |

## Boundaries

| Component | Owns | Does not own |
|-----------|------|--------------|
| **Shell** | App lifecycle, HTTP routes, dashboard chrome, job/status UX, wiring modules ↔ LLM ↔ data | Domain logic, provider SDKs called ad hoc from templates |
| **Module contract** | Lifecycle, config/credential hooks, inputs/outputs, optional write-back hooks (unused in PoC) | Storage engine details, which LLM vendor is active |
| **Modules** (in-repo packages) | Domain fetch, normalize, analyze, panel content | Global auth UI, choosing DuckDB schema for unrelated modules |
| **LLM provider** | Chat/completions (and later local model) behind one interface | Source fetching, persistence format |
| **Data plane** | Paths, DuckDB access helpers, cache conventions | Product copy, module-specific ranking rules |
| **Secrets** | Load keys/tokens from local files; never commit | Cloud secret managers (out of scope) |

### Module loading (PoC)

- In-repo Python packages  
- Explicit **registry** in the core (list/dict of module implementations)  
- Entry-point / plugin discovery deferred until multiple external packages justify it  

### Proposed package layout (indicative)

```
crawley/
  __main__.py          # python -m crawley
  app.py               # FastAPI app factory
  shell/               # routes, templates, static
  modules/
    contract.py        # Protocol / ABC
    registry.py
    investment/
    gmail_calendar/    # or split later
    fitness/           # stub
    …                  # placeholders
  llm/
    base.py
    openai_provider.py
    local_llama.py     # stub / Later
  data/
    duck.py
    paths.py
data/                  # runtime, gitignored
docs/
```

Exact names may shift in Sprint 1; boundaries above stay.

## Key flows

1. **Start & open dashboard**  
   Operator runs the entrypoint → single process listens on localhost → browser shows module nav and panels (stubs allowed where out of sprint).

2. **Investment PoC**  
   User triggers search/crawl on the investment panel → threaded fetch → raw artifacts on disk → structured rows in DuckDB → LLM provider synthesizes short summary/advice → HTML panel updates (HTMX partial or full render).

3. **Gmail / Calendar PoC (read-only)**  
   First-time OAuth in browser → tokens stored locally → module reads mail and/or calendar → summary via LLM (or structured skim) → panel. No write-back in PoC.

4. **Add a domain module**  
   Implement contract → register in registry → add nav entry / panel template → reuse data + LLM helpers. Core shell should not need a rewrite.

5. **Swap LLM (Later)**  
   Configure `LocalLlama` (or equivalent) behind the same provider interface; modules keep calling the interface, not OpenAI APIs directly.

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
| **Planned Sprint 1 missing** | `BACKLOG.md` / Planned Sprint 1 still TBD (S0.2). Architecture targets Now themes; story-level alignment pending PO Interview 2. |
| **DuckDB ops familiarity** | Chosen for analytics; if ops pain dominates early, thin repository layer eases a SQLite fallback for metadata-only paths. |
| **Google OAuth on WSL** | Browser redirect/localhost callback must be validated on the stakeholder’s setup; document the happy path in Sprint 1. |
| **OpenAI cost / rate limits** | PoC should cache fetches and bound prompt size; no silent unbounded crawl→LLM loops. |
| **HTMX UX ceiling** | Fine for PoC dashboards; interactive density limits may push a SPA later—not a dual UI stack for the same PoC. |
| **Thread safety** | DuckDB / shared state access from worker threads needs clear ownership (queue to main, or documented connection rules). |
| **Write-back** | Contract reserves hooks; do not request write scopes or implement mutations until a later sprint explicitly commits them. |
| **LAN / phone access** | Out of Now; if enabled later, bind/auth defaults must stay intrusion-minded (not open-to-LAN by default). |
