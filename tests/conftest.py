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
    import crawley.google_oauth as google_oauth
    import crawley.modules.investment_fetch as inv_fetch
    import crawley.settings as settings

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")
    monkeypatch.setattr(paths, "CALENDAR_DIR", data / "calendar")
    monkeypatch.setattr(paths, "FITNESS_DIR", data / "fitness")
    monkeypatch.setattr(paths, "WORK_DIR", data / "work")
    monkeypatch.setattr(paths, "CO_PARENTING_DIR", data / "co_parenting")
    monkeypatch.setattr(paths, "DIY_DIR", data / "diy")
    monkeypatch.setattr(paths, "FINANCE_DIR", data / "finance")
    monkeypatch.setattr(paths, "CODING_DIR", data / "coding_creative")
    monkeypatch.setattr(paths, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(duck, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(inv_fetch, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(google_oauth, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(google_oauth, "TOKEN_PATH", data / "secrets" / "google_token.json")
    monkeypatch.setattr(
        google_oauth, "LEGACY_TOKEN_PATH", data / "secrets" / "gmail_token.json"
    )
    monkeypatch.setattr(
        google_oauth, "PENDING_OAUTH_PATH", data / "secrets" / "google_oauth_pending.json"
    )
    monkeypatch.setattr(
        google_oauth, "LEGACY_PENDING_PATH", data / "secrets" / "gmail_oauth_pending.json"
    )
    monkeypatch.setattr(settings, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(settings, "SETTINGS_PATH", data / "secrets" / "settings.json")
    import crawley.writeback as writeback

    monkeypatch.setattr(writeback, "DATA_DIR", data)
    monkeypatch.setattr(writeback, "AUDIT_PATH", data / "writeback_audit.jsonl")

    ensure_data_dirs()
    init_schema()
    with TestClient(create_app()) as test_client:
        yield test_client
