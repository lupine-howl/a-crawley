# UX contract — Sender Inbox + ASX desk

**Status:** Draft for implement (2026-07-15)  
**Owner:** UX expert  
**Sprint gate:** S6.0 / B65 — architects implement Sender Inbox (S6.1+) and ASX surfaces (S7–S8) against this file  
**Shell:** FastAPI + Jinja2 + HTMX; themes `paper` / `slate` / `ink` / `moss` per [`docs/ux.md`](../ux.md)  
**Parent contract:** [`docs/ux.md`](../ux.md)

Stakeholder intents for this pass were confirmed via the PO pivot brief. This document is **implementable without further UX interview** unless a story blocks on an open assumption (listed below).

---

## 1. Design direction

Two operator desks inside the existing Crawley chrome — not marketing pages, not card dashboards.

| Desk | Module home | Metaphor | Default unit |
|------|-------------|----------|--------------|
| **Sender Inbox** | Gmail (nav label may stay **Gmail** or become **Inbox** — architect choice; panel title **Sender Inbox**) | People-centric mail desk (ChatInbox / Talanoa spirit; Shortwave-style bundling by person) | **Sender** |
| **ASX desk** | Investment | Research desk (ASX Desk / Morningstar-like profile clarity) + simulation ledger (Sharesight-like readability, paper only) | **Company (ticker)** |

**Shared visual rules**

1. One composition per first viewport: title + one sentence + primary control/progress + the list or profile body. No stats strips, promo chips, or multi-widget hero.
2. Brand stays in sidebar chrome; panel `h1` is secondary to **Crawley**.
3. No decorative card soup. Allowed containers: the existing `.panel` framing interactive work; list rows; section regions separated by hairlines / heading rhythm.
4. Tokens only — no hex in module partials. Extend tokens listed in §8 if needed.
5. Honest PoC caps (~20 emails / ~20 companies) are always visible, never hidden behind success theater.
6. Disclaimers for investment are quiet, durable footers — not floating badges on media.

---

## 2. Information architecture (shell)

Topology unchanged: sidebar brand + modules + Settings; main = banner + panel.

### 2.1 Nav

| Nav entry | Live surfaces (pivot) |
|-----------|------------------------|
| **Gmail** | Sender Inbox list → sender detail; ingest progress; legacy skim/run may remain as a secondary control or collapse under a disclosure until removed — **do not** make chronological stream the default |
| **Investment** | ASX desk (universe + scanner) → company profile; sub-routes for **Recommendations** and **Paper portfolio** (Sprint 8) |
| Other modules | Unchanged |

**Investment sub-nav** (secondary strip under panel title — text links or quiet segmented control, not pill clusters):

```
Desk  ·  Recommendations  ·  Paper portfolio
```

- Active segment uses existing active-nav contrast pattern adapted to inline links (`--ink` weight / underline or `--nav-active-*` on a compact control).
- **Desk** is the default Investment landing (Sprint 7+).
- Legacy Investment “run search / summary” PoC may live as a disclosure on Desk (“Classic search”) — not competing for first viewport.

**Gmail sub-nav** (optional, Sprint 6):

```
Senders  ·  (optional) Classic summary
```

Default = **Senders**. Chronological flood is never the primary.

### 2.2 Routes (suggested — architect owns final paths)

| Surface | Suggested path |
|---------|----------------|
| Sender list | `/modules/gmail` or `/modules/gmail/inbox` |
| Sender detail | `/modules/gmail/senders/{id}` |
| Ingest progress partial | HTMX fragment on list (poll while busy) |
| ASX desk | `/modules/investment` or `/modules/investment/asx` |
| Company profile | `/modules/investment/companies/{ticker}` |
| Recommendations | `/modules/investment/recommendations` |
| Paper portfolio | `/modules/investment/portfolio` |
| Simulation settings | Settings section **Paper portfolio** and/or deep-link from portfolio page |

---

## 3. Sender Inbox

### 3.1 First viewport — sender list

**Job:** See who matters in the PoC bundle; start/watch ingest; open a person.

