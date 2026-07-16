# a-crawley

**Crawley analytics** — local-first Python brain (JSON API + daemons) for ASX desk and Sender Inbox.

**Product UI:** separate **`crawley-ui`** app on [Phone Preview](https://github.com/lupine-howl/phone-preview) (published npm packages).  
**Pivot:** [`docs/migration-phone-preview.md`](./docs/migration-phone-preview.md) · [ADR-009](./docs/adr/009-phone-preview-analytics.md)

## Run analytics (WSL / Linux)

Requires [uv](https://docs.astral.sh/uv/) (Python 3.12+).

```bash
uv sync
cp .env.example .env
# OPENAI_API_KEY and/or LocalLlama; GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for Gmail
uv run python -m crawley
```

Analytics listens on http://127.0.0.1:8000 — **JSON only** (`/health`, `/v1/…`, OpenAPI). There is **no** Jinja/HTMX product dashboard (removed Sprint 35).  
Contract: [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md).

**OAuth:** Connect Google from `crawley-ui` deep-links to  
`/modules/gmail/oauth/start` → callback → minimal “connected” page → return to UI.  
Optional: `CRAWLEY_UI_ORIGIN=http://127.0.0.1:5173` for a return link on that page.

**Secrets (analytics host only — never in Vite):**

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored) |
| `data/` | DuckDB, crawl/mail artifacts (gitignored) |
| `data/secrets/` | OAuth tokens, settings |

**LAN / Tailscale:** `CRAWLEY_HOST=0.0.0.0`; trusted network only; OAuth redirect URIs must match the Host you Connect from.

**Daemons (optional):**

```bash
export CRAWLEY_ASX_WORKER=daemon CRAWLEY_GMAIL_WORKER=daemon
uv run python -m crawley
uv run crawley-asx-scanner watch
uv run crawley-gmail-ingest watch
```

## crawley-ui (product)

App lives in [`crawley-ui/`](./crawley-ui/) on published `@phone-preview/core` ≥ 0.6.1.

```bash
# Terminal A (repo root) — analytics
uv run python -m crawley

# Terminal B
cd crawley-ui && npm install && npm run dev
```

Vite proxies `/api/analytics` → this process (`:8000`). Persistence: Phone Preview IndexedDB (± Turso/Duck via Connections).  
Recipe pin: [`docs/build/consuming-published-core.md`](./docs/build/consuming-published-core.md).

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture + implement `current.md` only |
| UX expert | `.cursor/rules/ux-expert.mdc` | Pack IA / Phone Preview UX guidance |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Delivery status

- **Sprints 1–35** — HTMX PoC → dual-desk depth → Phone Preview migration (**closed**): [`docs/sprints/archive/`](./docs/sprints/archive/)
- **No active sprint** — migration band complete; see [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Shelved / quarantine** — Calendar + lite modules: [`src/crawley/_quarantine/`](./src/crawley/_quarantine/) · [`docs/sprints/shelved/README.md`](./docs/sprints/shelved/README.md)
- **Daemons:** [`docs/daemons/asx-scanner.md`](./docs/daemons/asx-scanner.md) · [`docs/daemons/gmail-ingest.md`](./docs/daemons/gmail-ingest.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) · [`ROADMAP.md`](./ROADMAP.md) · [`BACKLOG.md`](./BACKLOG.md)
- [`docs/architecture.md`](./docs/architecture.md) · [`docs/migration-phone-preview.md`](./docs/migration-phone-preview.md)
- [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md) · [`docs/api/openapi-v1.json`](./docs/api/openapi-v1.json)
- [`docs/build/consuming-published-core.md`](./docs/build/consuming-published-core.md)
