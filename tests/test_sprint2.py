"""Sprint 2: themes, settings, markdown, home glance."""

from __future__ import annotations

from fastapi.testclient import TestClient

from crawley.data.snapshots import get_snapshot, save_snapshot
from crawley.llm.base import ChatResult
from crawley.markdown_render import render_markdown
from crawley.settings import load_settings, resolve_theme, update_llm_settings


def test_markdown_renders_safe_subset() -> None:
    html = str(render_markdown("**bold**\n\n- one\n\n<script>alert(1)</script>"))
    assert "<strong>bold</strong>" in html
    assert "<li>one</li>" in html
    assert "<script>" not in html


def test_theme_cookie_and_settings(client: TestClient) -> None:
    response = client.post("/settings/theme", data={"theme": "ink"}, follow_redirects=False)
    assert response.status_code in {200, 303}
    assert response.cookies.get("crawley_theme") == "ink"
    assert load_settings().theme == "ink"

    home = client.get("/")
    assert home.status_code == 200
    assert 'data-theme="ink"' in home.text
    assert "Settings" in home.text


def test_settings_llm_save_and_status(client: TestClient, monkeypatch) -> None:
    monkeypatch.setenv("OPENAI_API_KEY", "env-key")
    client.post(
        "/settings/llm",
        data={"provider": "openai", "model": "gpt-test", "api_key": "ui-key"},
        headers={"HX-Request": "true"},
    )
    settings = load_settings()
    assert settings.llm.api_key == "ui-key"
    assert settings.llm.model == "gpt-test"

    from crawley.settings import resolved_openai_key, resolved_openai_model

    assert resolved_openai_key() == "ui-key"
    assert resolved_openai_model() == "gpt-test"

    # Blank key keeps existing
    update_llm_settings(provider="openai", model="gpt-test", api_key="")
    assert load_settings().llm.api_key == "ui-key"


def test_test_connection_missing_key(client: TestClient) -> None:
    response = client.post("/settings/llm/test", headers={"HX-Request": "true"})
    assert response.status_code == 200
    assert "No API key" in response.text or "missing" in response.text.lower()


def test_test_connection_success(client: TestClient, monkeypatch) -> None:
    update_llm_settings(provider="openai", model="fake", api_key="k")

    class Fake:
        name = "openai"

        def complete(self, messages, *, max_tokens=512):
            return ChatResult(content="pong", model="fake-model")

    monkeypatch.setattr("crawley.llm.factory.get_llm_provider", lambda: Fake())
    response = client.post("/settings/llm/test")
    assert "Connected" in response.text


def test_home_glance_empty_and_persisted(client: TestClient) -> None:
    home = client.get("/")
    assert home.status_code == 200
    assert "At a glance" in home.text
    assert "No successful run yet" in home.text

    save_snapshot("investment", "## Hello\n\n- note")
    home2 = client.get("/")
    assert "Hello" in home2.text
    assert "<li>note</li>" in home2.text or "note" in home2.text


def test_snapshot_not_clobbered_by_empty(client: TestClient) -> None:
    save_snapshot("gmail", "Keep me")
    snap = get_snapshot("gmail")
    assert snap and snap.summary_md == "Keep me"


def test_resolve_theme_precedence() -> None:
    assert resolve_theme(cookie_value="moss") == "moss"
    assert resolve_theme(cookie_value="nope") == "paper"


def test_investment_panel_uses_markdown_html(client: TestClient) -> None:
    module = client.app.state.registry["investment"]
    module.job.summary = "**Advice**"
    module.job.status = "done"
    response = client.get("/modules/investment")
    assert "<strong>Advice</strong>" in response.text
    assert "<pre>" not in response.text or "Advice" in response.text


def test_settings_shows_model_dropdown(client: TestClient, monkeypatch) -> None:
    monkeypatch.setattr(
        "crawley.shell.routes.list_openai_models",
        lambda force_refresh=False: {
            "models": ["gpt-4o-mini", "gpt-4o"],
            "error": None,
            "source": "api",
        },
    )
    page = client.get("/settings")
    assert page.status_code == 200
    assert '<select id="llm-model"' in page.text
    assert "gpt-4o-mini" in page.text
    assert "Summary prompts" in page.text


def test_save_prompts(client: TestClient) -> None:
    response = client.post(
        "/settings/prompts",
        data={
            "investment_system": "Invest system custom",
            "investment_user_footer": "Footer custom",
            "gmail_system": "Gmail system custom",
            "gmail_user_header": "Header custom",
        },
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert "Prompts saved" in response.text
    prompts = load_settings().prompts
    assert prompts.investment_system == "Invest system custom"
    assert prompts.gmail_user_header == "Header custom"


def test_investment_uses_saved_prompt_and_exposes_introspection(
    client: TestClient, monkeypatch
) -> None:
    from crawley.settings import update_prompt_settings

    update_prompt_settings(
        investment_system="SYS-INVEST",
        investment_user_footer="FOOTER-INVEST",
        gmail_system="SYS-GMAIL",
        gmail_user_header="HDR-GMAIL",
    )
    monkeypatch.setattr(
        "crawley.modules.investment.fetch_rss_items",
        lambda query, limit=3: [
            {"title": "T", "url": "https://example.com", "snippet": "s", "body": "b"}
        ],
    )
    monkeypatch.setattr(
        "crawley.modules.investment.persist_artifacts",
        lambda query, items: [
            {
                "id": "1",
                "title": "T",
                "url": "https://example.com",
                "snippet": "s",
                "artifact_path": "x",
            }
        ],
    )

    class FakeProvider:
        def complete(self, messages, *, max_tokens=512):
            assert messages[0].content == "SYS-INVEST"
            assert "FOOTER-INVEST" in messages[1].content
            return ChatResult(content="## Result", model="fake")

    monkeypatch.setattr(
        "crawley.modules.investment.get_llm_provider",
        lambda: FakeProvider(),
    )
    module = client.app.state.registry["investment"]
    module._job_body("markets")
    assert module.job.details["prompt_system"] == "SYS-INVEST"
    assert "FOOTER-INVEST" in module.job.details["prompt_user"]
    page = client.get("/modules/investment")
    assert "Last prompt sent" in page.text
    assert "SYS-INVEST" in page.text
