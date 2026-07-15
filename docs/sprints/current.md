# Sprint 6 — Sender Inbox PoC (+ UX contract)

**Status:** ready (next delivery; pivot replaces shelved co-parenting Sprint 6)  
**Duration:** one symbolic week  
**Backlog refs:** B65, B66, B67, B68, B69, B70  
**Depends on:** Sprint 5 Gmail OAuth + Markdown + jobs; UX pass for dashboards  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX contract:** [`docs/ux.md`](../ux.md) + [`docs/ux/sender-inbox-asx.md`](../ux/sender-inbox-asx.md)  
**Previous:** [`archive/sprint-5-lan-work-writeback.md`](archive/sprint-5-lan-work-writeback.md)  
**Planned source:** [`planned/sprint-6-sender-inbox.md`](planned/sprint-6-sender-inbox.md)  
**Shelved prior queue:** [`shelved/README.md`](shelved/README.md)

## Goal

Ship a **Sender Inbox PoC**: a polite background process ingests ~20 Gmail messages one-by-one with LLM categorization; the UI shows **senders (not a flat stream)**, each with an LLM **profile** and a **todo list** of actionable items. In the same sprint, lock UX for this inbox **and** the forthcoming ASX desk (Sprint 7–8).

Inspired by people-centric inboxes (e.g. ChatInbox / Talanoa / Shortwave-style bundling) — adapted to Crawley’s local HTMX shell.

## Demo

Operator can:

1. Confirm UX contract exists for Sender Inbox + ASX dashboards (`docs/ux/sender-inbox-asx.md`)
2. Start background ingest; watch progress as emails categorize one-at-a-time (stop at ~20)
3. Open **Sender Inbox**: groups by sender; no primary chronological flood
4. Open a sender → profile (LLM history sketch) + emails in bundle + **todos** extracted from that bundle
5. Restart app; categorized data + profiles + todos still present under `data/`

## Committed

Implement **in order** (S6.0 → … → S6.5). **Do not implement S6.1+ until S6.0 UX is confirmed** (or stakeholder waives in writing on the story).

### S6.0 — UX contract: Sender Inbox + ASX dashboards (B65)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B65 |
| Owner | UX expert |

**Acceptance criteria:**

- [ ] `docs/ux/sender-inbox-asx.md` (and pointers in `docs/ux.md`) specifies IA, primary layouts, empty/loading/progress states for:
  - Sender-grouped Inbox (list → sender detail → profile + todos)
  - ASX desk (universe / scanner progress / company profile)
  - Recommendations list + paper portfolio page (Sprint 8 surfaces)
- [ ] Respects shell themes/tokens; one composition; no card soup; brand present
- [ ] Stakeholder confirmed (or explicitly accepted as draft-for-implement)
- [ ] Parking lot for ideas that would expand sprint scope

---

### S6.1 — Background email ingest + LLM categorize (B66)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B66 |
| Depends on | S6.0 |

**Acceptance criteria:**

- [ ] Background worker pulls **one email at a time** (readable cadence; no burst hammering Gmail)
- [ ] Each message LLM-categorized onto a documented metric set (e.g. urgency, requires_reply, category/topic, sentiment, actionability, vip_hint — exact schema in architecture)
- [ ] Categories persisted locally; job progress visible (processed / cap)
- [ ] Failures skip/isolate one message without killing the worker
- [ ] Uses existing Google read path; no write-back required this sprint

---

### S6.2 — Sender-grouped Inbox view (B67)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B67 |
| Depends on | S6.0, S6.1 |

**Acceptance criteria:**

- [ ] Primary Gmail/Inbox surface is **grouped by sender** (not a chronological stream as the default)
- [ ] Sender row shows counts / latest activity / high-signal metric chips per UX
- [ ] Drill-in shows that sender’s ingested messages
- [ ] Matches UX contract; theme tokens only

---

### S6.3 — LLM sender profiles (B68)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B68 |
| Depends on | S6.2 |

**Acceptance criteria:**

- [ ] Each sender with ≥1 ingested mail gets an LLM profile summarizing interaction history (relationship, typical topics, open loops)
- [ ] Profile regenerates when new mail for that sender is ingested (or explicit refresh)
- [ ] Persisted under `data/`; shown on sender detail per UX

---

### S6.4 — Actionable todos from sender bundles (B69)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B69 |
| Depends on | S6.3 |

**Acceptance criteria:**

- [ ] LLM extracts actionable todos from the sender’s ingested bundle
- [ ] Todo list on sender detail; open/done toggle (local only)
- [ ] No auto-send / auto-calendar without confirm-first later stories

---

### S6.5 — PoC cap ~20 emails (B70)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B70 |
| Depends on | S6.1 |

**Acceptance criteria:**

- [ ] Hard stop (or clear pause) around **20** ingested emails for PoC
- [ ] UI states remaining capacity; Settings or panel control to reset PoC data (dev-friendly)
- [ ] Documented how to raise the cap later without redesign

## Explicitly out of sprint

- ASX scanner/profiles implementation → **Sprint 7**
- Recommendations + paper portfolio → **Sprint 8**
- Full mailbox crawl, multi-account, silent Gmail mutations
- Shelved sprints 6–40 life/depth items ([shelved](shelved/README.md))

## Parking lot

- Offline full-text search across categorized mail
- Merge Shortwave-like newsletter bundles as a sender class
- Un-shelve VIP rules (old B46) once PoC scales
