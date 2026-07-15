# Backlog

Prioritized work items. Product owner owns this file.  
**Working title:** Crawley  
**Status:** Sprint 2 active; Sprints 3–10 planned under `docs/sprints/planned/`

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

### B6 — Calendar module (read-only lite)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B15 |
| Planned sprint | 3 |

**Goal:** Calendar is a live module: bounded upcoming events → Markdown summary via shared Google read-only OAuth.

**Acceptance criteria (Sprint 1 stub — done):**

- [x] Calendar nav entry opens Coming soon / stub panel

**Acceptance criteria (Sprint 3):**

- [ ] Read-only Calendar fetch for a bounded upcoming window
- [ ] LLM Markdown summary; job busy/done/error; empty state honest
- [ ] Success snapshot for home glance
- [ ] Clear errors for missing Calendar scope / auth failure

**Out of scope:**

- Write-back, full sync, multi-calendar UX complexity

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
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B4 |
| Planned sprint | 4 |

**Goal:** Richer bounded sources, cache, clearer advice Markdown, better errors — still manual action only.

**Acceptance criteria:**

- [ ] Cache/reuse fetch artifacts for identical (or TTL) re-runs
- [ ] Bounded richer source metadata; hard caps preserved
- [ ] Improved advice Markdown structure; source list + summary in panel
- [ ] Clearer network/parse/LLM/empty error handling
- [ ] No trading/order affordances

**Out of scope:**

- Automated trading, brokerage APIs, portfolio accounting product

---

### B10 — Harden Gmail (read-only)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B5, B15 |
| Planned sprint | 3 |

**Goal:** Better Gmail skim quality and auth/error UX on shared Google credentials (Calendar is B6).

**Acceptance criteria:**

- [ ] Clearer Markdown summary structure (priorities / follow-ups)
- [ ] Better auth expiry, quota, and empty-inbox handling
- [ ] Still bounded; uses shared Google OAuth from B15
- [ ] No write-back

**Out of scope:**

- Send/labels mutation, full-history sync, multi-account

---

### B11 — Fitness beyond stub (lite)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Planned sprint | 4 |

**Goal:** Fitness lite: goal/context in → LLM introductory plan Markdown out; not medical care.

**Acceptance criteria:**

- [ ] Fitness leaves Coming soon; form for goal/context
- [ ] LLM Markdown breakdown; disclaimer not medical advice
- [ ] Job status + snapshot for home
- [ ] No wearable API required

**Out of scope:**

- Diagnosis, prescriptions, regulated health product claims
- Mandatory device integrations

---

### B12 — Phone-on-LAN access pattern

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B1 |
| Planned sprint | 5 |

**Goal:** Same browser UI on LAN only when consciously enabled; localhost default.

**Acceptance criteria:**

- [ ] Default bind localhost; explicit LAN enable with warning
- [ ] Documented WSL/firewall test path; disable returns to localhost
- [ ] Auth posture decided and documented (minimal gate **or** trusted-LAN-only)
- [ ] Settings and/or env control

**Out of scope:**

- Public internet exposure, reverse proxies as product feature

---

### B15 — Shared Google OAuth (Gmail + Calendar read-only)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B5 |
| Planned sprint | 3 |

**Goal:** One Google identity; Gmail + Calendar readonly scopes; reconsent if upgrading from Gmail-only.

**Acceptance criteria:**

- [ ] Installed-app OAuth with both readonly scopes
- [ ] Local tokens; upgrade/reconsent path
- [ ] Connected/reconnect surfaced in UI minimally
- [ ] No write scopes

**Out of scope:**

- Multi-account Google, Workspace admin features

---

### B16 — Home glance: additional module slots

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14 |
| Planned sprint | 4 |

**Goal:** Extend At a glance as modules go live (Fitness required in Sprint 4; Calendar expected from Sprint 3 store).

**Acceptance criteria:**

- [ ] Home shows last Fitness snapshot when present
- [ ] Keeps prior module snapshots; still one composition / truncate long bodies
- [ ] Participating modules listed in architecture.md

**Out of scope:**

- Full history browser

---

### B17 — Work module lite

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Planned sprint | 5 |

**Goal:** Work domain live: local tasks/notes → LLM prioritization Markdown.

**Acceptance criteria:**

- [ ] Work leaves Coming soon; local task/note capture
- [ ] Run → Markdown next-actions / prioritization
- [ ] Snapshot on home; no third-party OAuth required

**Out of scope:**

