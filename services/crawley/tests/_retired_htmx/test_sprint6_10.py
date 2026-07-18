"""Sprints 6–10: life modules, day brief, write-back, local LLM, shared context."""

from __future__ import annotations

from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from crawley.data.snapshots import save_snapshot
from crawley.day_brief import compose_day_brief_markdown
from crawley.llm.base import ChatResult, LLMError
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.modules.calendar import CalendarModule
from crawley.shared_context import (
    append_context_to_user_message,
    build_shared_context,
    save_standing_notes,
)


def test_life_modules_leave_coming_soon(client: TestClient) -> None:
    for mid in ("co-parenting", "diy", "finance-taxes", "coding-creative"):
        resp = client.get(f"/modules/{mid}")
        assert resp.status_code == 200
        assert "Coming soon" not in resp.text


def test_diy_run_snapshot_and_home(client: TestClient, monkeypatch) -> None:
    module = client.app.state.registry["diy"]
    fake = MagicMock()
    fake.complete.return_value = ChatResult(content="## Next steps\n- Buy screws", model="test")
    monkeypatch.setattr("crawley.modules.notes_lite.get_llm_provider", lambda: fake)
    module._job_body("# Shelf\n- Measure")
    assert module.job.status == "done"
    home = client.get("/")
    assert "Buy screws" in home.text or "Next steps" in home.text


def test_co_parenting_parse_and_empty_window(client: TestClient, monkeypatch) -> None:
    from crawley.modules import co_parenting as co

    entries = co.parse_schedule_text("2099-01-01 | all day | far future")
    assert entries[0]["date"] == "2099-01-01"
    module = client.app.state.registry["co-parenting"]
    # Force empty bounded window by using past dates only.
    module._job_body([{"date": "2000-01-01", "window": "old", "notes": ""}])
    assert module.job.status == "done"
    assert "Quiet window" in (module.job.summary or "")


def test_finance_disclaimer(client: TestClient) -> None:
    resp = client.get("/modules/finance-taxes")
    assert "not professional" in resp.text.lower()


def test_day_brief_partial_and_empty(client: TestClient) -> None:
    empty = compose_day_brief_markdown()
    assert empty["empty"] is True
    save_snapshot("calendar", "## Tomorrow\n- Dentist")
    partial = compose_day_brief_markdown()
    assert partial["empty"] is False
    assert partial["partial"] is True
    assert "Dentist" in partial["markdown"]
    assert "No successful Gmail" in partial["markdown"]
    home = client.get("/")
    assert "Day brief" in home.text


def test_calendar_propose_cancel_no_remote(client: TestClient) -> None:
    module = client.app.state.registry["calendar"]
    assert isinstance(module, CalendarModule)
    result = module.write_back(
        {
            "action": "propose",
            "summary": "Test event",
            "start": "2030-01-01T10:00:00Z",
            "end": "2030-01-01T11:00:00Z",
            "description": "draft only",
        }
    )
    assert result.error is None
    draft_id = result.details["draft"]["draft_id"]
    cancel = module.cancel_write_back(draft_id)
    assert cancel.error is None
    assert module.pending_draft is None
    settings = client.get("/settings")
    assert "Write-back audit" in settings.text


def test_local_llama_ping_unreachable() -> None:
    provider = LocalLlamaProvider(base_url="http://127.0.0.1:9", timeout_s=1)
    ping = provider.ping()
    assert ping["ok"] is False
    assert ping["state"] in {"unreachable", "timeout", "failure"}


def test_local_llama_settings_test(client: TestClient, monkeypatch) -> None:
    from crawley.settings import update_llm_settings

    update_llm_settings(
        provider="local_llama",
        model="llama3.2",
        api_key=None,
        base_url="http://127.0.0.1:9",
        timeout_s=1,
    )
    monkeypatch.setattr(
        "crawley.llm.factory.LocalLlamaProvider.ping",
        lambda self: {
            "ok": False,
            "state": "unreachable",
            "message": "Local LLM unreachable",
        },
    )
    resp = client.post("/settings/llm/test")
    assert resp.status_code == 200
    assert "unreachable" in resp.text.lower() or "Local LLM" in resp.text


def test_shared_context_caps_and_no_secrets(client: TestClient) -> None:
    save_standing_notes("Remember school pickup")
    save_snapshot("work", "x" * 2000)
    bundle = build_shared_context()
    assert "school pickup" in bundle.text
    assert len(bundle.text) <= 3600
    assert "OPENAI" not in bundle.text
    user = append_context_to_user_message("Base notes", bundle)
    assert "shared context" in user.lower()


def test_coding_with_shared_context(client: TestClient, monkeypatch) -> None:
    save_standing_notes("Prefer shippable slices")
    module = client.app.state.registry["coding-creative"]
    fake = MagicMock()
    fake.complete.return_value = ChatResult(content="## Focus now\n- Ship slice", model="t")
    monkeypatch.setattr("crawley.modules.coding_creative.get_llm_provider", lambda: fake)
    module._include_shared = True
    module._job_body("# Project\n- Ideas")
    assert module.job.status == "done"
    assert "Prefer shippable" in module.job.details["prompt_user"]
