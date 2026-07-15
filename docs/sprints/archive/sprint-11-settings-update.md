# Sprint 12 — Sender Inbox PoC

**Status:** ready (next delivery; Sprint 11 archived)  
**Duration:** one symbolic week  
**Backlog refs:** B65, B66, B67, B68, B69, B70  
**Depends on:** Sprint 11 Settings Update; Sprints 1–10 shell; UX [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)  
**Architecture:** [`docs/architecture.md`](../../architecture.md)  
**UX:** Sender Inbox per [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)  
**Previous:** [`archive/sprint-11-settings-update.md`](archive/sprint-11-settings-update.md)  
**Planned source:** [`planned/sprint-12-sender-inbox.md`](../planned/sprint-12-sender-inbox.md)

## Goal

Ship the **Sender Inbox PoC** (~20 emails): one-at-a-time categorize → grouped-by-sender → LLM profiles → todos.

## Demo

Operator can:

1. Accept/confirm UX contract (`docs/ux/sender-inbox-asx.md`) or land small amendments
2. Start background ingest; watch progress as emails categorize one-at-a-time (stop at ~20)
3. Open **Sender Inbox**: groups by sender; no primary chronological flood
4. Open a sender → profile (LLM history sketch) + emails in bundle + **todos**
5. Restart app; categorized data + profiles + todos still present under `data/`

## Committed

Implement **in order** (S12.1 → … → S12.6). Treat UX draft as implementable unless stakeholder revises it.

### S12.1 — UX contract confirm (Sender Inbox + ASX) (B65)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B65 |

**Acceptance criteria:**

- [ ] Stakeholder accepts `docs/ux/sender-inbox-asx.md` as implement contract (or lands small amendments)
- [ ] Settings → Update placement already shipped (Sprint 11); ASX surfaces remain specified for Sprints 13–14

---

### S12.2 — Background email ingest + LLM categorize (B66)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B66 |

**Acceptance criteria:**

- [ ] Background worker pulls **one email at a time**
- [ ] Each message LLM-categorized onto a documented metric set (schema in architecture)
- [ ] Progress visible; failures isolate one message
- [ ] Existing Google read path; no write-back required

---

### S12.3 — Sender-grouped Inbox view (B67)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B67 |

**Acceptance criteria:**

- [ ] Primary Inbox surface **grouped by sender**
- [ ] Drill-in to sender’s ingested messages; metric chips per UX
- [ ] Theme tokens only

---

### S12.4 — LLM sender profiles (B68)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B68 |

**Acceptance criteria:**

- [ ] LLM profile per sender with ingested mail; regenerate on new mail or refresh
- [ ] Persisted under `data/`; shown on sender detail

---

### S12.5 — Actionable todos from sender bundles (B69)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B69 |

**Acceptance criteria:**

- [ ] Todos extracted from sender bundle; open/done local toggle
- [ ] No auto-send / auto-calendar

---

### S12.6 — PoC cap ~20 emails (B70)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B70 |

**Acceptance criteria:**

- [ ] Hard stop ~20; remaining capacity visible; reset path documented

## Explicitly out of sprint

- Settings Update / git pull (Sprint 11 — done)
- ASX Investment PoC → Sprints **13–14**
- Full mailbox crawl; Gmail send; live brokerage orders

## Parking lot

- Newsletter bundles as a sender class
- Un-shelve Gmail confirm-first send after this PoC
