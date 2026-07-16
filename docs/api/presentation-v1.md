# Presentation API v1 — field contract

**Consumers:** `crawley-ui` (Phone Preview packs)  
**Producer:** Crawley analytics (this repo)  
**OpenAPI:** [`openapi-v1.json`](openapi-v1.json) · also served at runtime `/openapi.json`  
**ADR:** [ADR-009](../adr/009-phone-preview-analytics.md)

## Worker store vs presentation

| Role | Where | Who reads |
|------|--------|-----------|
| **Worker store** | `data/investment/asx/*.json`, DuckDB, fetch scratch | Analytics workers only |
| **Presentation** | JSON DTOs from `/v1/…` | `crawley-ui` only |

UI **must not** open worker files, scrape Yahoo/Gmail, or call LLM providers. Start jobs and read presentation endpoints.

OAuth redirect URIs remain on the analytics host.

## Endpoints (Sprint 31)

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/health` | Liveness |
| `GET` | `/v1/asx/companies` | Active-set company list |
| `GET` | `/v1/asx/companies/{ticker}` | Company detail |
| `POST` | `/v1/asx/scan/start` | Start scan (`{ "force": true }` re-runs when complete; Local Llama expands active set to hard ceiling) |
| `POST` | `/v1/asx/scan/stop` | Request stop (pause) |
| `POST` | `/v1/asx/scan/pause` | Request pause |
| `POST` | `/v1/asx/scan/resume` | Resume after pause |
| `POST` | `/v1/asx/scan/reset` | Clear PoC scan/profile data |
| `GET` | `/v1/asx/recommendations` | Recommendation rows |
| `POST` | `/v1/asx/recommendations/refresh` | Regenerate recommendations |
| `GET` | `/v1/asx/portfolio` | Paper portfolio view |
| `POST` | `/v1/asx/portfolio/trade` | Record paper trade |
| `GET`/`POST` | `/v1/asx/clusters` (+ `/refresh`) | News themes |
| `GET` | `/v1/asx/alerts` | Open alerts + rules |
| `GET` | `/v1/asx/holdings` | Holdings journal |
| `GET`/`PUT` | `/v1/asx/companies/{ticker}/notebook` | Research notebook |
| `GET`/`PUT` | `/v1/settings/llm` | LLM provider/model (no key echoed) |
| `POST` | `/v1/settings/llm/test` | Test connection |
| `GET` | `/v1/settings/llm/models` | Model list (OpenAI or Ollama tags) |
| `GET`/`PATCH` | `/v1/settings/scale` | Desk caps (`local_llama_uncapped`) |
| `GET` | `/v1/jobs` | Known jobs |
| `GET` | `/v1/jobs/{job_id}` | Job status (`asx-scan`) |

## `CompanyListItem`

| Field | Type | Notes |
|-------|------|-------|
| `ticker` | string | ASX code |
| `name` | string | Company name |
| `sector` | string | Sector or `—` |
| `scan_status` | string | `pending` / `ready` / `error` / … |
| `change_pct` | number\|null | From last scan snapshot |
| `move` | string | Display move e.g. `+1.20%` |
| `sentiment` | string | Normalized desk sentiment |
| `scanned_at` | string | ISO timestamp or empty |
| `error` | string | Per-company scan error |

List envelope: `companies`, `count`, `active_set_size`.

## `CompanyDetailResponse`

| Field | Type | Notes |
|-------|------|-------|
| `ticker`, `name`, `sector` | string | Identity |
| `scan_status` | string | Scan row status |
| `snapshot` | object | `price`, `change_pct`, `volume`, `currency`, `sentiment`, `headline`, `as_of`, `gaps[]` |
| `move` | string | Display |
| `headlines[]` | object | `title`, `url`, `source` |
| `sources_used[]` | string | Source ids used in last scan |
| `profile` | object | `status`, `markdown`, `error`, `updated_at` |
| `disclaimer` | string | Non-licensed research notice |

## `JobStatusResponse` (`id = asx-scan`)

| Field | Type | Notes |
|-------|------|-------|
| `id` | string | Stable id: `asx-scan` |
| `kind` | string | `asx_scan` |
| `status` | string | `idle` \| `busy` \| `paused` \| `done` \| `error` |
| `message` | string | Operator-facing line |
| `error` | string | Last job-level error |
| `progress` | object | `processed`, `total`, `remaining`, `current_ticker` |
| `updated_at` | string | ISO |
| `pause_requested` | bool | Pause flag |

Scan actions return `{ ok, message, job }`.

## Compatibility

- Additive fields are preferred for minor revisions.
- Breaking changes bump the `/v1` major path or document a migration in this file.
