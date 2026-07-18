# `@crawley/app` — Crawley product host

Phone Preview host for **Crawley**. Packs live in portable workspace packages under `packages/crawley-*` (Phase 4 plug-and-play).

Python analytics lives at the **repo root** (`src/crawley`). `npm run dev` in this app (or from the monorepo root) boots **API + UI** together.

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

From **repo root** (preferred):

```bash
npm install
npm run dev          # API (:8000) + Vite UI
```

Or from this package:

```bash
npm run dev          # same — concurrently api + vite
npm run dev:ui       # Vite only
npm run dev:api      # analytics only (uv from repo root)
```

Demo login (if prompted): `admin@demo.local` / `demo123`

## Packs wired here

| Package | Packs |
|---------|--------|
| `@crawley/asx` | desk, recommendations, portfolio, themes |
| `@crawley/inbox` | senderInboxPack |
| `@crawley/settings` | analyticsSettingsPack (LLM `systemTab`) |
