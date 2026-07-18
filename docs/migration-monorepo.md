# Migration — monorepo layout (Crawley → phone-preview Phase 4)

**Status:** Layout landed in this repo (2026-07-18)  
**ADR:** [`adr/010-monorepo-layout.md`](adr/010-monorepo-layout.md)

## Target (upstream phone-preview)

```
apps/
  crawley/                 ← UI host only (from this repo apps/crawley, minus analytics/)
packages/
  crawley-*/               ← packs (from this repo packages/crawley-*)
services/
  crawley/                 ← Python server (from this repo apps/crawley/analytics/)
```

| Piece | Monorepo home | Why |
|-------|---------------|-----|
| Vite / Phone Preview host | `apps/crawley` | Same as core / Learninator apps |
| TS packs + analytics-client | `packages/crawley-*` | Plug-and-play workspace libs |
| Python API + daemons + `data/` + pytest | **`services/crawley`** | Not an npm app; not a package — Option A from Core cleanup |

**Do not** put Python under `packages/` (wrong runtime) or leave it only as a Vite proxy with no tree. Nesting under `apps/crawley` also fights npm `apps/*` conventions; prefer `services/`.

## This repo today (transport shape)

```
apps/crawley/                         # @crawley/app (Vite host)
  analytics/                          # ← copy this folder → services/crawley in the mono
packages/crawley-*
```

## Merge order (Crawley steps)

1. Platform packages (Phases 1–2) land on phone-preview `main`.
2. Copy Learninator packs → `packages/` (upstream).
3. Copy **`packages/crawley-*` → `packages/`**, **UI → `apps/crawley`**, **`apps/crawley/analytics/` → `services/crawley`**.
4. Wire root **`dev:crawley`**: `uv run` in `services/crawley` (`:8000`) **+** Vite for `apps/crawley` (proxy `/api/analytics` → `:8000`).
5. Delete duplicated trees from product repos once CI is green; matrix includes `apps/crawley` build + `services/crawley` pytest.
## Plug-and-play checklist

- [x] Packs only depend on `@phone-preview/core` (+ `@crawley/analytics-client`)
- [x] UI via `FeaturePack` (`page` / `systemTab`)
- [x] No secrets in packs; analytics HTTP only
- [x] Host packs array is just imports from `@crawley/*`
- [x] Analytics `data/` + `tests/` nested under `apps/crawley/analytics` (not monorepo root)
- [ ] Swap `@phone-preview/core` → `@phone-preview/shell` when published
- [ ] Land folders into phone-preview monorepo workspaces

## Local commands

```bash
cd apps/crawley/analytics && uv sync && cp -n .env.example .env && cd -
npm install
npm run dev          # API + UI
# npm run dev:api    # analytics only
# npm run dev:ui     # Vite only
# npm run test:api   # pytest
```

If a root `crawley-ui/`, `src/`, `tests/`, or `data/` still exists on an old checkout, delete those leftovers — the host + brain live under `apps/crawley/`.
