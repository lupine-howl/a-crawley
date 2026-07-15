# Sprint 17 — Finance import lite (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B38  
**Depends on:** B22  

## Goal

Deepen Finance/Taxes planning with **local CSV (or similar) import** → LLM structured questions/reminders — still not brokerage, e-file, or licensed advice.

## Demo

1. Import a small CSV of transactions/categories
2. Run planning summary with disclaimer
3. No bank OAuth; no payments

## Committed

### S17.1 — Finance CSV import lite (B38)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B38 |

**Acceptance criteria:**

- [ ] Bounded CSV import under `data/`; schema flexibility documented
- [ ] Run → Markdown planning summary using import + notes
- [ ] Explicit non-advice disclaimer
- [ ] No brokerage APIs; no automated trading UI

**Out of scope:** Tax e-file, bank aggregation SaaS, portfolio accounting product
