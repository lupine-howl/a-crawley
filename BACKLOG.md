# Backlog

Prioritized work items. Product owner owns this file.  
**Working title:** Crawley  
**Status:** Sprints 1–20 closed; **Sprint 21 current** = Google OAuth ops (B89–B90); planned **22–30** = B44–B50, B52–B53 (un-shelved depth); remaining post-30 platform/depth stays shelved

Status values: `idea` | `ready` | `in_sprint` | `done` | `dropped` | `shelved`

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

## Shelved backlog (former planned Sprints 11–40; B44–B50 / B52–B53 un-shelved → 22–30)

### B32 — Native desktop shell wrapper

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B1 |
| Planned sprint | 12 |

**Goal:** Optional native window wrapping the existing web UI — one UI stack.

**Acceptance criteria:**

- [ ] Desktop launcher loads existing UI; browser path remains valid
- [ ] ADR for technology choice; README run notes for stakeholder machine
- [ ] Clear error if backend unavailable
- [ ] No parallel native feature widgets

**Out of scope:**

- App-store shipping, auto-update SaaS, mobile binary

---

### B33 — Opt-in scheduled Day brief

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B23 |
| Planned sprint | 13 |

**Goal:** Local opt-in schedule to refresh Day brief; default off; no scheduled write-back.

**Acceptance criteria:**

- [ ] Settings enable/disable + simple cadence; default off
- [ ] Scheduled refresh of Day brief documented (what it may fetch)
- [ ] No scheduled mutations (ADR-006)
- [ ] Missed-run behavior documented

**Out of scope:**

- Push notifications off-machine

---

### B34 — Co-parenting publish to Calendar

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B19, B25 |
| Planned sprint | 14 |

**Goal:** Confirm-first publish of selected co-parenting windows to Google Calendar.

**Acceptance criteria:**

- [ ] Select entries → draft events → confirm insert
- [ ] Local schedule remains source of truth unless published
- [ ] Audit entries; no silent sync loops
- [ ] Sole-operator only

**Out of scope:**

- Other-parent accounts, family ACLs

---

### B35 — Snapshot history browser

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Sprints 14–16 bundle |
| Depends on | B14 |
| Planned sprint | 15 |

**Goal:** Bounded history of successful summaries beyond last-only; browse/search locally.

**Acceptance criteria:**

- [x] Persist bounded N histories per module
- [x] Simple history UI with safe body view (escaped pre)
- [x] Retention/prune documented

**Out of scope:**

- Cloud sync of history

---

### B36 — Shared context depth (history pins)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Sprints 14–16 bundle |
| Depends on | B29, B35 |
| Planned sprint | 15 |

**Goal:** Pin/select history into shared context with hard caps.

**Acceptance criteria:**

- [x] Operator can pin history items into shared context
- [x] Hard caps; secrets never injected
- [x] Architecture updated

**Out of scope:**

- Full vector RAG platform

---

### B37 — Fitness data import lite

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Done — Sprints 14–16 bundle |
| Depends on | B11 |
| Planned sprint | 16 |

**Goal:** Bounded activity import to ground Fitness plans; keep non-medical framing.

**Acceptance criteria:**

- [x] Import path for bounded activity artifact
- [x] Optional use in Fitness Run prompt
- [x] Disclaimer retained; bad file errors clear

**Out of scope:**

- Continuous wearable productization

---

### B38 — Finance CSV import lite

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P2 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B22 |
| Planned sprint | 17 |

**Goal:** Local CSV import for Finance planning summaries — not brokerage or e-file.

**Acceptance criteria:**

- [ ] Bounded CSV import under `data/`
- [ ] Planning Markdown + non-advice disclaimer
- [ ] No bank/broker OAuth; no trading UI

**Out of scope:**

- Tax e-file, bank aggregation SaaS

---

### B39 — Investment watchlist

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P2 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B9 |
| Planned sprint | 18 |

**Goal:** Local watchlist scoping Investment runs; still manual advice only.

**Acceptance criteria:**

- [ ] Edit/save watchlist under `data/`
- [ ] Run can target watchlist within hard caps
- [ ] No order/trade affordances

