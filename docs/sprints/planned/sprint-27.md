# Sprint 27 — Gmail saved searches & query builder (planned)

**Status:** planned (Email/Investment depth arc; after Sprint 20)
**Duration:** one symbolic week  
**Backlog refs:** B50  
**Depends on:** B10, B23 helpful  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Operator **saved Gmail queries** (from/to/subject/newer_than…) and a simple query builder that drives bounded skims.

## Demo

1. Save/name a query
2. Run skim against saved query
3. Results → LLM skim or thread list

## Committed

### S27.1 — Gmail saved searches (B50)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B50 |

**Acceptance criteria:**

- [ ] Persist named queries under data/
- [ ] Panel query builder or advanced string field with examples
- [ ] Run bounded fetch for query; job status
- [ ] Invalid query / API errors actionable

---

**Out of scope (sprint):**

- Full offline mail search index product (may come later)
- Multi-account
- Automated trading / order placement (Icebox)

## Parking lot

- Offline DuckDB mail index sprint
