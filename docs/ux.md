# UX

UX expert owns this file. Update when a design pass lands.

**Working title:** Crawley  
**Status:** Confirmed — Sprint 2 design contract (2026-07-15); **Pivot UX** — Sender Inbox + ASX desk **Draft for implement** (2026-07-15)  
**Surfaces:** Local browser dashboard + module panels (FastAPI / Jinja2 / HTMX; see `docs/architecture.md`)  
**Sprint alignment:** S2.1–S2.4 (shell themes, Settings LLM, Markdown, At a glance) remain in force; **S11.0 / B65** pivot dashboards → [`docs/ux/sender-inbox-asx.md`](ux/sender-inbox-asx.md)

## Pivot — Sender Inbox + ASX desk (Sprints 11–13)

**Contract:** [`docs/ux/sender-inbox-asx.md`](ux/sender-inbox-asx.md)  
**Status:** Draft for implement (stakeholder intents locked via PO pivot; architects may proceed)

| Surface | Module | Default unit |
|---------|--------|--------------|
| Sender Inbox | Gmail | **Sender** (not chronological stream) |
| ASX desk | Investment | **Company** + scanner progress |
| Recommendations | Investment sub-route | Structured action rows |
| Paper portfolio | Investment sub-route | Simulated AUD ledger (not live trading) |

**Shell rules still bind:** one composition, brand in chrome, four themes/tokens, no card soup, IBM Plex, HTMX/Jinja only.

**Token extensions (optional for denser lists):** `--row-hover`, `--signal-border`, `--pos` / `--neg` (aliases of `--ok` / `--warn`), `--table-head`, optional `--space-6` — see pivot contract §8. Do not add purple/glow marketing accents.

Parking-lot ideas that expand scope live in the pivot file §11 (not here as sprint AC).

## Principles

1. **Personal operator tool, not marketing site** — One calm shell composition: brand, nav, status, active panel. No widget soup, promo chips, or decorative card grids.
2. **Brand readable in chrome** — “Crawley” in the sidebar remains the primary identity signal; panel titles are secondary.
3. **Middle density** — Airy brand + page header; compact module list and forms so nine domains fit without feeling sparse or cramped.
4. **Theme is atmosphere, not layout** — Switching themes recolors surfaces/type/accents; structure (sidebar + main) stays stable.
5. **Honest states** — LLM readiness, job busy/done/error, and Coming soon never impersonate live data or success.
6. **Immediate, reversible chrome choices** — Theme applies on select (no Save). LLM config Saves explicitly; Test connection is a separate action with clear outcomes.
7. **Accessible operator UI** — Visible focus, labeled controls, contrast that holds in every theme; keyboard-reachable Settings, theme radios, Save, and Test connection.
8. **Desktop-first, stack-faithful** — Server-rendered HTML/HTMX; evolve custom CSS variables. No SPA and no Node/Tailwind build unless architecture explicitly chooses later.

## Information architecture

### Shell chrome (unchanged topology)

```
┌─────────────┬──────────────────────────────────────┐
│ Crawley     │  [LLM status banner]                 │
│             │  ─────────────────────────────────   │
│ Investment  │  Panel title + description            │
│ Gmail       │  Panel body (live / stub / settings) │
│ Calendar …  │                                      │
│ …           │                                      │
│ ─────────   │                                      │
│ Settings    │                                      │
└─────────────┴──────────────────────────────────────┘
```

| Region | Role |
|--------|------|
| **Brand** | Link to dashboard home; display type; not crowded by controls |
| **Module nav** | All registered modules; live vs stub via subtle `soon` tag (keep existing pattern) |
| **Settings** | Nav footer item (below a hairline separator); durable entry for theme + LLM |
| **LLM banner** | Global readiness strip at top of main; clickable → Settings (LLM section) when not fully healthy; plain status when OK |
| **Panel root** | HTMX-swapped module or Settings content |

### Nav rules

- Active module: filled ink-on-panel (or theme inverse) as today — highest-contrast chrome affordance.
- Stub modules: same row style + muted `soon` tag; no lock icons, no disabled greying that suggests broken links.
- Settings: same `mod`-like row, but visually grouped under nav (separator + slightly quieter label weight optional). Active when Settings panel is open; no module is simultaneously active.
- Shortening visible labels is OK without dropping registry entries (architecture already notes density risk).

### Settings surface (S2.2)

Single Settings panel (not a modal; not a second app). Two sections, top → bottom:

1. **Appearance** — theme picker (S2.1)
2. **Language model** — provider/model/key + Test connection (S2.2)

Later credential UIs (Google, etc.) may join Settings; do not invent them this sprint. Leave vertical room / section pattern ready.

## Themes & tokens