**Out of scope:**

- Automated trading (Icebox)

---

### B40 — Optional LAN shared-secret gate

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B12 |
| Planned sprint | 19 |

**Goal:** Optional gate when LAN bind is enabled; localhost stays low-friction.

**Acceptance criteria:**

- [ ] Optional shared-secret (or basic gate) when LAN on
- [ ] Trusted-LAN-only without gate remains an explicit choice
- [ ] Documented in README + architecture

**Out of scope:**

- Enterprise SSO, public internet exposure features

---

### B41 — Local backup / export

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B1 |
| Planned sprint | 19 |

**Goal:** Operator-triggered local backup/export of app data with explicit secrets handling.

**Acceptance criteria:**

- [ ] Export archive written locally
- [ ] Secrets include/exclude choice documented
- [ ] No cloud upload

**Out of scope:**

- Remote backup SaaS

---

### B42 — Weekly review composition

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B23, B29 |
| Planned sprint | 20 |

**Goal:** Cross-module Weekly review Markdown the operator will reopen; one composition.

**Acceptance criteria:**

- [ ] Run Weekly review from bounded snapshots/shared context
- [ ] Persist result; home or panel slot
- [ ] Partial/empty honest; no fake data
- [ ] One composition (no widget dump)

**Out of scope:**

- Push digests off-machine

---

### B43 — Shell polish pass

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P2 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B7 |
| Planned sprint | 20 |

**Goal:** Close 11–20 with a short prioritized UX/reliability polish list inside the existing design system.

**Acceptance criteria:**

- [ ] PO polish list recorded in sprint file before implement
- [ ] Fixes use existing theme tokens / patterns
- [ ] No new domain modules in this item

**Out of scope:**

- Full redesign / second UI stack

---


### B44 — Gmail thread digests

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B10, B15 |
| Planned sprint | 22 |

**Goal:** Thread-level Gmail digests (bounded fetch + LLM asks/commitments).

**Acceptance criteria:**

- [ ] Gmail panel lists recent threads (bounded) or accepts a thread id/link from skim
- [ ] Fetch bounded messages in thread → local artifacts
- [ ] LLM Markdown digest: summary, asks, commitments, suggested next action (manual)
- [ ] Job busy/done/error; success snapshot
- [ ] No full-history sync; hard caps on messages/chars

**Out of scope:**

- Automated replies
- Automated trading / order placement (Icebox)

---

### B45 — Investment thesis & research notebook

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B9, B39 |
| Planned sprint | 23 |

**Goal:** Per-symbol/topic notebook and thesis notes seeding Investment LLM runs.

**Acceptance criteria:**

- [ ] Local notebook/thesis store per symbol or topic under data/
- [ ] Panel UX to view/edit notes
- [ ] Run can optionally include notebook slice in prompt (hard-capped)
- [ ] Advice Markdown remains non-order
- [ ] Empty notebook honest

**Out of scope:**

- Brokerage sync
- Automated trading / order placement (Icebox)

---

### B46 — Gmail VIP / local priority rules

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B10 |
| Planned sprint | 24 |

**Goal:** Local VIP/muted sender rules shaping Gmail prioritization.

**Acceptance criteria:**

- [ ] CRUD for local sender rules (VIP / muted / tags)
- [ ] Skim + digest prompts honor rules
- [ ] Clear UI for rules; no silent network calls beyond existing fetch
- [ ] Rules stored under data/; gitignored appropriately

**Out of scope:**

- Google filter sync product
- Automated trading / order placement (Icebox)

---

### B47 — Investment watchlist news clustering

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B39, B9 |
| Planned sprint | 25 |

**Goal:** Cluster watchlist news into cited themes.

**Acceptance criteria:**

- [ ] Bounded fetch across watchlist symbols/topics
- [ ] LLM or heuristic clustering into themes with source lists
- [ ] Panel shows clusters + summary; hard caps preserved
- [ ] No trade buttons; clear empty/error taxonomy

**Out of scope:**

- Streaming quotes product
- Order tickets
- Automated trading / order placement (Icebox)

