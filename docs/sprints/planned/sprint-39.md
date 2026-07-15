# Sprint 39 — Email × Investment signal bridge (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B62  
**Depends on:** B49, B54, B27, B39  
**Primary focus:** bridge  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** `@ux-expert` for bridge results (one composition; deep links, not a third dashboard)

## Goal

Cross-module depth: detect **mail that mentions holdings/watchlist** (and optional finance keywords) → bridge digest for Investment + Gmail panels / home.

## Demo

1. Run bridge scan on bounded mail + holdings/watchlist
2. Show hits with links to thread digest and symbol notebook
3. Confirm-first actions remain in home modules

## Committed

### S39.1 — Holdings-aware mail bridge (B62)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B62 |

**Acceptance criteria:**

- [ ] Bounded scan: match sender/subject/body keywords to holdings/watchlist symbols
- [ ] Bridge results Markdown + deep links
- [ ] False-positive controls (min token length, allowlist tickers)
- [ ] No auto-trading; no auto-send
- [ ] Architecture note on matching approach

---

**Out of scope (sprint):**

- Brokerage statement scraping as primary path
- Silent portfolio changes
- Automated trading / order placement (Icebox)

## Parking lot

- Include broker notification senders as VIP
