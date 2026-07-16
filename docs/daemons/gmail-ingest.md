# Gmail / Sender Inbox ingest daemon

**Sprint 34 / B97** · Mirror of [asx-scanner](asx-scanner.md) · Related [ADR-009](../adr/009-phone-preview-analytics.md)

## Process boundary

| Process | Role |
|---------|------|
| **Analytics API** (`uv run python -m crawley`) | `/health`, `/v1/…`, OAuth, optional in-process ingest |
| **gmail-ingest** (`uv run python -m crawley.daemons.gmail_ingest`) | Owns the one-message-at-a-time ingest loop |

Shared coordination is the **worker store** (`data/gmail/sender_inbox/ingest_state.json` + messages/profiles/todos). The UI never talks to Gmail/LLM; it starts jobs and reads `/v1/jobs/gmail-ingest` + `/v1/gmail/senders`.

Threads remain OK **inside** the ingest process. No Celery.

## Modes

### Default — in-process (PoC)

API submits ingest to its `ThreadPoolExecutor`. No second process required.

```bash
uv run python -m crawley
# UI / curl POST /v1/gmail/ingest/start
```

### Daemon — external worker

1. API queues work on disk (`start_requested`) instead of running the loop.
2. Ingest process claims and runs.

```bash
# Terminal A — API
export CRAWLEY_GMAIL_WORKER=daemon
uv run python -m crawley

# Terminal B — worker
uv run python -m crawley.daemons.gmail_ingest watch
# or: uv run crawley-gmail-ingest watch
```

One-shot (no watch loop):

```bash
uv run crawley-gmail-ingest once --force
```

## Job status

| Status | Meaning |
|--------|---------|
| `queued` | API accepted start; waiting for daemon claim |
| `busy` | Ingesting messages |
| `paused` / `idle` / `done` / `error` | Same semantics as HTMX PoC |

`GET /health` → `gmail_worker`: `in_process` | `daemon`.

## Caps

Default PoC cap is 20 (`CRAWLEY_SENDER_INBOX_CAP` / Settings). With **Local Llama**, ingest + keep-max pad to the hard ceiling (**200**) — same rationale as ASX (no per-call cost).

## Supervisord sketch

```ini
[program:crawley-api]
command=uv run python -m crawley
directory=/path/to/a-crawley
environment=CRAWLEY_GMAIL_WORKER="daemon",CRAWLEY_ASX_WORKER="daemon"

[program:crawley-gmail-ingest]
command=uv run crawley-gmail-ingest watch
directory=/path/to/a-crawley
autostart=true
autorestart=true
```