```
┌─────────────────────────────────────────────────────────────┐
│ Sender Inbox                                                │
│ People in your PoC bundle — grouped by sender, not by time. │
│                                                             │
│ [Start ingest]  Ingesting 7 / 20 · pause available          │
│ ─────────────────────────────────────────────────────────── │
│ Sender                          Mail  Latest     Signal     │
│ Jane Client <jane@…>              3   2h ago     reply · !  │
│ Billing Bot <noreply@…>           2   1d ago     action     │
│ …                                                           │
└─────────────────────────────────────────────────────────────┘
```

**Hierarchy**

| Element | Treatment |
|---------|-----------|
| `h1` | Sender Inbox — `--font-display` |
| One muted sentence | Explains people-first grouping + PoC cap |
| Progress / actions row | Primary: Start / Resume / Pause; status text uses `.job-busy` / `.job-done` / `.job-error` |
| Sender table or stacked rows | Primary content — **not** cards; hairline separators or compact table |

**Sender row (required columns / fields)**

| Field | Notes |
|-------|-------|
| Display name + email | Name emphasized; address muted if name present |
| Message count | Count in PoC bundle for this sender |
| Latest activity | Relative or short datetime of newest ingested message |
| Signal chips | Max **2–3** muted text chips from LLM categories (e.g. `reply`, `urgent`, `vip`) — not rainbow pills; use `--muted` border or typographic weight. Skip chips when all quiet. |
| Open todos (optional) | Small count if >0 open todos for that sender |

Row is a single interactive target (link/button) to sender detail. Keyboard-focusable.

**Sort (PoC default):** Most recent activity first; optional secondary boost for `urgent` / `requires_reply` (architect may weight — document in architecture). No filter chrome in first viewport beyond what’s needed for empty/progress.

### 3.2 Ingest progress

Background worker: **one email at a time**, hard stop ~20.

| State | UI |
|-------|-----|
| **Idle, 0 processed** | Primary **Start ingest**; copy: “Processes one message at a time · stops at ~20.” |
| **Busy** | Progress `processed / cap` (e.g. `7 / 20`); current subject/from one-liner (truncated/muted); **Pause**; HTMX poll (~1–2s) of progress region |
| **Paused** | Same counts; **Resume**; reason if paused at cap |
| **Done (cap)** | `.job-done`: “PoC cap reached (20). Reset in Settings or below to re-run.” |
| **Error (one message)** | `.job-error` for that message; worker continues; list still usable |
| **Worker dead / hard fail** | `.job-error` + Retry; do not fake done |

**Capacity / reset:** Visible remaining capacity (`13 left`). Dev-friendly **Reset PoC data** (secondary/warn-styled outline) clears ingested categories/profiles/todos for the PoC — confirm via simple confirm dialog or typed confirm only if architect prefers; PoC may use `confirm()` — label honestly.

**Motion (one of the 2–3 pass moments):** Progress count updates without full-page flash; prefer HTMX swap of a `#ingest-progress` fragment. No perpetual pulse.

### 3.3 Sender detail

**Job:** Understand the relationship, act on todos, skim the bundle.

```
┌─────────────────────────────────────────────────────────────┐
│ ← Senders                                                   │
│ Jane Client                                                 │
│ jane@example.com · 3 messages in PoC                        │
│                                                             │
│ Profile                                                     │
│ [LLM Markdown: relationship, topics, open loops]            │
│                                                             │
│ Todos                                        2 open         │
│ ☐ Reply with revised quote (from “Re: Proposal”)            │
│ ☐ Send calendar holds for Tue                               │
│ ☑ Acknowledged receipt of contract                          │
│                                                             │
│ Messages in bundle                                          │
│ • Re: Proposal …        urgent · reply     2h ago           │
│ • Catch-up …            —                  3d ago           │
└─────────────────────────────────────────────────────────────┘
```

**Section order (fixed)**

1. Back link + identity header (name as page title; email muted)
2. **Profile** — `.summary` Markdown region; regenerating state if profile job running
3. **Todos** — interactive checklist (local open/done)
4. **Messages in bundle** — compact list for this sender only (subject, 1–2 metric chips, date); expanding a message shows snippet/body in-place or a simple disclosure — not a third-pane SPA

**Profile states**

