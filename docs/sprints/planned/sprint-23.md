# Sprint 23 — Gmail VIP senders & local priority rules (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B46  
**Depends on:** B10, B44 helpful  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Local **VIP / priority sender rules** that reshape Gmail skim ranking and LLM priority sections — sole-operator rules, not Google filter sync yet.

## Demo

1. Define VIP/muted senders locally
2. Gmail Run uses rules in prioritization Markdown
3. Rules persist across restart

## Committed

### S23.1 — Gmail local priority rules (B46)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B46 |

**Acceptance criteria:**

- [ ] CRUD for local sender rules (VIP / muted / tags)
- [ ] Skim + digest prompts honor rules
- [ ] Clear UI for rules; no silent network calls beyond existing fetch
- [ ] Rules stored under data/; gitignored appropriately

---

**Out of scope (sprint):**

- Syncing Google filter DSL
- Multi-user shared rules
- Automated trading / order placement (Icebox)

## Parking lot

- Import rules from Google filters (later sprint)
