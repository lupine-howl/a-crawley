# Sprint 24 — Sender Inbox VIP / priority rules (planned)

**Status:** planned (after Sprint 23)  
**Duration:** one symbolic week  
**Backlog refs:** B46  
**Depends on:** Sprint 12 Sender Inbox; Sprint 15 search helpful  
**Primary focus:** gmail / sender inbox  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-24.md`](sprint-24.md) remains a shelved stub if present — prefer this file.

## Goal

Local VIP / muted sender rules that shape categorization priority and Sender Inbox ordering — no Google filter sync product.

## Demo

1. Mark a sender VIP or muted
2. Ingest/skim/list honors rules (VIP boosted; muted deprioritized)
3. Rules persist under data/

## Committed

### S24.1 — Local sender priority rules (B46)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B46 |

**Acceptance criteria:**

- [ ] CRUD for local sender rules (VIP / muted / tags)
- [ ] Categorization + sender list honor rules
- [ ] Clear UI for rules; no silent network calls beyond existing fetch
- [ ] Rules stored under data/; gitignored appropriately

## Explicitly out of sprint

- Google filter sync product
- Multi-user CRM

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