### Theme set (S2.1)

Four named themes covering light, dark, and “other.” Operator picks one; selection persists locally (cookie / localStorage / config — **architect chooses**; document in `docs/architecture.md`).

| Theme id | Kind | Intent |
|----------|------|--------|
| `paper` | Light (default) | Refined warm workspace — evolve current Sprint 1 shell, not the cream/terracotta cliché |
| `slate` | Light (cool) | Neutral tool chrome; blue-gray atmosphere |
| `ink` | Dark | Primary dark workspace; low glare for long sessions |
| `moss` | Dark (other) | Green-cast dark alternate — distinct from `ink`, not neon |

Switching theme sets `data-theme="{id}"` on `<html>` (or `<body>`). All chrome + module panels consume tokens only — no hex literals in panel partials.

### CSS variables (align with existing shell)

Keep and centralize the Sprint 1 names. Define each under `:root` / `[data-theme="…"]` (or `:root` defaults = `paper`).

**Core (required — already in `base.html`):**

| Token | Role |
|-------|------|
| `--bg` | Page canvas / gradient anchors |
| `--ink` | Primary text |
| `--muted` | Secondary text, tags, hints |
| `--line` | Borders, separators |
| `--panel` | Panel / banner / elevated surface fill |
| `--accent` | Busy / in-progress / interactive emphasis (not brand purple) |
| `--warn` | Errors, missing key, failure states |
| `--ok` | Success, connected, job done |

**Extensions (add for S2.1 polish):**

| Token | Role |
|-------|------|
| `--nav` | Sidebar surface (may equal `color-mix` of `--panel`) |
| `--nav-hover` | Module row hover |
| `--nav-active-bg` | Active module background |
| `--nav-active-fg` | Active module text |
| `--banner-ok-border` | LLM banner when healthy |
| `--banner-bad-border` | LLM banner when unhealthy |
| `--focus` | Focus ring color |
| `--radius` | Default control/panel radius (e.g. `0.35rem`–`0.5rem`) |
| `--font-sans` | UI body stack |
| `--font-display` | Brand + `h1` stack |

**Typography (keep purposeful stacks):**

- Display / brand / `h1`: `"IBM Plex Serif", Georgia, serif` → `--font-display`
- Body / controls: `"IBM Plex Sans", "Segoe UI", sans-serif` → `--font-sans`
- Load via system or existing approach; do not switch to Inter/Roboto/Arial as primary.

**Spacing (middle density):**

| Token | Value | Use |
|-------|-------|-----|
| `--space-1` | `0.25rem` | Tight gaps |
| `--space-2` | `0.5rem` | Form gaps |
| `--space-3` | `0.75rem` | Nav padding rhythm |
| `--space-4` | `1rem` | Panel inner |
| `--space-5` | `1.5rem` | Main padding |

Nav link padding stays compact (~`0.4–0.45rem` vertical). Main title block keeps slightly more air under the banner.

### Palette guidance (implementable targets)

Architect may tune hex values ± slightly for contrast (WCAG AA for text on `--bg` / `--panel`). Intent:

**`paper` (default light)**  
- Warm gray-paper canvas (near current `#f6f3ee`), panel near `#fffcf7`  
- Ink stone (`#1c1917`), muted warm gray  
- Accent teal (`#0f766e` family) — keep; avoid terracotta as accent  
- Soft dual-stop background (radial + linear) using token-tinted stops, not flat fill  

**`slate` (cool light)**  
- Cool gray canvas + white/near-white panel  
- Cool ink (`#0f172a` family), slate muted  
- Accent blue-teal or steel blue — restrained, not purple  

**`ink` (dark)**  
- Near-black / charcoal canvas; elevated panel one step lighter  
- Off-white ink text; muted gray secondary  
- Accent desaturated teal or cyan for busy/focus  
- Borders slightly luminous (`--line` above canvas, not harsh white)  

**`moss` (dark other)**  
- Deep green-gray canvas; panel with subtle green lift  
- Cream/off-white text; muted sage secondary  
- Accent muted moss/fern green  
- Distinct from `ink` at a glance (operator can tell them apart without reading the name)

### Motion (2–3 intentional moments max)

1. Theme change: short foreground/background color transition (~150–200ms) on `body` / surfaces — no layout animation.  
2. Active nav: instant or ≤100ms background swap.  
3. Optional: Test connection result region fades in once — not perpetual pulse.

Respect `prefers-reduced-motion: reduce` (disable transitions).

## Key flows

### F1 — Switch theme (S2.1)

1. Open **Settings** from nav (or LLM banner → Settings).  
2. Under **Appearance**, choose a theme (`paper` / `slate` / `ink` / `moss`).  
3. UI updates **immediately** (full page token swap or HTMX refresh of chrome — architect chooses mechanism).  
4. Choice persists across reload.  
5. No Save required for theme.