---

### B48 — Gmail labels confirm-first

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B31, B18 |
| Planned sprint | 26 |

**Goal:** Read labels; confirm-first apply/remove with audit.

**Acceptance criteria:**

- [ ] Read and display labels for messages/threads in panel
- [ ] Propose apply/remove → draft → confirm → execute → audit
- [ ] Reconsent if modify scope missing
- [ ] No bulk silent labeling; no auto-rules engine yet

**Out of scope:**

- Silent auto-label loops
- Automated trading / order placement (Icebox)

---

### B49 — Investment manual holdings journal

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B45, B39 |
| Planned sprint | 27 |

**Goal:** Operator-entered holdings for advice context — not broker truth.

**Acceptance criteria:**

- [ ] Local holdings table/file under data/
- [ ] Panel CRUD; validation for obvious junk rows
- [ ] Optional include in LLM context with hard cap
- [ ] UI states this is operator-entered, not broker-synced
- [ ] No order/rebalance execution

**Out of scope:**

- Brokerage OAuth
- Automated trading / order placement (Icebox)

---

### B50 — Gmail saved searches

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B10 |
| Planned sprint | 28 |

**Goal:** Named Gmail queries + builder for bounded skims.

**Acceptance criteria:**

- [ ] Persist named queries under data/
- [ ] Panel query builder or advanced string field with examples
- [ ] Run bounded fetch for query; job status
- [ ] Invalid query / API errors actionable

**Out of scope:**

- Full offline index (later)
- Automated trading / order placement (Icebox)

---

### B51 — Investment earnings & events skim

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B39 |
| Planned sprint | 28 |

**Goal:** Bounded earnings/events skim for watchlist.

**Acceptance criteria:**

- [ ] Bounded fetch of earnings/event-like sources for watchlist
- [ ] Markdown table/list of upcoming/recent events + LLM wrap
- [ ] Hard caps; cache where sensible
- [ ] Honest empty state when no events found

**Out of scope:**

- Paid data vendor product
- Auto trades
- Automated trading / order placement (Icebox)

---

### B52 — Gmail attachment skim

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B44 |
| Planned sprint | 29 |

**Goal:** Attachment metadata + opt-in bounded text extract for digests.

**Acceptance criteria:**

- [ ] List attachment metadata (name, type, size) for selected message/thread
- [ ] Opt-in text extract for allowlisted types under size cap; store under data/
- [ ] Never auto-exfiltrate; clear skip reasons for unsafe/huge files
- [ ] Optional include snippets in digest prompt

**Out of scope:**

- Arbitrary binary preview
- Automated trading / order placement (Icebox)

---

### B53 — Investment citations & source quality

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B9, B24 |
| Planned sprint | 30 |

**Goal:** Structured citations and domain mute/quality tags.

**Acceptance criteria:**

- [ ] Structured source records in DuckDB/files (url, title, retrieved_at, quality tag)
- [ ] Advice Markdown includes citations section
- [ ] Operator can mute/exclude domains for future runs
- [ ] Document quality rubric simply in architecture or module README

**Out of scope:**

- Paywall bypass product
- Automated trading / order placement (Icebox)

---

### B54 — Gmail follow-up tracker

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B44, B46 |
| Planned sprint | 31 |

**Goal:** Local pin/due follow-ups for threads; boost in skims.

**Acceptance criteria:**

- [ ] Local follow-up records (thread id, note, due optional, status)
- [ ] Panel list + pin from thread digest
- [ ] Optional boost in priority skim
- [ ] No auto-send reminders off-machine

**Out of scope:**

- Off-machine push notifications
- Automated trading / order placement (Icebox)

---

### B55 — Investment scenario & risk check

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B45, B49 |
| Planned sprint | 32 |

**Goal:** Scenario/risk checklist runs from notebook/holdings/watchlist.

**Acceptance criteria:**

- [ ] Scenario Run mode distinct from news skim
- [ ] Prompt template covers risks, invalidation, concentration (if holdings present)
- [ ] Non-advice disclaimer
- [ ] Snapshot for home/history

**Out of scope:**

