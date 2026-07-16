"""Sprints 14–16 tests."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import crawley.asx_desk.portfolio as portfolio
import crawley.asx_desk.store as store
from crawley.asx_desk.recommendations import normalize_recommendation
from crawley.data import snapshots
from crawley.modules import fitness_import
from crawley.settings import load_settings, update_simulation_settings
from crawley.shared_context import build_shared_context, list_pins, pin_history


def test_recommendations_and_portfolio_routes(client: TestClient) -> None:
    r = client.get("/modules/investment/recommendations")
    assert r.status_code == 200
    assert "Recommendations" in r.text
    assert "not advice" in r.text.lower() or "Not licensed" in r.text
    p = client.get("/modules/investment/portfolio")
    assert p.status_code == 200
    assert "Paper portfolio" in p.text
    assert "Simulation settings" in p.text or "simulation" in p.text.lower()


def test_paper_trade_and_fees(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(paths, "SECRETS_DIR", data / "secrets")
    import crawley.settings as settings

    monkeypatch.setattr(settings, "SECRETS_DIR", data / "secrets")
    monkeypatch.setattr(settings, "SETTINGS_PATH", data / "secrets" / "settings.json")

    update_simulation_settings(
        starting_cash=10_000,
        fee_flat=10,
        fee_pct=0,
        reset_portfolio_cash=True,
    )
    store.upsert_scan(
        "CBA",
        {
            "ticker": "CBA",
            "status": "ready",
            "snapshot": {"price": 100.0, "change_pct": 0, "sentiment": "mixed"},
            "headlines": [],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
            "error": "",
        },
    )
    ok, msg, port = portfolio.add_paper_trade(ticker="CBA", side="buy", qty=10, price=100)
    assert ok, msg
    # 1000 notional + 10 fee
    assert abs(port["cash"] - 8990) < 0.01
    view = portfolio.portfolio_view()
    assert view["positions"][0]["ticker"] == "CBA"
    assert view["equity_mtm"] == 1000


def test_normalize_recommendation() -> None:
    r = normalize_recommendation({"ticker": "bhp", "action": "buy", "urgency": "HIGH", "rationale": "x"})
    assert r["ticker"] == "BHP"
    assert r["action"] == "Buy"
    assert r["urgency"] == "high"


def test_snapshot_history_and_pins(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)

    snapshots.save_snapshot("gmail", "## One\nFirst")
    snapshots.save_snapshot("gmail", "## Two\nSecond")
    hist = snapshots.list_history(module_id="gmail")
    assert len(hist) >= 2
    ok, _ = pin_history(hist[0]["id"])
    assert ok
    assert list_pins()
    bundle = build_shared_context()
    assert "Pinned history" in bundle.text or "pinned" in bundle.text.lower()


def test_fitness_import(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "FITNESS_DIR", data / "fitness")

    ok, msg = fitness_import.save_activity_import(b"date,steps\n2026-07-01,8000\n", filename="a.csv")
    assert ok, msg
    assert "8000" in fitness_import.load_activity_import()
    bad, _ = fitness_import.save_activity_import(b"\x00\x01\x02binary")
    assert bad is False


def test_settings_simulation_and_history_ui(client: TestClient) -> None:
    snapshots.save_snapshot("investment", "## ASX\nGlance")
    page = client.get("/settings")
    assert page.status_code == 200
    assert "Paper portfolio" in page.text
    assert "Snapshot history" in page.text
    sim = client.post(
        "/settings/simulation",
        data={
            "starting_cash": "50000",
            "fee_flat": "5",
            "fee_pct": "0.2",
            "currency": "AUD",
            "broker_label": "SimCo",
        },
        headers={"HX-Request": "true"},
    )
    assert sim.status_code == 200
    assert load_settings().simulation.starting_cash == 50000
