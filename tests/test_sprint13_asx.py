"""Sprint 13 — ASX desk / profiles PoC."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import crawley.asx_desk.store as store
from crawley.asx_desk.schema import POC_CAP, normalize_snapshot
from crawley.asx_desk.sources import DEFAULT_SOURCES, load_config, set_source_enabled
from crawley.asx_desk.worker import start_scan


def test_investment_shows_asx_desk(client: TestClient) -> None:
    resp = client.get("/modules/investment")
    assert resp.status_code == 200
    assert "ASX desk" in resp.text
    assert "Start scan" in resp.text
    assert "CBA" in resp.text or "PoC set" in resp.text


def test_universe_loaded() -> None:
    uni = store.load_universe()
    assert uni["count"] >= 100
    assert uni["companies"][0]["ticker"] == "CBA"
    assert "provenance" in uni


def test_poc_set_and_desk_rows(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    store.reset_poc_data()
    state = store.set_poc_tickers(["CBA", "BHP", "NOTREAL", "CSL"])
    assert state["poc_tickers"] == ["CBA", "BHP", "CSL"]
    rows = store.desk_rows()
    assert [r["ticker"] for r in rows] == ["CBA", "BHP", "CSL"]
    assert all(r["status"] == "pending" for r in rows)


def test_snapshot_normalization() -> None:
    snap = normalize_snapshot({"price": "12.5", "change_pct": -1.2, "sentiment": "MIXED"})
    assert snap["price"] == 12.5
    assert snap["change_pct"] == -1.2
    assert snap["sentiment"] == "mixed"


def test_sources_toggle(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    cfg = load_config()
    assert len(cfg["sources"]) == len(DEFAULT_SOURCES)
    set_source_enabled("yahoo_chart", False)
    assert not any(s["id"] == "yahoo_chart" and s["enabled"] for s in load_config()["sources"])


def test_company_detail_route(client: TestClient) -> None:
    store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "error": "",
            "snapshot": {
                "price": 120.0,
                "change_pct": 1.2,
                "volume": 1000,
                "sentiment": "constructive",
                "gaps": [],
            },
            "headlines": [{"title": "CBA holds rates", "url": ""}],
            "sources_used": ["yahoo_chart"],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    store.save_profiles(
        {
            "CBA": {
                "markdown": "## Business\nBank.",
                "status": "ready",
                "error": "",
                "updated_at": "2026-07-16T00:00:00Z",
            }
        }
    )
    resp = client.get("/modules/investment/companies/CBA")
    assert resp.status_code == 200
    assert "CBA" in resp.text
    assert "Snapshot" in resp.text
    assert "Not licensed research" in resp.text


def test_scanner_isolates_error(monkeypatch, tmp_path) -> None:
    import crawley.asx_desk.fetch as fetch
    import crawley.asx_desk.worker as worker
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])

    def boom(*args, **kwargs):
        raise RuntimeError("source down")

    monkeypatch.setattr(fetch, "scan_company", boom)

    class ImmediateExecutor:
        def submit(self, fn, *args, **kwargs):
            fn(*args, **kwargs)
            return MagicMock()

    ok, _ = start_scan(ImmediateExecutor())
    assert ok is True
    scan = store.load_scans().get("CBA")
    assert scan is not None
    assert scan["status"] == "error"
    progress = store.progress_view(running=False)
    assert progress["processed"] == 1
    assert progress["status"] == "done"
