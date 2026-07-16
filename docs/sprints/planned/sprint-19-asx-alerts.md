# Sprint 19 — ASX local alerts + recommendation loop (planned)

**Status:** planned (after Sprint 14 paper portfolio)  
**Duration:** one symbolic week  
**Backlog refs:** B85, B86  
**Depends on:** B75–B77; ASX scanner  

## Goal

Local **in-panel alerts** for the ASX active set (price move / news keyword), and a light **recommendation feedback** loop (accept/dismiss/snooze) that informs the next regenerate — still informational; no live orders.

## Demo

1. Define alert rules; on scan/Run see triggered alerts on ASX desk  
2. Dismiss/snooze/accept a recommendation; next generate respects feedback  
3. Optional home chip for open alerts  

## Committed

### S19.1 — Local ASX alerts (B85)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B85 |

**Acceptance criteria:**

- [ ] Alert rule CRUD (ticker/topic, condition: keyword / move threshold note)
- [ ] Evaluation on scan/Run; list in ASX desk; optional home chip
- [ ] Explicit: informational only; no trades

### S19.2 — Recommendation feedback loop (B86)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B86 |

**Acceptance criteria:**

- [ ] Accept / dismiss / snooze on recommendation rows
- [ ] Persist feedback; next regenerate can exclude/dismissed or weight accepted
- [ ] Paper portfolio “accept → open trade” remains explicit separate action

**Out of scope:** SMS/email push off-machine; broker webhooks; automated trading