- Jira/Linear/Google Tasks sync (Later candidates)

---

### B18 — Write-back design (ADR + dry-run hooks)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B6, B5 |
| Planned sprint | 5 |

**Goal:** Lock how write-back will work before implementing mutations.

**Acceptance criteria:**

- [ ] ADR: confirm-before-write, draft-first, audit locally
- [ ] Contract hooks documented; dry-run/no-op only in app
- [ ] Architecture stages: propose → confirm → execute
- [ ] No live Gmail send / Calendar insert

**Out of scope:**

- Actual write API calls

---

### B19 — Co-parenting schedule lite

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Planned sprint | 6 |

**Goal:** Leave Coming soon with a local co-parenting schedule (handoffs / custody windows) the operator maintains, plus an LLM Markdown skim of what’s next — not a multi-user family product.

**Acceptance criteria:**

- [ ] Co-parenting leaves Coming soon; local schedule entries (dates/windows + short notes) persist under `data/`
- [ ] Run → Markdown “what’s next / conflicts to watch” summary (bounded window)
- [ ] Job status + success snapshot for home glance
- [ ] Clear empty state; no fake demo custody data
- [ ] Copy stays personal planning — no third-party co-parent accounts

**Out of scope:**

- Shared login for the other co-parent
- Court/legal document generation
- Mandatory Google Calendar sync (optional Later; local source of truth this sprint)

---

### B20 — DIY projects lite

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Planned sprint | 6 |

**Goal:** DIY domain live: local project notes / punch list → LLM next-steps Markdown.

**Acceptance criteria:**

- [ ] DIY leaves Coming soon; operator can save one or more project notes (title + free text / checklist)
- [ ] Run → Markdown suggested next steps / materials-to-consider framing (manual action only)
- [ ] Job status + success snapshot for home glance
- [ ] No e-commerce checkout or vendor scrape required

**Out of scope:**

- Shopping cart / price bots
- Photo-based AR measurement tools

---

### B21 — Home glance: Co-parenting + DIY slots

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14, B19, B20 |
| Planned sprint | 6 |

**Goal:** Extend At a glance when Co-parenting and DIY go live; keep one composition.

**Acceptance criteria:**

- [ ] Home shows last Co-parenting and DIY snapshots when present
- [ ] Prior module snapshots retained; long bodies truncated; no stub filler
- [ ] Participating modules list updated in `docs/architecture.md`

**Out of scope:**

- Full history browser; customizable home widget layout editor

---

### B22 — Finance / taxes lite

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Planned sprint | 7 |

**Goal:** Finance/Taxes leaves Coming soon with a safe personal planning path: local notes/context → LLM structured overview — not a brokerage or tax-filing product.

**Acceptance criteria:**

- [ ] Finance/Taxes leaves Coming soon; local context capture (notes / categories / questions)
- [ ] Run → Markdown planning summary (topics to review, questions for advisor, reminders) with explicit “not professional tax/financial advice” disclaimer
- [ ] Job status + success snapshot for home glance
- [ ] No brokerage/bank OAuth; no automated filing or payments

**Out of scope:**

- Portfolio accounting, brokerage APIs, tax e-file
- Advice framed as licensed professional care

---

### B23 — Home day brief (Calendar + Gmail)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B6, B10, B14 |
| Planned sprint | 7 |

**Goal:** One composed morning pull on home: combine last (or freshly runnable) Calendar + Gmail signals into a short day brief — habit/pull without a second UI stack.

**Acceptance criteria:**

- [ ] Home (or a single At a glance section) can show a **Day brief** Markdown composed from Calendar + Gmail snapshot inputs
- [ ] Operator can refresh brief from existing successful snapshots without inventing data when a module has never succeeded
- [ ] Empty/partial states honest (e.g. Calendar only, Gmail only, neither)
- [ ] Stays one composition — not a widget dump; truncates long bodies
- [ ] Approach noted in `docs/architecture.md`

**Out of scope:**

- Scheduled auto-runs overnight (Later candidate)
- Push notifications / email digest off-machine

---

### B24 — Home glance: Finance slot

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14, B22 |
| Planned sprint | 7 |

**Goal:** Add Finance snapshot to At a glance when Finance lite ships.

**Acceptance criteria:**

- [ ] Home shows last Finance snapshot when present
- [ ] Glance list updated in architecture.md; composition rules preserved

**Out of scope:**

- Charts / net-worth dashboards

---

### B25 — Calendar write-back (confirm-first)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B6, B15, B18 |
| Planned sprint | 8 |

