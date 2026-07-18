# ADR-010: Crawley monorepo layout (Phase 4 plug-and-play)

- **Status:** Accepted
- **Date:** 2026-07-18
- **Related:** [ADR-009](009-phone-preview-analytics.md) · phone-preview “Core repository cleanup” Phase 4

## Context

Phone Preview is consolidating into one monorepo:

```
apps/      core · core-plus · learninator · crawley
packages/  shell · content · interactives · ai · api · … · crawley-*
services/  crawley   ← Python analytics (not an npm app/package)
```

Product packs must be portable: move the folder, add to `apps/<name>` packs array. Crawley’s UI previously lived as a single `crawley-ui/` tree with app-private packs.

Upstream gap analysis: Python belongs under **`services/crawley`** (Option A — vendor/submodule + `dev:crawley` boots `:8000`). It is **not** an `apps/*` Vite host and **not** a `packages/*` workspace library.

## Decision

1. **This repo** mirrors the Crawley slice for copy into phone-preview.
2. **`apps/crawley`** — Phone Preview host only (`@crawley/app`); wires `starterPacks()` + `@crawley/*` packs.
3. **`packages/crawley-*`** — portable packs + analytics client (`@crawley/asx`, `@crawley/inbox`, `@crawley/settings`, `@crawley/analytics-client`).
4. **Python analytics → `services/crawley` in the monorepo** (uv project: `src/crawley`, `tests/`, `data/`, `pyproject.toml`). Separate runtime from npm; never an npm workspace member. In *this* product repo the same tree currently lives at `apps/crawley/analytics/` as a transport packaging convenience — **on merge, land it at `services/crawley`**, not under `apps/` or `packages/`. `DATA_DIR` stays beside the uv project; `REPO_ROOT` walks up to the git checkout for Settings → Update.
5. Platform packages (`@phone-preview/shell`, etc.) are **not** vendored here; consume published `@phone-preview/core` until shell ships, then swap peer imports (Learninator-style).
6. npm **workspaces** install/link `apps/*` and `packages/*` only. `services/` is orchestrated by root scripts (e.g. `dev:crawley` = Python `:8000` + Vite).

## Consequences

- **Positive:** Clear split — UI app / TS packs / Python service; merge does not put DuckDB/`data/` on monorepo root or inside `packages/`.
- **Negative:** Two package managers (uv + npm); temporary `@phone-preview/core` vs `@phone-preview/shell`; this repo’s `apps/crawley/analytics/` path must be remapped to `services/crawley` on copy.
- **Neutral:** Historical docs may say `crawley-ui/` or root `src/crawley`.
- **Local boot (mono):** `dev:crawley` must start Python on `:8000` **and** the Vite host (Vite proxy `/api/analytics` → `:8000` remains the local path; prod BFF/rewrites are a separate story).
