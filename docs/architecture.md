# Architecture

Senior architect / developer owns this file. Update when material decisions land.

**Working title:** Crawley (this repo = **analytics**)  
**Status:** Sprints 1–32 closed; **hard pivot** — Migration Sprint **33** (ASX daemon)  
**Migration:** [`migration-phone-preview.md`](migration-phone-preview.md) · [ADR-009](adr/009-phone-preview-analytics.md)  
**Host (analytics):** WSL2 / Linux; localhost default; opt-in LAN via Settings / `CRAWLEY_HOST`  
**Latest sprint:** [`sprints/current.md`](sprints/current.md) (Sprint 33)  
**API contract:** [`api/presentation-v1.md`](api/presentation-v1.md) · [`api/openapi-v1.json`](api/openapi-v1.json)  
**UI consume:** [`build/consuming-published-core.md`](build/consuming-published-core.md) · app [`../crawley-ui/`](../crawley-ui/)  
**Product UI:** `crawley-ui` (published `@phone-preview/core` ≥ 0.6.1)  
**Shelved:** [`sprints/shelved/`](sprints/shelved/README.md)  
**Prior sprints:** [`archive/`](sprints/archive/)  

## Overview

Crawley analytics is a **local-first Python brain**: FastAPI JSON API, daemon workers (ASX, Gmail ingest), DuckDB/filesystem worker store, Google OAuth, LLM. The **product UI** is **`crawley-ui`** (Phone Preview packs), not Jinja/HTMX.

```
┌─────────────────────────────────────────────┐
│  crawley-ui (Phone Preview)                   │
│  packs · IndexedDB (± Turso/Duck UI sync)     │
└──────────────────────┬──────────────────────┘
                       │ HTTP /v1 JSON
┌──────────────────────▼──────────────────────┐
│  Analytics API (this repo)                    │
│  /health · /v1/asx · /v1/jobs · OAuth         │
│  presentation DTOs (crawley.api)              │
└──────────┬─────────────────────┬────────────┘
           │                     │
┌──────────▼──────────┐  ┌───────▼────────────────┐
│  Daemons / workers  │  │  Worker store (Duck/files)│
│  asx · gmail · …    │→ │  publish → API DTOs       │
└─────────────────────┘  └──────────────────────────┘
```

**Shape (pivot):** analytics API + daemons; UI in `crawley-ui`.  
**Product domains (pivot):** ASX desk + Sender Inbox. Calendar + lite modules quarantined.  
**HTMX/Jinja:** **frozen** — bugfixes only; no new product features; delete in Sprint 35.  
**UX (product):** Phone Preview packs; legacy [`ux.md`](ux.md) / [`ux/sender-inbox-asx.md`](ux/sender-inbox-asx.md) inform pack IA until replaced.  

## Sprint delivery maps

### Sprint 31 (closed) — Analytics JSON API (ASX + jobs)

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S31.1 / B91** | Pivot lock; HTMX feature freeze; overview diagram = UI ↔ `/v1` ↔ workers |
| **S31.2 / B92** | `crawley.api.routes` · `GET /health` · `/v1/asx/companies` · scan start/pause/resume/reset · `/v1/jobs/{id}` |
| **S31.3 / B93** | `crawley.api.presentation` DTOs · `docs/api/presentation-v1.md` · `docs/api/openapi-v1.json` (+ runtime `/openapi.json`) |

**Job mapping:** ASX desk scan → stable job id `asx-scan` (wraps `asx_desk.worker` + `progress_view`). OAuth stays on analytics host.

### Sprint 32 (closed) — crawley-ui + asxDeskPack

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S32.1 / B94** | `crawley-ui/` via `create-phone-preview` · `@phone-preview/core` ≥ 0.6.1 · `starterPacks()` · Vite `/api/analytics` → `:8000` |
| **S32.2 / B95** | `crawley-ui/src/packs/asxDeskPack.tsx` · `src/lib/analytics.ts` · companies + scan + job poll + detail |

**Pack rule:** app-private packs only for desks; no education curriculum; no `--with-api` as analytics brain. Persistence = PP IndexedDB defaults.

**HTMX-era notes (closed):** Sprints 11–30 — Settings Update, Sender Inbox, ASX desk depth, paper, bridge, send/alerts/playbooks, OAuth/digests/notebook/VIP, clusters, labels/holdings/searches/attachments/citations. See maps below and [`archive/`](sprints/archive/).

