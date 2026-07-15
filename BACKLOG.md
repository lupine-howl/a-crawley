# Backlog

Prioritized work items. Product owner owns this file.  
**Working title:** Crawley  
**Status:** Sprints 1–10 closed (6–10 delivered as one bundle)

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
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B15 |
| Sprint | 3–4 |

**Goal:** Calendar is a live module: bounded upcoming events → Markdown summary via shared Google read-only OAuth.

**Acceptance criteria (Sprint 1 stub — done):**

- [x] Calendar nav entry opens Coming soon / stub panel

**Acceptance criteria (Sprint 3–4):**

- [x] Read-only Calendar fetch for a bounded upcoming window
- [x] LLM Markdown summary; job busy/done/error; empty state honest
- [x] Success snapshot for home glance
- [x] Clear errors for missing Calendar scope / auth failure

**Out of scope:**

- Write-back, full sync, multi-calendar UX complexity

---

### B7 — Themable UI & design polish

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B1, B2 |
| Sprint | 2 |

**Goal:** Evolve Sprint 1 custom CSS tokens into a clearer visual system with a **themable palette** (light/dark or named themes), informed by a UX expert pass (`docs/ux.md`) if available.

**Acceptance criteria:**

- [x] Theme tokens (colors, type/spacing as needed) live in one place and apply across shell + module panels
- [x] Operator can switch theme from the dashboard (persist locally)
- [x] Styling approach decision recorded in architecture (custom CSS themes vs later build tool)
- [x] Stub / Coming soon panels match the updated system

**Out of scope:**

- Full brand/marketing site
- Native desktop chrome styling

---

### B8 — LLM settings & connection test

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B3 |
| Sprint | 2 |

**Goal:** From the dashboard, configure which LLM model/provider settings to use and verify connectivity without digging through `.env` only.

**Acceptance criteria:**

- [x] Settings entry point on the dashboard (button/nav to settings panel)
- [x] Configure active model (and related PoC settings — e.g. model id); secrets stay local / not committed
- [x] **Test connection** action reports success/failure clearly in the UI
- [x] Modules use the configured provider/settings after save (document restart-required vs hot-reload)

**Out of scope:**

- Multi-user settings profiles
- LocalLlama install/ops (beyond selecting a stub/provider that isn’t ready)
- Cloud billing dashboards

---

### B13 — Markdown rendering for LLM summaries

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B4, B5 (summary panels exist) |
| Sprint | 2 |

**Goal:** Show Investment / Gmail (and similar) LLM output as formatted Markdown in the dashboard, not plain monospace text.

**Acceptance criteria:**

- [x] Panel summaries render Markdown→HTML safely (no script from model output)
- [x] Minimum: headings, paragraphs, bold/italic, lists, links
- [x] Styles use theme tokens; readable in all Sprint 2 themes
- [x] Approach noted in `docs/architecture.md`

**Out of scope:**

- Rich embed types (mermaid, math), in-app MD editor
- Replacing stub Coming soon content with Markdown docs

---

### B14 — Dashboard home At a glance

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B13 (Markdown render); B4, B5 |
| Sprint | 2 |

**Goal:** Give the operator a reason to reopen Crawley: home shows LLM/Gmail status plus **persisted** last successful Investment and Gmail summaries with deep links — not an empty dashboard stub.

**Acceptance criteria:**

- [x] `/` At a glance: status chips + last Investment + last Gmail (or empty hints)
- [x] Snapshots persist under `data/` across restarts; only successful runs update them
- [x] Markdown snippets reuse safe renderer; theme tokens; no fake stub data
- [x] Documented in `docs/architecture.md`

**Out of scope:**

- Full run history UI, scheduled auto-runs, “run all” batch

---

### B9 — Harden investment crawl & advice UX

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B4 |
| Sprint | 3–4 |

**Goal:** Richer bounded sources, cache, clearer advice Markdown, better errors — still manual action only.

**Acceptance criteria:**

- [x] Cache/reuse fetch artifacts for identical (or TTL) re-runs
- [x] Bounded richer source metadata; hard caps preserved
- [x] Improved advice Markdown structure; source list + summary in panel
- [x] Clearer network/parse/LLM/empty error handling
- [x] No trading/order affordances

