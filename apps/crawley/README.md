# `@crawley/app` — Crawley product host

Phone Preview host. Packs live in `packages/crawley-*`. Python analytics is **`services/crawley`** (not under this app).

## Layout

```
apps/crawley/          ← this host
packages/crawley-*
services/crawley/      ← Python API (uv)
```

**Merge:** copy all three trees into the phone-preview monorepo; register packs in this app (`crawleyPacks`).

## Run

From repo root:

```bash
cd services/crawley && uv sync && cp -n .env.example .env && cd ../..
npm install
npm run dev:crawley   # API + Vite
```

Demo login (if prompted): `admin@demo.local` / `demo123`

## Packs wired here

| Package | Packs |
|---------|--------|
| `@crawley/asx` | desk, recommendations, portfolio, themes |
| `@crawley/inbox` | senderInboxPack |
| `@crawley/settings` | analyticsSettingsPack (LLM `systemTab`) |