### Sprint 25 (closed) — ASX news theme clustering

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S25.1 / B47** | `asx_desk/clusters.py` · reuse scan headlines · LLM + heuristic · `/modules/investment/clusters` · `news_clusters.json` |

**Caps:** ≤80 headlines, ≤4/ticker, ≤8 themes, ≤8 sources/theme. Muted domains excluded. Not trade signals.

### Sprints 26–30 (closed) — Labels, holdings, searches, attachments, citations

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S26.1 / B48** | `gmail.modify` · `sender_inbox/labels.py` · propose/confirm/cancel · ADR-006 |
| **S27.1 / B49** | `asx_desk/holdings.py` · `/modules/investment/holdings` · capped prompt slice |
| **S28.1 / B50** | `sender_inbox/saved_searches.py` · bounded `messages.list(q=…)` |
| **S29.1 / B52** | `sender_inbox/attachments.py` · allowlist extract · digest slice |
| **S30.1 / B53** | `asx_desk/citations.py` · `## Citations` on profiles · muted domains |

**Citation quality rubric:** `trusted` / `ok` / `low` / `unknown`. Muted domains excluded from scan headlines and citation prompts.

### Sprints 21–24 (closed) — OAuth, digests, notebook, VIP

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S21.1 / B89** | Settings `#google` + Connect panels show `redirect_uri(_base_url)`; README Tailscale/Host notes |
| **S21.2 / B90** | `should_force_consent` · conditional `prompt=consent` · Testing vs Production docs |
| **S22.1 / B44** | `sender_inbox/digests.py` · `fetch_thread_messages` · artifacts under `thread_artifacts/` |
| **S23.1 / B45** | `asx_desk/notebook.py` · company panel edit · capped slice in profile/recommend |
| **S24.1 / B46** | `sender_inbox/rules.py` · VIP/muted CRUD · `group_senders` + `categorize_message` |

**OAuth consent:** `access_type=offline` always; force consent only when refresh missing or new scopes (Calendar write / Gmail send).

**Thread digests:** max 12 messages / hard-capped body chars; no full-mailbox sync; manual next action only.

**Notebook:** `data/investment/asx/notebooks/{TICKER}.json`; empty → no invented thesis; advice remains non-order.

**VIP rules:** local JSON only; not Google filter sync; VIP boosts sort; muted soft-deprioritizes.

### Sprints 18–20 (closed) — Send, alerts, playbooks

| Story | Architecture touchpoints |
|-------|--------------------------|
| **S18.1 / B84** | `gmail.send` opt-in OAuth · `pending_send_drafts.json` · propose/confirm/cancel · ADR-006 · audit |
| **S19.1 / B85** | `asx_desk/alerts.py` · rules + triggered JSON · evaluate after scan · home chip |
| **S19.2 / B86** | `asx_desk/feedback.py` · accept/dismiss/snooze · capped prompt slice on regenerate |
| **S20.1 / B87** | `playbooks.py` · `data/playbooks.json` · Run from desks / Settings |
| **S20.2 / B88** | Empty states · alert copy · compose/todos clarity · dual-desk maps (this section) |

**Gmail send boundary:** never requested with Calendar write casually; separate `?gmail_send=1` reconsent. Cancel = no `messages.send`.

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
| HTTP / product API | FastAPI JSON `/v1` | Presentation DTOs for `crawley-ui` |
| HTTP / legacy UI | Jinja2 + HTMX | **Frozen** — bugfixes only until Sprint 35 deletion |
| UI styling (legacy) | Custom CSS variables + `data-theme` | Four themes; no Node build in this repo |
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
| Google | OAuth installed-app | Gmail/Calendar **readonly** by default; optional `calendar.events` / `gmail.send`; softer consent (B90) |
| Write-back audit | `data/writeback_audit.jsonl` | Dry-run and live attempts |
| Thread digests | `data/gmail/sender_inbox/thread_digests.json` | Bounded per-thread LLM digests |
| Sender rules | `data/gmail/sender_inbox/sender_rules.json` | VIP / muted / tags |
| ASX notebooks | `data/investment/asx/notebooks/` | Per-ticker thesis + notes |

## Boundaries

