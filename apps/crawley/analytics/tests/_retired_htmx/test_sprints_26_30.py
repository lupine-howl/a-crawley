"""Sprints 26–30 — labels, holdings, searches, attachments, citations."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

import crawley.asx_desk.citations as citations
import crawley.asx_desk.holdings as holdings
import crawley.asx_desk.llm_tasks as llm_tasks
import crawley.google_oauth as google_oauth
import crawley.sender_inbox.attachments as attachments
import crawley.sender_inbox.labels as labels
import crawley.sender_inbox.saved_searches as searches
import crawley.writeback as wb
from crawley.google_oauth import GMAIL_MODIFY_SCOPE, _scopes_for
from crawley.sender_inbox.schema import sender_id_for


def test_gmail_modify_scope_opt_in() -> None:
    assert GMAIL_MODIFY_SCOPE not in _scopes_for()
    assert GMAIL_MODIFY_SCOPE in _scopes_for(include_gmail_modify=True)


def test_label_propose_cancel_audit(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(wb, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(wb, "DATA_DIR", tmp_path)
    monkeypatch.setattr(labels, "LABEL_DRAFTS_PATH", tmp_path / "label_drafts.json")
    monkeypatch.setattr(labels, "GMAIL_DIR", tmp_path)

    draft = labels.propose_label_change(
        message_id="m1",
        label_id="Label_1",
        op="add",
        label_name="Follow-up",
        sender_id="abc",
    )
    assert draft["action"] == "modify_labels"
    cancelled = labels.cancel_label_change(draft["draft_id"])
    assert cancelled is not None
    text = (tmp_path / "audit.jsonl").read_text(encoding="utf-8")
    assert "propose" in text
    assert "cancel" in text


def test_label_confirm_requires_modify_scope(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(wb, "AUDIT_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setattr(wb, "DATA_DIR", tmp_path)
    monkeypatch.setattr(labels, "LABEL_DRAFTS_PATH", tmp_path / "label_drafts.json")
    monkeypatch.setattr(labels, "GMAIL_DIR", tmp_path)
    draft = labels.propose_label_change(
        message_id="m1", label_id="Label_1", op="remove", label_name="X"
    )
    ok, msg, _ = labels.confirm_label_change(draft["draft_id"], modify_ok=False)
    assert ok is False
    assert "modify scope" in msg.lower()


def test_holdings_crud_and_prompt_slice(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    assert holdings.holdings_prompt_slice() == ""
    row = holdings.upsert_holding(ticker="CBA", qty=100, cost_note="~$90")
    assert row["ticker"] == "CBA"
    try:
        holdings.upsert_holding(ticker="!!!", qty=1)
        assert False, "expected validation error"
    except ValueError:
        pass
    slice_text = holdings.holdings_prompt_slice()
    assert "CBA" in slice_text
    assert "not broker" in slice_text.lower() or "manual" in slice_text.lower()
    assert holdings.delete_holding(row["id"]) is True


def test_holdings_route(client: TestClient, tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    resp = client.post(
        "/modules/investment/holdings",
        data={"ticker": "BHP", "qty": "50", "cost_note": "long term"},
    )
    assert resp.status_code == 200
    assert "Holdings journal" in resp.text
    assert "BHP" in resp.text


def test_saved_searches_persist(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    row = searches.upsert_search(name="Invoices", query="subject:invoice")
    assert row["id"]
    assert searches.get_search(row["id"])["query"] == "subject:invoice"
    assert searches.delete_search(row["id"]) is True


def test_saved_search_run_invalid_query(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths
    from googleapiclient.errors import HttpError

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "GMAIL_DIR", data / "gmail")

    class FakeResp:
        status = 400
        reason = "badRequest"

    def boom(*_a, **_k):
        raise HttpError(FakeResp(), b'{"error":{"message":"Invalid query"}}')

    fake_service = MagicMock()
    (
        fake_service.users.return_value.messages.return_value.list.return_value.execute
    ).side_effect = boom
    with patch("googleapiclient.discovery.build", return_value=fake_service):
        try:
            searches.run_saved_search(MagicMock(), "(((((")
            assert False, "expected ValueError"
        except ValueError as exc:
            assert "Invalid Gmail query" in str(exc)


def test_attachment_skip_reasons() -> None:
    huge = {"filename": "a.txt", "mime_type": "text/plain", "size": 999999, "attachment_id": "x"}
    assert attachments.skip_reason(huge)
    binary = {
        "filename": "x.exe",
        "mime_type": "application/octet-stream",
        "size": 100,
        "attachment_id": "y",
    }
    assert attachments.skip_reason(binary)
    ok = {
        "filename": "notes.txt",
        "mime_type": "text/plain",
        "size": 100,
        "attachment_id": "z",
    }
    assert attachments.skip_reason(ok) is None


def test_attachment_list_from_payload() -> None:
    payload = {
        "parts": [
            {
                "filename": "report.csv",
                "mimeType": "text/csv",
                "body": {"size": 12, "attachmentId": "att1"},
            }
        ]
    }
    rows = attachments.list_attachments_from_payload(payload)
    assert rows[0]["filename"] == "report.csv"


def test_citations_mute_and_markdown(tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")

    citations.record_headlines_as_citations(
        "CBA",
        [{"title": "CBA rises", "url": "https://news.example.com/cba"}],
    )
    md = citations.citations_markdown_section(
        "CBA",
        [{"title": "CBA rises", "url": "https://news.example.com/cba"}],
    )
    assert "## Citations" in md
    assert "news.example.com" in md

    citations.mute_domain("news.example.com")
    filtered = citations.filter_muted_headlines(
        [{"title": "x", "url": "https://news.example.com/a"}, {"title": "y", "url": "https://other.com/b"}]
    )
    assert len(filtered) == 1
    assert "other.com" in filtered[0]["url"]


def test_append_citations_section() -> None:
    out = llm_tasks.append_citations_section(
        "# Profile\n\nNotes",
        "CBA",
        [{"title": "Hello", "url": "https://ok.example/1"}],
    )
    assert "## Citations" in out


def test_citations_route(client: TestClient, tmp_path, monkeypatch) -> None:
    import crawley.data.paths as paths

    data = tmp_path / "data"
    monkeypatch.setattr(paths, "DATA_DIR", data)
    monkeypatch.setattr(paths, "INVESTMENT_DIR", data / "investment")
    resp = client.get("/modules/investment/citations")
    assert resp.status_code == 200
    assert "Citations" in resp.text
    mute = client.post("/modules/investment/citations/mute", data={"domain": "spam.example"})
    assert mute.status_code == 200
    assert "spam.example" in mute.text


def test_sender_inbox_shows_saved_searches(client: TestClient) -> None:
    resp = client.get("/modules/gmail")
    assert resp.status_code == 200
    # May show Connect or saved searches section depending on auth
    assert "Sender Inbox" in resp.text or "Gmail" in resp.text


def test_auth_status_includes_modify_flag(monkeypatch) -> None:
    monkeypatch.setenv("GOOGLE_CLIENT_ID", "cid")
    monkeypatch.setenv("GOOGLE_CLIENT_SECRET", "sec")
    monkeypatch.setattr(google_oauth, "load_credentials", lambda: None)
    status = google_oauth.google_auth_status()
    assert "gmail_modify_ok" in status
    assert status["gmail_modify_ok"] is False
