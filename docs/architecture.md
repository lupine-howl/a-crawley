# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley  
**Status:** Sprints 1–10 closed; **Sprint 11** Sender Inbox PoC (+ ASX desk UX) ready
**Host (Now):** WSL2 / Linux personal machine; **localhost by default**; opt-in LAN bind (`0.0.0.0`) via Settings / `CRAWLEY_HOST` (**restart required**)  
**Active sprint:** [`docs/sprints/current.md`](sprints/current.md) (Sprint 11 — Sender Inbox)  
**Shelved plans:** [`sprints/shelved/`](sprints/shelved/README.md)  
**Prior sprints:** [`archive/`](sprints/archive/)  

## Overview

Crawley is a **local-first personal assistant**: one Python process serves a browser UI, runs pluggable life modules, fetches from configured sources, and synthesizes advice via an LLM provider.

```
┌─────────────────────────────────────────────────────────┐
│  Browser (localhost)  ← HTMX / HTML                     │
└────────────────────────────┬────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────┐
│  Shell (FastAPI + Jinja2/HTMX)                          │
│  · dashboard / Day brief  · modules  · jobs  · Settings │
└──────────────┬─────────────────────────────┬────────────┘
               │                             │
┌──────────────▼──────────────┐   ┌──────────▼────────────┐
│  Module registry + contract  │   │  LLM provider          │
│  all top-tier modules live  │   │  OpenAI · LocalLlama   │
└──────────────┬──────────────┘   └───────────────────────┘
               │
┌──────────────▼──────────────────────────────────────────┐
│  Data plane                                               │
│  DuckDB · filesystem · snapshots · standing notes · audit │
└───────────────────────────────────────────────────────────┘
```

**Shape:** shared core + modules behind a stable contract.  
**Shipped:** Investment, Gmail, Calendar (read + confirm-first insert), Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative; Day brief; shared context seed; LocalLlama (Ollama HTTP); themable shell.  
**UX:** [`docs/ux.md`](ux.md) Sprint 2 design contract (later modules reuse form/snapshot patterns).  
**Not in PoC:** public hosting, multi-user auth, native desktop shell, automated trading, Gmail send.

## Sprint delivery maps

### Sprints 6–10 (bundled, closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S6** Co-parenting / DIY | `CoParentingModule` (JSON schedule); `DiyModule` (notes lite); snapshots |
| **S7** Finance / Day brief | `FinanceModule`; `day_brief.py` from Calendar+Gmail snapshots; home section |
| **S8** Calendar write-back | Confirm-first insert; `calendar.events` scope; draft UUID store; audit viewer |
| **S9** LocalLlama | [ADR-007](adr/007-local-llm-ollama.md); Ollama HTTP; Settings URL/model/timeout |
| **S10** Coding + shared context | `CodingCreativeModule`; [ADR-008](adr/008-shared-context.md); standing notes |

**Home At a glance participants:** Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative (+ Day brief section).

### Sprint 5 (closed)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S5.1** Phone-on-LAN | `bind.py` + Settings `network.lan_enabled`; trusted LAN only |
| **S5.2** Work lite | `WorkModule`; `data/work/notes.txt` |
| **S5.3** Write-back design | [ADR-006](adr/006-write-back-confirm.md); dry-run hooks |

### Sprint 3–4 / 2 / 1

See archive under [`sprints/archive/`](sprints/archive/) and earlier maps in git history.

## Stack

