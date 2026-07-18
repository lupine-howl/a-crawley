# Packages

Crawley product packs prepared for **phone-preview Phase 4** monorepo merge (`packages/crawley-*`).

| Package | Name | Role |
|---------|------|------|
| `crawley-analytics-client/` | `@crawley/analytics-client` | Fetch helpers + DTOs for `/api/analytics` → Python `/v1` |
| `crawley-asx/` | `@crawley/asx` | ASX desk / recommendations / portfolio / themes packs |
| `crawley-inbox/` | `@crawley/inbox` | Sender Inbox pack |
| `crawley-settings/` | `@crawley/settings` | LLM Settings `systemTab` pack |

## Plug-and-play rules (upstream)

1. Packs import platform types from `@phone-preview/core` today (peer). When `@phone-preview/shell` publishes, swap peer + imports.
2. Optional peers later: `content`, `interactives`, `ai` — Crawley does not use these.
3. UI via `FeaturePack` fields (`page`, `systemTab`, …).
4. Domain I/O only through `@crawley/analytics-client` (no secrets, no Yahoo/Gmail/LLM in the pack).

## Merge into phone-preview monorepo

```bash
# From this repo → phone-preview monorepo
cp -R packages/crawley-* <pp-monorepo>/packages/
cp -R apps/crawley <pp-monorepo>/apps/
# Add workspace entries; npm/pnpm install; ensure apps/crawley packs array includes @crawley/*
```

Platform packages (`shell`, `content`, `interactives`, `ai`, `api`, …) are owned by phone-preview — not duplicated here.
