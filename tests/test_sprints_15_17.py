"""Sprints 15–17 — inbox/ASX scale + email bridge."""

from __future__ import annotations

from fastapi.testclient import TestClient

import crawley.asx_desk.store as asx_store
import crawley.sender_inbox.store as inbox_store
from crawley.bridge.matcher import match_message, run_bridge_scan
from crawley.sender_inbox.schema import normalize_metrics, sender_id_for
from crawley.settings import HARD_SCALE_CEILING, clamp_scale_cap


def test_clamp_scale_ceiling() -> None:
    assert clamp_scale_cap(500, default=20) == HARD_SCALE_CEILING
    assert clamp_scale_cap(0, default=20) == 1
    assert clamp_scale_cap("50", default=20) == 50


def test_inbox_prune_and_filter(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")
    monkeypatch.setattr(paths, "SECRETS_DIR", data / "secrets")

    for i in range(5):
        sid = sender_id_for(f"u{i}@example.com")
        inbox_store.upsert_message(
            {
                "id": f"m{i}",
                "thread_id": f"t{i}",
                "from_name": f"User {i}",
                "from_addr": f"u{i}@example.com",
                "sender_id": sid,
                "subject": f"Subject {i} billing" if i % 2 == 0 else f"Hello {i}",
                "snippet": "hi",
                "body_text": "body",
                "internal_date": f"2026-07-1{i}T10:00:00Z",
                "metrics": normalize_metrics(
                    {
                        "urgency": "low",
                        "category": "billing" if i % 2 == 0 else "personal",
                        "brief": "x",
                    }
                ),
                "error": None,
                "ingested_at": f"2026-07-1{i}T10:01:00Z",
            }
        )

    dropped = inbox_store.prune_messages(keep_max=3)
    assert dropped == 2
    assert len(inbox_store.load_messages()) == 3

    billing = inbox_store.group_senders(category="billing")
    assert billing
    assert all("billing" in (r.get("categories") or []) for r in billing)

    found = inbox_store.group_senders(query="billing")
    assert found
    none = inbox_store.group_senders(query="zzz-no-match")
    assert none == []


def test_settings_scale_and_gmail_filter_ui(client: TestClient) -> None:
    settings = client.get("/settings")
    assert settings.status_code == 200
    assert "Desk scale" in settings.text

    resp = client.post(
        "/settings/scale",
        data={"inbox_cap": "40", "inbox_keep_max": "40", "asx_cap": "35"},
    )
    assert resp.status_code == 200
    assert "Desk scale saved" in resp.text or "ceiling" in resp.text.lower()

    g = client.get("/modules/gmail?q=test&category=work")
    assert g.status_code == 200
    assert "Sender Inbox" in g.text


def test_asx_active_cap_expand(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    monkeypatch.setattr(paths, "SECRETS_DIR", data / "secrets")

    asx_store.reset_poc_data()
    state = asx_store.sync_active_cap(35, expand_from_universe=True)
    assert state["cap"] == 35
    assert len(state["poc_tickers"]) == 35


def test_events_and_bridge_routes(client: TestClient) -> None:
    asx_store.set_poc_tickers(["CBA", "BHP"])
    sid = sender_id_for("broker@example.com")
    inbox_store.upsert_message(
        {
            "id": "mb1",
            "thread_id": "tb1",
            "from_name": "Broker",
            "from_addr": "broker@example.com",
            "sender_id": sid,
            "subject": "Thoughts on CBA results",
            "snippet": "CBA reported",
            "body_text": "Holding CBA into results season.",
            "internal_date": "2026-07-16T10:00:00Z",
            "metrics": normalize_metrics({"category": "work", "brief": "CBA note"}),
            "error": None,
            "ingested_at": "2026-07-16T10:01:00Z",
        }
    )

    ev = client.get("/modules/investment/events")
    assert ev.status_code == 200
    assert "Earnings" in ev.text

    br = client.get("/modules/investment/bridge")
    assert br.status_code == 200
    assert "bridge" in br.text.lower()

    payload = run_bridge_scan()
    assert payload["status"] == "ready"
    assert any(h["ticker"] == "CBA" for h in payload["hits"])
    assert any(h.get("sender_id") == sid for h in payload["hits"])


def test_bridge_match_word_boundary() -> None:
    allow = {
        "CBA": {
            "ticker": "CBA",
            "name": "Commonwealth Bank",
            "in_poc": True,
            "in_portfolio": False,
        }
    }
    hits = match_message(
        {
            "id": "1",
            "sender_id": "abc",
            "subject": "XCBAX noise",
            "snippet": "",
            "body_text": "",
        },
        allow,
    )
    assert hits == []
    hits2 = match_message(
        {
            "id": "2",
            "sender_id": "abc",
            "subject": "Buy CBA today",
            "snippet": "",
            "body_text": "",
        },
        allow,
    )
    assert len(hits2) == 1
    assert hits2[0]["matched_via"] == "ticker"


def test_asx_cap_route(client: TestClient) -> None:
    resp = client.post("/modules/investment/asx/cap", data={"cap": "30"})
    assert resp.status_code == 200
    assert "ASX desk" in resp.text or "Active set" in resp.text
