# Migration — monorepo layout (Crawley → phone-preview Phase 4)

**Status:** Layout matches Core cleanup Option A (2026-07-18)  
**ADR:** [`adr/010-monorepo-layout.md`](adr/010-monorepo-layout.md)

## Target (this repo = merge source)

```
apps/
  crawley/                 # UI host only
packages/
  crawley-*                # portable packs
services/
  crawley/                 # Python API + daemons + data + pytest
```

| Piece | Path | Why |
|-------|------|-----|
| Vite / Phone Preview host | `apps/crawley` | Same as core / Learninator apps |
| TS packs + analytics-client | `packages/crawley-*` | Plug-and-play workspace libs |
| Python API + daemons + `data/` + pytest | **`services/crawley`** | Not an npm app; not a package |

## Merge into phone-preview

1. Copy `apps/crawley` → `apps/crawley`
2. Copy `packages/crawley-*` → `packages/`
3. Copy `services/crawley` → `services/crawley`
4. Wire root **`dev:crawley`**: Python `:8000` + Vite (proxy `/api/analytics` → `:8000`)
5. CI matrix: `apps/crawley` build + `services/crawley` pytest

## Plug-and-play checklist

- [x] Packs depend on `@phone-preview/core` (+ `@crawley/analytics-client`)
- [x] UI via `FeaturePack` (`page` / `systemTab`)
- [x] No secrets in packs; analytics HTTP only
- [x] Python under `services/crawley` (not monorepo root, not `packages/`)
- [ ] Swap `@phone-preview/core` → `@phone-preview/shell` when published
- [ ] Prod path for `/api/analytics` (BFF / rewrites) — separate from local Vite proxy

## Local commands

```bash
cd services/crawley && uv sync && cp -n .env.example .env && cd ../..
npm install
npm run dev:crawley
npm run test:api
```

Delete leftovers on old checkouts: root `crawley-ui/`, `src/`, `tests/`, `data/`, `apps/crawley/analytics/`.
