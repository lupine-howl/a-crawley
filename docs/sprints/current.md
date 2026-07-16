# Sprints 14–16 — ASX paper desk + history + fitness import

**Status:** done (bundled delivery)  
**Duration:** three symbolic weeks  
**Backlog refs:** B75–B77 (14); B35–B36 (15); B37 (16)  
**Depends on:** Sprint 13 ASX desk; UX [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md) §§5–6  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-13-asx-profiles.md`](archive/sprint-13-asx-profiles.md)  
**Planned sources:** [`planned/sprint-14-asx-paper-portfolio.md`](planned/sprint-14-asx-paper-portfolio.md) · [`planned/sprint-15.md`](planned/sprint-15.md) · [`planned/sprint-16.md`](planned/sprint-16.md)

## Goal

1. **Sprint 14:** Structured ASX recommendations + simulated paper portfolio + simulation settings (no live broker).  
2. **Sprint 15:** Bounded snapshot history browser + pin history into shared context.  
3. **Sprint 16:** Fitness activity import lite grounding plans (non-medical).

## Demo

1. Refresh recommendations from scanned profiles → Paper trade into portfolio → see cash/MTM/P&L with fees  
2. Browse snapshot history; pin an item into shared context  
3. Import a small activity file; Fitness run cites it with disclaimer  

## Committed

### S14.1 — Structured recommendations (B75) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B75 |

**Acceptance criteria:**

- [x] Recommendations as structured rows (ticker, action, rationale, urgency, related profile link, generated_at)
- [x] Generated from PoC company set via LLM + metrics; regenerable
- [x] UI list per UX; export optional not required
- [x] Non-advice disclaimer

---

### S14.2 — Paper portfolio tracker (B76) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B76 |

**Acceptance criteria:**

- [x] Separate Investment sub-page/route for paper portfolio
- [x] Create paper trades from a recommendation or manual entry (qty, side, price defaulting to last scan)
- [x] Track positions, cash, simple P&L using latest available prices from scanner store
- [x] Local persistence under `data/`; no broker API orders

---

### S14.3 — Simulation settings (B77) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B77 |

**Acceptance criteria:**

- [x] Settings: starting cash, fee per trade and/or %, default currency AUD, optional broker name label (cosmetic)
- [x] Fees applied in simulation math
- [x] Documented: these settings do **not** enable live trading

---

### S15.1 — Snapshot history browser (B35) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B35 |

**Acceptance criteria:**

- [x] Persist more than “last success” (bounded N per module; `snapshot_history.json`)
- [x] Simple history UI in Settings; open body safely (escaped `<pre>`, truncated)
- [x] Prune/retention documented (UI + architecture)

---

### S15.2 — Shared context depth / pins (B36) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B36 |

**Acceptance criteria:**

- [x] Operator can pin/select history items into shared context
- [x] Hard caps; secrets never injected
- [x] Architecture + ADR-008: history vs seed standing notes

---

### S16.1 — Fitness import lite (B37) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B37 |

**Acceptance criteria:**

- [x] Import path for a bounded activity artifact under `data/fitness/`
- [x] Fitness Run can optionally include import slice in prompt
- [x] Medical disclaimer retained; no diagnosis framing
- [x] Clear errors for bad/oversized files

## Explicitly out of sprint

- Live brokerage OAuth / order placement  
- Tax/CGT engine; continuous wearable sync  
- Co-parenting→Calendar publish (still shelved B34)

## Parking lot

- Multi-currency portfolio  
- Full Markdown render for history bodies (escaped pre is enough for PoC)
