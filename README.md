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

**Settings:** Theme (Paper / Slate / Ink / Moss), Network/LAN, **Update** (git pull), LLM provider/model/key (or LocalLlama base URL/timeout), editable summary prompts, and write-back audit live under **Settings**. Theme applies immediately (cookie). Saved LLM settings are stored in `data/secrets/settings.json` and **override** `.env` when a key is saved there; leave the key blank to keep the stored/env value. Changes apply on the next request (no restart). Use **Test connection** to verify the provider.

**Update (git pull):** Settings → **Update** → **Pull latest** runs `git fetch` + fast-forward-only merge of the **current branch’s upstream**. Allowed on localhost and trusted LAN/Tailscale (warns when LAN-bound — there is still no login gate). For hot reload after a pull that changes `src/crawley/`, set `CRAWLEY_RELOAD=1` and restart once beforehand. Merge conflicts / diverged history must be fixed in a terminal — the UI will not resolve them.

**Local LLM (Ollama):** install/run [Ollama](https://ollama.com/), `ollama pull llama3.2` (or your model), then Settings → Provider **LocalLlama** → base URL `http://127.0.0.1:11434` → model id → **Test connection**. OpenAI remains selectable anytime.

Secrets stay local:

| Path | Purpose |
|------|---------|
| `.env` | API keys (gitignored; see `.env.example`) |
| `data/` | DuckDB, caches, crawl/mail/calendar artifacts (gitignored except `.gitkeep`) |
| `data/secrets/` | OAuth tokens (`google_token.json`; legacy `gmail_token.json`) and `settings.json` |

Default bind is localhost only (`127.0.0.1:8000`). To reach a phone on the same LAN or over **Tailscale**:

1. Settings → **Network / LAN** → enable “Allow LAN / Tailscale access” → **Save** → **restart** the process  
   (or set `CRAWLEY_HOST=0.0.0.0` in `.env` and restart).
2. Open `http://<lan-or-tailscale-ip>:8000` from the other device. On startup, Crawley prints **Try also** URLs when LAN-bound.
3. **Trusted network only — there is no login.** Disable LAN in Settings (or clear `CRAWLEY_HOST`) and restart to return to localhost-only.

**Tailscale / WSL tip:** Tailscale must run in the **same** environment as Crawley. If Crawley is in WSL and Tailscale is only on Windows, the Windows Tailscale IP often will not reach the WSL process — install Tailscale inside that WSL distro, or forward the Windows port to WSL. `CRAWLEY_HOST` in the environment overrides the Settings toggle until removed.

**Dev hot reload:** set `CRAWLEY_RELOAD=1` in `.env` and restart once. Uvicorn then restarts the app when files under `src/crawley/` change (including after Settings → **Pull latest**). Leave it off for day-to-day phone/LAN use.

**Manual proof (Sprint 11):** With `CRAWLEY_RELOAD=1`, open Settings → Update, note the short SHA, pull a commit that touches `src/crawley/` (or pull after pushing such a commit), watch the server log for a reload, and confirm the Settings page shows the new SHA / “Pulled … hot reload should apply”.

**ASX desk (Investment):** Open **Investment** — panel title **ASX desk**. Curated universe (~193 tickers) with a PoC set of **~20**. **Start scan** enriches one company at a time (Yahoo price snapshot + Google News headlines + LLM sentiment/profile). Open a ticker for Snapshot + Profile + sources. Subnav: **Recommendations** (structured actions from profiles) and **Paper portfolio** (simulated trades, MTM from scan prices, fees from Settings). Toggle sources / edit ASX prompts under Desk disclosures. Reset clears `data/investment/asx/`. Cap: `CRAWLEY_ASX_POC_CAP`. Classic RSS search remains under a disclosure. Not licensed research; **no live brokerage orders**.

**Snapshot history / pins:** Settings → **Snapshot history** — browse/search bounded past summaries; pin items into shared context (hard caps). Fitness panel accepts a bounded activity file import for optional plan grounding.

**Sender Inbox (Gmail):** Open **Gmail** in the nav — panel title **Sender Inbox**. Connect Google, then **Start ingest**. Crawley pulls **one INBOX message at a time**, LLM-categorizes it, groups by sender (not chronology), and builds a profile + local todos per sender. Hard stop at **~20** messages (raise later with `CRAWLEY_SENDER_INBOX_CAP` in `.env` and restart). Progress shows `processed / cap` and remaining capacity; **Reset PoC data** clears `data/gmail/sender_inbox/`. Classic inbox skim lives under a disclosure. No auto-send / auto-calendar from todos.

**Google OAuth notes:** The redirect URI is always `{request Host}/modules/gmail/oauth/callback` — e.g. `http://127.0.0.1:8000/modules/gmail/oauth/callback` on localhost, or `http://100.x.y.z:8000/modules/gmail/oauth/callback` / MagicDNS when you Connect from a Tailscale client. Settings → **Google OAuth** (and the Connect panel) show the **exact** URI for the Host you are using — copy it into Google Cloud → **Authorized redirect URIs** (not JavaScript origins). Enable **Gmail API** and **Google Calendar API**. Default scopes are Gmail + Calendar **read-only**. Calendar event insert uses an optional `calendar.events` write scope — use **Reconnect for Calendar write** on the Calendar panel (never requests Gmail send). Gmail send uses a separate `?gmail_send=1` reconnect. Local HTTP is allowed for `127.0.0.1` / `localhost` and trusted personal LAN/Tailscale hosts. Tokens live on the **server** (`data/secrets/`) and are reused by every client of that one Crawley process.

**OAuth consent / weekly re-auth:** Connect keeps `access_type=offline` but only forces Google’s full consent screen when a refresh token is missing or you request new scopes (Calendar write / Gmail send). Normal API use refreshes quietly. If Google Cloud OAuth clients stay in **Testing** publishing status, refresh tokens expire in ~**7 days** — that is the usual cause of weekly re-auth prompts; move the client to **Production** (or re-consent) when you need longer-lived refresh tokens.

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

- **Sprints 1–5** — PoC closed; retro: [`docs/sprints/archive/sprints-1-5-retrospective.md`](./docs/sprints/archive/sprints-1-5-retrospective.md)
- **Sprints 6–10** — **implemented** (life modules, Day brief, Calendar write-back, LocalLlama, shared context): [`docs/sprints/archive/sprint-6-10-life-modules-llm-context.md`](./docs/sprints/archive/sprint-6-10-life-modules-llm-context.md) · [code verification](./docs/sprints/archive/sprint-6-10-code-verification.md)
- **Sprint 11** — Settings Update (git pull + hot reload) (**closed**): [`docs/sprints/archive/sprint-11-settings-update.md`](./docs/sprints/archive/sprint-11-settings-update.md)
- **Sprint 12** — Sender Inbox PoC (**closed**): [`docs/sprints/archive/sprint-12-sender-inbox.md`](./docs/sprints/archive/sprint-12-sender-inbox.md)
- **Sprint 13** — ASX desk scanner + profiles (**closed**): [`docs/sprints/archive/sprint-13-asx-profiles.md`](./docs/sprints/archive/sprint-13-asx-profiles.md)
- **Sprint 14** — ASX paper desk (+ history/pins + Fitness import B35–B37) (**closed**): [`docs/sprints/archive/sprint-14-asx-paper-portfolio.md`](./docs/sprints/archive/sprint-14-asx-paper-portfolio.md)
- **Sprints 15–17** — Inbox/ASX scale + email bridge (**closed**): [`docs/sprints/archive/sprint-15-17-scale-bridge.md`](./docs/sprints/archive/sprint-15-17-scale-bridge.md)
- **Sprints 18–20** — Gmail send + ASX alerts + playbooks (**closed**): [`docs/sprints/archive/sprint-18-20-send-alerts-playbooks.md`](./docs/sprints/archive/sprint-18-20-send-alerts-playbooks.md)
- **Sprints 21–24** — OAuth ops + digests + notebook + VIP (**closed**): [`docs/sprints/archive/sprint-21-24-oauth-digests-notebook-vip.md`](./docs/sprints/archive/sprint-21-24-oauth-digests-notebook-vip.md)
- **Sprint 25** — ASX news theme clustering (**current**): [`docs/sprints/current.md`](./docs/sprints/current.md)
- **Sprints 26–30** — Email/ASX depth (planned): [`docs/sprints/planned/README.md`](./docs/sprints/planned/README.md)
- **Shelved** — former 31–40 / platform Later remnants: [`docs/sprints/shelved/README.md`](./docs/sprints/shelved/README.md)


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

`@architect-developer` implements [`docs/sprints/current.md`](./docs/sprints/current.md) (**Sprint 21** — Google OAuth ops). Planned **22–30**: thread digests → ASX notebook → VIP rules → news clusters → labels → holdings journal → saved searches → attachments → citations. UX: `docs/ux/sender-inbox-asx.md`.
