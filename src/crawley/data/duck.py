"""DuckDB helpers with a process-wide write lock."""

from __future__ import annotations

import threading
from collections.abc import Iterator
from contextlib import contextmanager

import duckdb

from crawley.data.paths import DUCKDB_PATH, ensure_data_dirs

_write_lock = threading.Lock()


@contextmanager
def duck_connection(*, read_only: bool = False) -> Iterator[duckdb.DuckDBPyConnection]:
    ensure_data_dirs()
    if read_only:
        con = duckdb.connect(str(DUCKDB_PATH), read_only=True)
        try:
            yield con
        finally:
            con.close()
        return

    with _write_lock:
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
