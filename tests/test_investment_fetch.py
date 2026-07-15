"""Investment fetch / run path tests."""

from __future__ import annotations

import time

import httpx
import pytest
from fastapi.testclient import TestClient

from crawley.llm.base import ChatResult
from crawley.modules.investment import InvestmentModule
from crawley.modules.investment_fetch import (
    InvestmentFetchError,
    fetch_rss_items,
    parse_rss_items,
)
from tests.fixtures.sample_news_rss import SAMPLE_RSS, TRUNCATED_RSS


def test_parse_rss_items_respects_limit() -> None:
    items = parse_rss_items(SAMPLE_RSS, limit=3)
    assert len(items) == 3
    assert items[0]["title"] == "Markets climb on earnings"
    assert items[0]["url"] == "https://example.com/a"
    assert "Markets climb" in items[0]["snippet"]


def test_parse_rss_rejects_truncated_xml() -> None:
    with pytest.raises(InvestmentFetchError, match="could not be parsed"):
        parse_rss_items(TRUNCATED_RSS)


def test_fetch_rss_items_uses_http_body(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    import crawley.modules.investment_fetch as inv

    monkeypatch.setattr(inv, "INVESTMENT_DIR", tmp_path)

    class FakeResponse:
        content = SAMPLE_RSS

        def raise_for_status(self) -> None:
            return None

    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, url: str):
            assert "news.google.com/rss/search" in url
            assert "US" in url or "stock" in url
            return FakeResponse()

    monkeypatch.setattr("crawley.modules.investment_fetch.httpx.Client", FakeClient)
    items, meta = fetch_rss_items("US stock market outlook", limit=2, use_cache=False)
    assert len(items) == 2
    assert meta["cache_hit"] == "false"


def test_fetch_rss_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeClient:
        def __init__(self, *args, **kwargs) -> None:
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

        def get(self, url: str):
            raise httpx.ConnectError("boom")

    monkeypatch.setattr("crawley.modules.investment_fetch.httpx.Client", FakeClient)
    with pytest.raises(InvestmentFetchError, match="request failed"):
        fetch_rss_items("q")


def test_investment_run_endpoint_async_path(client: TestClient, monkeypatch) -> None:
    """POST /run starts a job; mocked fetch+LLM reach done."""

    monkeypatch.setattr(
        "crawley.modules.investment.fetch_rss_items",
        lambda query, limit=3, use_cache=True: (
            [
                {
                    "title": "T",
                    "url": "https://example.com",
                    "snippet": "s",
                    "body": "body",
                }
            ],
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

    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="Synthesized notes.", model="fake")

    monkeypatch.setattr(
        "crawley.modules.investment.get_llm_provider",
        lambda: FakeProvider(),
    )

    response = client.post(
        "/modules/investment/run",
        data={"query": "markets"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "busy" in response.text or "done" in response.text or "Status:" in response.text

    module: InvestmentModule = client.app.state.registry["investment"]
    for _ in range(50):
        if module.job.status in {"done", "error"}:
            break
        time.sleep(0.05)
    assert module.job.status == "done"
    assert "Synthesized" in module.job.summary

    status = client.get(
        "/modules/investment/status",
        headers={"HX-Request": "true"},
    )
    assert status.status_code == 200
    assert "Synthesized" in status.text


def test_investment_job_maps_fetch_error(client: TestClient, monkeypatch) -> None:
    def boom(query: str, *, limit: int = 3, use_cache: bool = True):
        raise InvestmentFetchError("News feed XML could not be parsed")

    monkeypatch.setattr("crawley.modules.investment.fetch_rss_items", boom)
    module: InvestmentModule = client.app.state.registry["investment"]
    module._job_body("q")
    assert module.job.status == "error"
    assert "could not be parsed" in module.job.message


@pytest.mark.network
def test_live_google_news_rss_parse() -> None:
    """Optional live check — skipped in default CI if network blocked."""
    items, _meta = fetch_rss_items("US stock market outlook", limit=3, use_cache=False)
    assert len(items) >= 1
    assert items[0]["title"]
    assert items[0]["url"].startswith("http")
