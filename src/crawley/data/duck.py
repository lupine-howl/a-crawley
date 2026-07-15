"""DuckDB helpers with a process-wide connection lock.

DuckDB rejects opening the same file with mixed configs (e.g. read_only vs
read_write) while another connection is live. All access here uses one mode
and is serialized under `_db_lock` so HTMX status polls cannot race a job write.
"""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

import duckdb

from crawley.data.paths import DUCKDB_PATH, ensure_data_dirs

_db_lock = threading.Lock()


@contextmanager
def duck_connection(*, read_only: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
    """Open the shared DB. `read_only` is accepted for callers but ignored —
    every connection uses the same read-write config under a process lock.
    """
    del read_only  # kept for API compatibility; mixed modes break DuckDB
    ensure_data_dirs()
    with _db_lock:
        con = duckdb.connect(str(DUCKDB_PATH))
        try:
            yield con
        finally:
            con.close()


def init_schema() -> None:
    with duck_connection() as con:
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS investment_artifacts (
                id VARCHAR PRIMARY KEY,
                fetched_at TIMESTAMP,
                query VARCHAR,
                source_url VARCHAR,
                title VARCHAR,
                artifact_path VARCHAR,
                snippet VARCHAR
            );
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS gmail_messages (
                id VARCHAR PRIMARY KEY,
                fetched_at TIMESTAMP,
                internal_date TIMESTAMP,
                subject VARCHAR,
                from_addr VARCHAR,
                snippet VARCHAR
            );
            """
        )
        con.execute(
            """
            CREATE TABLE IF NOT EXISTS calendar_events (
                id VARCHAR PRIMARY KEY,
                fetched_at TIMESTAMP,
                start_at VARCHAR,
                end_at VARCHAR,
                title VARCHAR,
                location VARCHAR,
                description VARCHAR
            );
            """
        )