| Layer | Choice | Notes |
|-------|--------|-------|
| Language | Python 3.12+ | Hard requirement |
| Packaging / run | `uv` | `uv run python -m crawley` |
| HTTP / UI | FastAPI + Jinja2 + HTMX | Server-rendered local browser UI |
| UI styling | Custom CSS variables + `data-theme` | Four themes; no Node build |
| Operator settings | `data/secrets/settings.json` | Theme, LLM (incl. local URL/timeout), prompts, LAN |
| Bind | `127.0.0.1` default; LAN `0.0.0.0` | Restart required; trusted LAN only |
| LLM | Provider interface | OpenAI + **LocalLlama (Ollama HTTP)** |
| Markdown | `markdown-it-py` + `bleach` | Safe subset |
| Snapshots | `data/snapshots.json` | Last successful module summaries + Day brief |
| Shared context | Standing notes + capped snapshots | Opt-in prompt injection; ADR-008 |
| Process | Single process | Threads for I/O |
| Analytical store | DuckDB | Local file under `data/` |
| Google | OAuth installed-app | Gmail/Calendar **readonly** by default; optional `calendar.events` for insert |
| Write-back audit | `data/writeback_audit.jsonl` | Dry-run and live attempts |

## Boundaries

| Component | Owns | Does not own |
|-----------|------|--------------|
| **Shell** | Routes, chrome, Day brief UI, Settings, job UX | Domain ranking rules |
| **Module contract** | Lifecycle, I/O, write-back capability | Vector DB / plugin discovery |
| **Modules** | Domain fetch/notes/analyze/panel | Global auth UX |
| **LLM provider** | Completions behind one interface | Source fetching |
| **Shared context** | Caps + standing notes bundle | Secret storage |
| **Write-back** | Propose/confirm/audit; Calendar insert | Gmail send (deferred) |

### Module loading

- Explicit in-repo registry  
- **All top-tier modules live:** Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative  

## Key flows

1. **Start & open dashboard** — localhost; Day brief + glances for all live modules.  
2. **Notes lite modules** — Save notes → Run → LLM Markdown → snapshot.  
3. **Co-parenting** — Schedule lines → bounded window → Markdown.  
4. **Google read** — Shared readonly OAuth → Gmail/Calendar skim.  
5. **Calendar write** — Propose draft (UUID) → Confirm → `events.insert` → audit (or Cancel = no write). Reconnect with `?calendar_write=1` for events scope.  
6. **Day brief** — Compose from Calendar+Gmail snapshots; optional LLM regenerate; optional shared context.  
7. **Local LLM** — Settings LocalLlama → base URL/model/timeout → Test → modules use provider.  
8. **Shared context** — Standing notes + capped snapshots; opt-in into prompts.  
9. **LAN enable** — Settings toggle / `CRAWLEY_HOST`; trusted LAN only.

## Decisions (ADR log)

| ID | Decision | Date | Status |
|----|----------|------|--------|
| [ADR-001](adr/001-fastapi-htmx.md) | FastAPI + Jinja2/HTMX for local UI | 2026-07-15 | Accepted |
| [ADR-002](adr/002-duckdb-filesystem.md) | DuckDB + filesystem (+ Parquet) data plane | 2026-07-15 | Accepted |
| [ADR-003](adr/003-single-process-threads.md) | Single process; threads for crawl I/O | 2026-07-15 | Accepted |
| [ADR-004](adr/004-module-contract-registry.md) | Module Protocol + explicit in-repo registry | 2026-07-15 | Accepted |
| [ADR-005](adr/005-llm-provider-interface.md) | LLM provider interface; OpenAI first | 2026-07-15 | Accepted |
| [ADR-006](adr/006-write-back-confirm.md) | Write-back: confirm, draft-first | 2026-07-15 | Accepted |
| [ADR-007](adr/007-local-llm-ollama.md) | LocalLlama via Ollama HTTP | 2026-07-15 | Accepted |
| [ADR-008](adr/008-shared-context.md) | Shared context seed (caps, opt-in) | 2026-07-15 | Accepted |

## Risks & open questions

| Item | Notes |
|------|-------|
| **Google OAuth on WSL** | Residual redirect risk; write scope needs explicit reconnect. |
| **OpenAI / local cost & latency** | Bounds preserved; local timeouts fail loudly. |
| **Calendar write** | Confirm-first only; primary calendar; no recurring-series editor. |
| **Day brief clutter** | One composition; truncate long snapshot bodies in CSS. |
| **Shared context** | Caps may drop detail; opt-in default keeps prompts cheap. |
| **LAN / phone access** | Trusted LAN only; no auth gate. |