**Control pattern:** Radio list or segmented group labeled with theme names (not only icons). Show a tiny swatch row (bg + accent) beside each name for recognition. Keyboard: arrow keys / tab within group.

### F2 — Open Settings & configure LLM (S2.2)

1. Enter via **Settings** nav item, or from LLM banner when unhealthy.  
2. **Language model** section fields (PoC):  
   - **Provider** — `OpenAI` (ready) · `LocalLlama` (visible but marked not ready / disabled submit path if selected — no install ops this sprint)  
   - **Model** — text input (placeholder e.g. `gpt-4o-mini` or current default)  
   - **API key** — password-style input; never echo full stored secret in HTML source after save — show empty with hint “Leave blank to keep existing” or “Set via Settings or `.env`”  
3. **Save** writes local gitignored settings (precedence vs `.env` documented by architect).  
4. Modules use saved settings per hot-reload vs restart policy (document in README / architecture — UX assumes post-save banner refresh; if restart required, show a one-line notice after Save).

**Out of PoC settings:** temperature, max tokens, billing, multi-profile. Parked.

### F3 — Test connection (S2.2)

1. Operator clicks **Test connection** (enabled when a testable provider is selected; for LocalLlama placeholder, button disabled or returns an explicit “not available yet” failure — prefer disabled + muted hint).  
2. Button shows busy label (`Testing…`) and is disabled while in flight.  
3. Result region below the form (not only toast):

| State | Visual | Copy intent (tune wording OK) |
|-------|--------|--------------------------------|
| **Success** | `--ok` border/text; optional brief check affordance via text, not emoji pile | “Connected — model responded.” Include provider + model name. |
| **Failure** | `--warn` | Short actionable reason: auth/key, network, model not found. No full traceback in UI; log server-side. |
| **Missing key** | `--warn`, same severity as Sprint 1 banner | “No API key configured. Add one here or in `.env`.” Banner and Settings stay consistent. |

4. Test is **optional** for saving — Save does not require a prior successful test. Banner reflects current known readiness after Save / Test / load.

### F4 — Coming soon stub (unchanged IA, polished chrome)

1. Operator opens a stub module.  
2. Panel shows quiet stub treatment (see Component patterns).  
3. No Run buttons, no fake charts, no “sample data.”

### F5 — Live module jobs (preserve Sprint 1 behavior)

Busy / done / error job lines continue to use `--accent` / `--ok` / `--warn`. Theme must not wash out these states.

### F6 — Dashboard home At a glance (S2.4 — PO add)

1. Operator opens **Crawley** brand / Dashboard (`/`).  
2. Sees one calm composition: short **status row** (LLM, Gmail auth) + **Last Investment** + **Last Gmail**.  
3. Successful module runs update those sections; restart still shows last success.  
4. Empty: muted hint + link into the module — never placeholder prose that looks like a model answer.  
5. Deep link from unhealthy LLM chip → Settings (LLM).  

Keep chrome brand-first; glance content is the single job of the home panel — no stub-module cards, stats strips, or promo tiles.

## Component patterns

### LLM status banner

- Classes: retain `.llm` / `.ok` / `.bad` pattern; borders via `--banner-ok-border` / `--banner-bad-border` (or `color-mix` from `--ok` / `--warn`).  
- Healthy: concise one-liner (`LLM (openai): ready` style).  
- Unhealthy: warning color + message; entire banner or an explicit “Open settings” link goes to Settings LLM section.  
- Do not put theme switcher in the banner.

### Theme picker

- Fieldset legend: **Theme** or **Appearance**.  
- One selected theme at a time; visible selected state using `--nav-active-*` or a clear checked radio affordance.  
- Names in UI: **Paper**, **Slate**, **Ink**, **Moss** (match ids above).

### Settings form

- Labels above fields (match `.run-form label` size/muted color).  
- Primary actions: **Save settings** (solid / ink fill button).  
- Secondary: **Test connection** (outline or quieter button — border `--ink` or `--line`, transparent/`--panel` fill, `--ink` text) so Save remains the primary commit.  
- Group spacing with `--space-4` between Appearance and Language model.

### Panels

- `.panel` is the container for **interactive** module work and Settings — allowed “card” because it frames operator action.  
- Dashboard home intro: title + one muted sentence; no extra card if empty state has nothing to do.  
- Avoid nesting panels.

### Coming soon stubs (**quiet**)

- One panel.  
- Headline: **Coming soon** (`.coming`) — keep familiar wording.  
- One short muted sentence (module description or “Not available in this sprint.”).  
- No CTAs, progress bars, or fake inputs.  
- Nav `soon` tag remains the only list-level badge.

