# ASX scanner daemon

**Sprint 33 / B96** · Evolves [ADR-003](../adr/003-single-process-threads.md) · Related [ADR-009](../adr/009-phone-preview-analytics.md)

## Process boundary

| Process | Role |
|---------|------|
| **Analytics API** (`uv run python -m crawley`) | `/health`, `/v1/…`, OAuth, optional in-process scan |
| **asx-scanner** (`uv run python -m crawley.daemons.asx_scanner`) | Owns the one-ticker-at-a-time scan loop |

Shared coordination is the **worker store** (`data/investment/asx/scan_state.json` + scans/profiles). The UI never talks to Yahoo/LLM; it starts jobs and reads `/v1/jobs/asx-scan`.

Threads remain OK **inside** the scanner process. No Celery.

## Modes

### Default — in-process (PoC)

API submits the scan to its `ThreadPoolExecutor`. No second process required.

```bash
uv run python -m crawley
# UI / curl POST /v1/asx/scan/start
```

### Daemon — external worker

1. API queues work on disk (`start_requested`) instead of running the loop.
2. Scanner process claims and runs.

```bash
# Terminal A — API
export CRAWLEY_ASX_WORKER=daemon
uv run python -m crawley

# Terminal B — worker
uv run python -m crawley.daemons.asx_scanner watch
# or: uv run crawley-asx-scanner watch
```

Then `POST /v1/asx/scan/start` (optionally `{ "force": true }`) → job status `queued` then `busy` via `/v1/jobs/asx-scan`.

### One-shot (no API)

```bash
uv run python -m crawley.daemons.asx_scanner once --force
uv run python -m crawley.daemons.asx_scanner status
```

## CLI

| Command | Purpose |
|---------|---------|
| `once [--force]` | Run one scan in this process |
| `watch [--poll 1.0]` | Loop: claim API-queued starts |
| `status` | Print job JSON from disk |

## supervisord example

```ini
[program:crawley-api]
command=uv run python -m crawley
directory=/path/to/a-crawley
environment=CRAWLEY_ASX_WORKER="daemon"
autostart=true
autorestart=true

[program:crawley-asx-scanner]
command=uv run python -m crawley.daemons.asx_scanner watch
directory=/path/to/a-crawley
autostart=true
autorestart=true
```

## Stop / pause

`POST /v1/asx/scan/stop` (or pause) sets `pause_requested` on disk (or cancels a queued start). The daemon loop honours pause between tickers.
