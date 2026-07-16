# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley  
**Status:** Sprints 1–17 closed (15–17 = inbox/ASX scale + email bridge)  
**Host (Now):** WSL2 / Linux personal machine; **localhost by default**; opt-in LAN bind (`0.0.0.0`) via Settings / `CRAWLEY_HOST` (**restart required**)  
**Latest sprint:** [`docs/sprints/current.md`](sprints/current.md) (Sprints 15–17 done)  
**Sprint 14 (closed):** [`sprints/archive/sprint-14-asx-paper-portfolio.md`](sprints/archive/sprint-14-asx-paper-portfolio.md)  
**Next planned:** pivot Sprints 18–20 — [`sprints/planned/README.md`](sprints/planned/README.md)  
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
**Sprint 11:** Settings → **Update** runs local `git fetch` + **ff-only** merge of the current branch upstream (`git_update.py`). Allowed on localhost and trusted LAN/Tailscale (UI warns; no login gate). Relies on `CRAWLEY_RELOAD=1` (Uvicorn watches `src/crawley/`) for hot reload after watched files change. No scheduled auto-pull; no conflict UI. LAN bind helpers recognize Tailscale CGNAT / MagicDNS for personal http OAuth and startup “try also” URLs.  
**Sprint 12:** Gmail panel is **Sender Inbox** — background one-mail ingest, LLM categorization, sender-grouped UI, profiles, local todos, ~20 PoC cap (`sender_inbox/`). Classic inbox skim remains under a disclosure.  
**Sprint 13:** Investment panel is **ASX desk** — curated universe (~193), one-company-at-a-time scanner (Yahoo chart + Google News RSS), LLM profiles, sources registry (`asx_desk/`).  
**Sprint 14:** ASX recommendations + paper portfolio + simulation settings; also shipped bounded snapshot history + shared-context pins (B35–B36) and Fitness activity import lite (B37).  
**Sprints 15–17:** Desk scale (Settings, hard ceiling 200); Sender Inbox search/prune; ASX active-set scale + events skim; Email × ASX bridge (`bridge/matcher.py`).

## Sprint delivery maps

### Sprints 15–17 (closed) — Scale + bridge

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S15.1 / B79** | `ScaleSettings` · `sync_ingest_cap` · `prune_messages` (keep newest N) · Settings `#desk-scale` |
| **S15.2 / B80** | `group_senders(query, category, todo)` · Gmail filter form |
| **S16.1 / B81** | `sync_active_cap` · Desk “Apply size” · same one-at-a-time scanner |
| **S16.2 / B82** | `fetch_events_for_ticker` · `events.json` · `/modules/investment/events` |
| **S17.1 / B83** | `bridge/matcher.py` · allowlist = active set ∪ paper · whole-word match · `/modules/investment/bridge` |

**Scale bounds:** hard ceiling **200** for inbox ingest and ASX active set. Not a full-mailbox or market-wide product.

**Bridge matching:** allowlist only (active PoC set ∪ paper holdings); `\bTICKER\b` word boundaries; company-name match if name ≥ 5 chars; short English blocklist; max 200 messages / 60 hits. No auto-trade / auto-send.

### Sprint 14 (closed) — Paper desk + history + fitness import

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S14.1 / B75** | `asx_desk/recommendations.py` · `llm_tasks.generate_recommendations` · `/modules/investment/recommendations` |
| **S14.2 / B76** | `asx_desk/portfolio.py` · ledger `data/investment/asx/portfolio.json` · MTM from scan prices · `/modules/investment/portfolio` |
| **S14.3 / B77** | `SimulationSettings` in `settings.json` · fees in paper math · Settings `#paper-portfolio` |
| **S15.1 / B35** | `snapshot_history.json` · max 20/module · Settings `#snapshot-history` search |
| **S15.2 / B36** | Pins in `shared_context_meta.json` · injected into `build_shared_context` · ADR-008 |
| **S16.1 / B37** | `fitness_import.py` · `data/fitness/activity_import.txt` · optional Fitness prompt slice |

**Simulation boundary:** paper ledger never calls brokerage order APIs. Settings (cash, fees, AUD, cosmetic broker label) affect simulation only.

