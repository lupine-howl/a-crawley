# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley  
**Status:** Sprints 1–5 closed; next delivery Sprint 6 (Co-parenting + DIY)  
**Host (Now):** WSL2 / Linux personal machine; **localhost by default**; opt-in LAN bind (`0.0.0.0`) via Settings / `CRAWLEY_HOST` (**restart required**)  
**Active sprint:** [`docs/sprints/current.md`](sprints/current.md) (Sprint 6 ready)  
**Prior sprints:** [`archive/`](sprints/archive/) · [1–5 retro](sprints/archive/sprints-1-5-retrospective.md)  

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

**Shape:** shared core + modules behind a stable contract (read paths first; write-back **designed** with dry-run only — ADR-006).  
**Shipped:** Investment, Gmail, Calendar, Fitness, **Work**; themable shell; Settings (LLM, prompts, **LAN**); Markdown; home At a glance for live modules.  
**UX:** [`docs/ux.md`](ux.md) Sprint 2 design contract.  
**Not in PoC yet:** public hosting, multi-user auth, local LLM ops, native desktop shell, automated trading, **live** write-back mutations.  

## Sprint delivery maps

### Sprint 1 (closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S1.1** Project skeleton & local run | `uv`, `python -m crawley`, FastAPI/Uvicorn localhost, `.env.example`, gitignored `data/` / secrets paths |
| **S1.2** Dashboard, contract, registry & stubs | Shell nav + panels; module Protocol/ABC; explicit registry; Coming soon for non-lite modules (incl. Calendar, Fitness) |
| **S1.3** OpenAI LLM provider | Provider interface + OpenAI via env; LocalLlama placeholder; clear errors if key missing/invalid |
| **S1.4** Investment lite | Threaded bounded fetch → `data/` artifacts + DuckDB rows → LLM synthesis on Investment panel; busy/done/error status |
| **S1.5** Gmail lite (read-only) | Installed-app OAuth (Gmail read-only scope only); bounded inbox scan → panel summary; local tokens |

### Sprint 5 (closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S5.1** Phone-on-LAN | `bind.py` + Settings `network.lan_enabled`; env `CRAWLEY_HOST` wins; restart required; **no auth — trusted LAN only** |
| **S5.2** Work lite | `WorkModule`; `data/work/notes.txt`; LLM prioritize; snapshot |
| **S5.3** Write-back design | [ADR-006](adr/006-write-back-confirm.md); `WriteBackCapability`; dry-run `write_back()` + `data/writeback_audit.jsonl` |

**Home At a glance participants:** Investment, Gmail, Calendar, Fitness, Work.

**Write-back stages (design):** propose draft → show draft/diff (UI Later) → explicit confirm → execute mutation (Later) → local audit log. Today only propose + dry-run audit.

### Sprint 3–4 (bundled, closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S3.1** Shared Google OAuth | `google_oauth.py`; Gmail + Calendar readonly scopes; `google_token.json` (+ legacy `gmail_token.json`); reconsent when Calendar missing |
| **S3.2** Calendar live | `CalendarModule`; Calendar API → `data/calendar/` + DuckDB `calendar_events` → LLM → snapshot |
| **S3.3** Harden Gmail | Shared creds; Priorities/Follow-ups prompts; auth/quota/empty handling |
| **S4.1** Investment depth | Query cache TTL under `data/investment/cache/`; richer Markdown advice; error taxonomy |
| **S4.2** Fitness lite | Goal form + last goal file; non-clinical disclaimer; snapshot |
| **S4.3** Home glance | Snapshots for `investment`, `gmail`, `calendar`, `fitness` |

### Sprint 2 (closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S2.1–S2.4** | Themes, LLM settings/test, Markdown, home glance foundation |

## Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.12+ | Hard requirement for core, modules, crawl, analysis, LLM calls |
| Packaging / run | `uv` | `uv run python -m crawley` (or equivalent entrypoint) |
| HTTP / UI | FastAPI + Jinja2 + HTMX | Server-rendered local browser UI; optional native wrapper Later |
| UI styling | Custom CSS variables + `data-theme` | Four themes (`paper`/`slate`/`ink`/`moss`); no Node/Tailwind build |
| Operator settings | `data/secrets/settings.json` | Theme + LLM + prompts + `network.lan_enabled`; gitignored |
| Bind | `127.0.0.1` default; LAN `0.0.0.0` | Settings toggle and/or `CRAWLEY_HOST`; **restart required**; trusted LAN only (no auth) |
| Theme persistence | Cookie `crawley_theme` + settings file | Cookie wins for immediate apply / first paint |
| LLM config precedence | Settings key overrides `.env` when set | Blank Settings key keeps `OPENAI_API_KEY`; hot-reload per request |
| Markdown | `markdown-it-py` + `bleach` | Safe subset for summaries / home glance |
| Snapshots | `data/snapshots.json` | Last successful live-module summaries for home |
| Process | Single process | Uvicorn hosts the app; I/O concurrency via threads |
| Crawl / fetch | `ThreadPoolExecutor` (or equivalent) | Multi-thread for I/O-bound work; no separate worker service |
| Analytical store | DuckDB | Local file DB under `data/`; sorting, joins, ML feature pulls |
| Raw / cache | Filesystem under `data/` | Crawl dumps, mail/calendar/work notes, investment query cache |
| Large batches | Parquet via DuckDB / Polars | When tabular volume grows (optional) |
| Dataframe / ML | Polars (preferred) / pandas, numpy, scikit-learn as needed | Keep heavy models behind module/provider boundaries |
| LLM | Provider interface | `OpenAI` for Now; `LocalLlama` placeholder only |
| Google | OAuth installed-app | Gmail + Calendar **read-only**; write paths dry-run only (ADR-006) |
| Secrets | Local files | `.env` for API keys; Google tokens under gitignored local config/data |
| Write-back audit | `data/writeback_audit.jsonl` | Dry-run intents only until a live write sprint |

