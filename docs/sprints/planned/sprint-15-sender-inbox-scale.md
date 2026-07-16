# Sprint 15 — Sender Inbox scale (planned)

**Status:** done (delivered in [`../current.md`](../current.md) Sprints 15–17 bundle)  

**Duration:** one symbolic week  
**Backlog refs:** B79, B80  
**Depends on:** Sprint 12 Sender Inbox PoC  
**UX:** Keep people-first IA; progress for larger caps

## Goal

Move Sender Inbox past the ~20-email PoC: higher ingest cap, retention/prune policy, and basic search/filter across categorized senders — still one-at-a-time background pull.

## Demo

1. Raise/configure ingest cap (e.g. 100) with clear progress  
2. Search/filter senders or categories  
3. Old ingest pruned or capped per documented retention  
4. Profiles/todos still regenerate sanely

## Committed

### S15.1 — Configurable ingest cap + retention (B79)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B79 |

**Acceptance criteria:**

- [x] Operator-configurable ingest cap (above 20) with hard ceiling documented
- [x] Retention/prune policy for categorized messages (keep N / age) under `data/`
- [x] Progress UI scales; reset path remains

### S15.2 — Sender Inbox search & filter (B80)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B80 |

**Acceptance criteria:**

- [x] Filter senders by name/domain and/or category metrics
- [x] Simple search over sender list + optional subject snippet
- [x] Empty/no-match honest; theme tokens

**Out of scope:** Full offline mailbox index product; multi-account