**Out of scope:**

- Automated trading, brokerage APIs, portfolio accounting product

---

### B10 — Harden Gmail (read-only)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B5, B15 |
| Sprint | 3–4 |

**Goal:** Better Gmail skim quality and auth/error UX on shared Google credentials (Calendar is B6).

**Acceptance criteria:**

- [x] Clearer Markdown summary structure (priorities / follow-ups)
- [x] Better auth expiry, quota, and empty-inbox handling
- [x] Still bounded; uses shared Google OAuth from B15
- [x] No write-back

**Out of scope:**

- Send/labels mutation, full-history sync, multi-account

---

### B11 — Fitness beyond stub (lite)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Sprint | 3–4 |

**Goal:** Fitness lite: goal/context in → LLM introductory plan Markdown out; not medical care.

**Acceptance criteria:**

- [x] Fitness leaves Coming soon; form for goal/context
- [x] LLM Markdown breakdown; disclaimer not medical advice
- [x] Job status + snapshot for home
- [x] No wearable API required

**Out of scope:**

- Diagnosis, prescriptions, regulated health product claims
- Mandatory device integrations

---

### B12 — Phone-on-LAN access pattern

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B1 |
| Sprint | 5 |

**Goal:** Same browser UI on LAN only when consciously enabled; localhost default.

**Acceptance criteria:**

- [x] Default bind localhost; explicit LAN enable with warning
- [x] Documented WSL/firewall test path; disable returns to localhost
- [x] Auth posture decided and documented (minimal gate **or** trusted-LAN-only)
- [x] Settings and/or env control

**Out of scope:**

- Public internet exposure, reverse proxies as product feature

---

### B15 — Shared Google OAuth (Gmail + Calendar read-only)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B5 |
| Sprint | 3–4 |

**Goal:** One Google identity; Gmail + Calendar readonly scopes; reconsent if upgrading from Gmail-only.

**Acceptance criteria:**

- [x] Installed-app OAuth with both readonly scopes
- [x] Local tokens; upgrade/reconsent path
- [x] Connected/reconnect surfaced in UI minimally
- [x] No write scopes

**Out of scope:**

- Multi-account Google, Workspace admin features

---

### B16 — Home glance: additional module slots

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14 |
| Sprint | 3–4 |

**Goal:** Extend At a glance as modules go live (Fitness required in Sprint 4; Calendar expected from Sprint 3 store).

**Acceptance criteria:**

- [x] Home shows last Fitness snapshot when present
- [x] Keeps prior module snapshots; still one composition / truncate long bodies
- [x] Participating modules listed in architecture.md

**Out of scope:**

- Full history browser

---

### B17 — Work module lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Sprint | 5 |

**Goal:** Work domain live: local tasks/notes → LLM prioritization Markdown.

**Acceptance criteria:**

- [x] Work leaves Coming soon; local task/note capture
- [x] Run → Markdown next-actions / prioritization
- [x] Snapshot on home; no third-party OAuth required

**Out of scope:**

- Jira/Linear/Google Tasks sync (Later candidates)

---

### B18 — Write-back design (ADR + dry-run hooks)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B6, B5 |
| Sprint | 5 |

**Goal:** Lock how write-back will work before implementing mutations.

**Acceptance criteria:**

- [x] ADR: confirm-before-write, draft-first, audit locally
- [x] Contract hooks documented; dry-run/no-op only in app
- [x] Architecture stages: propose → confirm → execute
- [x] No live Gmail send / Calendar insert

**Out of scope:**

- Actual write API calls

---

### B19 — Co-parenting schedule lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Sprint | 6 |

**Goal:** Leave Coming soon with a local co-parenting schedule (handoffs / custody windows) the operator maintains, plus an LLM Markdown skim of what’s next — not a multi-user family product.

**Acceptance criteria:**

- [x] Co-parenting leaves Coming soon; local schedule entries (dates/windows + short notes) persist under `data/`
- [x] Run → Markdown “what’s next / conflicts to watch” summary (bounded window)
- [x] Job status + success snapshot for home glance
- [x] Clear empty state; no fake demo custody data
- [x] Copy stays personal planning — no third-party co-parent accounts

