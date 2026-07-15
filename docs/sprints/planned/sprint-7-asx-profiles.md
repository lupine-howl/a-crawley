# Sprint 7 — ASX company scanner + profiles PoC (planned)

**Status:** planned (activates after Sprint 6 Sender Inbox PoC / shared UX contract)  
**Duration:** one symbolic week  
**Backlog refs:** B71, B72, B73, B74  
**Depends on:** B65 UX ASX dashboard contract; B4/B9 Investment module exists  
**Architecture:** background worker patterns from Sprint 6 email ingest; sources + prompt registry  
**UX:** Implement ASX dashboard per `docs/ux.md` / `docs/ux/sender-inbox-asx.md` (locked in Sprint 6)

## Goal

Pivot Investment toward an **ASX-first research desk**: maintain a large ASX company universe, run a **slow background scanner** (price movement, market data, news/sentiment), and build an LLM **company profile** per symbol using metrics and source types favored by professional investors — PoC proves the loop on **~20 companies**.

## Demo

Operator can:

1. See an ASX universe list (full curated list shipped; PoC processing limited to 20)
2. Start/stop background scan; watch progress (N/20 companies enriched)
3. Open a company profile aggregating price/market/news sentiment + structured metrics
4. Inspect configured **sources** and **prompt templates** used for enrichment
5. No live brokerage orders

## Committed

### S7.1 — ASX universe list (B71)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B71 |

**Acceptance criteria:**

- [ ] Curated ASX company list under `data/` (ticker, name, sector if available) — aim large (e.g. ASX 200+ or fuller dump); document provenance
- [ ] PoC processing set of **20** selectable (default first 20 or operator pick)
- [ ] Investment nav surfaces ASX desk (per UX), not only legacy search PoC

---

### S7.2 — Background ASX scanner (B72)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B72 |

**Acceptance criteria:**

- [ ] Background job processes **one company at a time** (or similarly polite cadence)
- [ ] Per company: fetch bounded price/market snapshot + news/headlines for sentiment
- [ ] Progress UI; pause/resume; errors isolated per company
- [ ] Hard caps; polite rate limits; artifacts under `data/`

---

### S7.3 — Company profiles (B73)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B73 |

**Acceptance criteria:**

- [ ] LLM (or hybrid) profile per scanned company: business summary, recent price move, sentiment, key risks/watch items, metric snapshot
- [ ] Metric set documented (pro-investor oriented: e.g. price/volume move, valuation/yield/quality proxies **as available from free/bounded sources** — architect notes gaps honestly)
- [ ] Profile view per UX; regenerable
- [ ] Explicit non-advice / not a licensed research product copy

---

### S7.4 — Sources registry + prompt library (B74)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B74 |

**Acceptance criteria:**

- [ ] Configurable **source list** (URLs/feeds/APIs) with enable flags; document defaults inspired by common pro workflows (exchange announcements, reputable wires, filings where reachable) — no scrape of TOS-forbidden targets
- [ ] Editable **prompt templates** for scan vs profile vs sentiment (Settings or module)
- [ ] Architecture note: scan vs curated-source modes

**Out of scope (sprint):**

- Live order placement
- Paper portfolio UI (Sprint 8)
- Full fundamental data warehouse / paid terminal replacement

## Parking lot

- HotCopper-style forums (quality/noise tradeoff)
- Franking / dividend calendar depth
- Tie-in to shelved watchlist/basket stories later