| State | UI |
|-------|-----|
| Ready | Rendered Markdown in `.summary` |
| Generating | `.job-busy` “Updating profile…” above empty/stale body; keep last good body if present |
| Empty (no mail yet) | Should not happen on detail; if race: muted “Profile appears after first message.” |
| Error | `.job-error` + **Retry profile**; keep prior body if any |

**Todo pattern**

- Checkbox + short action text + muted provenance (“from {subject}”)
- Toggle open ↔ done via HTMX; done items sink below open or show struck muted text — pick one, stay consistent
- No auto-send, no calendar write — copy never implies the todo will execute externally

**Message list:** Secondary to profile + todos. Do not lead with a Gmail-like stream.

### 3.4 Empty & auth states (Sender Inbox)

| Condition | Treatment |
|-----------|-----------|
| Google not connected | Quiet panel: connect via existing Gmail OAuth path; no fake senders |
| Connected, never ingested | Empty list + **Start ingest** as hero action under the one sentence |
| Ingested but zero senders (edge) | Muted error honesty + reset |
| LLM unhealthy | Banner already global; Start may still enqueue but fail categorization with per-item error — do not hide LLM banner |

### 3.5 Copy hierarchy (Sender Inbox)

- Brand: Crawley (nav)
- Panel title: **Sender Inbox** / sender **display name**
- Supporting sentence: one line only on list
- Actions: Start / Pause / Resume / Reset / todo toggles
- Avoid emoji chips and “AI powered” marketing labels

---

## 4. ASX desk (Sprint 7)

### 4.1 First viewport — universe + scanner

**Job:** See the universe, watch the slow scan of the PoC set (~20), open a company.

```
┌─────────────────────────────────────────────────────────────┐
│ ASX desk                                                    │
│ Research slice · scanner enriches one company at a time.    │
│ Desk · Recommendations · Paper portfolio                    │
│                                                             │
│ [Start scan]  Scanning 4 / 20 · CBA … pause                 │
│ PoC set: 20 of 312 in universe · [Configure set]            │
│ ─────────────────────────────────────────────────────────── │
│ Ticker  Name              Sector     Move    Sentiment      │
│ CBA     CommBank          Banks     +1.2%   constructive    │
│ BHP     BHP Group         Materials −0.4%   mixed           │
│ …                                                           │
└─────────────────────────────────────────────────────────────┘
```

**Hierarchy**

| Element | Role |
|---------|------|
| `h1` ASX desk | Display type |
| One sentence | Research + polite scan + not live trading |
| Sub-nav | Desk / Recommendations / Paper portfolio |
| Scanner progress row | Same job semantics as email ingest |
| Universe / PoC table | Primary body — rows, not cards |

**Row fields:** ticker (emphasized), name, sector (if known), price move (tokenized up=`--ok` / down=`--warn` or muted neutrals — avoid traffic-light rainbow), sentiment word/chip (one), scan status (pending / ready / error). Entire row opens company profile.

**Universe vs PoC set:** Show total universe size + “PoC processing N.” Configure set (first 20 / operator pick) via secondary control — modal or simple checklist panel below fold is fine; keep it out of the title block.

### 4.2 Scanner progress

| State | UI |
|-------|-----|
| Idle | **Start scan** |
| Busy | `n / 20` + current ticker; **Pause** |
| Paused / cap | Done or resume; capacity honesty |
| Per-company error | Row shows error affordance; scan continues |
| Rate-limit wait | `.job-busy` with calm “Waiting on source…” — not a spinner festival |

### 4.3 Company profile

**Job:** Pro-investor oriented clarity — what is this company, what moved, what’s the read, what to watch.

```
┌─────────────────────────────────────────────────────────────┐
│ ← ASX desk                                                  │
│ CBA · Commonwealth Bank of Australia                        │
│ Banks · last scan 10:42                                     │
│                                                             │
│ Snapshot          +1.2% · vol … · yield … (as available)    │
│                                                             │
│ Profile                                                     │
│ [MD: business summary, move, sentiment, risks/watch]        │
│                                                             │
│ Sources used                                     [Manage]   │
│ ASX announcements · wire · …                                │
│                                                             │
│ Not licensed research · personal simulation notes only      │
└─────────────────────────────────────────────────────────────┘
```

**Section order**