**Out of scope:**

- Shared login for the other co-parent
- Court/legal document generation
- Mandatory Google Calendar sync (optional Later; local source of truth this sprint)

---

### B20 — DIY projects lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Sprint | 6 |

**Goal:** DIY domain live: local project notes / punch list → LLM next-steps Markdown.

**Acceptance criteria:**

- [x] DIY leaves Coming soon; operator can save one or more project notes (title + free text / checklist)
- [x] Run → Markdown suggested next steps / materials-to-consider framing (manual action only)
- [x] Job status + success snapshot for home glance
- [x] No e-commerce checkout or vendor scrape required

**Out of scope:**

- Shopping cart / price bots
- Photo-based AR measurement tools

---

### B21 — Home glance: Co-parenting + DIY slots

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14, B19, B20 |
| Sprint | 6 |

**Goal:** Extend At a glance when Co-parenting and DIY go live; keep one composition.

**Acceptance criteria:**

- [x] Home shows last Co-parenting and DIY snapshots when present
- [x] Prior module snapshots retained; long bodies truncated; no stub filler
- [x] Participating modules list updated in `docs/architecture.md`

**Out of scope:**

- Full history browser; customizable home widget layout editor

---

### B22 — Finance / taxes lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B2, B13 |
| Sprint | 7 |

**Goal:** Finance/Taxes leaves Coming soon with a safe personal planning path: local notes/context → LLM structured overview — not a brokerage or tax-filing product.

**Acceptance criteria:**

- [x] Finance/Taxes leaves Coming soon; local context capture (notes / categories / questions)
- [x] Run → Markdown planning summary (topics to review, questions for advisor, reminders) with explicit “not professional tax/financial advice” disclaimer
- [x] Job status + success snapshot for home glance
- [x] No brokerage/bank OAuth; no automated filing or payments

**Out of scope:**

- Portfolio accounting, brokerage APIs, tax e-file
- Advice framed as licensed professional care

---

### B23 — Home day brief (Calendar + Gmail)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B6, B10, B14 |
| Sprint | 7 |

**Goal:** One composed morning pull on home: combine last (or freshly runnable) Calendar + Gmail signals into a short day brief — habit/pull without a second UI stack.

**Acceptance criteria:**

- [x] Home (or a single At a glance section) can show a **Day brief** Markdown composed from Calendar + Gmail snapshot inputs
- [x] Operator can refresh brief from existing successful snapshots without inventing data when a module has never succeeded
- [x] Empty/partial states honest (e.g. Calendar only, Gmail only, neither)
- [x] Stays one composition — not a widget dump; truncates long bodies
- [x] Approach noted in `docs/architecture.md`

**Out of scope:**

- Scheduled auto-runs overnight (Later candidate)
- Push notifications / email digest off-machine

---

### B24 — Home glance: Finance slot

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B14, B22 |
| Sprint | 7 |

**Goal:** Add Finance snapshot to At a glance when Finance lite ships.

**Acceptance criteria:**

- [x] Home shows last Finance snapshot when present
- [x] Glance list updated in architecture.md; composition rules preserved

**Out of scope:**

- Charts / net-worth dashboards

---

### B25 — Calendar write-back (confirm-first)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next |
| Depends on | B6, B15, B18 |
| Sprint | 8 |

**Goal:** First real mutation path: propose a Calendar event draft → show draft/diff → explicit confirm → insert via Google API → local audit entry. Implements ADR-006 stages for one surface only.

**Acceptance criteria:**

- [x] Calendar (or shared write UI) can propose an event draft from operator input and/or LLM suggestion
- [x] Confirm step required; cancel leaves no remote write
- [x] On confirm: Calendar insert with appropriate write scope; success/failure clear in UI
- [x] Local audit log entry (what, when, outcome) under `data/`
- [x] Reconsent path if current token lacks write scope; no silent scope creep into Gmail send
- [x] UX/ADR stages match Sprint 5 design (propose → confirm → execute → audit)

**Out of scope:**

- Gmail send / labels mutation (separate item)
- Bulk import, recurring-series editors, multi-calendar complexity beyond one primary calendar
- Silent/scheduled automation without confirm

