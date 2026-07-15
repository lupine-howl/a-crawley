# ADR-006: Write-back requires explicit confirm (draft-first)

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Crawley modules may eventually mutate Google (Gmail send/labels, Calendar insert) and other systems. Product constraints forbid silent automation and multi-user ACLs. Sprint 5 designs the contract so later sprints can add mutations safely.

## Decision

1. **Explicit user confirm** is required before any live mutation. No background or scheduled writes in the personal OS PoC.
2. **Draft-first stages:** propose → show diff/draft → confirm → execute → append a **local audit log**.
3. **Per-module capability flags** (`WriteBackCapability`): `supported`, `dry_run_only`, human `label`.
4. Per-module: Gmail remains **dry-run only**. Calendar insert is live after confirm (Sprint 8) with a session draft UUID; Cancel performs no remote write.
5. Out of scope: silent automation, multi-user ACLs, cloud secret managers, Gmail send.

## Consequences

- **Positive:** Confirm-first Calendar path proves the stages; audit trail covers dry-run and live attempts.
- **Negative:** Gmail mutations still deferred; primary-calendar-only insert.
- **Later:** Gmail draft-then-send; undo/delete from audit row.
