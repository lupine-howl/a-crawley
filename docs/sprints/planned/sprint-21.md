# Sprint 21 — Gmail thread digests (planned)

**Status:** shelved (superseded numbering — Sender Inbox + ASX pivot is Sprints 11–13 using `sprint-11-sender-inbox.md` etc.)  
**Duration:** one symbolic week  
**Backlog refs:** B44  
**Depends on:** B10, B15; Sprint 11 write-back helpful but not required for read  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**UX:** Prefer short `@ux-expert` pass when new Gmail chrome (lists, multi-select, rules) ships

## Goal

Deepen Gmail **read** path: open a thread (or recent threads), fetch bounded messages, produce an LLM **thread digest** with open questions / commitments.

## Demo

1. Pick a recent thread → Markdown digest (participants, asks, deadlines)
2. Job status + snapshot; empty/error honest
3. Still bounded; no full mailbox sync

## Committed

### S21.1 — Gmail thread digest (B44)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B44 |

**Acceptance criteria:**

- [ ] Gmail panel lists recent threads (bounded) or accepts a thread id/link from skim
- [ ] Fetch bounded messages in thread → local artifacts
- [ ] LLM Markdown digest: summary, asks, commitments, suggested next action (manual)
- [ ] Job busy/done/error; success snapshot
- [ ] No full-history sync; hard caps on messages/chars

---

**Out of scope (sprint):**

- Full mailbox index product
- Silent auto-replies
- Automated trading / order placement (Icebox)

## Parking lot

- Thread → Calendar event propose (later)
