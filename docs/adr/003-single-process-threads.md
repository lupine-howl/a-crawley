# ADR-003: Single process with threads for crawl I/O

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Deploy target is a personal WSL/Linux machine. Crawl and fetch benefit from concurrency; a full worker/queue service adds operational surface for a solo PoC.

## Decision

Run Crawley as **one Python process** (Uvicorn + FastAPI). Use a **thread pool** (e.g. `ThreadPoolExecutor`) for I/O-bound crawl/fetch. No separate worker service, Celery, or multi-container Compose requirement for PoC.

## Consequences

- **Positive:** Simple launch and debugging; enough parallelism for network-bound work.
- **Negative:** CPU-heavy ML in-request can block; long jobs need clear status UX and careful shared-state rules (especially DuckDB).
- **Later:** Process/worker split or job queue only if PoC proves the single process insufficient.
