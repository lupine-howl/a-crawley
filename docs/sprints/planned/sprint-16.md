# Sprint 16 — Fitness data import lite (planned)

**Status:** done (legacy shelved plan; delivered with Sprint 14 in [`../current.md`](../current.md) — **not** pivot Sprint 16)  
**Pivot Sprint 16:** [`sprint-16-asx-scale-events.md`](sprint-16-asx-scale-events.md)  

**Duration:** one symbolic week  
**Backlog refs:** B37  
**Depends on:** B11  
**UX:** Import path + keep medical disclaimer

## Goal

Deepen Fitness without clinical claims: optional **manual export / file import** (or one read-only popular source if low-friction) to ground LLM plans in recent activity — wearables remain optional.

## Demo

1. Import a bounded activity file (or connect one read-only optional source — architect documents choice)
2. Run Fitness plan that cites imported context
3. Disclaimer remains; empty import honest

## Committed

### S16.1 — Fitness import lite (B37)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B37 |

**Acceptance criteria:**

- [x] Import path for a bounded activity artifact under `data/`
- [x] Fitness Run can optionally include import slice in prompt
- [x] Medical disclaimer retained; no diagnosis framing
- [x] Clear errors for bad/oversized files

**Out of scope:** Continuous wearable sync product, coaching marketplace
