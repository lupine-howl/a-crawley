# `@crawley/app` — Crawley product host

Phone Preview host for **Crawley**. Packs live in portable workspace packages under `packages/crawley-*` (Phase 4 plug-and-play).

Python analytics brain stays at the **repo root** (`uv run python -m crawley`) — not inside this npm app.

## Layout (this repo)

```
apps/crawley/                 ← this host
packages/crawley-analytics-client/
packages/crawley-asx/
packages/crawley-inbox/
packages/crawley-settings/
src/crawley/                  ← Python analytics (separate runtime)
```

## Portability (product packs)

| Rule | Crawley status |
|------|----------------|
| Import platform from `@phone-preview/shell` (or `core` until shell ships) | Packs peer-depend on `@phone-preview/core` ≥ 0.6.1 |
| UI via pack fields (`page`, `systemTab`, …) | Yes |
| Domain services via `packServices` / analytics HTTP only | Yes — `@crawley/analytics-client` |
| Own migrations / API registrar if needed | N/A (analytics owns `/v1`) |

**Merge into phone-preview monorepo:** copy `apps/crawley` + `packages/crawley-*`, then register packs in `apps/crawley` (already exported as `crawleyPacks`).

## Run

From **repo root**:

```bash
# Terminal A — analytics
uv run python -m crawley

# Terminal B — UI
npm install
npm run dev
```

Or: `npm run dev -w @crawley/app`

Demo login (if prompted): `admin@demo.local` / `demo123`

## Packs wired here

| Package | Packs |
|---------|--------|
| `@crawley/asx` | desk, recommendations, portfolio, themes |
| `@crawley/inbox` | senderInboxPack |
| `@crawley/settings` | analyticsSettingsPack (LLM `systemTab`) |