**History vs standing notes:** `snapshots.json` = last success per module; `snapshot_history.json` = bounded ring; standing notes = operator seed; pins = opt-in history excerpts in the shared-context bundle (hard caps).

### Sprint 13 (closed) — ASX desk

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S13.1 / B71** | `asx_desk/assets/universe.json` · PoC set in `scan_state.json` |
| **S13.2 / B72** | `asx_desk/worker.py` · one ticker at a time · pause/resume · rate limit |
| **S13.3 / B73** | Profiles JSON · `/modules/investment/companies/{ticker}` · snapshot metrics |
| **S13.4 / B74** | `sources_config.json` · scan/profile/sentiment prompts · enable flags |

### ASX metric / source notes

| Metric | Source | Gap honesty |
|--------|--------|-------------|
| Last price / % move / volume | Yahoo Finance chart `TICKER.AX` (scan mode) | May be unavailable; UI shows — |
| Headlines / sentiment input | Google News RSS (scan mode) | Not official ASX; tone via LLM |
| Exchange announcements | Curated placeholder (disabled) | No auto-scrape; enable when TOS-safe feed exists |
| PE / yield / quality | Not fetched in PoC | Documented gap — never invent numbers |

**Modes:** **scan** = polite automated fetches for the PoC set; **curated** = operator/enable-gated sources without hostile scraping.

### Sprint 12 (closed) — Sender Inbox

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S12.1 / B65** | UX contract `docs/ux/sender-inbox-asx.md` accepted for implement |
| **S12.2 / B66** | `sender_inbox/worker.py` · one-at-a-time Gmail fetch + LLM metrics |
| **S12.3 / B67** | `/modules/gmail` sender list · `/modules/gmail/senders/{id}` |
| **S12.4 / B68** | Profiles JSON under `data/gmail/sender_inbox/` |
| **S12.5 / B69** | Todos JSON + HTMX toggle; no send/calendar |
| **S12.6 / B70** | Cap default 20 · `CRAWLEY_SENDER_INBOX_CAP` · Reset PoC data |

### Sender Inbox categorization schema

Persisted under `data/gmail/sender_inbox/` (`messages.json`, `profiles.json`, `todos.json`, `ingest_state.json`).

Per-message **metrics** (LLM JSON, normalized in `sender_inbox/schema.py`):

| Field | Type | Notes |
|-------|------|-------|
| `urgency` | `low\|medium\|high\|critical` | Drives sort boost + `urgent` signal |
| `requires_reply` | bool | Adds `reply` signal |
| `action_needed` | bool | Adds `action` signal |
| `vip` | bool | Adds `vip` signal |
| `category` | `personal\|work\|billing\|newsletter\|other` | Coarse class |
| `signals` | string[] | Max 5; UI shows ≤3 quiet chips |
| `brief` | string | One-line summary |

**Sort:** newest activity first, with boost for high/critical urgency and `requires_reply`.  
**Cap:** default 20; raise later via env `CRAWLEY_SENDER_INBOX_CAP` (restart).

### Sprint 11 (closed) — Settings Update

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S11.1 / B78** | `git_update.py` · `POST /settings/update/pull` · Settings `#update` · ff-only · LAN/Tailscale allowed + warn · `CRAWLEY_RELOAD` |

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
| Snapshots | `data/snapshots.json` + `snapshot_history.json` | Last success + bounded history (≤20/module) |
| Shared context | Standing notes + capped snapshots + optional pins | Opt-in prompt injection; ADR-008 |
| Paper portfolio | `data/investment/asx/portfolio.json` | Simulation ledger; fees from Settings |
| Fitness import | `data/fitness/activity_import.txt` | Bounded text/CSV; optional in Fitness prompt |
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
8. **Shared context** — Standing notes + capped snapshots + optional history pins; opt-in into prompts.  
9. **ASX paper desk** — Refresh recommendations → paper trade → portfolio MTM; simulation settings only.  
10. **Snapshot history** — Browse/search Settings history; pin into shared context (capped).  
11. **Fitness import** — Upload bounded activity file; optional include on Fitness run.  
12. **LAN enable** — Settings toggle / `CRAWLEY_HOST`; trusted LAN only.

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
