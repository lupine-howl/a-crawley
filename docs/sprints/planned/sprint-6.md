# Sprint 6 — Co-parenting + DIY lite (planned)

**Status:** closed (delivered in Sprint 6–10 bundle)  
**Duration:** one symbolic week  
**Backlog refs:** B19, B20, B21  
**Depends on:** Sprint 2 Markdown/home; Sprint 5 Work lite as template for local-note modules  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Short `@ux-expert` pass if Co-parenting schedule entry needs a form pattern beyond Work/Fitness; else reuse those conventions

## Goal

Grow day-to-day life coverage: move **Co-parenting** and **DIY** past Coming soon with local-first lite paths (schedule windows + project notes → LLM Markdown), and show both on home At a glance — still sole-operator, no multi-user.

## Demo

Operator can:

1. Maintain a small local co-parenting schedule (handoff windows / notes) and run a “what’s next” Markdown skim
2. Capture DIY project notes and get LLM next-steps Markdown
3. See last Co-parenting and DIY snapshots on dashboard home alongside prior modules
4. Never see fake custody/demo project data; untouched stubs stay quiet

## Committed

### S6.1 — Co-parenting schedule lite (B19)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B19 |

**Acceptance criteria:**

- [ ] Co-parenting leaves Coming soon
- [ ] Local schedule entries persist under `data/` (dates/windows + short notes)
- [ ] Run → bounded-window Markdown summary (what’s next / conflicts to watch)
- [ ] Job busy/done/error; honest empty state
- [ ] Success snapshot for home glance
- [ ] No other-parent accounts or shared login

---

### S6.2 — DIY projects lite (B20)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B20 |

**Acceptance criteria:**

- [ ] DIY leaves Coming soon
- [ ] Operator can save project note(s) locally
- [ ] Run → Markdown next steps / materials-to-consider (manual action only)
- [ ] Job status + success snapshot for home
- [ ] No vendor scrape or checkout flows

---

### S6.3 — Home glance: Co-parenting + DIY (B21)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B21 |
| Depends on | S6.1, S6.2 |

**Acceptance criteria:**

- [ ] Home shows last Co-parenting and DIY when present
- [ ] Prior snapshots retained; truncate long bodies; no stub filler
- [ ] Glance participants documented in `docs/architecture.md`

**Out of scope (sprint):**

- Google Calendar sync for co-parenting (Later; local source of truth here)
- Finance live module, Day brief, write-back mutations
- LocalLlama ops, native desktop shell

## Architect notes

- Reuse Work/Fitness patterns: notes file under `data/<module>/`, LLM Markdown, snapshot id in home store.
- Prefer a structured schedule store (JSON/DuckDB rows) over freeform-only for Co-parenting so “bounded window” filtering is trivial.
- Do **not** request Calendar write scopes in this sprint.

## Parking lot

- Import co-parenting windows from Calendar (after shared context / write-back soak)
- DIY photo attachments
