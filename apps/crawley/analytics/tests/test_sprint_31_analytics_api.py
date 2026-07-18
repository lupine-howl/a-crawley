"""Sprint 31 — Analytics JSON API (ASX + jobs)."""

from __future__ import annotations

from fastapi.testclient import TestClient

import crawley.asx_desk.store as store


def test_health_json(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert body["service"] == "crawley-analytics"
    assert "version" in body


def test_asx_companies_list(client: TestClient) -> None:
    store.reset_poc_data()
    store.set_poc_tickers(["CBA", "BHP"])
    resp = client.get("/v1/asx/companies")
    assert resp.status_code == 200
    body = resp.json()
    assert body["count"] == 2
    tickers = [c["ticker"] for c in body["companies"]]
    assert tickers == ["CBA", "BHP"]
    row = body["companies"][0]
    assert "name" in row and "scan_status" in row and "sentiment" in row
    assert "data/" not in str(body)


def test_asx_company_detail(client: TestClient) -> None:
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
            "headlines": [{"title": "CBA holds rates", "url": "https://example.com"}],
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
    resp = client.get("/v1/asx/companies/CBA")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ticker"] == "CBA"
    assert body["scan_status"] == "ready"
    assert body["snapshot"]["price"] == 120.0
    assert body["profile"]["status"] == "ready"
    assert "Bank" in body["profile"]["markdown"]
    assert body["headlines"][0]["title"] == "CBA holds rates"
    assert "Not licensed research" in body["disclaimer"]


def test_asx_company_detail_unknown(client: TestClient) -> None:
    resp = client.get("/v1/asx/companies/NOTAREALTICKER")
    assert resp.status_code == 404


def test_scan_start_and_job_status(client: TestClient, monkeypatch) -> None:
    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])

    started: list[bool] = []

    def fake_start(executor, *, force: bool = False) -> tuple[bool, str]:
        started.append(True)
        return True, "Scan started."

    monkeypatch.setattr("crawley.asx_desk.worker.start_scan", fake_start)
    monkeypatch.setattr("crawley.asx_desk.worker.is_running", lambda: False)

    resp = client.post("/v1/asx/scan/start")
    assert resp.status_code == 200
    body = resp.json()
    assert body["ok"] is True
    assert started == [True]
    assert body["job"]["id"] == "asx-scan"
    assert body["job"]["kind"] == "asx_scan"
    assert "progress" in body["job"]

    job = client.get("/v1/jobs/asx-scan")
    assert job.status_code == 200
    assert job.json()["id"] == "asx-scan"

    listed = client.get("/v1/jobs")
    assert listed.status_code == 200
    ids = [j["id"] for j in listed.json()["jobs"]]
    assert "asx-scan" in ids


def test_scan_pause_and_reset(client: TestClient, monkeypatch) -> None:
    store.reset_poc_data()
    store.set_poc_tickers(["CBA"])
    store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "error": "",
            "snapshot": {"price": 1.0, "change_pct": 0, "sentiment": "mixed"},
            "headlines": [],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )

    paused: list[bool] = []
    monkeypatch.setattr(
        "crawley.asx_desk.worker.request_pause",
        lambda: paused.append(True),
    )

    pause = client.post("/v1/asx/scan/pause")
    assert pause.status_code == 200
    assert pause.json()["ok"] is True
    assert paused

    reset = client.post("/v1/asx/scan/reset")
    assert reset.status_code == 200
    assert reset.json()["ok"] is True
    assert store.load_scans() == {}


def test_unknown_job(client: TestClient) -> None:
    resp = client.get("/v1/jobs/nope")
    assert resp.status_code == 404


def test_openapi_includes_v1_paths(client: TestClient) -> None:
    import json
    from pathlib import Path

    resp = client.get("/openapi.json")
    assert resp.status_code == 200
    spec = resp.json()
    assert spec["openapi"].startswith("3.")
    paths = spec["paths"]
    assert "/health" in paths
    assert "/v1/asx/companies" in paths
    assert "/v1/asx/companies/{ticker}" in paths
    assert "/v1/asx/scan/start" in paths
    assert "/v1/jobs/{job_id}" in paths

    from crawley.data.paths import REPO_ROOT

    checked_in = REPO_ROOT / "docs" / "api" / "openapi-v1.json"
    artifact = json.loads(checked_in.read_text(encoding="utf-8"))
    for path in (
        "/health",
        "/v1/asx/companies",
        "/v1/asx/companies/{ticker}",
        "/v1/asx/scan/start",
        "/v1/jobs/{job_id}",
    ):
        assert path in artifact["paths"]
