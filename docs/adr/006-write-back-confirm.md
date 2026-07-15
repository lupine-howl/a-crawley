# ADR-006: Write-back requires explicit confirm (draft-first)

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Crawley modules may eventually mutate Google (Gmail send/labels, Calendar insert) and other systems. Product constraints forbid silent automation and multi-user ACLs. Sprint 5 designs the contract so later sprints can add mutations safely.

## Decision

1. **Explicit user confirm** is required before any live mutation. No background or scheduled writes in the personal OS PoC.
2. **Draft-first stages:** propose → show diff/draft → confirm → execute → append a **local audit log**.
3. **Per-module capability flags** (`WriteBackCapability`): `supported`, `dry_run_only`, human `label`.
4. Until a dedicated implementation sprint: **`write_back()` is dry-run only** — records intent under `data/writeback_audit.jsonl` and **must not** call Gmail send / Calendar insert APIs.
5. Out of scope: silent automation, multi-user ACLs, cloud secret managers.

## Consequences

- **Positive:** Modules can declare future write paths without shipping mutations; operators can exercise dry-run hooks now.
- **Negative:** Confirm UI / diff rendering is deferred; dry-run is weaker than a full staged UX.
- **Later:** Real write-back sprint after ADR soak; expand audit and confirm UI per module.
