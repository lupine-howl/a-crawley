# a-crawley

**Crawley** — local-first personal assistant (ASX desk + Sender Inbox).

| Layer | Location |
|-------|----------|
| **Product UI** | `apps/crawley` + `packages/crawley-*` |
| **Analytics** | `services/crawley` — Python JSON API + daemons + `data/` + pytest |

**Monorepo shape:** phone-preview Phase 4 — [`docs/migration-monorepo.md`](./docs/migration-monorepo.md) · [ADR-010](./docs/adr/010-monorepo-layout.md)

```
apps/crawley/                 # Vite / Phone Preview host
packages/crawley-*            # portable packs
services/crawley/             # Python analytics (uv)
```

Copy into phone-preview as-is: `apps/crawley`, `packages/crawley-*`, `services/crawley`.

## Run

Requires Node 20+ and [uv](https://docs.astral.sh/uv/) (Python 3.12+).

```bash
cd services/crawley && uv sync && cp -n .env.example .env && cd ../..
npm install
npm run dev          # or: npm run dev:crawley  → API :8000 + Vite
```

```bash
npm run dev:api      # analytics only
npm run dev:ui       # Vite only
npm run test:api     # pytest in services/crawley
```

JSON contract: [`docs/api/presentation-v1.md`](./docs/api/presentation-v1.md).  
OAuth: `/modules/gmail/oauth/start`. Optional `CRAWLEY_UI_ORIGIN`.

**Daemons (optional)** — from `services/crawley`:

```bash
export CRAWLEY_ASX_WORKER=daemon CRAWLEY_GMAIL_WORKER=daemon
uv run python -m crawley
uv run crawley-asx-scanner watch
uv run crawley-gmail-ingest watch
```

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture + implement `current.md` only |
| UX expert | `.cursor/rules/ux-expert.mdc` | Pack IA / Phone Preview UX guidance |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) · [`ROADMAP.md`](./ROADMAP.md) · [`BACKLOG.md`](./BACKLOG.md)
- [`docs/architecture.md`](./docs/architecture.md) · [`docs/migration-monorepo.md`](./docs/migration-monorepo.md)