- VaR product
- Auto hedging
- Automated trading / order placement (Icebox)

---

### B56 — Gmail newsletter digest

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B23, B50 |
| Planned sprint | 33 |

**Goal:** Cluster newsletters/bulk mail into keep/drop digest (manual).

**Acceptance criteria:**

- [ ] Heuristic/LLM clustering of bulk/newsletter-like mail in bounded window
- [ ] Markdown digest per sender/group with keep/unsubscribe/archive suggestions
- [ ] No automatic unsubscribe HTTP calls unless confirm-first in a later story
- [ ] Respect VIP rules (do not treat VIP as bulk)

**Out of scope:**

- Unconfirmed mass unsubscribe
- Automated trading / order placement (Icebox)

---

### B57 — Investment theme/sector baskets

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B39, B47 |
| Planned sprint | 34 |

**Goal:** Named baskets scoping Investment fetches/advice.

**Acceptance criteria:**

- [ ] Local basket CRUD under data/
- [ ] Investment Run target: watchlist | basket | ad-hoc
- [ ] Cluster/advice paths accept basket scope
- [ ] No ETF auto-trading

**Out of scope:**

- Auto-rebalance
- Automated trading / order placement (Icebox)

---

### B58 — Gmail archive/trash batch

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B25, B31 |
| Planned sprint | 35 |

**Goal:** Multi-select confirm-first archive/trash with audit.

**Acceptance criteria:**

- [ ] Multi-select from recent skim/search results
- [ ] Propose archive or trash → confirm → execute → audit
- [ ] Clear irreversible copy for trash
- [ ] Caps on batch size

**Out of scope:**

- Auto-delete without confirm
- Automated trading / order placement (Icebox)

---

### B59 — Investment local alerts

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B39 |
| Planned sprint | 36 |

**Goal:** In-panel/local alerts for watchlist conditions; informational only.

**Acceptance criteria:**

- [ ] Alert rule CRUD (symbol/topic, condition type: keyword / manual threshold note)
- [ ] Evaluation on Run and/or opt-in schedule (reuse job patterns; default off)
- [ ] Triggered alerts list in Investment panel; optional home chip
- [ ] Explicit: alerts are informational; no trades

**Out of scope:**

- SMS push
- Automated trading / order placement (Icebox)

---

### B60 — Gmail people context

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B46, B44 |
| Planned sprint | 37 |

**Goal:** Frequent contacts + notes to improve digests/priority.

**Acceptance criteria:**

- [ ] Derive frequent contacts from bounded recent mail (local)
- [ ] Operator notes per person; VIP link to rules
- [ ] Optional inject into thread digest / priority skim (capped)
- [ ] No CRM multi-user features

**Out of scope:**

- Full CRM
- Automated trading / order placement (Icebox)

---

### B61 — Investment comparative analysis

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B45, B53 |
| Planned sprint | 38 |

**Goal:** A vs B bounded compare with citations.

**Acceptance criteria:**

- [ ] UI to select two scopes (symbol/topic/basket)
- [ ] Bounded dual fetch + comparison Markdown template
- [ ] Citations/source quality reused
- [ ] No winner-as-order framing; manual decision copy

**Out of scope:**

- Pair-trade execution
- Automated trading / order placement (Icebox)

---

### B62 — Email × Investment bridge

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B49, B39, B54 |
| Planned sprint | 39 |

**Goal:** Mail mentions of holdings/watchlist → bridge digest + deep links.

**Acceptance criteria:**

- [ ] Bounded scan: match sender/subject/body keywords to holdings/watchlist symbols
- [ ] Bridge results Markdown + deep links
- [ ] False-positive controls (min token length, allowlist tickers)
- [ ] No auto-trading; no auto-send
- [ ] Architecture note on matching approach

**Out of scope:**

- Broker statement as only source
- Auto trades
- Automated trading / order placement (Icebox)

---

### B63 — Gmail & Investment operator playbooks

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P1 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B50, B39, B45 |
| Planned sprint | 40 |

**Goal:** Named playbooks binding module + scope + prompt for one-click deep runs.

**Acceptance criteria:**

