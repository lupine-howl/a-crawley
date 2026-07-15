# Sprint 2 — Themes, settings, Markdown & home glance

**Status:** closed (archived)  
**Duration:** one symbolic week  
**Backlog refs:** B7, B8, B13, B14  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX contract:** [`docs/ux.md`](../ux.md) (Confirmed — Sprint 2 design; home glance = PO add)  
**Previous:** [`sprint-1-local-shell.md`](sprint-1-local-shell.md)

## Goal

Make the local dashboard feel intentional and worth reopening: **themable palette**, **LLM settings** + **Test connection**, **Markdown-rendered** summaries, and a **home At a glance** that shows persisted last Investment/Gmail results with status chips — not an empty “pick a module” stub.

## Demo (definition of done for the sprint)

Operator can:

1. Switch among Paper / Slate / Ink / Moss themes from Settings → Appearance; choice applies immediately and persists across reload
2. Open Settings, configure LLM (provider / model / key), Save locally
3. Run **Test connection** and see clear success, failure, or missing-key results
4. Run Investment or Gmail summary and see the result as **formatted Markdown** in the module panel
5. On **/ (Dashboard)**, see **At a glance**: LLM readiness, Gmail auth state, and last successful Investment + Gmail summary snippets (Markdown), with deep links into each module / Settings
6. Restart the app and still see those last summaries on home (persisted under `data/`)
7. Coming soon stubs still quiet and thematic

## Committed

Implement **in order** (S2.1 → S2.2 → S2.3 → S2.4) unless dependencies already satisfied. Treat `docs/ux.md` as the design contract for S2.1–S2.2; S2.3–S2.4 follow AC below.

### S2.1 — Themable UI & design polish (B7)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B7 |
| Depends on | Sprint 1 shell; `docs/ux.md` |

**Acceptance criteria:**

- [x] Theme tokens from `docs/ux.md` (core + extensions) live in one place; panels consume tokens only (no hex in partials)
- [x] Four themes: `paper`, `slate`, `ink`, `moss` via `data-theme` on `<html>` (or body); default `paper`
- [x] Settings → **Appearance** theme picker; apply **immediately** (no Save); selection persists locally
- [x] Stub / Coming soon, banner, jobs use tokenized colors; quiet stub treatment per UX
- [x] Styling approach recorded in `docs/architecture.md` (custom CSS themes; no Node build this sprint)
- [x] `prefers-reduced-motion` respected for theme transitions

**Out of scope:**

- Full brand/marketing site, native desktop chrome
- Node/Tailwind build
- Per-module accent colors / custom theme editor

---

### S2.2 — LLM settings & connection test (B8)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B8 |
| Depends on | S2.1 (Settings chrome); B3 done |

**Acceptance criteria:**

- [x] **Settings** nav footer entry (+ unhealthy LLM banner deep-link to Settings LLM section)
- [x] Language model section: provider (OpenAI ready; LocalLlama placeholder not operable), model, API key (password field; blank = keep existing)
- [x] **Save settings** persists locally/gitignored; precedence vs `.env` documented
- [x] **Test connection** with success / failure / missing-key UI states per `docs/ux.md` F3
- [x] Modules use configured settings after save (hot-reload vs restart documented in README or architecture)
- [x] Missing/invalid key still surfaces clearly on banner (Sprint 1 parity)

**Out of scope:**

- Multi-user profiles, LocalLlama install/ops, billing UI
- Temperature / max tokens / Google credentials in Settings
- Redesigning Investment/Gmail domain fetch logic (B9–B10)

---

### S2.3 — Markdown rendering for panel summaries (B13)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B13 |
| Depends on | S2.1 recommended (summary styles use theme tokens) |

**Acceptance criteria:**