1. Back + identity (ticker dominant; name secondary)
2. **Snapshot** — compact metric line or 2×2 definition list **without** card chrome; missing metrics show “—” honestly
3. **Profile** — Markdown `.summary`
4. **Sources used** — muted list; link to Settings / sources registry
5. Footer disclaimer (always)

**Optional:** **Regenerate profile** secondary button when scan data exists.

**Metric guidance (display):** Prefer labels professionals recognize when data exists (price, % move, volume, yield/PE/quality proxies). Never invent numbers for missing free-source gaps — show em dash + tooltip or muted “unavailable.”

### 4.4 Sources + prompts (B74)

Accessible from Desk header disclosure or Settings section **Investment sources**:

- Enable/disable source rows (name, kind, status)
- Prompt templates: scan / profile / sentiment — textarea pattern already used in Settings
- Do not put the full prompt editor in the first viewport of Desk

---

## 5. Recommendations list (Sprint 8)

**Job:** Structured simulation ideas from profiles — actionable rows, not a blog.

**Sub-nav:** Recommendations active.

```
┌─────────────────────────────────────────────────────────────┐
│ Recommendations                                             │
│ Structured ideas from the PoC company set · not advice.     │
│ Desk · Recommendations · Paper portfolio                    │
│                                                             │
│ [Refresh]  Updated 10:45 · 8 rows                           │
│ ─────────────────────────────────────────────────────────── │
│ Ticker  Action   Urgency   Rationale (one line)      →      │
│ CBA     Watch    low       Yield support; wait for…  open   │
│ XYZ     Avoid    medium    Sentiment weak vs peers…  open   │
└─────────────────────────────────────────────────────────────┘
```

**Row schema (UI columns)**

| Column | Content |
|--------|---------|
| Ticker | Link to company profile |
| Action | Controlled vocabulary — e.g. `Buy` / `Add` / `Hold` / `Trim` / `Avoid` / `Watch` (architect freezes enum); styled as text weight, not colored pills overload. Soft color OK: constructive actions lean `--ok`, caution lean `--warn`, neutrals `--muted` |
| Urgency / confidence | Single muted qualifier |
| Rationale | One line; expand disclosure for full text |
| Generated | Relative time (optional column) |
| Act | **Paper trade** secondary control → portfolio create flow with fields prefilled (Sprint 8) |

**States:** empty (no profiles yet → link Desk), generating, ready, error. Always show non-advice sentence under the title or as footer.

**No card grid of idea tiles.** One list composition.

---

## 6. Paper portfolio (Sprint 8)

**Job:** Readable simulation ledger — cash, positions, simple P&L; never brokerage orders.

**Sub-nav:** Paper portfolio active. Separate page/route (not a modal).

```
┌─────────────────────────────────────────────────────────────┐
│ Paper portfolio                                             │
│ Simulated AUD book · fees applied · no live broker.         │
│ Desk · Recommendations · Paper portfolio                    │
│                                                             │
│ Cash $98,420.00    Equity MTM $12,110    P&L +$210          │
│ Fee model: $10 + 0.1% · [Simulation settings]               │
│                                                             │
│ Positions                                                   │
│ Ticker  Qty   Avg     Last    MTM      P&L                  │
│ CBA     50    118.20  120.10  6,005    +95                  │
│                                                             │
│ Ledger                                                      │
│ … fills / fees chronologically (compact)                    │
│                                                             │
│ [Add paper trade]                                           │
└─────────────────────────────────────────────────────────────┘
```

**Hierarchy**

1. Title + one simulation honesty sentence  
2. Summary line: cash · equity MTM · total P&L (definition list or single horizontal metrics row — **not** three cards)  
3. Link to **Simulation settings** (Settings panel section)  
4. Positions table  
5. Ledger (recent trades/fees)  
6. **Add paper trade** (manual) — form fields: ticker, side, qty, price (default last scan), optional note  

**From recommendation:** “Paper trade” prefills ticker/side/price; operator confirms submit.

**Empty:** Muted “No positions yet” + link Recommendations or Add paper trade — never sample stocks as fake holdings.

**Settings (B77) fields (UI):** starting cash, fee flat and/or %, currency AUD (fixed for PoC), cosmetic broker label. Explicit helper: “These settings do not enable live trading.”

**Gains/losses:** Use `--ok` / `--warn` for signed P&L text; respect theme contrast.