- [ ] Named playbooks binding module + query/watchlist/basket + prompt template
- [ ] One-click Run from Gmail/Investment or Settings
- [ ] Playbooks stored locally; exportable with backup patterns if present

**Out of scope:**

- New domain modules
- Automated trading

---

### B64 — Gmail + Investment depth polish

| Field | Value |
|-------|-------|
| Status | shelved |
| Priority | P2 |
| Roadmap theme | Shelved (after Sprint 10; deferred for Sender Inbox + ASX pivot) |
| Depends on | B63 |
| Planned sprint | 40 |

**Goal:** PO-prioritized polish/reliability pass on deep email/investment surfaces.

**Acceptance criteria:**

- [ ] PO polish list for Gmail+Investment (errors, density, caps, empty states) recorded in sprint file
- [ ] Address list within theme tokens
- [ ] Update architecture module maps for deep email/investment surfaces

**Out of scope:**

- Full redesign
- Icebox items

---

## Active pivot backlog (Sprints 11–20)

### B65 — UX: Sender Inbox + ASX dashboards

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B7 |
| Planned sprint | 12 |

**Goal:** UX expert design contract for Sender-grouped Inbox and ASX research desk (profiles, recommendations, paper portfolio pages) before implementation.

**Acceptance criteria:**

- [x] `docs/ux/sender-inbox-asx.md` covers IA, layouts, states for Sender Inbox + ASX desk + recommendations + paper portfolio
- [x] Integrated into `docs/ux.md` (pointers / summary)
- [x] Uses existing theme tokens; one composition; implementable for HTMX/Jinja
- [x] Stakeholder confirmed or accepted as draft-for-implement

**Out of scope:**

- Implementing Python modules
- Expanding into shelved sprint scope

**Reference patterns:** people-centric inboxes (ChatInbox, Talanoa, Shortwave bundles); ASX research desks (company profiles / scanners akin to ASX Desk, Morningstar-style profile clarity, Sharesight-like portfolio readability for paper mode).

---

### B66 — Background email ingest + LLM categorization

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B5, B10, B65 |
| Planned sprint | 12 |

**Goal:** Polite background process pulls **one email at a time** and LLM-categorizes each on a useful metric schema.

**Acceptance criteria:**

- [x] One-at-a-time ingest with visible progress
- [x] Persisted category metrics per message (schema documented)
- [x] Isolated errors; uses existing Gmail read auth
- [x] No Gmail write-back required

**Out of scope:**

- Full-history sync; multi-account

---

### B67 — Sender-grouped Inbox view

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B66, B65 |
| Planned sprint | 12 |

**Goal:** Default Inbox UI grouped by **sender**, not a chronological stream.

**Acceptance criteria:**

- [x] Sender list as primary surface per UX
- [x] Drill-in to sender’s ingested messages
- [x] Metric chips / counts; theme tokens

**Out of scope:**

- Native mobile app; multi-user shared inbox

---

### B68 — LLM sender profiles

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B67 |
| Planned sprint | 12 |

**Goal:** Per-sender LLM profile describing interaction history from ingested mail.

**Acceptance criteria:**

- [x] Profile generated/updated from sender bundle
- [x] Persisted; shown on sender detail
- [x] Empty/low-data honest state

**Out of scope:**

- CRM multi-user; LinkedIn scraping

---

### B69 — Actionable todos from email bundles

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B68 |
| Planned sprint | 12 |

**Goal:** Extract actionable todos from each sender’s ingested emails; local open/done.

**Acceptance criteria:**

- [x] Todos extracted via LLM from sender bundle
- [x] List + open/done toggle locally
- [x] No auto-send / auto-calendar

**Out of scope:**

- Push notifications off-machine

---

### B70 — Sender Inbox PoC cap (~20 emails)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B66 |
| Planned sprint | 12 |

**Goal:** Hard PoC bound of ~20 ingested emails with clear UI and reset path.

**Acceptance criteria:**

- [x] Cap enforced (~20)
- [x] Progress/remaining visible; reset documented
- [x] Path to raise cap later documented

**Out of scope:**

- Production-scale mailbox indexing

