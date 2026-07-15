# Sprint 37 — Gmail people & frequent contacts context (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B60  
**Depends on:** B46, B44  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Build a local **people context** (frequent contacts, last thread snippet, VIP flag) to improve digests and priority skims.

## Demo

1. See people list derived from bounded mail
2. Pin notes on a person
3. Digests can include people notes

## Committed

### S37.1 — People context lite (B60)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B60 |

**Acceptance criteria:**

- [ ] Derive frequent contacts from bounded recent mail (local)
- [ ] Operator notes per person; VIP link to rules
- [ ] Optional inject into thread digest / priority skim (capped)
- [ ] No CRM multi-user features

---

**Out of scope (sprint):**

- Full CRM product
- Scraping LinkedIn
- Automated trading / order placement (Icebox)

## Parking lot

- Person → co-parenting/work cross-links via shared context