- [x] Investment and Gmail job summaries render as **HTML from Markdown** in the panel (not `<pre>` plain text)
- [x] Safe rendering: no raw script execution from model output (escape / sanitize / trusted Markdown subset — architect chooses a Python-side library; no Node)
- [x] Basic Markdown supported at minimum: headings, paragraphs, bold/italic, lists, links (links open safely — e.g. `target`/`rel` sensible for localhost app)
- [x] Summary typography uses theme tokens (`--ink`, `--muted`, `--font-sans`, spacing); readable under all four themes
- [x] Empty / error job states unchanged (no fake Markdown success)
- [x] Brief note in `docs/architecture.md` (library + sanitize approach)

**Out of scope:**

- Full CommonMark/GFM edge cases, mermaid, KaTeX, user-authored wiki
- Editing Markdown in the UI
- Replacing Coming soon copy with MD documents

---

### S2.4 — Dashboard home At a glance (B14)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B14 |
| Depends on | S2.3 (reuse Markdown renderer); S2.2 optional for LLM chip accuracy |

**Why this feature (ROI):** Sprint 1 home is a one-line empty state — weak against the “habit / pull” success metric. Persisted last summaries + status chips reuse S2.3 Markdown and existing module state with little new domain logic, and give a daily reopen reason without scheduling or a second UI stack.

**Acceptance criteria:**

- [x] `/` (Dashboard) shows one **At a glance** composition (not a widget dump):
  - **Status row:** LLM readiness (short); Gmail connected / not connected / needs setup; theme name optional
  - **Last Investment:** timestamp + Markdown body of last **successful** run, or empty hint + link to Investment
  - **Last Gmail:** timestamp + Markdown body of last **successful** run, or empty hint + link to Gmail
  - Deep links: open Investment, Gmail, Settings (LLM) as appropriate
- [x] Last successful summaries **persist under gitignored `data/`** and survive process restart (JSON file or DuckDB table — architect chooses; document in architecture)
- [x] On successful Investment / Gmail job completion, home snapshot updates (same store)
- [x] Errors / busy runs do **not** overwrite last successful snapshot
- [x] Stub modules never appear as fake “last run” cards; no inventing demo content
- [x] Layout uses theme tokens; one panel or two clear sections max — brand + glance stays primary (align with UX “one composition”)
- [x] Truncate or collapse very long bodies on home if needed (e.g. CSS max-height + “Open module for full”) — full text remains on module panel

**Implementation notes (architect):**

1. Add something like `crawley/data/snapshots.py` (or DuckDB `module_snapshots`) with `{module_id, summary_md, updated_at, status}`.
2. Call `save_snapshot` from Investment/Gmail success paths only.
3. Dashboard context loads snapshots + `llm_status()` + Gmail auth probe (reuse existing gmail helpers; don’t start OAuth from home).
4. Reuse the S2.3 `render_markdown()` helper for snippet HTML; mark safe with same sanitize policy.
5. Tests: success persists; error does not clobber; home renders empty hints; restart simulation via reload from store.

**Out of scope:**

- History list / timeline of all past runs
- Scheduled/automatic refresh of Investment or Gmail from home
- Multi-module “Run all”
- Analytics charts or portfolio widgets

## Explicitly out of sprint

- Calendar / shared Google / Gmail harden → **Sprint 3** ([planned](planned/sprint-3.md))
- Investment depth / Fitness lite → **Sprint 4** ([planned](planned/sprint-4.md))
- Phone-on-LAN / Work / write-back design → **Sprint 5** ([planned](planned/sprint-5.md))
- Write-back mutations, local LLM ops, automated trading → Later / Icebox

## Parking lot

- Settings sections for Google OAuth / module credentials later (Sprint 3 touches connect state lightly)
- `prefers-color-scheme` auto theme default when no saved choice
- Streaming Markdown polish if responses become long
- UX pass polish for `.summary` MD + home glance densify after S2.4 lands
- Snapshot retention / prune of older runs (not required until history exists)
- Prompt history / A-B testing beyond editable templates + last-run introspection (Sprint 2 operator ask)
- Full planned index: [`planned/README.md`](planned/README.md)
