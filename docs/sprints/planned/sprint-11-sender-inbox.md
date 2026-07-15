# Sprint 11 — Sender Inbox PoC (+ UX contract)

**Status:** promoted to [`../current.md`](../current.md) (Sprint 11 ready)
**Duration:** one symbolic week  
**Backlog refs:** B65–B70  
**Previous shelved:** Co-parenting/DIY sprint filed as shelved `sprint-11.md`  
**Architecture:** background worker + Gmail read; DuckDB/files for categories/profiles/todos  
**UX:** `@ux-expert` locks Sender Inbox + ASX dashboard contracts before implement stories

## Goal

Pivot Gmail from skim-summary toward a **sender-grouped Inbox**: background process pulls **one email at a time**, LLM-categorizes useful metrics, builds **sender profiles**, extracts **todos**, PoC capped at **~20 emails**. Also deliver the **UX design contract** for both Sender Inbox and ASX dashboards (ASX implementation in Sprint 7–8).

## Demo

See [`../current.md`](../current.md).
