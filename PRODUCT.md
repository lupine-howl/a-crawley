# Product

**Working title:** Crawley  
**Status:** **Hard pivot (2026-07-16)** — Phone Preview `crawley-ui` is the product surface; this repo is **Crawley analytics** (JSON API + daemons). See [`docs/migration-phone-preview.md`](docs/migration-phone-preview.md) · [`docs/adr/009-phone-preview-analytics.md`](docs/adr/009-phone-preview-analytics.md).

## Problem

A single person’s investing and email still mean tab-hopping and ad-hoc LLM chats. Crawley’s PoC proved local ASX + Gmail analysis, but the **HTMX shell is the wrong product surface** and the **process model mixes UI with long-running workers**.

**Who feels it:** The stakeholder alone (personal use). No commercial audience.

## Product vision

Crawley is a **local-first, AI-rich personal assistant** with a clear split:

- **Presentation:** `crawley-ui` — Phone Preview host (published `@phone-preview/*`), packs for desks, UI persistence via IndexedDB (± Turso/Duck sync through Phone Preview’s light backend).
- **Analytics:** Python in this repo — semi-autonomous daemons (ASX scan, Gmail ingest, …) with private worker storage that **publish** results; a thin FastAPI **JSON API** for jobs + presentation reads; Google OAuth and LLM stay here.
- **Domains in scope for the pivot:** **Investment / ASX desk** and **Gmail / Sender Inbox** only. Calendar and other life modules are shelved for later.

## Target users

- **Primary:** The stakeholder (sole operator).
- **Secondary:** None (no multi-user).

## Goals

1. **Correct architecture** — UI starts jobs and reads presentation data; never scrapes or calls LLM/Google APIs directly.
2. **Operator habit** — Reopen `crawley-ui` for ASX desk + Sender Inbox in a normal week.
3. **Local privacy** — Secrets on the analytics host; no public SaaS.
4. **Path to local LLM** — OpenAI + LocalLlama remain behind the analytics LLM interface.

## Non-goals

- Public hosting / multi-tenant SaaS  
- Multi-user / family accounts  
- Dedicated native mobile binary (Phone Preview may run on phone browsers; not a store app)  
- **Live brokerage order placement** (paper/simulation allowed)  
- Rebuilding ASX/Gmail pipelines in TypeScript  
- Keeping Jinja/HTMX as the product UI  
- Shipping Calendar or lite life modules in this pivot  
- Silent mutations without confirm (ADR-006 still governs analytics write-backs)

## Constraints

| Area | Constraint |
|------|------------|
| Analytics runtime | Python (`crawley` package in this repo) |
| Product UI | `crawley-ui` via npm + published Phone Preview packages |
| UI persistence | Primarily IndexedDB; Turso/Duck per Phone Preview persistence story — not the analytics brain |
| API contract | Versioned `/v1` JSON + OpenAPI owned by this repo |
| Google | Single identity; OAuth callbacks on analytics host |
| Advice model | Manual apply; paper ≠ live orders |
| Audience | Personal use only |

## Success metrics

| Metric | Target | Notes |
|--------|--------|-------|
| Pivot Sprint 31 | `curl` drives ASX scan + company JSON with no browser | **Met** (API shipped) |
| Pivot Sprint 32 | Operator uses `crawley-ui` ASX pack against analytics | UI gate |
| Habit | Weekly ASX + Inbox use without HTMX | Qualitative |
| Privacy | Secrets never in Vite | Hard rule |

## Modular domains (intent)

**Now (pivot):** ASX desk, Sender Inbox.  
**Later (shelved):** Calendar (light daemon + pack), Day brief composition, other life modules, depth 31–40 items, platform Later (desktop shell, etc.).

## Decisions log (Interview 1 — original)

- Working title: **Crawley**
- Python brain + local UI; personal sole user
- Automated trading Icebox

## Decisions log (Hard pivot — Phone Preview + analytics)

- Phone Preview **`crawley-ui`** is the product UI; this repo is analytics + daemons ([ADR-009](docs/adr/009-phone-preview-analytics.md))
- Consume **published** `@phone-preview/*`; ask PP team for setup recipe (create host, IndexedDB/Turso, proxy, OAuth deep link)
- UI persistence: **IndexedDB** primary; Turso/Duck are PP persistence options — confirm in PP code/docs
- **Delete** Jinja/HTMX product UI after ASX + Gmail API coverage — no permanent ops HTML
- **Calendar removed** from product surface for now (bring back later)
- Lite modules (Fitness, Co-parenting, DIY, Work, Finance, Coding) **quarantined / dropped** from product
- Depth band 21–30 remains shipped history; **do not** expand HTMX features
- Migration sprints **31–35**; former shelved depth 31–40 stays shelved under backlog B54+ until post-migration
- Icebox unchanged
