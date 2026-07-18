# a-crawley

**Crawley** — local-first personal assistant (ASX desk + Sender Inbox).

| Layer | Location |
|-------|----------|
| **Product UI** | `apps/crawley` (Phone Preview host) + `packages/crawley-*` packs |
| **Analytics** | `src/crawley` — Python JSON API + daemons |

**Monorepo:** matches phone-preview Phase 4 plug-and-play shape — [`docs/migration-monorepo.md`](./docs/migration-monorepo.md) · [ADR-010](./docs/adr/010-monorepo-layout.md)  
**Pivot:** [`docs/migration-phone-preview.md`](./docs/migration-phone-preview.md) · [ADR-009](./docs/adr/009-phone-preview-analytics.md)

```
apps/crawley/
packages/crawley-analytics-client/
packages/crawley-asx/
packages/crawley-inbox/
packages/crawley-settings/
src/crawley/          # Python analytics
```

## Run analytics (WSL / Linux)

Requires [uv](https://docs.astral.sh/uv/) (Python 3.12+).

```bash
uv sync
cp .env.example .env
uv run python -m crawley
```

JSON only at http://127.0.0.1:8000 (`/health`, `/v1/…`). Contract: [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md).

**OAuth:** `/modules/gmail/oauth/start` (deep-link from UI). Optional `CRAWLEY_UI_ORIGIN` for return link.

**Daemons (optional):**

```bash
export CRAWLEY_ASX_WORKER=daemon CRAWLEY_GMAIL_WORKER=daemon
uv run python -m crawley
uv run crawley-asx-scanner watch
uv run crawley-gmail-ingest watch
```

## Run product UI (+ API)

Requires Node 20+ and `uv` (analytics). From repo root:

```bash
npm install
npm run dev
```

That starts **both** the analytics API (`:8000`) and Vite UI via `@crawley/app`. Vite proxies `/api/analytics` → `:8000`.

Split processes if you prefer:

```bash
npm run dev:api   # uv run python -m crawley
npm run dev:ui    # Vite only
```

Packs are workspace packages (`@crawley/asx`, `@crawley/inbox`, `@crawley/settings`). There is no root `crawley-ui/` — that host lives at `apps/crawley`.

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture + implement `current.md` only |
| UX expert | `.cursor/rules/ux-expert.mdc` | Pack IA / Phone Preview UX guidance |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Delivery status

- **Sprints 1–35** — closed (migration to Phone Preview complete): [`docs/sprints/archive/`](./docs/sprints/archive/)
- **Monorepo layout** — `apps/` + `packages/crawley-*` for upstream Phase 4 merge
- **No active sprint** — [`docs/sprints/current.md`](./docs/sprints/current.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) · [`ROADMAP.md`](./ROADMAP.md) · [`BACKLOG.md`](./BACKLOG.md)
- [`docs/architecture.md`](./docs/architecture.md) · [`docs/migration-monorepo.md`](./docs/migration-monorepo.md)
- [`docs/build/consuming-published-core.md`](./docs/build/consuming-published-core.md)