---

### B71 — ASX company universe list

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B65 |
| Planned sprint | 13 |

**Goal:** Ship a large curated ASX company list; PoC processes a 20-company slice.

**Acceptance criteria:**

- [x] Large list in `data/` with provenance documented
- [x] Selectable PoC set of 20
- [x] Surfaced in ASX desk UI

**Out of scope:**

- Global equities coverage

---

### B72 — Background ASX scanner

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B71 |
| Planned sprint | 13 |

**Goal:** Slow background process scans price movement, market data, and news/sentiment per company.

**Acceptance criteria:**

- [x] One-company-at-a-time (or similarly polite) cadence
- [x] Bounded fetches; progress UI; pause/resume
- [x] Artifacts under `data/`; rate limits respected

**Out of scope:**

- Paid terminal data contracts without ADR

---

### B73 — ASX company profiles (pro-investor style)

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B72, B74 |
| Planned sprint | 13 |

**Goal:** LLM/hybrid profile per company collating scan data + sentiment using metrics/sources favored by professional investors (as available from free/bounded sources).

**Acceptance criteria:**

- [x] Profile view per UX with metrics + narrative + sentiment
- [x] Metric/source rubric documented; gaps called out honestly
- [x] Non-advice disclaimer
- [x] Regenerable after new scans

**Out of scope:**

- Licensed research product claims
- Live trading

**Reference patterns:** company-profile clarity (Morningstar / Simply Wall St / ASX Desk–style overviews) without cloning proprietary scores.

---

### B74 — Investment sources registry + prompt library

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Next — Pivot |
| Depends on | B9 |
| Planned sprint | 13 |

**Goal:** Configurable source list and prompt templates for ASX scan/profile/sentiment.

**Acceptance criteria:**

- [x] Source registry with enable flags + documented defaults
- [x] Prompt templates editable (scan / profile / sentiment / recommendations)
- [x] Architecture notes scan vs curated-source modes
- [x] Avoid TOS-hostile scraping targets

**Out of scope:**

- Bundling proprietary paid feeds in-repo

---

### B75 — Structured ASX actionable recommendations

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Done — Pivot |
| Depends on | B73 |
| Planned sprint | 14 (current) |

**Goal:** Structured list of actionable recommendations generated from company profiles.

**Acceptance criteria:**

- [x] Structured rows (ticker, action, rationale, links, timestamps)
- [x] Regenerable from PoC set
- [x] Non-advice disclaimer; UX list layout

**Out of scope:**

- Auto-routing orders to a broker

---

### B76 — Simulated (paper) portfolio tracker

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Done — Pivot |
| Depends on | B75 |
| Planned sprint | 14 (current) |

**Goal:** Separate page tracking a **paper** portfolio of trades from recommendations (or manual), marked-to-market from scan prices.

**Acceptance criteria:**

- [x] Separate portfolio surface per UX
- [x] Open paper positions from recommendations; local ledger
- [x] Simple P&L / cash using latest scanned prices
- [x] **No brokerage order API calls**

**Out of scope:**

- Live automated trading (Icebox)
- Full CGT/tax engine (Sharesight-class) in PoC

**Reference patterns:** portfolio readability inspired by Sharesight-style tracking — simulation only.

---

### B77 — Brokerage / simulation settings

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B76 |
| Planned sprint | 14 (current) |

**Goal:** Settings for paper trading assumptions (cash, fees, AUD, cosmetic broker label).

**Acceptance criteria:**

- [x] Settings persisted locally; applied to simulation math
- [x] Documented that settings never enable live trading
- [x] Clear UI copy

**Out of scope:**

- Real broker OAuth

---

### B78 — Settings Update: git pull + hot reload

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P0 |
| Roadmap theme | Next — Pivot |
| Depends on | B1 |
| Sprint | 11 |

**Goal:** From the dashboard (Settings → **Update**), pull the latest application code from git and confirm the running process **hot-reloads** when reload is enabled — so the operator can update Crawley without a manual terminal dance.

**Acceptance criteria:**

