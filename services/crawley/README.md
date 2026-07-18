# `services/crawley` — Python analytics

Local-first FastAPI brain + optional daemons. This is the monorepo landing zone for the Crawley Python server (Core cleanup Option A).

## Layout

```
services/crawley/
  src/crawley/     # Python package
  tests/           # pytest
  data/            # worker store (gitignored runtime)
  pyproject.toml
```

## Commands

```bash
uv sync
cp .env.example .env   # first time
uv run python -m crawley
uv run python -m pytest
```

From repo root:

```bash
npm run dev:crawley    # API (:8000) + Vite UI
npm run dev:api        # analytics only
npm run test:api       # pytest
```

Optional daemons (from this directory):

```bash
export CRAWLEY_ASX_WORKER=daemon CRAWLEY_GMAIL_WORKER=daemon
uv run python -m crawley
uv run crawley-asx-scanner watch
uv run crawley-gmail-ingest watch
```
