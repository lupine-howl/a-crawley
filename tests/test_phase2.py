"""Tests for module registry and LLM provider wiring."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from crawley.app import create_app
from crawley.llm.base import LLMError
from crawley.llm.factory import get_llm_provider, llm_status
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.openai_provider import OpenAIProvider
from crawley.modules.registry import build_registry, nav_modules


EXPECTED_NAV = [
    "investment",
    "gmail",
    "calendar",
    "fitness",
    "co-parenting",
    "diy",
    "work",
    "finance-taxes",
    "coding-creative",
]


def test_registry_top_tier_nav_order() -> None:
    registry = build_registry()
    assert [m.meta.id for m in nav_modules(registry)] == EXPECTED_NAV
    assert registry["calendar"].panel_context()["coming_soon"] is True
    assert registry["fitness"].panel_context()["coming_soon"] is True
    assert registry["investment"].panel_context()["coming_soon"] is False


def test_openai_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("CRAWLEY_LLM_PROVIDER", "openai")
    with pytest.raises(LLMError, match="missing"):
        OpenAIProvider(api_key="")
    status = llm_status()
    assert status["ok"] is False
    assert "api key" in str(status["message"]).lower() or "missing" in str(status["message"]).lower()


def test_local_llama_placeholder() -> None:
    provider = LocalLlamaProvider()
    with pytest.raises(LLMError, match="placeholder"):
        provider.complete([])


def test_dashboard_and_stub_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app())
    home = client.get("/")
    assert home.status_code == 200
    assert "Crawley" in home.text
    assert "Investment" in home.text
    assert "Calendar" in home.text

    cal = client.get("/modules/calendar")
    assert cal.status_code == 200
    assert "Coming soon" in cal.text

    inv = client.get("/modules/investment")
    assert inv.status_code == 200
    assert "Coming soon" not in inv.text


def test_get_llm_openai_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("CRAWLEY_LLM_PROVIDER", "openai")
    with pytest.raises(LLMError, match="missing"):
        get_llm_provider()
