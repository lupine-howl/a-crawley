"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from crawley.app import create_app
from crawley.data.duck import init_schema
from crawley.data.paths import ensure_data_dirs


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch, tmp_path):
    monkeypatch.setenv("OPENAI_API_KEY", "")
    import crawley.data.duck as duck
    import crawley.data.paths as paths
    import crawley.modules.gmail as gmail_mod
    import crawley.modules.investment_fetch as inv_fetch

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")
    monkeypatch.setattr(paths, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(duck, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(inv_fetch, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(gmail_mod, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(gmail_mod, "GMAIL_DIR", data / "gmail")
    monkeypatch.setattr(gmail_mod, "TOKEN_PATH", data / "secrets" / "gmail_token.json")
    monkeypatch.setattr(
        gmail_mod, "PENDING_OAUTH_PATH", data / "secrets" / "gmail_oauth_pending.json"
    )

    ensure_data_dirs()
    init_schema()
    with TestClient(create_app()) as test_client:
        yield test_client
