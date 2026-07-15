# Sprint 2 — Themes, settings, Markdown & home glance

**Duration:** one symbolic week  
**Backlog refs:** B7, B8, B13, B14  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX contract:** [`docs/ux.md`](../ux.md) (Confirmed — Sprint 2 design; home glance = PO add)  
**Previous:** [`archive/sprint-1-local-shell.md`](archive/sprint-1-local-shell.md)

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
| Status | todo |
| Backlog ref | B7 |
| Depends on | Sprint 1 shell; `docs/ux.md` |

**Acceptance criteria:**

- [ ] Theme tokens from `docs/ux.md` (core + extensions) live in one place; panels consume tokens only (no hex in partials)
- [ ] Four themes: `paper`, `slate`, `ink`, `moss` via `data-theme` on `<html>` (or body); default `paper`
- [ ] Settings → **Appearance** theme picker; apply **immediately** (no Save); selection persists locally
- [ ] Stub / Coming soon, banner, jobs use tokenized colors; quiet stub treatment per UX
- [ ] Styling approach recorded in `docs/architecture.md` (custom CSS themes; no Node build this sprint)
- [ ] `prefers-reduced-motion` respected for theme transitions

**Out of scope:**

- Full brand/marketing site, native desktop chrome
- Node/Tailwind build
- Per-module accent colors / custom theme editor

---

### S2.2 — LLM settings & connection test (B8)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B8 |
| Depends on | S2.1 (Settings chrome); B3 done |

**Acceptance criteria:**

- [ ] **Settings** nav footer entry (+ unhealthy LLM banner deep-link to Settings LLM section)
- [ ] Language model section: provider (OpenAI ready; LocalLlama placeholder not operable), model, API key (password field; blank = keep existing)
- [ ] **Save settings** persists locally/gitignored; precedence vs `.env` documented
- [ ] **Test connection** with success / failure / missing-key UI states per `docs/ux.md` F3
- [ ] Modules use configured settings after save (hot-reload vs restart documented in README or architecture)
- [ ] Missing/invalid key still surfaces clearly on banner (Sprint 1 parity)

**Out of scope:**

- Multi-user profiles, LocalLlama install/ops, billing UI
- Temperature / max tokens / Google credentials in Settings
- Redesigning Investment/Gmail domain fetch logic (B9–B10)

---

### S2.3 — Markdown rendering for panel summaries (B13)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B13 |
| Depends on | S2.1 recommended (summary styles use theme tokens) |

**Acceptance criteria:**

- [ ] Investment and Gmail job summaries render as **HTML from Markdown** in the panel (not `<pre>` plain text)
- [ ] Safe rendering: no raw script execution from model output (escape / sanitize / trusted Markdown subset — architect chooses a Python-side library; no Node)
- [ ] Basic Markdown supported at minimum: headings, paragraphs, bold/italic, lists, links (links open safely — e.g. `target`/`rel` sensible for localhost app)
- [ ] Summary typography uses theme tokens (`--ink`, `--muted`, `--font-sans`, spacing); readable under all four themes
- [ ] Empty / error job states unchanged (no fake Markdown success)
- [ ] Brief note in `docs/architecture.md` (library + sanitize approach)

**Out of scope:**

- Full CommonMark/GFM edge cases, mermaid, KaTeX, user-authored wiki
- Editing Markdown in the UI
- Replacing Coming soon copy with MD documents

---

### S2.4 — Dashboard home At a glance (B14)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B14 |
| Depends on | S2.3 (reuse Markdown renderer); S2.2 optional for LLM chip accuracy |

**Why this feature (ROI):** Sprint 1 home is a one-line empty state — weak against the “habit / pull” success metric. Persisted last summaries + status chips reuse S2.3 Markdown and existing module state with little new domain logic, and give a daily reopen reason without scheduling or a second UI stack.

**Acceptance criteria:**

- [ ] `/` (Dashboard) shows one **At a glance** composition (not a widget dump):
  - **Status row:** LLM readiness (short); Gmail connected / not connected / needs setup; theme name optional
  - **Last Investment:** timestamp + Markdown body of last **successful** run, or empty hint + link to Investment
  - **Last Gmail:** timestamp + Markdown body of last **successful** run, or empty hint + link to Gmail
  - Deep links: open Investment, Gmail, Settings (LLM) as appropriate
- [ ] Last successful summaries **persist under gitignored `data/`** and survive process restart (JSON file or DuckDB table — architect chooses; document in architecture)
- [ ] On successful Investment / Gmail job completion, home snapshot updates (same store)
- [ ] Errors / busy runs do **not** overwrite last successful snapshot
- [ ] Stub modules never appear as fake “last run” cards; no inventing demo content
- [ ] Layout uses theme tokens; one panel or two clear sections max — brand + glance stays primary (align with UX “one composition”)
- [ ] Truncate or collapse very long bodies on home if needed (e.g. CSS max-height + “Open module for full”) — full text remains on module panel

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

- Calendar real fetch (B6 later / B10)
- Harden investment or Gmail depth (B9–B10)
- Fitness beyond stub (B11)
- Phone-on-LAN (B12)
- Write-back, local LLM ops, automated trading

## Parking lot

- Settings sections for Google OAuth / module credentials later
- `prefers-color-scheme` auto theme default when no saved choice
- Streaming Markdown polish if responses become long
- UX pass polish for `.summary` MD + home glance densify after S2.4 lands
- Snapshot retention / prune of older runs (not required until history exists)
