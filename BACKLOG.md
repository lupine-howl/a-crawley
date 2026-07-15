# Backlog

Prioritized work items. Product owner owns this file.  
**Working title:** Crawley  
**Status:** Sprint 1 closed 2026-07-15; Sprint 2 active (B7, B8, B13, B14)

Status values: `idea` | `ready` | `in_sprint` | `done` | `dropped`

## Priority order

### B1 — Runnable shell & local dashboard

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | — |

**Goal:** Operator can start Crawley locally and open a browser dashboard on localhost.

**Acceptance criteria:**

- [x] `uv`-managed Python project with documented run command (e.g. `uv run python -m crawley`)
- [x] FastAPI + Jinja2/HTMX serves a dashboard on localhost
- [x] `.env.example` documents required secrets; secrets stay gitignored
- [x] README (or short run section) covers start → open browser on WSL/Linux

**Out of scope:**

- LAN/phone bind, auth hardening beyond localhost defaults
- Native desktop wrapper

---

### B2 — Module contract, registry & top-tier stubs

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B1 |

**Goal:** Stable module contract + nav so domains can be added without rewriting the shell; non-PoC modules show Coming soon.

**Acceptance criteria:**

- [x] Module Protocol/ABC (lifecycle, config/credential hooks, inputs/outputs; write-back hooks reserved unused)
- [x] Explicit in-repo registry wiring modules into the shell
- [x] Dashboard nav includes top-tier entries: Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative (names may be shortened in UI)
- [x] Clicking a stub module shows a clear Coming soon (or equivalent) panel — no crash, no fake data
- [x] Fitness is stub-only in Sprint 1 (contract-compliant panel)

**Out of scope:**

- Real fetch/LLM for stub modules
- Plugin entry-point discovery outside the repo

---

### B3 — OpenAI LLM provider (PoC)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B1 |

**Goal:** Modules call one LLM interface; OpenAI is the PoC implementation.

**Acceptance criteria:**

- [x] Provider interface in core; OpenAI implementation configured via env
- [x] LocalLlama stub or placeholder exists but is not required to run
- [x] Failed/missing API key surfaces a clear UI/ops error (no silent hang)
- [x] Prompt/output size bounded enough for PoC (no unbounded crawl→LLM loops)

**Out of scope:**

- Local model install/ops
- Multi-provider routing UI

---

### B4 — Investment module (lite PoC)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B2, B3 |

**Goal:** From the Investment panel, run a **small** search/scrape and see an LLM-synthesized summary/advice the user can act on manually.

**Acceptance criteria:**

- [x] Investment panel with a clear trigger (e.g. “Run search”)
- [x] Small bounded fetch (few sources / limited pages) → raw artifacts under `data/`
- [x] Structured rows landed in DuckDB (enough for the summary path)
- [x] LLM summary/advice rendered in the panel (HTMX partial or full refresh)
- [x] Job/status feedback while work runs (at least simple busy/done/error)

**Out of scope:**

- Broad market coverage, portfolios, backtesting
- Automated trading / order placement
- Unbounded crawl depth or scheduled background crawls

---

### B5 — Gmail module (lite PoC, read-only)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B2, B3 |

**Goal:** Connect one Google identity (read-only), scan a thin slice of inbox, show an LLM (or structured) email summary in the panel.

**Acceptance criteria:**

- [x] OAuth installed-app flow works on stakeholder WSL/Linux + browser; tokens stored locally (gitignored)
- [x] Read-only Gmail scope only; happy path documented briefly
- [x] Quick inbox scan (bounded message count / recent window) → panel summary the user can skim
- [x] Clear errors for missing credentials, revoked token, or API failure

**Out of scope:**

- Gmail write-back / send / labels mutation
- Full-history sync or multi-account
- Deep thread analytics

---

### B6 — Calendar module (stub in Sprint 1; real read Later/Next)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Now (stub done) / Next (real) |
| Depends on | B2 |

**Goal:** Calendar appears as a first-class nav entry; Sprint 1 is Coming soon (or stub). Real read-only Calendar summary is a follow-on.

**Acceptance criteria (Sprint 1):**

- [x] Calendar nav entry opens Coming soon / stub panel

**Acceptance criteria (later — not Sprint 1):**

- [ ] Read-only Calendar fetch + skim/summary (may share Google OAuth with Gmail)

**Out of scope (Sprint 1):**

- Real Calendar API calls

---