## Boundaries

| Component | Owns | Does not own |
|-----------|------|--------------|
| **Shell** | App lifecycle, HTTP routes, dashboard chrome, job/status UX, wiring modules ↔ LLM ↔ data | Domain logic, provider SDKs called ad hoc from templates |
| **Module contract** | Lifecycle, config/credential hooks, inputs/outputs, write-back capability + dry-run | Live mutation APIs until a later sprint |
| **Modules** (in-repo packages) | Domain fetch, normalize, analyze, panel content | Global auth UI, choosing DuckDB schema for unrelated modules |
| **LLM provider** | Chat/completions (and later local model) behind one interface | Source fetching, persistence format |
| **Data plane** | Paths, DuckDB access helpers, cache conventions | Product copy, module-specific ranking rules |
| **Secrets** | Load keys/tokens from local files; never commit | Cloud secret managers (out of scope) |
| **Bind / LAN** | Resolve host from env or Settings; warn on LAN | Network authentication (none — trusted LAN only) |

### Module loading (Sprint 1)

- In-repo Python packages  
- Explicit **registry** in the core (list/dict of module implementations)  
- Entry-point / plugin discovery deferred until multiple external packages justify it  
- **Top-tier nav (all registered):** Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative  
- **Live:** Investment, Gmail, Calendar, Fitness, Work  
- **Coming soon stubs:** Co-parenting, DIY, Finance/Taxes, Coding/Creative  

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

1. **Start & open dashboard**  
   Operator runs the entrypoint → single process listens on localhost → browser shows module nav; Investment, Gmail, Calendar, and Fitness are live; other top-tier entries show Coming soon.

2. **Investment**  
   User triggers a **bounded** search → optional query cache → threaded fetch → artifacts + DuckDB → LLM summary → panel + home snapshot.

3. **Google read-only (Gmail + Calendar)**  
   Shared OAuth (both readonly scopes) → tokens local → bounded inbox or upcoming-events skim → Markdown summary on panel + snapshot. Reconnect if Calendar scope missing. No write-back.

4. **Fitness lite**  
   Goal/context form → LLM introductory plan (disclaimer) → snapshot. No wearables.

5. **Work lite**  
   Local notes → Save and/or Prioritize → LLM Markdown → snapshot.

6. **Write-back dry-run**  
   Operator triggers dry-run on a capable module → draft recorded in local audit log → **no** remote mutation.

7. **LAN enable**  
   Settings toggle (or `CRAWLEY_HOST`) → restart → bind `0.0.0.0` with startup warning; trusted LAN only.

8. **Stub module click**  
   User opens DIY (or other stub) → Coming soon panel.

9. **Swap LLM (Later)**  
   Configure `LocalLlama` behind the same provider interface.  

## Decisions (ADR log)

Use `docs/adr/` for full write-ups when a choice has lasting impact. Summarize here:

| ID | Decision | Date | Status |
|----|----------|------|--------|
| [ADR-001](adr/001-fastapi-htmx.md) | FastAPI + Jinja2/HTMX for local UI | 2026-07-15 | Accepted |
| [ADR-002](adr/002-duckdb-filesystem.md) | DuckDB + filesystem (+ Parquet) data plane | 2026-07-15 | Accepted |
| [ADR-003](adr/003-single-process-threads.md) | Single process; threads for crawl I/O | 2026-07-15 | Accepted |
| [ADR-004](adr/004-module-contract-registry.md) | Module Protocol + explicit in-repo registry | 2026-07-15 | Accepted |
| [ADR-005](adr/005-llm-provider-interface.md) | LLM provider interface; OpenAI first | 2026-07-15 | Accepted |
| [ADR-006](adr/006-write-back-confirm.md) | Write-back: confirm, draft-first, dry-run only for now | 2026-07-15 | Accepted |

## Risks & open questions

| Item | Notes |
|------|-------|
| **Google OAuth on WSL** | Happy path documented in README; residual risk for Windows browser → WSL port forwarding. Manual verify recommended; no live E2E test. |
| **OpenAI cost / rate limits** | Bound fetches and prompt size (B3/B4/B5); no silent unbounded crawl→LLM loops. Sprint 2 settings (B8) must not remove bounds. |
| **DuckDB + threads** | Write lock in data helpers; keep ownership rules clear as modules grow. |
| **Nav density** | Nine top-tier stubs may feel crowded; shortening labels is OK without dropping registry entries. |
| **Calendar / shared Google auth** | Shared readonly Gmail+Calendar OAuth shipped; watch WSL redirect / reconsent paths. |
| **Theme persistence** | Cookie `crawley_theme` + `settings.json` (documented). |
| **LLM settings vs `.env`** | Settings API key overrides env when non-empty; blank Keep/env fallback; hot-reload per request. |
| **HTMX UX ceiling** | Fine for Now; SPA migration Later if needed — not a second UI stack. |
| **Write-back** | ADR-006 dry-run only; live Gmail/Calendar mutations deferred. |
| **LAN / phone access** | Opt-in bind; trusted LAN only; **no auth gate**; WSL port forwarding may be needed. |
