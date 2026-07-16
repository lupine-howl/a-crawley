# Sprint 30 — Investment citations & source quality (planned)

**Status:** shelved (superseded — active plan is [`sprint-30-asx-citations.md`](sprint-30-asx-citations.md) · B53 citations)
**Duration:** one symbolic week  
**Backlog refs:** B53  
**Depends on:** B9, B24  
**Primary focus:** investment  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass for notebook/holdings/compare layouts; keep non-trading copy clear

## Goal

Make Investment advice **auditable**: structured citations, source quality tags (primary wire / blog / aggregator), and panel affordances to open/copy sources.

## Demo

1. Advice shows citation list with quality tags
2. Operator can exclude weak sources from next run
3. Still bounded

## Committed

### S30.1 — Citations & source quality (B53)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B53 |

**Acceptance criteria:**

- [ ] Structured source records in DuckDB/files (url, title, retrieved_at, quality tag)
- [ ] Advice Markdown includes citations section
- [ ] Operator can mute/exclude domains for future runs
- [ ] Document quality rubric simply in architecture or module README

---

**Out of scope (sprint):**

- SEO spam network crawler
- Paywalled full-text scraping product
- Automated trading / order placement (Icebox)

## Parking lot

- Trust scores learned over time (later)
