"""Tests for Investment / Gmail lite paths."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from crawley.data.duck import duck_connection, init_schema
from crawley.data.paths import ensure_data_dirs
from crawley.llm.base import ChatResult
from crawley.modules.investment import InvestmentModule
from crawley.modules.investment_fetch import persist_artifacts


def test_investment_panel_has_run_control(client: TestClient) -> None:
    response = client.get("/modules/investment")
    assert response.status_code == 200
    assert "ASX desk" in response.text
    assert "Start scan" in response.text or "Resume" in response.text or "Scanning" in response.text
    assert "Classic search" in response.text
    assert "Run search" in response.text


def test_persist_artifacts_writes_duckdb_and_files(tmp_path, monkeypatch) -> None:
    import crawley.data.duck as duck
    import crawley.data.paths as paths
    import crawley.modules.investment_fetch as inv_fetch

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(paths, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(duck, "DUCKDB_PATH", data / "crawley.duckdb")
    monkeypatch.setattr(inv_fetch, "INVESTMENT_DIR", data / "investment")
    ensure_data_dirs()
    init_schema()

    rows = persist_artifacts(
        "test query",
        [
            {
                "title": "Example",
                "url": "https://example.com/a",
                "snippet": "hello",
                "body": "body text",
            }
        ],
    )
    assert len(rows) == 1
    assert (data / "investment").exists()
    with duck_connection(read_only=True) as con:
        count = con.execute("SELECT count(*) FROM investment_artifacts").fetchone()[0]
    assert count == 1


def test_investment_job_error_without_llm_key(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    def fake_items(query: str, *, limit: int = 3, use_cache: bool = True):
        return (
            [
                {
                    "title": "T",
                    "url": "https://example.com",
                    "snippet": "s",
                    "body": "body",
                }
            ],
            {"cache_hit": "false"},
        )

    monkeypatch.setattr(
        "crawley.modules.investment.fetch_rss_items",
        fake_items,
    )
    monkeypatch.setattr(
        "crawley.modules.investment.persist_artifacts",
        lambda query, items: [
            {
                "id": "1",
                "title": "T",
                "url": "https://example.com",
                "snippet": "s",
                "artifact_path": "x",
            }
        ],
    )

    module: InvestmentModule = client.app.state.registry["investment"]
    module._job_body("q")
    assert module.job.status == "error"
    assert "OPENAI_API_KEY" in module.job.message or "missing" in module.job.message.lower()


def test_investment_job_success_with_mock_llm(client: TestClient, monkeypatch) -> None:
    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="Hold steady; watch earnings.", model="fake")

    monkeypatch.setattr(
        "crawley.modules.investment.fetch_rss_items",
        lambda query, limit=3, use_cache=True: (
            [{"title": "T", "url": "https://example.com", "snippet": "s", "body": "b"}],
            {"cache_hit": "false"},
        ),
    )
    monkeypatch.setattr(
        "crawley.modules.investment.persist_artifacts",
        lambda query, items: [
            {
                "id": "1",
                "title": "T",
                "url": "https://example.com",
                "snippet": "s",
                "artifact_path": "x",
            }
        ],
    )
    monkeypatch.setattr(
        "crawley.modules.investment.get_llm_provider",
        lambda: FakeProvider(),
    )

    module: InvestmentModule = client.app.state.registry["investment"]
    module._job_body("markets")
    assert module.job.status == "done"
    assert "Hold steady" in module.job.summary


def test_gmail_panel_shows_config_error(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    response = client.get("/modules/gmail")
    assert response.status_code == 200
    assert "GOOGLE_CLIENT_ID" in response.text


def test_gmail_oauth_start_without_config_redirects(client: TestClient, monkeypatch) -> None:
    monkeypatch.delenv("GOOGLE_CLIENT_ID", raising=False)
    monkeypatch.delenv("GOOGLE_CLIENT_SECRET", raising=False)
    response = client.get("/modules/gmail/oauth/start", follow_redirects=False)
    assert response.status_code in {302, 303}
    module = client.app.state.registry["gmail"]
    assert module.job.status == "error"
