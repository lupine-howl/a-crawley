"""Sprint 25 — ASX news theme clustering."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient

import crawley.asx_desk.clusters as clusters
import crawley.asx_desk.store as asx_store


def test_heuristic_clusters_earnings_and_dividends() -> None:
    headlines = [
        {"ticker": "CBA", "title": "CBA earnings beat guidance", "url": "https://a.example/1"},
        {"ticker": "WBC", "title": "Westpac lifts dividend payout", "url": "https://b.example/2"},
        {"ticker": "BHP", "title": "Iron ore prices steady", "url": "https://c.example/3"},
        {"ticker": "XYZ", "title": "Company opens new office", "url": "https://d.example/4"},
    ]
    themes = clusters.cluster_headlines_heuristic(headlines)
    names = {t["theme"] for t in themes}
    assert "Earnings & results" in names
    assert "Dividends & capital" in names
    assert "Commodities & energy" in names
    earn = next(t for t in themes if t["theme"] == "Earnings & results")
    assert any(s["ticker"] == "CBA" for s in earn["sources"])


def test_collect_reuses_scan_headlines_and_respects_caps(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    asx_store.set_poc_tickers(["CBA", "BHP"])
    asx_store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 1, "gaps": []},
            "headlines": [
                {"title": f"CBA story {i}", "url": f"https://news.example/cba{i}"}
                for i in range(10)
            ],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    asx_store.upsert_scan(
        "BHP",
        {
            "ticker": "BHP",
            "status": "ready",
            "snapshot": {"price": 1, "gaps": []},
            "headlines": [{"title": "BHP copper update", "url": "https://news.example/bhp"}],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    rows, ticker_count = clusters.collect_active_headlines(max_per_ticker=2, max_headlines=80)
    assert ticker_count == 2
    assert len(rows) == 3  # 2 CBA + 1 BHP
    assert sum(1 for r in rows if r["ticker"] == "CBA") == 2


def test_build_clusters_empty_active_set(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    asx_store.set_poc_tickers([])
    # Empty poc may still load default from universe on load_scan_state — force empty
    state = asx_store.load_scan_state()
    state["poc_tickers"] = []
    asx_store.save_scan_state(state)
    result = clusters.build_clusters(prefer_llm=False)
    assert result["status"] == "empty"
    assert result["themes"] == []


def test_build_clusters_heuristic_ready(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    asx_store.set_poc_tickers(["CBA"])
    asx_store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 100, "gaps": []},
            "headlines": [
                {"title": "CBA full year earnings rise", "url": "https://news.example/earn"},
                {"title": "Bank holds dividend steady", "url": "https://news.example/div"},
            ],
            "sources_used": ["google_news_rss"],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    result = clusters.build_clusters(prefer_llm=False)
    assert result["status"] == "ready"
    assert result["method"] == "heuristic"
    assert result["headline_count"] == 2
    assert result["themes"]
    assert "## " in result["markdown"] or "Earnings" in result["markdown"]


def test_muted_domain_excluded_from_collect(tmp_path, monkeypatch) -> None:
    import crawley.asx_desk.citations as citations
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    asx_store.set_poc_tickers(["CBA"])
    asx_store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 1, "gaps": []},
            "headlines": [
                {"title": "Spam headline", "url": "https://spam.example/x"},
                {"title": "OK headline earnings", "url": "https://ok.example/y"},
            ],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    citations.mute_domain("spam.example")
    rows, _ = clusters.collect_active_headlines()
    assert len(rows) == 1
    assert rows[0]["url"] == "https://ok.example/y"


def test_clusters_route_and_refresh(client: TestClient, tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    asx_store.set_poc_tickers(["CBA"])
    asx_store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 1, "gaps": []},
            "headlines": [{"title": "CBA earnings update", "url": "https://n.example/1"}],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )

    def sync_start(executor, *, prefer_llm: bool = True):
        result = clusters.build_clusters(prefer_llm=False)
        clusters.save_clusters(result)
        return True, "done"

    monkeypatch.setattr(clusters, "start_cluster_refresh", sync_start)

    get = client.get("/modules/investment/clusters")
    assert get.status_code == 200
    assert "News themes" in get.text
    assert "not trade" in get.text.lower()

    post = client.post("/modules/investment/clusters/refresh")
    assert post.status_code == 200
    saved = clusters.load_clusters()
    assert saved["status"] == "ready"
    assert saved["themes"]
    assert "Earnings" in post.text or "theme" in post.text.lower()


def test_start_cluster_refresh_runs_and_persists(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    asx_store.set_poc_tickers(["CBA"])
    asx_store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 1, "gaps": []},
            "headlines": [{"title": "CBA dividend update", "url": "https://n.example/d"}],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    with ThreadPoolExecutor(max_workers=1) as ex:
        ok, msg = clusters.start_cluster_refresh(ex, prefer_llm=False)
        assert ok is True
        # Drain the submitted job
        ex.shutdown(wait=True)
    saved = clusters.load_clusters()
    assert saved["status"] == "ready"
    assert saved["themes"]
    assert "Clustering" in msg or "headline" in msg.lower()