- [x] Settings → **Update** section (or equally obvious dashboard control) with **Pull latest**
- [x] Runs git pull (or fetch + ff-only merge) on the app checkout; UI shows success / up-to-date / error
- [x] Documents and/or enables `CRAWLEY_RELOAD=1` (uvicorn reload on `src/crawley/` changes) as the supported path
- [x] Demonstrates/tests that a pull changing watched files triggers reload (automated test preferred)
- [x] Localhost-minded safety (disable or strong warn when LAN bind); no secret leakage in UI logs
- [x] Architecture + README note; no scheduled auto-pull

**Out of scope:**

- Cloud deploy, CI triggers, conflict resolution UI
- Pulling unrelated repos

---


### B79 — Sender Inbox raised cap & retention

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B70 |
| Planned sprint | 15 |

**Goal:** Raise the ~20 email PoC cap with documented retention/prune so Sender Inbox remains operable at modest scale.

**Acceptance criteria:**

- [x] Configurable or raised ingest cap with clear UI of progress/remaining
- [x] Retention/prune policy documented and enforced (oldest or reset path)
- [x] Architecture note on scale bounds; still not full-mailbox product

**Out of scope:**

- Full-history Gmail sync; multi-account

---

### B80 — Sender Inbox search & filter

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B67, B69 |
| Planned sprint | 15 |

**Goal:** Local search/filter across senders, categories, and todos without a second UI stack.

**Acceptance criteria:**

- [x] Filter/search by sender, category metric, and/or todo open/done
- [x] Results stay within Sender Inbox IA (list → detail)
- [x] Empty filter state honest; theme tokens

**Out of scope:**

- Full-text Gmail offline index product; CRM export

---

### B81 — ASX desk scale beyond PoC slice

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B71, B72, B73 |
| Planned sprint | 16 |

**Goal:** Expand scanning/profiles beyond the 20-company PoC with operator-controlled set size and polite cadence.

**Acceptance criteria:**

- [x] Operator can expand/select active universe beyond 20 within hard max
- [x] Scanner/profile jobs remain one-at-a-time (or equally polite); progress clear
- [x] Caps and rate-limit posture documented

**Out of scope:**

- Global equities; paid terminal contracts without ADR

---

### B82 — ASX earnings & events skim

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B73, B74 |
| Planned sprint | 16 |

**Goal:** Bounded earnings/events skim for the active ASX set — calendar of catalysts, not auto trades.

**Acceptance criteria:**

- [x] Bounded fetch of earnings/event-like sources for active set
- [x] Markdown/list of upcoming/recent events + optional LLM wrap
- [x] Hard caps; honest empty; non-advice disclaimer

**Out of scope:**

- Paid data vendor product; auto trades (Icebox)

---

### B83 — Email × ASX bridge

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B67, B73, B76 |
| Planned sprint | 17 |

**Goal:** Surface when Sender Inbox / mail mentions tickers or companies in the ASX desk or paper book — bridge digest + deep links.

**Acceptance criteria:**

- [x] Bounded match of sender/subject/body (or categories) to ASX tickers / paper holdings
- [x] Bridge results with deep links to Sender + ASX profile / paper position
- [x] False-positive controls; no auto-trading or auto-send
- [x] Architecture note on matching approach

**Out of scope:**

- Broker statement as sole source; CRM enrichment

---

### B84 — Gmail confirm-first send

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B15, B18, B25 |
| Planned sprint | 18 |

**Goal:** First Gmail mutation: propose draft reply/compose → confirm → send → audit (ADR-006). Complements Sender Inbox todos that need a real reply.

**Acceptance criteria:**

- [x] Propose draft from operator input and/or LLM suggestion (e.g. from sender todo)
- [x] Confirm required; cancel leaves no remote send
- [x] On confirm: Gmail send with write scope; reconsent if needed
- [x] Local audit entry; success/failure clear
- [x] No silent/scheduled send

**Out of scope:**

- Bulk send; auto-reply loops; labels mutation (shelved B48)

---

### B85 — ASX local alerts

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B72, B76 |
| Planned sprint | 19 |

**Goal:** In-app/local alerts for ASX desk or paper book conditions — informational only.

