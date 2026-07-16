# Sprint 22 — Sender Inbox thread digests (planned)

**Status:** planned (after Sprint 21)  
**Duration:** one symbolic week  
**Backlog refs:** B44  
**Depends on:** Sprint 12+ Sender Inbox; Gmail send (18) helpful for reply from digest  
**Primary focus:** gmail / sender inbox  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-22.md`](sprint-22.md) remains a shelved stub if present — prefer this file.

## Goal

Deepen Sender Inbox **read** path: open a thread (or recent threads for a sender), fetch bounded messages, produce an LLM **thread digest** with open questions / commitments — still local-first, no full mailbox sync.

## Demo

1. Pick a sender thread → Markdown digest (participants, asks, deadlines)
2. Job status + snapshot; empty/error honest
3. Optional deep link to confirm-first compose (no auto-send)

## Committed

### S22.1 — Thread digest from Sender Inbox (B44)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B44 |

**Acceptance criteria:**

- [ ] Sender Inbox (or Gmail panel) lists recent threads for a sender (bounded) or accepts a thread id from ingested mail
- [ ] Fetch bounded messages in thread → local artifacts under data/
- [ ] LLM Markdown digest: summary, asks, commitments, suggested next action (manual)
- [ ] Job busy/done/error; success snapshot
- [ ] No full-history sync; hard caps on messages/chars

## Explicitly out of sprint

- Full mailbox index
- Silent auto-replies
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
