# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and Cursor agent roles.

**Working title:** Crawley — local-first personal assistant.

## Run locally (WSL / Linux)

Requires [uv](https://docs.astral.sh/uv/) (installs/uses Python 3.12+ for you — no system Python install needed).

```bash
# From the repo root
uv sync
cp .env.example .env
# Set OPENAI_API_KEY for module summaries (or configure in Settings after start)
# Set GOOGLE_CLIENT_ID + GOOGLE_CLIENT_SECRET for Gmail/Calendar (Desktop OAuth; enable Gmail API + Calendar API)
uv run python -m crawley
```

Open http://127.0.0.1:8000 in your browser.

**Settings:** Theme (Paper / Slate / Ink / Moss), LLM provider/model/key, and editable summary prompts live under **Settings**. Theme applies immediately (cookie). Saved LLM settings are stored in `data/secrets/settings.json` and **override** `.env` when a key is saved there; leave the key blank to keep the stored/env value. Changes apply on the next request (no restart). Use **Test connection** to verify the provider.

Secrets stay local:

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored; see `.env.example`) |
| `data/` | DuckDB, caches, crawl/mail/calendar artifacts (gitignored except `.gitkeep`) |
| `data/secrets/` | OAuth tokens (`google_token.json`; legacy `gmail_token.json`) and `settings.json` |

Default bind is localhost only (`127.0.0.1:8000`). To reach a phone on the same LAN:

1. Settings → **Network / LAN** → enable “Allow LAN access” → **Save** → **restart** the process  
   (or set `CRAWLEY_HOST=0.0.0.0` in `.env` and restart).
2. Open `http://<your-lan-ip>:8000` from the phone (WSL2: publish/forward the port from Windows if needed).
3. **Trusted LAN only — there is no login.** Disable LAN in Settings (or clear `CRAWLEY_HOST`) and restart to return to localhost-only.

`CRAWLEY_HOST` in the environment overrides the Settings toggle until removed.

**Dev hot reload:** set `CRAWLEY_RELOAD=1` in `.env` and restart once. Uvicorn then restarts the app when files under `src/crawley/` change (including after `git pull`). Leave it off for day-to-day phone/LAN use.

**Google OAuth notes:** redirect URI used is `http://127.0.0.1:8000/modules/gmail/oauth/callback` — add it under **Authorized redirect URIs** (not JavaScript origins). Enable **Gmail API** and **Google Calendar API**. Scopes are read-only for both. If you previously connected Gmail only, use **Connect Google** again to grant Calendar. Local HTTP is allowed automatically for `127.0.0.1` / `localhost`.

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
- **Sprints 1–5** — PoC closed; retro: [`docs/sprints/archive/sprints-1-5-retrospective.md`](./docs/sprints/archive/sprints-1-5-retrospective.md)
- **Sprint 5** — LAN + Work + write-back design (archived): [`docs/sprints/archive/sprint-5-lan-work-writeback.md`](./docs/sprints/archive/sprint-5-lan-work-writeback.md)
- **Sprint 6** — Co-parenting + DIY lite (**ready**): [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Sprints 7–20** — planned: [`docs/sprints/planned/`](./docs/sprints/planned/README.md)

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

## Next delivery

`@architect-developer` implements [`docs/sprints/current.md`](./docs/sprints/current.md) (**Sprint 6**). Optional `@ux-expert` pass for Co-parenting schedule forms first.
