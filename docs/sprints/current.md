# Sprint 14 — ASX recommendations + paper portfolio

**Status:** ready (next delivery; Sprint 13 archived)  
**Duration:** one symbolic week  
**Backlog refs:** B75, B76, B77  
**Depends on:** Sprint 13 ASX profiles (B73); UX [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md) §§5–6  
**Architecture:** [`docs/architecture.md`](../architecture.md) — simulation ledger local-only; never calls brokerage order APIs  
**UX:** Recommendations list + separate paper portfolio page per UX contract  
**Previous:** [`archive/sprint-13-asx-profiles.md`](archive/sprint-13-asx-profiles.md)  
**Planned source:** [`planned/sprint-14-asx-paper-portfolio.md`](planned/sprint-14-asx-paper-portfolio.md)

## Goal

Turn ASX profiles into a **structured actionable recommendations** list, and a separate module page for a **simulated (paper) portfolio** that tracks hypothetical trades from those recommendations — with Settings for brokerage fee assumptions. **No live order routing.**

## Demo

Operator can:

1. Generate/refresh a structured recommendations list from current profiles (provisional language; personal simulation framing)
2. Open **Paper portfolio**; accept/simulate a recommendation into a position; see MTM from latest scanned prices
3. Configure simulation settings (starting cash, fee model, AUD)
4. See clear disclaimer: not advice; not connected to a real broker

## Committed

Implement **in order** (S14.1 → S14.2 → S14.3).

### S14.1 — Structured recommendations (B75)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B75 |

**Acceptance criteria:**

- [ ] Recommendations as structured rows (ticker, action, rationale, confidence/urgency, related profile link, generated_at)
- [ ] Generated from PoC company set via LLM + metrics; regenerable
- [ ] UI list per UX; non-advice disclaimer

---

### S14.2 — Simulated portfolio tracker (B76)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B76 |
| Depends on | S14.1 |

**Acceptance criteria:**

- [ ] Separate Investment sub-page/route for paper portfolio
- [ ] Create paper trades from a recommendation or manual entry (qty, side, price defaulting to last scan)
- [ ] Track positions, cash, simple P&L using latest scanner prices
- [ ] Local persistence under `data/`; no broker API orders

---

### S14.3 — Brokerage / simulation settings (B77)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B77 |
| Depends on | S14.2 |

**Acceptance criteria:**

- [ ] Settings: starting cash, fee per trade and/or %, default currency AUD, optional cosmetic broker label
- [ ] Fees applied in simulation math
- [ ] Documented: settings do **not** enable live trading

## Explicitly out of sprint

- Real brokerage OAuth / order placement (Icebox)
- Tax/CGT engine; multi-currency beyond AUD PoC
- Sender Inbox scale / Gmail send → Sprints 15+

## Parking lot

- Compare paper vs manual holdings journal
- Alert email about paper fills (unlikely)