### Buttons & inputs

- Primary: filled `--ink` on `--panel` text (or theme inverse); hover slightly lightens/darkens via `color-mix`, not a second accent rainbow.  
- Disabled: opacity ~0.55, `not-allowed`.  
- Inputs: `--line` border, `--panel` fill, `--ink` text; focus outline/`box-shadow` using `--focus`.  
- Radius from `--radius`.

### Job / summary blocks

- Status line: `.job-busy` / `.job-done` / `.job-error` → token colors.  
- Summaries: **rendered Markdown → HTML** in `.summary` (Sprint 2.3) — not a monospace `<pre>` dump of raw model text.  
- Prose inherits `--font-sans` / `--ink`; headings may use `--font-display` at small sizes; lists and paragraphs use `--space-*` rhythm.  
- Code/pre inside Markdown (if present): muted panel-tint background, still tokenized — keep readable, not neon.  
- Do not style summaries as marketing cards; one `.summary` region inside the panel is enough.

### Summary Markdown (S2.3 — PO add after UX lock)

| State | Behavior |
|-------|----------|
| Success with body | Safe MD→HTML in `.summary` |
| Empty / no job | No summary region |
| Error | Job error line only; do not MD-render stack traces |

Trusted subset focus: headings, paragraphs, emphasis, lists, links. Architect owns sanitize library choice (Python, no Node).

## Sprint alignment

| Story | UX contract |
|-------|-------------|
| **S2.1** | Four themes via tokens above; Settings Appearance picker; immediate apply + persist; stubs/panels/banner consume tokens; custom CSS variables (no Node build) |
| **S2.2** | Settings nav entry (+ banner deep-link); LLM fields + Save; Test connection states; missing key parity with banner |
| **S2.3** | Markdown→HTML for Investment/Gmail summaries; tokenized `.summary` styles; safe sanitize (see Component patterns) |
| **S2.4** | Home At a glance: status chips + persisted last Investment/Gmail MD snippets; one composition; empty honest hints (see F6) |
| **S11.0 / B65** | Sender Inbox + ASX desk IA/layouts/states — [`docs/ux/sender-inbox-asx.md`](ux/sender-inbox-asx.md) (Draft for implement) |
| **S11.1–S6.5** | Implement Sender Inbox per pivot contract §3 |
| **S12 / S13** | Implement ASX desk, recommendations, paper portfolio per pivot §§4–6 |

Architect implements; optional markup snippets in PRs are fine. Do not change Product/Roadmap/backlog from this pass.

## Assumptions (stakeholder defaults)

Made where questions were unanswered — challenge before lock:

| Topic | Assumption |
|-------|------------|
| Visual direction | Multi-theme system with modern operator-tool aesthetics; `paper` refines Sprint 1 rather than inventing a marketing look |
| Theme count | Four: Paper, Slate, Ink, Moss |
| Density | Middle — calm brand/header, denser nav |
| Theme UX | Settings only; apply immediately; persistence → architect |
| Settings entry | Nav footer **Settings** + unhealthy LLM banner links into Settings |
| LLM fields | Provider, model, API key; no temperature/max tokens in PoC |
| Test connection | Optional after Save; explicit success / failure / missing-key UI |
| LocalLlama | Visible placeholder; not operable; Test disabled or explicit not-ready |
| Stubs | Quiet “Coming soon” |
| Stack | No SPA; no Node build; desktop-first |
| Fonts | Keep IBM Plex Sans + Serif |

## Parking lot

- Per-module accent colors  
- Custom theme editor / user-uploaded CSS  
- System `prefers-color-scheme` auto-follow (can seed default later; not required if last explicit choice exists)  
- Settings sections for Google OAuth / module credentials  
- Temperature, max tokens, streaming indicator polish  
- Collapsible nav groups when module count grows  
- Native desktop window chrome  
- Marketing/landing page outside the app shell  
- **Pivot desks:** multi-account Gmail, newsletter bundle classes, live brokerage, CGT/multi-currency, forum noise sources — see [`docs/ux/sender-inbox-asx.md`](ux/sender-inbox-asx.md) §11  

## Open questions (resolve on lock)

1. Confirm the four theme names/ids (`paper`, `slate`, `ink`, `moss`) or rename.  
2. Confirm Settings entry = nav footer + banner deep-link (not Settings-only, not banner-only).  
3. Confirm quiet “Coming soon” copy is fine as-is.  
4. Any veto on keeping IBM Plex?

Once stakeholder lock: status = **Confirmed — Sprint 2 design contract**. (Locked 2026-07-15; S2.3 Markdown + S2.4 home glance added by PO without reopening theme decisions.)
