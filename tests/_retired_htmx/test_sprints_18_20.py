"""Sprints 18–20 — Gmail send, ASX alerts/feedback, playbooks."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import crawley.asx_desk.alerts as alerts
import crawley.asx_desk.feedback as feedback
import crawley.asx_desk.store as asx_store
import crawley.modules.gmail as gmail_mod
import crawley.playbooks as playbooks
from crawley.asx_desk.feedback import apply_feedback_to_rows, set_disposition
from crawley.google_oauth import GMAIL_SEND_SCOPE, _scopes_for
from crawley.modules.registry import build_registry


def test_gmail_send_scope_opt_in() -> None:
    assert GMAIL_SEND_SCOPE not in _scopes_for()
    assert GMAIL_SEND_SCOPE in _scopes_for(include_gmail_send=True)


def test_gmail_propose_cancel_no_send(tmp_path, monkeypatch) -> None:
    import crawley.writeback as wb

    monkeypatch.setattr(wb, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(wb, "DATA_DIR", tmp_path)
    monkeypatch.setattr(gmail_mod, "SEND_DRAFTS_PATH", tmp_path / "drafts.json")
    monkeypatch.setattr(gmail_mod, "GMAIL_DIR", tmp_path)

    gmail = build_registry()["gmail"]
    proposed = gmail.write_back(
        {
            "action": "propose",
            "to": "x@example.com",
            "subject": "Ping",
            "body": "Body text",
        }
    )
    assert proposed.error is None
    draft_id = proposed.details["draft"]["draft_id"]
    # Confirm without send scope fails without remote call
    with patch.object(gmail, "auth_status", return_value={"gmail_send_ok": False, "connected": True}):
        failed = gmail.write_back({"action": "confirm", "draft_id": draft_id})
    assert failed.error
    assert "send scope" in failed.error.lower()

    cancelled = gmail.write_back({"action": "cancel", "draft_id": draft_id})
    assert cancelled.error is None
    text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "propose" in text
    assert "cancel" in text


def test_alerts_keyword_and_home_chip(client: TestClient, tmp_path, monkeypatch) -> None:
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
            "snapshot": {
                "price": 100,
                "change_pct": 4.5,
                "sentiment": "mixed",
                "headline": "CBA earnings beat",
                "gaps": [],
            },
            "headlines": [{"title": "CBA earnings beat", "url": ""}],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    alerts.add_rule(ticker="CBA", condition="keyword", value="earnings")
    triggered = alerts.evaluate_alerts()
    assert any("earnings" in (a.get("message") or "").lower() for a in triggered)

    # Route smoke on client fixture paths
    resp = client.get("/modules/investment")
    assert resp.status_code == 200
    assert "Local alerts" in resp.text


def test_recommendation_feedback_hides_dismissed(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    set_disposition("CBA", "dismissed", note="already owned")
    rows = apply_feedback_to_rows(
        [
            {"ticker": "CBA", "action": "Buy", "urgency": "high", "rationale": "x"},
            {"ticker": "BHP", "action": "Hold", "urgency": "low", "rationale": "y"},
        ]
    )
    assert [r["ticker"] for r in rows] == ["BHP"]


def test_playbooks_default_and_run(client: TestClient) -> None:
    rows = playbooks.load_playbooks()
    assert any(p["id"] == "morning-mail" for p in rows)
    settings = client.get("/settings")
    assert settings.status_code == 200
    assert "Playbooks" in settings.text

    # Run ASX playbook — may fail if no profiles; should not 500
    resp = client.post("/modules/playbooks/asx-morning/run")
    assert resp.status_code == 200


def test_feedback_and_send_routes(client: TestClient) -> None:
    asx_store.save_recommendations(
        {
            "rows": [
                {
                    "ticker": "CSL",
                    "action": "Watch",
                    "urgency": "low",
                    "rationale": "thin",
                    "generated_at": "2026-07-16T00:00:00Z",
                }
            ],
            "updated_at": "2026-07-16T00:00:00Z",
            "status": "ready",
            "error": "",
        }
    )
    resp = client.post(
        "/modules/investment/recommendations/feedback",
        data={"ticker": "CSL", "disposition": "snoozed"},
    )
    assert resp.status_code == 200
    assert "Recommendations" in resp.text
