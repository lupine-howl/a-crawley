# Retrospective — Sprints 1–5

**Date:** 2026-07-15  
**Owner:** Product owner  
**Scope:** Evaluate PoC through Sprint 5 close; inform Sprints 6–20 sequencing.

## Verdict

**Ship / continue.** Sprints 1–5 delivered the Now vision and the “harden personal OS” Next slice: a local modular shell with real Google + Investment signal, habit-oriented home glance, opt-in LAN, and a written write-back safety model (dry-run only). Success metrics for the PoC are met or clearly on track; remaining gaps are intentional Later items already sequenced (life stubs, live mutations, local LLM).

## Scorecard vs product goals

| Goal / metric | Result | Evidence |
|---------------|--------|----------|
| Local personal OS shell | **Met** | FastAPI/HTMX shell, registry/contract, themes, Settings, jobs |
| Signal from real sources | **Met** | Investment search + LLM; Gmail + Calendar read-only; home snapshots |
| Room to grow domains | **Met (pattern proven)** | Fitness + Work left Coming soon; stubs remain for Co-parenting/DIY/Finance/Coding |
| Privacy by locality | **Met** | Localhost default; secrets gitignored; LAN opt-in, trusted-LAN-only (no auth) |
| Habit / pull | **On track** | Home At a glance + Markdown summaries; qualitative weekly use still on stakeholder |
| Path to local LLM | **PoC gate cleared** | OpenAI path proven via Settings + Test connection; LocalLlama still placeholder → Sprint 9 |
| Write-back readiness | **Design met; live muted** | ADR-006 + dry-run hooks; no live send/insert yet → Sprint 8+ |

## What worked

1. **Vertical slices over platform thrash** — lite Investment/Gmail first, then shell polish, then Google depth, then reach/Work/design.
2. **Stable module contract early** — Fitness/Work (and remaining stubs) slotted without forking the core.
3. **UX contract for Sprint 2** — themes/Settings stayed coherent; Markdown + glance amplified reopen value.
4. **Bundling 3–4** — shared Google OAuth + Calendar/Gmail/Investment/Fitness delivered as one compound sprint reduced OAuth thrash.
5. **Write-back design before mutations** — ADR-006 keeps confirm-first discipline visible before live API risk.

## Friction / risks

| Risk | Severity | Mitigation for 6–20 |
|------|----------|---------------------|
| Live Google OAuth / LAN not fully E2E-automated | Medium | Keep README paths; treat as ops checklist on promote |
| Trusted-LAN-only (no gate) | Medium | Optional shared-secret later (Sprint 19); leave Sprint 5 decision unless phone use expands |
| Home glance can densify as modules ship | Medium | Day brief (7) + shared context (10) + history/search (15); keep one composition |
| Dry-run ≠ real confirm UX | Medium | Sprint 8 Calendar write-back must land propose→confirm UI, not only API |
| Compound sprint docs (3–4) harder to audit | Low | Prefer single-sprint archives going forward; keep planned files |

## Out of scope that stayed out (good)

- Automated trading, multi-user, public hosting, medical/financial regulated framing
- Native desktop wrapper, local LLM ops, live Gmail/Calendar mutations

## Documentation close-out (this pass)

- [x] Archive Sprint 5 → `sprint-5-lan-work-writeback.md`
- [x] Promote Sprint 6 → `docs/sprints/current.md`
- [x] Mark backlog B1–B18 AC complete; status done
- [x] Refresh README / ROADMAP / PRODUCT status for post–Sprint 5
- [x] Sequence Sprints 11–20 from After-10 / Later themes

## Recommendations into 6–20

1. Deliver remaining **top-tier lite modules** (6–7, 10) before deep integrations.
2. Land **one** live mutation surface (Calendar, 8) before Gmail send (11).
3. Prove **local LLM** (9) after habit modules exist; keep OpenAI selectable.
4. Treat **desktop shell** (12) as chrome around the same UI — not a rewrite.
5. Pull wearables / CSV finance / watchlists only after lite domains and write-back soak (16–18).
6. Do **not** schedule Icebox items (trading, multi-user, SaaS) without an explicit PRODUCT revision.
