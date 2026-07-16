# Sprint 13 — ASX company scanner + profiles PoC

**Status:** closed  
**Duration:** one symbolic week  
**Backlog refs:** B71, B72, B73, B74  
**Depends on:** Sprint 12 Sender Inbox; B65 UX ASX contract; Investment module  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** ASX desk per [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md) §4  
**Previous:** [`sprint-12-sender-inbox.md`](sprint-12-sender-inbox.md)  
**Planned source:** [`../planned/sprint-13-asx-profiles.md`](../planned/sprint-13-asx-profiles.md)  
**Next:** [`../current.md`](../current.md) (Sprint 14 — recommendations + paper portfolio)

## Goal

Pivot Investment toward an **ASX-first research desk**: large curated universe, slow background scanner, LLM company profiles — PoC on **~20 companies**.

## Demo

1. See ASX universe + PoC set of 20 on Investment → ASX desk  
2. Start/pause scan; watch N/20 progress  
3. Open company profile (metrics + Markdown + sources + non-advice footer)  
4. Inspect/toggle sources and ASX prompt templates  
5. No live brokerage orders

## Committed

### S13.1 — ASX universe list (B71)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B71 |

**Acceptance criteria:**

- [x] Curated ASX company list (~193) in `src/crawley/asx_desk/assets/universe.json` with provenance
- [x] PoC processing set of **20** (default first 20; operator can reconfigure)
- [x] Investment nav surfaces ASX desk (legacy search under disclosure)

---

### S13.2 — Background ASX scanner (B72)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B72 |

**Acceptance criteria:**

- [x] Background job processes **one company at a time**
- [x] Per company: bounded price/market snapshot + news/headlines
- [x] Progress UI; pause/resume; errors isolated per company
- [x] Hard caps; polite rate limits; artifacts under `data/investment/asx/`

---

### S13.3 — Company profiles (B73)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B73 |

**Acceptance criteria:**

- [x] LLM profile per scanned company with metric snapshot
- [x] Metric set documented; gaps honest
- [x] Profile view per UX; regenerable
- [x] Non-advice disclaimer

---

### S13.4 — Sources registry + prompt library (B74)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B74 |

**Acceptance criteria:**

- [x] Configurable source list with enable flags + documented defaults
- [x] Editable prompt templates for scan / profile / sentiment
- [x] Architecture note: scan vs curated-source modes

## Explicitly out of sprint

- Paper portfolio / recommendations UI → Sprint **14**
- Live order placement
- Paid terminal data contracts

## Parking lot

- HotCopper-style forums
- Franking / dividend calendar depth
