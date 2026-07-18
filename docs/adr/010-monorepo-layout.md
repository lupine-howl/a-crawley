# ADR-010: Crawley monorepo layout (Phase 4 plug-and-play)

- **Status:** Accepted
- **Date:** 2026-07-18
- **Related:** [ADR-009](009-phone-preview-analytics.md) · phone-preview “Core repository cleanup” Phase 4

## Context

Phone Preview is consolidating into one monorepo:

```
apps/     core · core-plus · learninator · crawley
packages/ shell · content · interactives · ai · api · … · crawley-*
```

Product packs must be portable: move the folder, add to `apps/<name>` packs array. Crawley’s UI previously lived as a single `crawley-ui/` tree with app-private packs.

## Decision

1. **This repo** adopts the same `apps/` + `packages/` shape for the Crawley slice only.
2. **`apps/crawley`** — Phone Preview host (`@crawley/app`); wires `starterPacks()` + `@crawley/*` packs.
3. **`packages/crawley-*`** — portable packs + analytics client (`@crawley/asx`, `@crawley/inbox`, `@crawley/settings`, `@crawley/analytics-client`).
4. **Python analytics** nests under **`apps/crawley/analytics/`** (`src/crawley`, `tests/`, `data/`, `pyproject.toml`) so merge does not pollute the monorepo root. Separate runtime from the npm workspace (uv); not an npm package. `DATA_DIR` is under that analytics root; `REPO_ROOT` walks up to the git checkout for Settings → Update.
5. Platform packages (`@phone-preview/shell`, etc.) are **not** vendored here; consume published `@phone-preview/core` until shell ships, then swap peer imports.
6. npm **workspaces** at the repo root install/link `apps/*` and `packages/*` (only packages with `package.json` — analytics is ignored by npm).

## Consequences

- **Positive:** Copy-paste merge (`apps/crawley` + `packages/crawley-*`); packs reusable; analytics `data/`/`tests/` stay inside the Crawley app tree.
- **Negative:** Two package managers (uv + npm); temporary `@phone-preview/core` vs future `@phone-preview/shell` rename.
- **Neutral:** Historical sprint docs may still say `crawley-ui/` or root `src/crawley`; treat as `apps/crawley` (+ `analytics/`). Delete leftover root `crawley-ui/`, `src/`, `tests/`, `data/` on old checkouts.
- **Local boot:** `npm run dev` starts analytics API + Vite host together (`@crawley/app`).
