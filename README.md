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

Legacy HTMX UI may still open at http://127.0.0.1:8000 until Sprint 35 — **not** the product surface. Prefer JSON (`/health`, `/v1/…` as Sprint 31 lands) + `crawley-ui`.

**Secrets (analytics host only — never in Vite):**

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored) |
| `data/` | DuckDB, crawl/mail artifacts (gitignored) |
| `data/secrets/` | OAuth tokens, settings |

**LAN / Tailscale:** Settings or `CRAWLEY_HOST=0.0.0.0`; trusted network only; OAuth redirect URIs must match the Host you Connect from. Tokens stay on the server.

## crawley-ui (product)

Scaffold/run via **npm** using **published** `@phone-preview/*` packages (ask Phone Preview team for the current create recipe). Dev-proxy `/api/analytics` → this process. UI persistence is primarily **IndexedDB** (± Turso/Duck sync per Phone Preview).

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture + implement `current.md` only |
| UX expert | `.cursor/rules/ux-expert.mdc` | Pack IA / Phone Preview UX guidance |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Delivery status

- **Sprints 1–30** — HTMX PoC + dual-desk depth (**closed**): [`docs/sprints/archive/`](./docs/sprints/archive/)
- **Sprint 31** — Analytics JSON API ASX + jobs (**current**): [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Sprints 32–35** — `crawley-ui`, ASX daemon, Gmail API/pack, HTMX cutover: [`docs/sprints/planned/README.md`](./docs/sprints/planned/README.md)
- **Shelved** — Calendar product, lite modules, old depth 31–40 stubs: [`docs/sprints/shelved/README.md`](./docs/sprints/shelved/README.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) · [`ROADMAP.md`](./ROADMAP.md) · [`BACKLOG.md`](./BACKLOG.md)
- [`docs/architecture.md`](./docs/architecture.md) · [`docs/migration-phone-preview.md`](./docs/migration-phone-preview.md)

## Next delivery

`@architect-developer` implements [`docs/sprints/current.md`](./docs/sprints/current.md) (**Sprint 31** — `/v1` ASX + jobs + OpenAPI). Do not add Jinja product features.
