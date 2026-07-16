# Sprint 35 — Cutover: delete HTMX, quarantine modules (planned)

**Status:** planned (after Sprint 34)  
**Duration:** one symbolic week  
**Backlog refs:** B99, B100  
**Depends on:** ASX + Sender Inbox usable from `crawley-ui`  

## Goal

**Delete** the Jinja/HTMX product UI from this repo (no permanent ops HTML). Quarantine **Calendar** and lite life modules from the product registry/nav. Operator Settings/ops live in `crawley-ui`.

## Demo

1. Analytics serves JSON (+ OpenAPI) only for product paths — no dashboard HTML dependency  
2. Calendar / Fitness / etc. not reachable as product surfaces  
3. README run path: start analytics + start `crawley-ui`  

## Committed

### S35.1 — Remove Jinja product UI (B99)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B99 |

**Acceptance criteria:**

- [ ] Product HTML/HTMX routes and templates removed (or isolated so they are not the run path)  
- [ ] README documents analytics + `crawley-ui` as the supported operator path  
- [ ] Tests updated; no requirement to render Jinja for CI green  
- [ ] ADR-001 marked superseded for product surface (ADR-009 already does)  

### S35.2 — Quarantine Calendar + lite modules (B100)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B100 |

**Acceptance criteria:**

- [ ] Calendar and lite modules (Fitness, Co-parenting, DIY, Work, Finance, Coding) removed from product registry/nav or clearly quarantined non-loaded  
- [ ] Code may remain on disk under quarantine until deleted; not part of supported product  
- [ ] PRODUCT/ROADMAP Later notes Calendar return path  
- [ ] Day brief / home glance HTMX composition retired with shell  

## Explicitly out of sprint

- Rebuilding Calendar pack  
- Un-shelving depth 31–40  
- Live brokerage  
