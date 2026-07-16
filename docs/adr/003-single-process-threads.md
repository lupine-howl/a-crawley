# ADR-003: Process model — API + optional ASX daemon (threads inside workers)

- **Status:** Accepted (evolved) — see also [ADR-009](009-phone-preview-analytics.md)
- **Date:** 2026-07-15 (evolved 2026-07-16, Sprint 33)
- **Supersedes:** “always one Uvicorn process owns every scan forever”

## Context

Deploy target is a personal WSL/Linux machine. Crawl and fetch benefit from concurrency; a full Celery/K8s stack is unnecessary for a solo PoC. ADR-009 splits product UI from analytics and calls for **clear daemon entrypoints** so long-running ASX scans are not ambiguously owned by the API process alone.

## Decision

1. **Default PoC:** Analytics API may still run the ASX scan on an in-process `ThreadPoolExecutor` (`CRAWLEY_ASX_WORKER` unset).
2. **Explicit daemon (Sprint 33):** Prefer `python -m crawley.daemons.asx_scanner` (`once` / `watch`) as the scan-loop owner. With `CRAWLEY_ASX_WORKER=daemon`, the API **queues** starts via `scan_state.json`; the daemon **claims** and runs. Job status remains on `/v1/jobs/asx-scan`.
3. **Threads OK inside a worker process.** No Celery, Redis queue, or multi-host orchestrator required.
4. Documented ops: [`docs/daemons/asx-scanner.md`](../daemons/asx-scanner.md) (incl. supervisord example).

## Consequences

- **Positive:** Clear process boundary; API can stay responsive; same presentation contract for UI/`curl`.
- **Negative:** Two processes to run in daemon mode; operators must set `CRAWLEY_ASX_WORKER=daemon` consistently.
- **Neutral:** Worker scratch stays on the filesystem (ADR-002); presentation is still JSON DTOs.
