# ADR-006: Write-back requires explicit confirm (draft-first)

- **Status:** Accepted (amended Sprints 18, 26)
- **Date:** 2026-07-15
- **Amended:** 2026-07-16

## Context

Crawley modules may mutate Google (Gmail send, Calendar insert, Gmail labels) and other systems. Product constraints forbid silent automation and multi-user ACLs.

## Decision

1. **Explicit user confirm** is required before any live mutation. No background or scheduled writes in the personal OS PoC.
2. **Draft-first stages:** propose → show draft → confirm → execute → append a **local audit log**.
3. **Per-module capability flags** (`WriteBackCapability`): `supported`, `dry_run_only`, human `label`.
4. **Calendar** insert is live after confirm (Sprint 8) with opt-in `calendar.events` scope.
5. **Gmail send** is live after confirm (Sprint 18) with separate opt-in `gmail.send` scope (`?gmail_send=1`). Cancel performs no remote send. Audit stages: propose / cancel / execute.
6. **Gmail labels** apply/remove is live after confirm (Sprint 26) with separate opt-in `gmail.modify` scope (`?gmail_modify=1`). Cancel performs no remote mutation. No bulk silent labeling.
7. Out of scope: silent automation, multi-user ACLs, bulk send, cloud secret managers.

## Consequences

- **Positive:** Three live confirm-first surfaces (Calendar + Gmail send + Gmail labels) share the same audit trail.
- **Negative:** Operators must reconsent for each write scope; primary-calendar-only insert; send is irreversible from Crawley.
- **Follow-up:** Undo/delete from audit row; draft-only (Gmail drafts API) if preferred later.