**Acceptance criteria:**

- [x] Alert rule CRUD (ticker/topic, condition type: keyword / threshold note / paper P&L note)
- [x] Evaluation on scan/recommend and/or opt-in schedule (default off)
- [x] Triggered alerts list on ASX desk; optional home chip
- [x] Explicit: informational; no trades

**Out of scope:**

- SMS/email push off-machine; live brokerage orders

---

### B86 — Recommendation feedback loop

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Done — Pivot |
| Depends on | B75, B76 |
| Planned sprint | 19 |

**Goal:** Operator can mark recommendations acted / dismissed / watched so later runs can bias (soft) without inventing fake P&L.

**Acceptance criteria:**

- [x] Per-recommendation disposition persisted locally
- [x] Regenerated lists respect dispositions (hide dismissed or section them)
- [x] Optional note field; architecture note on feedback use in prompts (capped)

**Out of scope:**

- ML ranking product; broker sync of fills

---

### B87 — Dual-desk operator playbooks

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P1 |
| Roadmap theme | Done — Pivot |
| Depends on | B67, B75, B76 |
| Planned sprint | 20 |

**Goal:** Named playbooks binding Sender Inbox and/or ASX desk scopes + prompts for one-click deep runs.

**Acceptance criteria:**

- [x] Named playbooks (module + scope + prompt template) stored locally
- [x] One-click Run from Sender Inbox / ASX / Settings
- [x] Exportable with local backup patterns if present

**Out of scope:**

- New life-domain modules; automated trading

---

### B88 — Dual-desk polish & reliability

| Field | Value |
|-------|-------|
| Status | done |
| Priority | P2 |
| Roadmap theme | Done — Pivot |
| Depends on | B87 |
| Planned sprint | 20 |

**Goal:** PO-prioritized polish/reliability pass on Sender Inbox + ASX + paper surfaces.

**Acceptance criteria:**

- [x] PO polish list recorded in sprint file before implement
- [x] Address list within theme tokens; no second UI stack
- [x] Architecture module maps updated for dual-desk surfaces

**Out of scope:**

- Full redesign; Icebox items

---


### B89 — Tailscale / LAN Google first-Connect ergonomics

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B15, B12 |
| Planned sprint | 21 (current) |

**Goal:** Operator can complete **first Connect Google** from a Tailscale or trusted LAN client without guessing redirect URIs — UI + docs make the exact callback URL obvious.

**Acceptance criteria:**

- [ ] Connect / Google auth UI shows the exact OAuth redirect URI for the current request Host (copyable) when on a trusted personal host
- [ ] README documents Tailscale/LAN Connect steps, same-environment Tailscale tip, and token reuse on one server across clients
- [ ] Localhost Connect path unchanged
- [ ] Test covers redirect URI construction for Tailscale-like Host (or trusted-host helper)

**Out of scope:**

- Public internet OAuth / SaaS multi-tenant auth
- Per-browser Google sessions (token remains server-side)

---

### B90 — Softer Google OAuth consent prompts

| Field | Value |
|-------|-------|
| Status | ready |
| Priority | P1 |
| Roadmap theme | Next — Depth 21–30 |
| Depends on | B15 |
| Planned sprint | 21 (current) |

**Goal:** Stop forcing Google’s full consent screen on every Connect/Reconnect; only force when a refresh token is missing or new scopes are requested. Document Google Testing-mode refresh expiry as the usual “weekly re-auth” cause.

**Acceptance criteria:**

- [ ] `authorization_url` does not always pass `prompt=consent`; force consent only when refresh token missing or requesting scopes not already granted
- [ ] `access_type=offline` retained for refresh tokens on first grant
- [ ] Auto-refresh via `load_credentials` unchanged for normal API use
- [ ] README notes Testing (~7-day refresh) vs Production publishing status
- [ ] Tests cover consent-forced vs consent-optional paths

**Out of scope:**

- Changing Google Cloud app verification / Production publishing for the stakeholder (docs only)
- Multi-account Google

---

<!-- Add new items above this line. Planned sprints: docs/sprints/planned/ -->
