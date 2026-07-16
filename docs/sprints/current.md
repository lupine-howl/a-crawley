# Sprints 15–17 — Inbox/ASX scale + email bridge

**Status:** done (bundled delivery)  
**Duration:** three symbolic weeks  
**Backlog refs:** B79–B80 (15); B81–B82 (16); B83 (17)  
**Depends on:** Sprint 12 Sender Inbox; Sprint 13–14 ASX desk + paper  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Previous:** [`archive/sprint-14-asx-paper-portfolio.md`](archive/sprint-14-asx-paper-portfolio.md)  
**Planned sources:** [`planned/sprint-15-sender-inbox-scale.md`](planned/sprint-15-sender-inbox-scale.md) · [`planned/sprint-16-asx-scale-events.md`](planned/sprint-16-asx-scale-events.md) · [`planned/sprint-17-email-asx-bridge.md`](planned/sprint-17-email-asx-bridge.md)

**Numbering note:** Pivot Sprints 15–17 (this file). Legacy shelved `sprint-15.md` / `sprint-16.md` (history/fitness) were delivered with Sprint 14.

## Goal

1. **Sprint 15:** Raise Sender Inbox ingest cap with retention/prune + search/filter.  
2. **Sprint 16:** Enlarge ASX active set + bounded earnings/events skim.  
3. **Sprint 17:** Holdings-aware mail ↔ ASX bridge digest with deep links.

## Demo

1. Set inbox cap (e.g. 100); search/filter senders; old mail pruned  
2. Expand ASX active set (e.g. 50); run events skim  
3. Run bridge → hits with links to sender + company  

## Committed

### S15.1 — Configurable ingest cap + retention (B79) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B79 |

**Acceptance criteria:**

- [x] Operator-configurable ingest cap (Settings → Desk scale) with hard ceiling 200
- [x] Retention/prune (keep newest N) under `data/gmail/sender_inbox/`
- [x] Progress UI scales; reset path remains

---

### S15.2 — Sender Inbox search & filter (B80) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B80 |

**Acceptance criteria:**

- [x] Filter senders by name/domain and category metrics
- [x] Simple search over sender list + subject
- [x] Empty/no-match honest; theme tokens

---

### S16.1 — ASX active-set scale (B81) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B81 |

**Acceptance criteria:**

- [x] Operator can enlarge active scan set beyond 20 within hard ceiling 200
- [x] Scanner/progress UI handles larger N; pause/resume preserved
- [x] Universe list still the source; provenance unchanged

---

### S16.2 — Earnings & events skim (B82) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B82 |

**Acceptance criteria:**

- [x] Bounded fetch of earnings/event-like signals for active set (Google News RSS)
- [x] Markdown/table of headlines + Investment → Events page
- [x] Hard caps; honest empty; non-advice copy

---

### S17.1 — Holdings-aware mail bridge (B83) · done

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B83 |

**Acceptance criteria:**

- [x] Bounded match of subject/body to ASX tickers / paper holdings
- [x] Bridge results + deep links (sender + company)
- [x] False-positive controls documented
- [x] Architecture note on matching approach
- [x] No auto-trading; no auto-send

## Explicitly out of sprint

- Full offline mailbox index; multi-account  
- Paid data terminals; auto trades  
- Gmail confirm-first send (Sprint 18)  

## Parking lot

- Fuzzy company-name matching beyond allowlist  
