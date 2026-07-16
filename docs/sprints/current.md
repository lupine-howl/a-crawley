# Current sprint — 35: Cutover (delete HTMX, quarantine modules)

**Theme:** Roadmap Theme 3 — Phone Preview is the only product UI  
**Dates:** —  
**Goal:** **Delete** the Jinja/HTMX product UI from the supported run path. Quarantine **Calendar** and lite life modules. Operator Settings/ops live in `crawley-ui`. Analytics serves JSON (+ OpenAPI) for product paths.

**Prerequisites:** Sprint 34 Gmail ingest + Sender Inbox pack (closed). Follow [migration plan](../migration-phone-preview.md) Phase 5 and [ADR-009](../adr/009-phone-preview-analytics.md).

**Out of scope:** Calendar pack; rebuilding ASX/Gmail in TypeScript; un-shelving depth 31–40 stubs.

---

## Stories

### S35.1 — Remove Jinja product UI (B99)

**Points:** 5  
**Status:** Todo  
**BACKLOG:** B99  

**Acceptance criteria:**

- [ ] Product HTML/HTMX routes and templates removed (or isolated so they are not the run path)
- [ ] README documents analytics + `crawley-ui` as the supported operator path
- [ ] Tests updated; no requirement to render Jinja for CI green
- [ ] ADR-001 marked superseded for product surface (ADR-009 already does)

---

### S35.2 — Quarantine Calendar + lite modules (B100)

**Points:** 3  
**Status:** Todo  
**BACKLOG:** B100  

**Acceptance criteria:**

- [ ] Calendar / Fitness / etc. not reachable as product surfaces
- [ ] PRODUCT Later notes Calendar return
- [ ] Day brief HTMX composition retired with shell

---

## Parking lot

- Calendar as light daemon + pack (post-cutover)
- Labels / send / VIP packs on Sender Inbox

---

## Sprint review checklist

- [ ] All stories Done or explicitly deferred with reason
- [ ] `uv run pytest` green
- [ ] Architecture + README updated
- [ ] Archive this file → `archive/sprint-35-cutover.md`
