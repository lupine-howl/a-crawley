# Sprint 10 — Coding/Creative lite + shared context (planned)

**Status:** planned (activates after Sprint 9 closes)  
**Duration:** one symbolic week  
**Backlog refs:** B28, B29, B30  
**Depends on:** Sprint 2 home glance; Sprint 7 Day brief preferred as first consumer of shared context  
**Architecture:** [`docs/architecture.md`](../architecture.md) + shared-context ADR/section  
**UX:** Optional pass for standing-notes editor + context disclosure (“what the model can see”)

## Goal

Finish the original top-tier stub set with **Coding/Creative** lite, and plant the Later theme of **stronger local data organisation**: a thin cross-module shared context (recent snapshots + standing notes) that Day brief and/or one module can optionally use — still local-first, hard-capped, no vector-DB productization.

## Demo

Operator can:

1. Use Coding/Creative: local notes → LLM next-steps Markdown; snapshot on home
2. Edit short **standing notes** and see that shared context is documented and size-capped
3. Run Day brief (or one module) with optional shared-context slice included in the prompt
4. Confirm secrets/tokens are never pulled into that context bundle
5. Still no native desktop wrapper, public hosting, or automated trading

## Committed

### S10.1 — Coding / Creative projects lite (B28)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B28 |

**Acceptance criteria:**

- [ ] Coding/Creative leaves Coming soon
- [ ] Local notes/context under `data/`
- [ ] Run → Markdown priorities / next experiments
- [ ] Job status + success snapshot for home
- [ ] No mandatory Git forge OAuth

---

### S10.2 — Cross-module context seed (B29)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B29 |
| Depends on | B14, B23 |

**Acceptance criteria:**

- [ ] Shared-context bundle from recent successful snapshots + optional standing notes (files/DuckDB — architect chooses)
- [ ] At least Day brief **or** one module can optionally include a bounded context slice in the LLM prompt
- [ ] Hard size caps; never inject API keys/tokens from secrets into prompts
- [ ] Architecture ADR/section: in/out of context; opt-in vs default
- [ ] Minimal UI to view/edit standing notes (Home or Settings)

---

### S10.3 — Home glance: Coding/Creative slot (B30)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B30 |
| Depends on | S10.1 |

**Acceptance criteria:**

- [ ] Home shows last Coding/Creative snapshot when present
- [ ] Glance participants list updated in architecture.md

**Out of scope (sprint):**

- Vector DB / embeddings RAG product
- Native desktop shell (remains unscheduled Later)
- Gmail write-back, automated trading, multi-user

## Parking lot (after Sprint 10)

- Gmail draft-then-send write-back → **[Sprint 11](sprint-11.md)**
- Optional **native desktop shell** → **[Sprint 12](sprint-12.md)**
- Scheduled overnight Day brief → **[Sprint 13](sprint-13.md)**
- Co-parenting ↔ Calendar sync → **[Sprint 14](sprint-14.md)**
- Deeper shared memory / history → **[Sprint 15](sprint-15.md)**
- Wearables / finance import / watchlist → Sprints **16–18**; LAN gate + weekly review → **19–20** ([index](README.md))
- Brokerage / automated trading remain **Icebox**
