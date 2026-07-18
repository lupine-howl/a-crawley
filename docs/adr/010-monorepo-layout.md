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
4. **Python analytics** remains at repo root (`src/crawley`, `uv run python -m crawley`) — separate runtime from the npm workspace; not nested under `packages/` until a later decision.
5. Platform packages (`@phone-preview/shell`, etc.) are **not** vendored here; consume published `@phone-preview/core` until shell ships, then swap peer imports.
6. npm **workspaces** at the repo root install/link `apps/*` and `packages/*`.

## Consequences

- **Positive:** Copy-paste merge into phone-preview monorepo; packs reusable; clear ownership boundary.
- **Negative:** Two package managers (uv + npm); temporary `@phone-preview/core` vs future `@phone-preview/shell` rename.
- **Neutral:** Historical docs may still say `crawley-ui/`; treat as `apps/crawley`.