---

### B26 — Write-back audit log viewer (lite)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Next |
| Depends on | B25 |
| Sprint | 8 |

**Goal:** Operator can skim recent write-back attempts without opening raw files.

**Acceptance criteria:**

- [x] Settings or Calendar panel lists recent audit entries (bounded, newest first)
- [x] Shows timestamp, module, action summary, success/failure
- [x] No edit/replay of mutations required this sprint

**Out of scope:**

- Full SIEM, export pipelines, multi-user ACLs

---

### B27 — LocalLlama provider operable

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B3, B8 |
| Sprint | 9 |

**Goal:** Prove the path off cloud for core advice: a local Llama-class (or compatible) provider works behind the existing LLM interface when the operator has a local runtime.

**Acceptance criteria:**

- [x] `LocalLlama` (or named local provider) implements the provider interface against a documented local runtime (e.g. Ollama HTTP — architect chooses; document in ADR/architecture)
- [x] Settings: select local provider, configure base URL / model id; **Test connection** works
- [x] Modules use the active provider after save (hot-reload vs restart documented)
- [x] Clear errors when daemon unreachable, model missing, or timeout
- [x] README covers install/run assumptions for the stakeholder machine; OpenAI remains available as fallback choice
- [x] PoC success metric “path to local LLM” advanced — cloud not deleted

**Out of scope:**

- Bundling/shipping model weights in the repo
- GPU provisioning productization
- Multi-provider routing UI beyond single active selection

---

### B31 — Local provider bounds & module-run errors

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B27 |
| Sprint | 9 |

**Goal:** Local LLM runs must fail loudly and predictably — timeouts/bounds and distinct mid-job daemon errors so busy state never hangs silently.

**Acceptance criteria:**

- [x] Documented timeouts / max output bounds suitable for local hardware
- [x] Module run surfaces distinct errors for daemon-down mid-job vs timeout vs cloud-path failures
- [x] No silent hang in busy state; cancel-or-fail path documented
- [x] Architecture notes local-vs-cloud latency expectations

**Out of scope:**

- Auto GPU installers
- Per-module provider overrides

---

### B28 — Coding / Creative projects lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B2, B13 |
| Sprint | 10 |

**Goal:** Coding/Creative leaves Coming soon: local project notes / focus context → LLM next-steps Markdown for personal creative/coding work.

**Acceptance criteria:**

- [x] Coding/Creative leaves Coming soon; local notes/context persist under `data/`
- [x] Run → Markdown priorities / next experiments (manual action)
- [x] Job status + success snapshot for home glance
- [x] No mandatory GitHub/GitLab OAuth this sprint

**Out of scope:**

- IDE plugin, CI integration, auto-commits
- Replacing the operator’s editor

---

### B29 — Cross-module context seed

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Later → scheduled |
| Depends on | B14, B23 |
| Sprint | 10 |

**Goal:** Stronger local organisation: a thin **shared context** store modules/home can read (recent snapshots + optional short operator “standing notes”) so LLM prompts can cite cross-domain signal without a second product.

**Acceptance criteria:**

- [x] Documented shared-context bundle (files/DuckDB — architect chooses) built from recent successful snapshots + optional standing notes
- [x] At least one module path and/or Day brief can optionally include a bounded slice of shared context in the LLM prompt
- [x] Hard caps on context size; secrets/tokens never injected into prompts from this store
- [x] Architecture ADR or section: what is in/out of shared context; opt-in vs default
- [x] Home or Settings can view/edit standing notes (minimal)

**Out of scope:**

- Vector DB / RAG productization
- Automatic PII redaction suite
- Fine-tuned personal model

---

### B30 — Home glance: Coding/Creative slot

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Later → scheduled |
| Depends on | B14, B28 |
| Sprint | 10 |

**Goal:** Coding/Creative snapshot appears on At a glance when present.

**Acceptance criteria:**

- [x] Home shows last Coding/Creative snapshot when present
- [x] Glance participants list updated in architecture.md

**Out of scope:**

- Per-module pin/hide preferences UI

---

<!-- Add new items above this line. Planned sprints: docs/sprints/planned/ -->
