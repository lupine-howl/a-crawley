"""API support for crawley-ui expansion (LLM settings, force scan, extras)."""

from __future__ import annotations

from fastapi.testclient import TestClient

import crawley.asx_desk.store as store


def test_llm_settings_roundtrip(client: TestClient) -> None:
    get = client.get("/v1/settings/llm")
    assert get.status_code == 200
    assert "provider" in get.json()
    assert "has_api_key" in get.json()
    assert "api_key" not in get.json()

    put = client.put(
        "/v1/settings/llm",
        json={
            "provider": "local_llama",
            "model": "llama3.2",
            "base_url": "http://127.0.0.1:11434",
            "timeout_s": 45,
        },
    )
    assert put.status_code == 200
    body = put.json()
    assert body["provider"] == "local_llama"
    assert body["model"] == "llama3.2"

    scale = client.get("/v1/settings/scale")
    assert scale.status_code == 200
    assert scale.json()["local_llama_uncapped"] is True
    assert scale.json()["asx_cap"] >= 200


def test_force_scan_start_when_complete(client: TestClient, monkeypatch) -> None:
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

    blocked = client.post("/v1/asx/scan/start", json={"force": False})
    assert blocked.status_code == 200
    assert blocked.json()["ok"] is False

    started: list[bool] = []

    def fake_start(executor, *, force: bool = False):
        started.append(force)
        return True, "Scan started."

    monkeypatch.setattr("crawley.asx_desk.worker.start_scan", fake_start)
    forced = client.post("/v1/asx/scan/start", json={"force": True})
    assert forced.status_code == 200
    assert forced.json()["ok"] is True
    assert started == [True]


def test_asx_extra_endpoints(client: TestClient) -> None:
    assert client.get("/v1/asx/recommendations").status_code == 200
    assert client.get("/v1/asx/portfolio").status_code == 200
    assert client.get("/v1/asx/clusters").status_code == 200
    assert client.get("/v1/asx/alerts").status_code == 200
    assert client.get("/v1/asx/holdings").status_code == 200
    nb = client.get("/v1/asx/companies/CBA/notebook")
    assert nb.status_code == 200
    put = client.put(
        "/v1/asx/companies/CBA/notebook",
        json={"thesis": "Hold", "notes": "Watch margins"},
    )
    assert put.status_code == 200
    assert put.json()["thesis"] == "Hold"


def test_scan_stop_endpoint(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "crawley.asx_desk.worker.stop_scan",
        lambda: (True, "Stop requested."),
    )
    resp = client.post("/v1/asx/scan/stop")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True
