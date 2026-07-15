# Sprint 12 — Sender Inbox PoC

**Status:** planned (activates after Sprint 11 Update)  
**Duration:** one symbolic week  
**Backlog refs:** B65, B66, B67, B68, B69, B70  
**Depends on:** Sprint 11 Update preferred; Sprints 1–10 shell; UX [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Sender Inbox per [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)

## Goal

Ship the **Sender Inbox PoC** (~20 emails): one-at-a-time categorize → grouped-by-sender → LLM profiles → todos.

## Demo

1. Ingest ~20 mails one-by-one → sender groups → profile + todos  
2. Restart still shows categorized data / profiles / todos under `data/`

## Committed

### S12.1 — UX contract confirm (Sender Inbox + ASX) (B65)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B65 |

**Acceptance criteria:**

- [ ] Stakeholder accepts `docs/ux/sender-inbox-asx.md` as implement contract (or lands small amendments)
- [ ] Settings → Update placement already specified (Sprint 11); ASX surfaces remain specified for Sprints 13–14

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

- Settings Update / git pull (Sprint 11)
- ASX Investment PoC → Sprints 13–14
- Full mailbox crawl; Gmail send; live brokerage orders
