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

Legacy HTMX UI may still open at http://127.0.0.1:8000 until Sprint 35 — **not** the product surface. Prefer JSON (`/health`, `/v1/…`) + `crawley-ui`. Contract: [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md).

**Secrets (analytics host only — never in Vite):**

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored) |
| `data/` | DuckDB, crawl/mail artifacts (gitignored) |
| `data/secrets/` | OAuth tokens, settings |

**LAN / Tailscale:** Settings or `CRAWLEY_HOST=0.0.0.0`; trusted network only; OAuth redirect URIs must match the Host you Connect from. Tokens stay on the server.

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

- **Sprints 1–33** — HTMX PoC + dual-desk depth + analytics `/v1` + `crawley-ui` + ASX daemon (**closed**): [`docs/sprints/archive/`](./docs/sprints/archive/)
- **Sprint 34** — Sender Inbox API + pack (**current**): [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Sprint 35** — HTMX cutover: [`docs/sprints/planned/README.md`](./docs/sprints/planned/README.md)
- **Shelved** — Calendar product, lite modules, old depth 31–40 stubs: [`docs/sprints/shelved/README.md`](./docs/sprints/shelved/README.md)
- **ASX daemon ops:** [`docs/daemons/asx-scanner.md`](./docs/daemons/asx-scanner.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) · [`ROADMAP.md`](./ROADMAP.md) · [`BACKLOG.md`](./BACKLOG.md)
- [`docs/architecture.md`](./docs/architecture.md) · [`docs/migration-phone-preview.md`](./docs/migration-phone-preview.md)
- [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md) · [`docs/api/openapi-v1.json`](./docs/api/openapi-v1.json)
- [`docs/build/consuming-published-core.md`](./docs/build/consuming-published-core.md)

## Next delivery

`@architect-developer` implements [`docs/sprints/current.md`](./docs/sprints/current.md) (**Sprint 34** — Sender Inbox JSON API + `senderInboxPack`). Do not add Jinja product features.
