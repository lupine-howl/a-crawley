# Backlog

Prioritized work items. Product owner owns this file.  
**Working title:** Crawley  
**Status:** Interview 2 draft — awaiting stakeholder confirm

Status values: `idea` | `ready` | `in_sprint` | `done` | `dropped`

## Priority order

### B1 — Runnable shell & local dashboard

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | — |

**Goal:** Operator can start Crawley locally and open a browser dashboard on localhost.

**Acceptance criteria:**

- [ ] `uv`-managed Python project with documented run command (e.g. `uv run python -m crawley`)
- [ ] FastAPI + Jinja2/HTMX serves a dashboard on localhost
- [ ] `.env.example` documents required secrets; secrets stay gitignored
- [ ] README (or short run section) covers start → open browser on WSL/Linux

**Out of scope:**

- LAN/phone bind, auth hardening beyond localhost defaults
- Native desktop wrapper

---

### B2 — Module contract, registry & top-tier stubs

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B1 |

**Goal:** Stable module contract + nav so domains can be added without rewriting the shell; non-PoC modules show Coming soon.

**Acceptance criteria:**

- [ ] Module Protocol/ABC (lifecycle, config/credential hooks, inputs/outputs; write-back hooks reserved unused)
- [ ] Explicit in-repo registry wiring modules into the shell
- [ ] Dashboard nav includes top-tier entries: Investment, Gmail, Calendar, Fitness, Co-parenting, DIY, Work, Finance/Taxes, Coding/Creative (names may be shortened in UI)
- [ ] Clicking a stub module shows a clear Coming soon (or equivalent) panel — no crash, no fake data
- [ ] Fitness is stub-only in Sprint 1 (contract-compliant panel)

**Out of scope:**

- Real fetch/LLM for stub modules
- Plugin entry-point discovery outside the repo

---

### B3 — OpenAI LLM provider (PoC)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B1 |

**Goal:** Modules call one LLM interface; OpenAI is the PoC implementation.

**Acceptance criteria:**

- [ ] Provider interface in core; OpenAI implementation configured via env
- [ ] LocalLlama stub or placeholder exists but is not required to run
- [ ] Failed/missing API key surfaces a clear UI/ops error (no silent hang)
- [ ] Prompt/output size bounded enough for PoC (no unbounded crawl→LLM loops)

**Out of scope:**

- Local model install/ops
- Multi-provider routing UI

---

### B4 — Investment module (lite PoC)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B2, B3 |

**Goal:** From the Investment panel, run a **small** search/scrape and see an LLM-synthesized summary/advice the user can act on manually.

**Acceptance criteria:**

- [ ] Investment panel with a clear trigger (e.g. “Run search”)
- [ ] Small bounded fetch (few sources / limited pages) → raw artifacts under `data/`
- [ ] Structured rows landed in DuckDB (enough for the summary path)
- [ ] LLM summary/advice rendered in the panel (HTMX partial or full refresh)
- [ ] Job/status feedback while work runs (at least simple busy/done/error)

**Out of scope:**

- Broad market coverage, portfolios, backtesting
- Automated trading / order placement
- Unbounded crawl depth or scheduled background crawls

---

### B5 — Gmail module (lite PoC, read-only)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P0 |
| Roadmap theme | Now |
| Depends on | B2, B3 |

**Goal:** Connect one Google identity (read-only), scan a thin slice of inbox, show an LLM (or structured) email summary in the panel.

**Acceptance criteria:**

- [ ] OAuth installed-app flow works on stakeholder WSL/Linux + browser; tokens stored locally (gitignored)
- [ ] Read-only Gmail scope only; happy path documented briefly
- [ ] Quick inbox scan (bounded message count / recent window) → panel summary the user can skim
- [ ] Clear errors for missing credentials, revoked token, or API failure

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
| Roadmap theme | Now (stub) / Next (real) |
| Depends on | B2 |

**Goal:** Calendar appears as a first-class nav entry; Sprint 1 is Coming soon (or stub). Real read-only Calendar summary is a follow-on.

**Acceptance criteria (Sprint 1):**

- [ ] Calendar nav entry opens Coming soon / stub panel

**Acceptance criteria (later — not Sprint 1):**

- [ ] Read-only Calendar fetch + skim/summary (may share Google OAuth with Gmail)

**Out of scope (Sprint 1):**

- Real Calendar API calls

---

### B7 — Harden investment crawl & advice UX

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

### B8 — Harden Gmail + add Calendar read summary

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

### B9 — Fitness beyond stub

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

### B10 — Phone-on-LAN access pattern

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
