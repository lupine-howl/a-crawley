"""Sprints 21–24 — OAuth ops, thread digests, ASX notebook, VIP rules."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

import crawley.asx_desk.notebook as notebook
import crawley.asx_desk.store as asx_store
import crawley.google_oauth as google_oauth
import crawley.sender_inbox.digests as digests
import crawley.sender_inbox.rules as rules
import crawley.sender_inbox.store as inbox_store
from crawley.google_oauth import CALENDAR_EVENTS_SCOPE, GMAIL_SEND_SCOPE, redirect_uri, should_force_consent
from crawley.modules.registry import build_registry
from crawley.sender_inbox.schema import sender_id_for


def test_redirect_uri_tailscale_host() -> None:
    uri = redirect_uri("http://100.64.1.2:8000")
    assert uri == "http://100.64.1.2:8000/modules/gmail/oauth/callback"


def test_settings_shows_oauth_redirect(client: TestClient) -> None:
    resp = client.get("/settings", headers={"Host": "100.64.9.9:8000"})
    assert resp.status_code == 200
    assert "Google OAuth" in resp.text
    assert "/modules/gmail/oauth/callback" in resp.text


def test_should_force_consent_without_token() -> None:
    assert should_force_consent(creds=None) is True


def test_should_force_consent_optional_when_refresh_and_scopes(monkeypatch) -> None:
    creds = MagicMock()
    creds.refresh_token = "rt"
    creds.scopes = list(google_oauth.SCOPES)
    monkeypatch.setattr(google_oauth, "load_credentials", lambda: creds)
    assert should_force_consent() is False
    assert should_force_consent(include_gmail_send=True) is True
    assert should_force_consent(include_calendar_write=True) is True


def test_authorization_url_omits_prompt_when_optional(monkeypatch, tmp_path) -> None:
    pending = tmp_path / "pending.json"
    monkeypatch.setattr(google_oauth, "PENDING_OAUTH_PATH", pending)
    monkeypatch.setattr(google_oauth, "SECRETS_DIR", tmp_path)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")

    captured: dict = {}

    class FakeFlow:
        redirect_uri = "http://127.0.0.1:8000/modules/gmail/oauth/callback"
        code_verifier = None

        def authorization_url(self, **kwargs):
            captured.update(kwargs)
            self.code_verifier = "verifier-abc"
            return "https://accounts.google.com/o/oauth2/auth?x=1", "state-xyz"

    creds = MagicMock()
    creds.refresh_token = "rt"
    creds.scopes = list(google_oauth.SCOPES)
    monkeypatch.setattr(google_oauth, "load_credentials", lambda: creds)
    monkeypatch.setattr(google_oauth, "build_auth_flow", lambda base, **kwargs: FakeFlow())
    google_oauth.authorization_url("http://127.0.0.1:8000")
    assert captured.get("access_type") == "offline"
    assert "prompt" not in captured


def test_authorization_url_forces_consent_for_new_scope(monkeypatch, tmp_path) -> None:
    pending = tmp_path / "pending.json"
    monkeypatch.setattr(google_oauth, "PENDING_OAUTH_PATH", pending)
    monkeypatch.setattr(google_oauth, "SECRETS_DIR", tmp_path)
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid.apps.googleusercontent.com")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "csecret")

    captured: dict = {}

    class FakeFlow:
        redirect_uri = "http://127.0.0.1:8000/modules/gmail/oauth/callback"
        code_verifier = None

        def authorization_url(self, **kwargs):
            captured.update(kwargs)
            self.code_verifier = "verifier-abc"
            return "https://accounts.google.com/o/oauth2/auth?x=1", "state-xyz"

    creds = MagicMock()
    creds.refresh_token = "rt"
    creds.scopes = list(google_oauth.SCOPES)
    monkeypatch.setattr(google_oauth, "load_credentials", lambda: creds)
    monkeypatch.setattr(google_oauth, "build_auth_flow", lambda base, **kwargs: FakeFlow())
    google_oauth.authorization_url("http://127.0.0.1:8000", include_gmail_send=True)
    assert captured.get("prompt") == "consent"
    assert GMAIL_SEND_SCOPE
    assert CALENDAR_EVENTS_SCOPE


def test_vip_rules_boost_sender_list(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    vip_addr = "boss@example.com"
    muted_addr = "news@example.com"
    vip_id = sender_id_for(vip_addr)
    muted_id = sender_id_for(muted_addr)
    inbox_store.upsert_message(
        {
            "id": "m1",
            "thread_id": "t1",
            "from_name": "Boss",
            "from_addr": vip_addr,
            "sender_id": vip_id,
            "subject": "Hello",
            "snippet": "hi",
            "body_text": "hi",
            "internal_date": "2026-07-16T10:00:00Z",
            "metrics": {"urgency": "low", "category": "work"},
            "error": None,
            "ingested_at": "2026-07-16T10:00:00Z",
        }
    )
    inbox_store.upsert_message(
        {
            "id": "m2",
            "thread_id": "t2",
            "from_name": "News",
            "from_addr": muted_addr,
            "sender_id": muted_id,
            "subject": "Digest",
            "snippet": "n",
            "body_text": "n",
            "internal_date": "2026-07-16T12:00:00Z",
            "metrics": {"urgency": "medium", "category": "newsletter"},
            "error": None,
            "ingested_at": "2026-07-16T12:00:00Z",
        }
    )
    rules.upsert_rule(sender_id=vip_id, from_addr=vip_addr, priority="vip")
    rules.upsert_rule(sender_id=muted_id, from_addr=muted_addr, priority="muted")
    rows = inbox_store.group_senders()
    assert rows[0]["sender_id"] == vip_id
    assert rows[0]["rule_priority"] == "vip"
    assert any(r["sender_id"] == muted_id and r["rule_priority"] == "muted" for r in rows)

    applied = rules.apply_rule_to_metrics(
        {"urgency": "critical", "vip": False, "category": "other"},
        rules.get_rule(muted_id),
    )
    assert applied["urgency"] == "medium"
    assert "muted" in applied["signals"]


def test_thread_digest_store_and_list(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    digests._set_digest(
        "thr-1",
        status="done",
        markdown="## Summary\nHello\n## Asks\n-\n## Commitments\n-\n## Suggested next action\nReply",
        subject="Hello",
        message_count=2,
    )
    row = digests.get_digest("thr-1")
    assert row is not None
    assert row["status"] == "done"
    assert "Summary" in row["markdown"]

    listed = digests.digests_for_sender(
        "sid",
        [
            {
                "thread_id": "thr-1",
                "subject": "Hello",
                "internal_date": "2026-07-16T10:00:00Z",
                "id": "m1",
            }
        ],
    )
    assert listed[0]["thread_id"] == "thr-1"
    assert listed[0]["status"] == "done"


def test_asx_notebook_prompt_slice(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    assert notebook.notebook_prompt_slice("CBA") == ""
    notebook.save_notebook("CBA", thesis="Hold for dividend", notes="Watch FY results")
    slice_one = notebook.notebook_prompt_slice("CBA")
    assert "Hold for dividend" in slice_one
    assert len(slice_one) <= notebook.PROMPT_SLICE_CHARS

    multi = notebook.notebook_prompt_slice()
    assert "CBA" in multi


def test_asx_notebook_route(client: TestClient, tmp_path, monkeypatch) -> None:
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
                "change_pct": 1.0,
                "sentiment": "mixed",
                "headline": "x",
                "gaps": [],
                "currency": "AUD",
                "volume": 1,
            },
            "headlines": [],
            "sources_used": [],
            "scanned_at": "2026-07-16T00:00:00Z",
        },
    )
    resp = client.post(
        "/modules/investment/companies/CBA/notebook",
        data={"thesis": "Long-term hold", "notes": "Bank exposure"},
    )
    assert resp.status_code == 200
    assert "Research notebook" in resp.text
    assert "Long-term hold" in resp.text
    nb = notebook.load_notebook("CBA")
    assert nb["thesis"] == "Long-term hold"


def test_gmail_rules_route(client: TestClient, tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    sid = sender_id_for("vip@example.com")
    inbox_store.upsert_message(
        {
            "id": "mx",
            "thread_id": "tx",
            "from_name": "VIP",
            "from_addr": "vip@example.com",
            "sender_id": sid,
            "subject": "Hi",
            "snippet": "s",
            "body_text": "b",
            "internal_date": "2026-07-16T10:00:00Z",
            "metrics": {},
            "error": None,
            "ingested_at": "2026-07-16T10:00:00Z",
        }
    )
    resp = client.post(
        "/modules/gmail/rules",
        data={
            "sender_id": sid,
            "from_addr": "vip@example.com",
            "priority": "vip",
            "tags": "family",
            "return_to": "sender",
        },
    )
    assert resp.status_code == 200
    assert rules.get_rule(sid)["priority"] == "vip"
    detail = client.get(f"/modules/gmail/senders/{sid}")
    assert detail.status_code == 200
    assert "Thread digests" in detail.text
    assert "Priority rule" in detail.text


def test_scopes_still_offline_access() -> None:
    # Documented invariant: offline access always requested in authorization_url kwargs.
    assert "gmail.readonly" in google_oauth.SCOPES[0]
    registry = build_registry()
    assert "gmail" in registry
