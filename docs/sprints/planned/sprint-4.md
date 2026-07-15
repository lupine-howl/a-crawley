# Sprint 4 — Investment depth + Fitness lite (planned)

**Status:** planned (activates after Sprint 3 closes)  
**Duration:** one symbolic week  
**Backlog refs:** B9, B11, B16  
**Depends on:** Sprint 2 Markdown/home; Sprint 3 optional but Calendar on home can wait  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Optional fitness panel patterns; keep quiet stubs for untouched domains

## Goal

Deepen the **Investment** PoC into something you would reopen for a real skim (better sources, cache, advice shape), and move **Fitness** past Coming soon with a safe, non-clinical lite path (goals/plan breakdown — not medical diagnosis).

## Demo

Operator can:

1. Run Investment with improved bounded fetch (cache hits when re-running same/similar query; clearer errors)
2. See a richer Markdown advice layout (still manual action only; no trading)
3. Open Fitness, enter or select a simple goal prompt, get an LLM introductory plan/breakdown in-panel
4. Fitness success snapshots appear on home At a glance (alongside Investment)
5. No automated trading; no regulated medical claims in UI copy

## Committed

### S4.1 — Harden Investment crawl & advice (B9)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B9 |

**Acceptance criteria:**

- [ ] Caching of raw fetch artifacts / query keys under `data/` to avoid redundant network+LLM when re-run is identical within a TTL or explicit “Use cache”
- [ ] Slightly richer source mix or metadata still **bounded** (hard cap on items/pages)
- [ ] Advice Markdown template improved (e.g. what’s moving / risks / watch list — still not orders)
- [ ] Stronger error taxonomy: network, parse, LLM, empty results
- [ ] Panel UX: show source list + summary (theme tokens; no chart soup required)
- [ ] Automated trading remains impossible from UI

---

### S4.2 — Fitness module lite (B11)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B11 |

**Acceptance criteria:**

- [ ] Fitness leaves Coming soon
- [ ] Operator provides a short goal/context (form input); optional saved last goal locally
- [ ] LLM returns Markdown introductory breakdown (habits / starter plan framing)
- [ ] Explicit UI disclaimer: not medical advice; personal planning only
- [ ] Job status + Markdown render + success snapshot for home
- [ ] No wearables/API required this sprint (manual prompt path only)

---

### S4.3 — Home glance: Investment + Fitness slots (B16)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B16 |
| Depends on | S4.1, S4.2, S2.4 store |

**Acceptance criteria:**

- [ ] Home At a glance shows last Fitness (and keeps Investment/Gmail/Calendar if present)
- [ ] Layout stays one composition — collapse/truncate long bodies; no stub filler cards
- [ ] Document which modules participate in glance in architecture.md

**Out of scope (sprint):**

- Wearable integrations, meal/nutrition tracking products
- Portfolio tracking, brokerage APIs
- Phone-on-LAN, write-back

## Parking lot

- Investment watchlist symbols file
- Fitness data import (Strava/etc.) Later
