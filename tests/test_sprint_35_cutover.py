"""Sprint 35 — HTMX cutover: no product Jinja shell; quarantine lite modules."""

from __future__ import annotations

from fastapi.testclient import TestClient

from crawley.modules.registry import build_registry


def test_registry_empty_no_lite_modules() -> None:
    reg = build_registry()
    assert reg == {}
    for mid in (
        "calendar",
        "fitness",
        "work",
        "co_parenting",
        "diy",
        "finance",
        "coding_creative",
        "gmail",
        "investment",
    ):
        assert mid not in reg


def test_product_html_routes_gone(client: TestClient) -> None:
    assert client.get("/").status_code == 404
    assert client.get("/settings").status_code == 404
    assert client.get("/modules/gmail").status_code == 404
    assert client.get("/modules/investment").status_code == 404
    assert client.get("/modules/calendar").status_code == 404
    assert client.get("/modules/fitness").status_code == 404


def test_json_api_and_oauth_paths_remain(client: TestClient) -> None:
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["ok"] is True

    assert client.get("/v1/asx/companies").status_code == 200
    assert client.get("/v1/gmail/senders").status_code == 200
    assert client.get("/v1/jobs/asx-scan").status_code == 200
    assert client.get("/v1/jobs/gmail-ingest").status_code == 200

    conn = client.get("/v1/gmail/connection")
    assert conn.status_code == 200
    assert conn.json()["oauth_start_path"] == "/modules/gmail/oauth/start"

    # Missing Google client → friendly HTML error page (not Jinja dashboard)
    start = client.get("/modules/gmail/oauth/start", follow_redirects=False)
    assert start.status_code in {200, 302, 303, 307, 400}
    if start.status_code in {200, 400}:
        assert "crawley-ui" in start.text
        assert "Google" in start.text or "connect" in start.text.lower() or "failed" in start.text.lower()


def test_app_has_no_shell_router() -> None:
    from crawley.app import create_app

    app = create_app()
    paths = {getattr(r, "path", None) for r in app.routes}
    assert "/" not in paths or all(
        getattr(r, "path", None) != "/" or getattr(r, "methods", None) == {"HEAD"}
        for r in app.routes
    )
    # Dashboard home must not be a TemplateResponse route
    for r in app.routes:
        endpoint = getattr(r, "endpoint", None)
        if endpoint and getattr(endpoint, "__module__", "").startswith("crawley.shell"):
            raise AssertionError(f"shell route still mounted: {r}")