**Goal:** First real mutation path: propose a Calendar event draft → show draft/diff → explicit confirm → insert via Google API → local audit entry. Implements Sprint 5 ADR stages for one surface only.

**Acceptance criteria:**

- [ ] Calendar (or shared write UI) can propose an event draft from operator input and/or LLM suggestion
- [ ] Confirm step required; cancel leaves no remote write
- [ ] On confirm: Calendar insert with appropriate write scope; success/failure clear in UI
- [ ] Local audit log entry (what, when, outcome) under `data/`
- [ ] Reconsent path if current token lacks write scope; no silent scope creep into Gmail send
- [ ] UX/ADR stages match Sprint 5 design (propose → confirm → execute → audit)

**Out of scope:**

- Gmail send / labels mutation (separate item)
- Bulk import, recurring-series editors, multi-calendar complexity beyond one primary calendar
- Silent/scheduled automation without confirm

---

### B26 — Write-back audit log viewer (lite)

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B25 |
| Planned sprint | 8 |

**Goal:** Operator can skim recent write-back attempts without opening raw files.

**Acceptance criteria:**

- [ ] Settings or Calendar panel lists recent audit entries (bounded, newest first)
- [ ] Shows timestamp, module, action summary, success/failure
- [ ] No edit/replay of mutations required this sprint

**Out of scope:**

- Full SIEM, export pipelines, multi-user ACLs

---

### B27 — LocalLlama provider operable

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B3, B8 |
| Planned sprint | 9 |

**Goal:** Prove the path off cloud for core advice: a local Llama-class (or compatible) provider works behind the existing LLM interface when the operator has a local runtime.

**Acceptance criteria:**

- [ ] `LocalLlama` (or named local provider) implements the provider interface against a documented local runtime (e.g. Ollama HTTP — architect chooses; document in ADR/architecture)
- [ ] Settings: select local provider, configure base URL / model id; **Test connection** works
- [ ] Modules use the active provider after save (hot-reload vs restart documented)
- [ ] Clear errors when daemon unreachable, model missing, or timeout
- [ ] README covers install/run assumptions for the stakeholder machine; OpenAI remains available as fallback choice
- [ ] PoC success metric “path to local LLM” advanced — cloud not deleted

**Out of scope:**

- Bundling/shipping model weights in the repo
- GPU provisioning productization
- Multi-provider routing UI beyond single active selection

---

### B28 — Coding / Creative projects lite

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B2, B13 |
| Planned sprint | 10 |

**Goal:** Coding/Creative leaves Coming soon: local project notes / focus context → LLM next-steps Markdown for personal creative/coding work.

**Acceptance criteria:**

- [ ] Coding/Creative leaves Coming soon; local notes/context persist under `data/`
- [ ] Run → Markdown priorities / next experiments (manual action)
- [ ] Job status + success snapshot for home glance
- [ ] No mandatory GitHub/GitLab OAuth this sprint

**Out of scope:**

- IDE plugin, CI integration, auto-commits
- Replacing the operator’s editor

---

### B29 — Cross-module context seed

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B14, B23 |
| Planned sprint | 10 |

**Goal:** Stronger local organisation: a thin **shared context** store modules/home can read (recent snapshots + optional short operator “standing notes”) so LLM prompts can cite cross-domain signal without a second product.

**Acceptance criteria:**

- [ ] Documented shared-context bundle (files/DuckDB — architect chooses) built from recent successful snapshots + optional standing notes
- [ ] At least one module path and/or Day brief can optionally include a bounded slice of shared context in the LLM prompt
- [ ] Hard caps on context size; secrets/tokens never injected into prompts from this store
- [ ] Architecture ADR or section: what is in/out of shared context; opt-in vs default
- [ ] Home or Settings can view/edit standing notes (minimal)

**Out of scope:**

- Vector DB / RAG productization
- Automatic PII redaction suite
- Fine-tuned personal model

---

### B30 — Home glance: Coding/Creative slot

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P2 |
| Roadmap theme | Later → scheduled |
| Depends on | B14, B28 |
| Planned sprint | 10 |

**Goal:** Coding/Creative snapshot appears on At a glance when present.

**Acceptance criteria:**

- [ ] Home shows last Coding/Creative snapshot when present
- [ ] Glance participants list updated in architecture.md

**Out of scope:**

- Per-module pin/hide preferences UI

---

<!-- Add new items above this line. Planned sprints: docs/sprints/planned/ -->
