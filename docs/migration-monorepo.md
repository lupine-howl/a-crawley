# Migration — monorepo layout (Crawley → phone-preview Phase 4)

**Status:** Layout landed in this repo (2026-07-18)  
**ADR:** [`adr/010-monorepo-layout.md`](adr/010-monorepo-layout.md)

## Target (upstream phone-preview)

```
apps/
  core/
  core-plus/
  learninator/
  crawley/                 ← from this repo apps/crawley
packages/
  shell/
  content/
  interactives/
  ai/
  api/
  api-vercel/
  education/               # from Learninator
  crawley-*/               ← from this repo packages/crawley-*
```

## This repo today

```
apps/crawley/                      # @crawley/app
packages/crawley-analytics-client/ # @crawley/analytics-client
packages/crawley-asx/              # @crawley/asx
packages/crawley-inbox/            # @crawley/inbox
packages/crawley-settings/         # @crawley/settings
src/crawley/                       # Python analytics (unchanged runtime)
```

## Merge order (Crawley steps)

1. Platform packages (Phases 1–2) land on phone-preview `main`.
2. Copy Learninator packs → `packages/` (upstream).
3. **Copy `packages/crawley-*` + `apps/crawley` from this repo** into the monorepo.
4. Delete duplicated host/pack trees from product repos once CI is green.
5. Single CI matrix: build/test each app (including `apps/crawley`).

## Plug-and-play checklist

- [x] Packs only depend on `@phone-preview/core` (+ `@crawley/analytics-client`)
- [x] UI via `FeaturePack` (`page` / `systemTab`)
- [x] No secrets in packs; analytics HTTP only
- [x] Host packs array is just imports from `@crawley/*`
- [ ] Swap `@phone-preview/core` → `@phone-preview/shell` when published
- [ ] Land folders into phone-preview monorepo workspaces

## Local commands

```bash
# Analytics
uv run python -m crawley

# UI (repo root)
npm install
npm run dev
```