---

## 7. Cross-cutting patterns

### 7.1 Panels & lists

- Outer `.panel` optional once per major region; prefer **one** panel wrapping the desk body, with internal sections — avoid nested `.panel` cards per row.
- Tables: full-width, `--line` row separators, compact padding (`--space-2` / `--space-3`).
- On narrow widths (phone-on-LAN): stack sender/company rows as two-line blocks; keep sidebar collapse behavior as already shipped.

### 7.2 Chips / signals

Reuse glance `.chip` sparingly for **status** (scan/ingest). Category signals on rows should be quieter than glance chips — typographic tags (`.signal` class proposal: `font-size: 0.75rem; color: var(--muted)`).

### 7.3 Markdown

Reuse `.summary` / `.summary-body` sanitize path from Sprint 2–5 for profiles and expanded rationales.

### 7.4 Motion (pass budget)

1. Theme transition (existing).  
2. Ingest/scan progress fragment swap.  
3. Optional: todo checkbox strike-through ≤150ms when `prefers-reduced-motion: no-preference`.

No ambient chart animations in PoC.

### 7.5 Accessibility

- Progress regions: `aria-live="polite"` on ingest/scan status.  
- Tables: proper `<th>` / scope.  
- Sub-nav: `aria-current="page"` on active segment.  
- Disclaimers not only color-dependent.

---

## 8. Token / CSS extensions

Existing Sprint 2 tokens remain the base. Add only if architect needs them for density:

| Token | Role |
|-------|------|
| `--row-hover` | List/table row hover (may alias `--nav-hover`) |
| `--signal-border` | Quiet tag outline (`color-mix` from `--line`) |
| `--pos` | Optional alias of `--ok` for + price / + P&L |
| `--neg` | Optional alias of `--warn` for − move / − P&L |
| `--table-head` | Muted header text (may equal `--muted`) |
| `--space-6` | Optional `2rem` for section breaks inside long profiles |

Typography unchanged: IBM Plex Sans + Serif via `--font-sans` / `--font-display`.

Do **not** introduce purple accents, glow, or cream/terracotta marketing palette.

---

## 9. Sprint mapping

| Sprint / story | UX surfaces locked here |
|----------------|-------------------------|
| S6.0 / B65 | This file + pointer in `docs/ux.md` |
| S6.1–S6.5 | §3 Sender Inbox (list, progress, detail, profile, todos, cap) |
| S7.1–S7.4 | §4 ASX desk, profile, sources/prompts entry |
| S8.1–S8.3 | §5 Recommendations, §6 Paper portfolio + simulation settings |

---

## 10. Assumptions (draft-for-implement defaults)

| Topic | Default |
|-------|---------|
| Nav label Gmail vs Inbox | Keep **Gmail** in sidebar; panel title **Sender Inbox** |
| Chronological mail view | Not default; optional classic summary only |
| Investment landing | ASX desk replaces search-first layout |
| Recs + portfolio | Sub-routes under Investment, not new top-level modules |
| Action vocabulary | Architect freezes enum; UX shows readable labels above |
| Currency | AUD only in PoC portfolio UI |
| Confirmation for Reset PoC | `confirm()` acceptable for PoC |

Challenge these only if implementation cost or product docs disagree.

---

## 11. Parking lot (out of scope)

- Multi-account Gmail / shared inboxes  
- Newsletter “bundle class” as first-class sender type (Shortwave clone)  
- VIP rules engine (shelved backlog)  
- Offline full-text search across all mail  
- Live brokerage OAuth / order placement  
- Tax/CGT, multi-currency portfolio  
- HotCopper-style forums as default sources  
- Franking / dividend calendar depth  
- Watchlist baskets as separate IA (later shelved stories)  
- Native desktop chrome around desks  
- Per-module accent colors beyond tokens above  
- Chronological Inbox as equal peer (only classic escape hatch)

---

## 12. Handoff

Architects: implement against this file + [`docs/ux.md`](../ux.md). Do not invent a second UI stack. Material technical choices (schema, paths, store) go in `docs/architecture.md`.

Stakeholder: treat status **Draft for implement** as accepted for S6.0 unless vetoed; further polish can land mid-sprint without reopening IA.

