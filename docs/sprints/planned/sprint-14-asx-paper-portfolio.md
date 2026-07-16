# Sprint 14 — ASX recommendations + paper portfolio (planned)

**Status:** done (delivered in [`../current.md`](../current.md) Sprints 14–16 bundle)
**Duration:** one symbolic week  
**Backlog refs:** B75, B76, B77  
**Depends on:** B73 company profiles; B65 UX for recommendations + portfolio pages  
**Architecture:** simulation ledger local-only; never calls brokerage order APIs  
**UX:** Recommendations list + separate portfolio page per UX contract

## Goal

Turn ASX profiles into a **structured actionable recommendations** list, and a separate module page for a **simulated (paper) portfolio** that tracks hypothetical trades derived from those recommendations — with Settings for brokerage fee assumptions etc. **No live order routing.**

## Demo

Operator can:

1. Generate/refresh a structured recommendations list from current profiles (buy/hold/avoid-style language stay provisional; frames as personal simulation ideas)
2. Open **Paper portfolio** page; accept/simulate a recommendation into a position; see MTM using latest scanned prices
3. Configure simulation settings (starting cash, fee model, currency AUD)
4. Clear disclaimer: not advice; not connected to a real broker

## Committed

### S14.1 — Structured recommendations (B75)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B75 |

**Acceptance criteria:**

- [x] Recommendations as structured rows (ticker, action, rationale, confidence/urgency, related profile link, generated_at)
- [x] Generated from PoC company set via LLM + metrics; regenerable
- [x] UI list per UX; export optional not required
- [x] Non-advice disclaimer

---

### S14.2 — Simulated portfolio tracker (B76)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B76 |

**Acceptance criteria:**

- [x] Separate Investment sub-page/route for paper portfolio
- [x] Create paper trades from a recommendation or manual entry (qty, side, price defaulting to last scan)
- [x] Track positions, cash, simple P&amp;L using latest available prices from scanner store
- [x] Local persistence under `data/`; no broker API orders
- [x] Inspired by portfolio trackers (e.g. Sharesight-style clarity) but simulation-only

---

### S14.3 — Brokerage / simulation settings (B77)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B77 |

**Acceptance criteria:**

- [x] Settings: starting cash, fee per trade and/or %, default currency AUD, optional broker name label (cosmetic)
- [x] Fees applied in simulation math
- [x] Documented: these settings do **not** enable live trading

**Out of scope (sprint):**

- Real brokerage OAuth / order placement (Icebox)
- Tax/CGT engine
- Multi-currency complexity beyond AUD PoC

## Parking lot

- Un-shelve confirm-first write-back for alerting email about paper fills (unlikely)
- Compare paper vs operator’s real holdings journal (shelved B49)
