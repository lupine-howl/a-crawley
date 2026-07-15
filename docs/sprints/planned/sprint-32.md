# Sprint 32 — Investment scenario & risk check (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B55  
**Depends on:** B45, B49 preferred  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Structured **scenario / risk-check** runs: operator picks thesis + holdings/watchlist → LLM stress questions, risks, what-to-watch — still not advice-as-orders.

## Demo

1. Run scenario checklist Markdown
2. Inputs from notebook/holdings/watchlist
3. Disclaimer visible

## Committed

### S32.1 — Scenario & risk check prompts (B55)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B55 |

**Acceptance criteria:**

- [ ] Scenario Run mode distinct from news skim
- [ ] Prompt template covers risks, invalidation, concentration (if holdings present)
- [ ] Non-advice disclaimer
- [ ] Snapshot for home/history

---

**Out of scope (sprint):**

- VaR engine productization
- Auto hedging
- Automated trading / order placement (Icebox)

## Parking lot

- Compare scenarios over time using history