| Component | Owns | Does not own |
|-----------|------|--------------|
| **Analytics API** (`crawley.api`) | `/health`, `/v1` presentation DTOs, job control, OpenAPI | Pack UI / IndexedDB |
| **Shell (legacy)** | HTMX routes, chrome, Settings HTML (frozen) | New product features |
| **Module contract** | Lifecycle, I/O, write-back capability | Vector DB / plugin discovery |
| **Modules / desks** | Domain fetch/analyze/workers | Global auth UX; browser secrets |
| **LLM provider** | Completions behind one interface | Source fetching |
| **Shared context** | Caps + standing notes bundle | Secret storage |
| **Write-back** | Propose/confirm/audit; Calendar insert; Gmail send | Brokerage orders |

### Module loading

- Explicit in-repo registry  
- **All top-tier modules live:** Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative  

## Key flows

0. **Analytics JSON (pivot)** — `crawley-ui` → `GET /v1/asx/companies` / `POST /v1/asx/scan/start` → `GET /v1/jobs/asx-scan`; OpenAPI at `/openapi.json`.  
1. **Start & open dashboard (legacy HTMX)** — localhost; Day brief + glances for all live modules.  
2. **Notes lite modules** — Save notes → Run → LLM Markdown → snapshot.  
3. **Co-parenting** — Schedule lines → bounded window → Markdown.  
4. **Google read** — Shared readonly OAuth → Gmail/Calendar skim.  
5. **Calendar write** — Propose draft (UUID) → Confirm → `events.insert` → audit (or Cancel = no write). Reconnect with `?calendar_write=1` for events scope.  
6. **Day brief** — Compose from Calendar+Gmail snapshots; optional LLM regenerate; optional shared context.  
7. **Local LLM** — Settings LocalLlama → base URL/model/timeout → Test → modules use provider.  
8. **Shared context** — Standing notes + capped snapshots + optional history pins; opt-in into prompts.  
9. **ASX paper desk** — Refresh recommendations → paper trade → portfolio MTM; simulation settings only.  
10. **Google Connect (LAN)** — Settings shows Host redirect URI → Connect; consent only when needed.  
11. **Thread digest** — Sender detail → Digest thread → Markdown snapshot.  
12. **ASX notebook** — Edit thesis/notes → regenerate profile with capped slice.  
13. **VIP rules** — Mark VIP/muted → list order + categorize honor rules.  
10. **Snapshot history** — Browse/search Settings history; pin into shared context (capped).  
11. **Fitness import** — Upload bounded activity file; optional include on Fitness run.  
12. **LAN enable** — Settings toggle / `CRAWLEY_HOST`; trusted LAN only.

## Decisions (ADR log)

| ID | Decision | Date | Status |
|----|----------|------|--------|
| [ADR-001](adr/001-fastapi-htmx.md) | FastAPI + Jinja2/HTMX for local UI | 2026-07-15 | **Superseded** for product surface by ADR-009 |
| [ADR-002](adr/002-duckdb-filesystem.md) | DuckDB + filesystem (+ Parquet) worker store | 2026-07-15 | Accepted |
| [ADR-003](adr/003-single-process-threads.md) | Single process; threads for crawl I/O | 2026-07-15 | **Evolving** → API + daemon entrypoints (ADR-009) |
| [ADR-004](adr/004-module-contract-registry.md) | Module Protocol + explicit in-repo registry | 2026-07-15 | Accepted (quarantine non-ASX/Gmail in Sprint 35) |
| [ADR-005](adr/005-llm-provider-interface.md) | LLM provider interface; OpenAI first | 2026-07-15 | Accepted |
| [ADR-006](adr/006-write-back-confirm.md) | Write-back: confirm, draft-first | 2026-07-15 | Accepted (stays on analytics host) |
| [ADR-007](adr/007-local-llm-ollama.md) | LocalLlama via Ollama HTTP | 2026-07-15 | Accepted |
| [ADR-008](adr/008-shared-context.md) | Shared context seed (caps, opt-in) | 2026-07-15 | Accepted |
| [ADR-009](adr/009-phone-preview-analytics.md) | Phone Preview UI + Python analytics/daemons | 2026-07-16 | **Accepted** |

## Risks & open questions

| Item | Notes |
|------|-------|
| **Google OAuth on WSL** | Residual redirect risk; write scope needs explicit reconnect. |
| **OpenAI / local cost & latency** | Bounds preserved; local timeouts fail loudly. |
| **Calendar write** | Confirm-first only; primary calendar; no recurring-series editor. |
| **Day brief clutter** | One composition; truncate long snapshot bodies in CSS. |
| **Shared context** | Caps may drop detail; opt-in default keeps prompts cheap. |
| **LAN / phone access** | Trusted LAN only; no auth gate. |
