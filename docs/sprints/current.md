# Sprint 2 — Themes & LLM operator settings

**Duration:** one symbolic week  
**Backlog refs:** B7, B8  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-1-local-shell.md`](archive/sprint-1-local-shell.md)

## Goal

Make the local dashboard feel more intentional and operable day-to-day: a **themable palette** across shell and panels, plus a dashboard control to **configure the LLM** and **test the connection** without relying only on raw `.env` edits.

## Demo (definition of done for the sprint)

Operator can:

1. Switch theme (or palette) from the dashboard and see it apply across shell + module panels; choice persists across reload
2. Open settings, choose/configure the active LLM model (PoC), save locally
3. Run **Test connection** and see a clear success or failure result in the UI
4. Use Investment or Gmail summary path still working with the configured model settings

## Committed

Implement **in order** (S2.1 → S2.2) unless dependencies already satisfied.

### S2.1 — Themable UI & design polish (B7)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B7 |
| Depends on | Sprint 1 shell |

**Acceptance criteria:**

- [ ] Theme tokens (colors; type/spacing as needed) live in one place and apply across shell + module panels
- [ ] Operator can switch theme from the dashboard; selection persists locally
- [ ] Styling approach decided and recorded in `docs/architecture.md` (evolve Sprint 1 custom CSS vs introduce a build later)
- [ ] Stub / Coming soon panels match the updated system
- [ ] Optional: incorporate `@ux-expert` guidance from `docs/ux.md` if available this sprint; otherwise ship a clean interim theme set

**Out of scope:**

- Full brand/marketing site
- Native desktop chrome
- Node/Tailwind build unless explicitly chosen in architecture note

---

### S2.2 — LLM settings & connection test (B8)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B8 |
| Depends on | S2.1 recommended (shared settings chrome OK to land with S2.2); B3 done |

**Acceptance criteria:**

- [ ] Settings entry point on the dashboard (button/nav → settings panel)
- [ ] Configure active model / related PoC LLM settings; secrets stay local and gitignored
- [ ] **Test connection** reports success/failure clearly in the UI
- [ ] Modules use configured settings after save (document restart-required vs hot-reload in README or architecture)
- [ ] Missing/invalid key still surfaces clearly (parity with Sprint 1 banner behavior)

**Out of scope:**

- Multi-user settings profiles
- LocalLlama install/ops beyond selecting a non-ready provider placeholder
- Cloud billing dashboards
- Redesigning Investment/Gmail domain logic (B9–B10)

## Explicitly out of sprint

- Calendar real fetch (B6 later / B10)
- Harden investment or Gmail depth (B9–B10)
- Fitness beyond stub (B11)
- Phone-on-LAN (B12)
- Write-back, local LLM ops, automated trading

## Parking lot

- UX expert (`@ux-expert` → `docs/ux.md`) theme proposals may arrive mid-sprint — fold into S2.1 if timely; else backlog follow-up
- Settings chrome may later hold Google / module credentials UI — keep LLM-only this sprint unless trivial
- Persist theme via cookie, localStorage, or small local config file — architect chooses; document in architecture.md