### B7 — Themable UI & design polish

| Field | Value |
|-------|-------|
| Status | in_sprint |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B1, B2 |
| Sprint | 2 |

**Goal:** Evolve Sprint 1 custom CSS tokens into a clearer visual system with a **themable palette** (light/dark or named themes), informed by a UX expert pass (`docs/ux.md`) if available.

**Acceptance criteria:**

- [ ] Theme tokens (colors, type/spacing as needed) live in one place and apply across shell + module panels
- [ ] Operator can switch theme from the dashboard (persist locally)
- [ ] Styling approach decision recorded in architecture (custom CSS themes vs later build tool)
- [ ] Stub / Coming soon panels match the updated system

**Out of scope:**

- Full brand/marketing site
- Native desktop chrome styling

---

### B8 — LLM settings & connection test

| Field | Value |
|-------|-------|
| Status | in_sprint |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B3 |
| Sprint | 2 |

**Goal:** From the dashboard, configure which LLM model/provider settings to use and verify connectivity without digging through `.env` only.

**Acceptance criteria:**

- [ ] Settings entry point on the dashboard (button/nav to settings panel)
- [ ] Configure active model (and related PoC settings — e.g. model id); secrets stay local / not committed
- [ ] **Test connection** action reports success/failure clearly in the UI
- [ ] Modules use the configured provider/settings after save (document restart-required vs hot-reload)

**Out of scope:**

- Multi-user settings profiles
- LocalLlama install/ops (beyond selecting a stub/provider that isn’t ready)
- Cloud billing dashboards

---

### B13 — Markdown rendering for LLM summaries

| Field | Value |
|-------|-------|
| Status | in_sprint |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B4, B5 (summary panels exist) |
| Sprint | 2 |

**Goal:** Show Investment / Gmail (and similar) LLM output as formatted Markdown in the dashboard, not plain monospace text.

**Acceptance criteria:**

- [ ] Panel summaries render Markdown→HTML safely (no script from model output)
- [ ] Minimum: headings, paragraphs, bold/italic, lists, links
- [ ] Styles use theme tokens; readable in all Sprint 2 themes
- [ ] Approach noted in `docs/architecture.md`

**Out of scope:**

- Rich embed types (mermaid, math), in-app MD editor
- Replacing stub Coming soon content with Markdown docs

---

### B14 — Dashboard home At a glance

| Field | Value |
|-------|-------|
| Status | in_sprint |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B13 (Markdown render); B4, B5 |
| Sprint | 2 |

**Goal:** Give the operator a reason to reopen Crawley: home shows LLM/Gmail status plus **persisted** last successful Investment and Gmail summaries with deep links — not an empty dashboard stub.

**Acceptance criteria:**

- [ ] `/` At a glance: status chips + last Investment + last Gmail (or empty hints)
- [ ] Snapshots persist under `data/` across restarts; only successful runs update them
- [ ] Markdown snippets reuse safe renderer; theme tokens; no fake stub data
- [ ] Documented in `docs/architecture.md`

**Out of scope:**

- Full run history UI, scheduled auto-runs, “run all” batch

---

### B9 — Harden investment crawl & advice UX

| Field | Value |
|-------|-------|
| Status | idea |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B4 |

**Goal:** Richer sources, clearer advice presentation, better caching/error handling after lite PoC proves the path.

**Acceptance criteria:**

- [ ] TBD in a later planning pass

**Out of scope:**

- Automated trading

---

### B10 — Harden Gmail + add Calendar read summary

| Field | Value |
|-------|-------|
| Status | idea |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B5, B6 |

**Goal:** Deeper mail summary quality; Calendar read-only summary beside Gmail.

**Acceptance criteria:**

- [ ] TBD in a later planning pass

**Out of scope:**

- Write-back

---

### B11 — Fitness beyond stub

| Field | Value |
|-------|-------|
| Status | idea |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B2 |

**Goal:** Fitness module that does more than Coming soon (goals breakdown / source TBD).

**Acceptance criteria:**

- [ ] TBD

---

### B12 — Phone-on-LAN access pattern

| Field | Value |
|-------|-------|
| Status | idea |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B1 |

**Goal:** Same browser UI reachable on LAN only when consciously enabled; intrusion-minded defaults.

**Acceptance criteria:**

- [ ] TBD

---

<!-- Add new items above this line, highest priority first. Keep sprint detail in docs/sprints/current.md -->
