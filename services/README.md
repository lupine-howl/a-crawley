# Services

Non-npm runtimes that product apps call over HTTP.

| Service | Role |
|---------|------|
| [`crawley/`](crawley/) | Python analytics API + daemons (ASX, Gmail ingest) — uv project |

In the phone-preview monorepo this folder lands as `services/crawley` (Core cleanup Option A). It is **not** an `apps/*` host and **not** a `packages/*` workspace library.
