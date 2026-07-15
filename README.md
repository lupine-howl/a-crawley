# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and two Cursor agent roles.

**Working title:** Crawley — local-first personal assistant.

## Run locally (WSL / Linux)

Requires [uv](https://docs.astral.sh/uv/) (installs/uses Python 3.12+ for you — no system Python install needed).

```bash
# From the repo root
uv sync
cp .env.example .env
# Set OPENAI_API_KEY for Investment / Gmail summaries
# Set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for Gmail (Desktop OAuth app; Gmail API enabled)
uv run python -m crawley
```

Open http://127.0.0.1:8000 in your browser.

Secrets stay local:

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored; see `.env.example`) |
| `data/` | DuckDB, caches, crawl/mail artifacts (gitignored except `.gitkeep`) |
| `data/secrets/` | OAuth token files (e.g. `gmail_token.json`) |

Default bind is localhost only (`127.0.0.1:8000`). Override with `CRAWLEY_HOST` / `CRAWLEY_PORT` if needed.

**Gmail OAuth notes:** redirect URI used is `http://127.0.0.1:8000/modules/gmail/oauth/callback` — add it under **Authorized redirect URIs** (not JavaScript origins). Local HTTP is allowed automatically for `127.0.0.1` / `localhost`.

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture doc, then implements sprint |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Delivery status

- **Sprint 0** — bootstrap (archived): [`docs/sprints/archive/sprint-0-bootstrap.md`](./docs/sprints/archive/sprint-0-bootstrap.md)
- **Sprint 1** — local shell + lite Investment & Gmail (closed): [`docs/sprints/archive/sprint-1-local-shell.md`](./docs/sprints/archive/sprint-1-local-shell.md)
- **Sprint 2** — themes & LLM settings (active): [`docs/sprints/current.md`](./docs/sprints/current.md)

## Bootstrap sequence (complete)

1. **PO Interview 1** — `PRODUCT.md` + `ROADMAP.md`
2. **PO Interview 2** — `BACKLOG.md` + Planned Sprint 1
3. **Architect Interview 1** — `docs/architecture.md`
4. **Architect Interview 2** — implement Sprint 1

Ongoing: PO plans the next sprint in `docs/sprints/current.md`; architect implements that file only.

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) — project brief
- [`ROADMAP.md`](./ROADMAP.md) — Now / Next / Later
- [`BACKLOG.md`](./BACKLOG.md) — prioritized work
- [`docs/sprints/current.md`](./docs/sprints/current.md) — active sprint
- [`docs/architecture.md`](./docs/architecture.md) — technical decisions

## Enabling a rule on an Agent chat

These rules use `alwaysApply: false`. Type `@product-owner` or `@architect-developer` in Agent chat, then confirm via the context ring → **Rules**.

## How to run Sprint 2

`@architect-developer`, then:

> Read AGENTS.md, docs/architecture.md, and docs/sprints/current.md. Implement Sprint 2 (S2.1 themes, then S2.2 LLM settings & connection test) in order. If AC is unclear, mark the story blocked and stop. Do not expand into B9–B12.

PO review when done: check demo bar in `docs/sprints/current.md`, then archive and plan Sprint 3.
