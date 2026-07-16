# Sprint 29 — Gmail attachment skim (planned)

**Status:** planned (after Sprint 28)  
**Duration:** one symbolic week  
**Backlog refs:** B52  
**Depends on:** Sprint 22 thread digests preferred  
**Primary focus:** gmail  
**Architecture:** [`docs/architecture.md`](../architecture.md)  
**Collision note:** Bare [`sprint-29.md`](sprint-29.md) remains a shelved stub if present — prefer this file.

## Goal

Attachment metadata + opt-in bounded text extract for digests — never auto-exfiltrate large/unsafe files.

## Demo

1. List attachment metadata on a message/thread
2. Opt-in extract for allowlisted types under size cap
3. Optional include snippets in digest prompt

## Committed

### S29.1 — Attachment metadata + opt-in extract (B52)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B52 |

**Acceptance criteria:**

- [ ] List attachment metadata (name, type, size) for selected message/thread
- [ ] Opt-in text extract for allowlisted types under size cap; store under data/
- [ ] Never auto-exfiltrate; clear skip reasons for unsafe/huge files
- [ ] Optional include snippets in digest prompt

## Explicitly out of sprint

- Arbitrary binary preview
- Automated trading

## Parking lot

- Tie-ins to playbooks (Sprint 20) when useful
