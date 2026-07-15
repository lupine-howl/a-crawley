# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and Cursor agent roles.

**Working title:** Crawley — local-first personal assistant.

## Run locally (WSL / Linux)

Requires [uv](https://docs.astral.sh/uv/) (installs/uses Python 3.12+ for you — no system Python install needed).

```bash
# From the repo root
uv sync
cp .env.example .env
# Set OPENAI_API_KEY for Investment / Gmail summaries (or configure in Settings after start)
# Set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for Gmail (Desktop OAuth app; Gmail API enabled)
uv run python -m crawley
```

Open http://127.0.0.1:8000 in your browser.

**Settings:** Theme (Paper / Slate / Ink / Moss) and LLM provider/model/key live under **Settings**. Theme applies immediately (cookie). Saved LLM settings are stored in `data/secrets/settings.json` and **override** `.env` when a key is saved there; leave the key blank to keep the stored/env value. Changes apply on the next request (no restart). Use **Test connection** to verify the provider.

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
| UX expert | `.cursor/rules/ux-expert.mdc` | IA, themes, interaction specs (`docs/ux.md`) |

Shared contract: [`AGENTS.md`](./AGENTS.md)

### UX expert — design pass

`@ux-expert`, then:

> You are the UX expert. Read PRODUCT.md, docs/architecture.md, docs/sprints/current.md, and docs/ux.md. Interview me about visual/interaction goals for this sprint, then write docs/ux.md with implementable guidance for the architect. Do not implement application code.

## Delivery status

- **Sprint 0** — bootstrap (archived): [`docs/sprints/archive/sprint-0-bootstrap.md`](./docs/sprints/archive/sprint-0-bootstrap.md)
- **Sprint 1** — local shell + lite Investment & Gmail (closed): [`docs/sprints/archive/sprint-1-local-shell.md`](./docs/sprints/archive/sprint-1-local-shell.md)
- **Sprint 2** — themes, LLM settings, Markdown, home glance (active): [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Sprints 3–5** — planned: [`docs/sprints/planned/`](./docs/sprints/planned/README.md)

## Bootstrap sequence (complete)

1. **PO Interview 1** — `PRODUCT.md` + `ROADMAP.md`
2. **PO Interview 2** — `BACKLOG.md` + Planned Sprint 1
3. **Architect Interview 1** — `docs/architecture.md`
4. **Architect Interview 2** — implement Sprint 1

Ongoing: PO plans the next sprint in `docs/sprints/current.md`; UX expert may lock `docs/ux.md` for UI stories; architect implements that file only.

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) — project brief
- [`ROADMAP.md`](./ROADMAP.md) — Now / Next / Later
- [`BACKLOG.md`](./BACKLOG.md) — prioritized work
- [`docs/sprints/current.md`](./docs/sprints/current.md) — active sprint
- [`docs/architecture.md`](./docs/architecture.md) — technical decisions
- [`docs/ux.md`](./docs/ux.md) — UX / visual & interaction design

## Enabling a rule on an Agent chat

These rules use `alwaysApply: false`. Type `@product-owner`, `@architect-developer`, or `@ux-expert` in Agent chat, then confirm via the context ring → **Rules**.

## How to run Sprint 2

Optional design pass first — `@ux-expert` (see prompt under Agent roles).

Then `@architect-developer`:

> Read AGENTS.md, docs/architecture.md, docs/ux.md, and docs/sprints/current.md. Implement Sprint 2 in order: S2.1 themes, S2.2 LLM settings & connection test, S2.3 Markdown summaries, S2.4 home At a glance (persisted last runs). If AC is unclear, mark the story blocked and stop. Do not expand into B9–B12.

PO review when done: check demo bar in `docs/sprints/current.md`, then archive and plan Sprint 3.
