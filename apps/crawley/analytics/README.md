# Crawley analytics (Python)

Local-first FastAPI brain + optional daemons. Nesting under `apps/crawley/analytics` keeps the Crawley slice self-contained for phone-preview Phase 4 merge (no `data/` / `tests/` / `src/` at monorepo root).

## Layout

```
apps/crawley/analytics/
  src/crawley/     # Python package
  tests/           # pytest
  data/            # worker store (gitignored runtime)
  pyproject.toml
```

## Commands

From this directory:

```bash
uv sync
cp .env.example .env   # first time
uv run python -m crawley
uv run pytest
```

From monorepo root (preferred with UI):

```bash
npm run dev            # API + Vite
npm run dev:api        # analytics only
uv run --directory apps/crawley/analytics pytest
```

Optional daemons: set `CRAWLEY_ASX_WORKER=daemon` / `CRAWLEY_GMAIL_WORKER=daemon`, then `uv run crawley-asx-scanner watch` / `uv run crawley-gmail-ingest watch` from this directory.
