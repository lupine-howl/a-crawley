# ADR-002: DuckDB + filesystem data plane

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

The stakeholder wants local persistence optimized for sorting and organising **large datasets** and analysing them with ML and/or LLMs. Personal, single-machine, no SaaS DB. Options: SQLite-only, Postgres local, files/JSON only, or an analytics-oriented hybrid.

## Decision

Use a **hybrid local data plane**:

- **DuckDB** file(s) under gitignored `data/` for queryable structured data and analytical workloads
- **Filesystem** for raw crawl/mail dumps and caches
- **Parquet** (read/written via DuckDB and/or Polars) when tabular batches get large

Access goes through small helpers/repositories so modules do not embed engine-specific SQL everywhere.

## Consequences

- **Positive:** Strong local analytics (filters, joins, exports) without running a DB server; aligns with Polars/ML workflows.
- **Negative:** Team must learn DuckDB connection/threading rules; slightly less “obvious” than SQLite alone.
- **Follow-up:** If metadata-only paths need maximum simplicity, repositories may keep a narrow SQLite option later without abandoning DuckDB for analytics.
