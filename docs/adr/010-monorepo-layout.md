# ADR-010: Crawley monorepo layout (Phase 4 plug-and-play)

- **Status:** Accepted
- **Date:** 2026-07-18
- **Related:** [ADR-009](009-phone-preview-analytics.md) · phone-preview “Core repository cleanup” Phase 4

## Context

Phone Preview consolidates into one monorepo:

```
apps/      core · core-plus · learninator · crawley
packages/  shell · content · interactives · ai · api · … · crawley-*
services/  crawley   ← Python analytics
```

Product packs are portable: move the folder, add to `apps/<name>` packs array. Upstream gap analysis places Python under **`services/crawley`** (Option A) — not `apps/*`, not `packages/*`.

## Decision

1. **This repo** mirrors the merge-ready Crawley slice.
2. **`apps/crawley`** — Phone Preview host only (`@crawley/app`); wires packs.
3. **`packages/crawley-*`** — portable packs + `@crawley/analytics-client`.
4. **`services/crawley`** — uv project (`src/crawley`, `tests/`, `data/`, `pyproject.toml`). Never an npm workspace member. `DATA_DIR` beside the uv project; `REPO_ROOT` walks up to the git checkout for Settings → Update.
5. Platform packages are not vendored; consume `@phone-preview/core` until `@phone-preview/shell` ships.
6. npm workspaces: `apps/*` + `packages/*` only. Root scripts: `dev:crawley` / `dev:api` / `test:api` orchestrate the Python service.

## Consequences

- **Positive:** Copy-paste into phone-preview; clear UI / packs / service split.
- **Negative:** Two package managers (uv + npm); temporary `core` vs `shell` peer name.
- **Local boot:** `npm run dev:crawley` starts Python `:8000` + Vite. Prod analytics proxy is out of scope here.
