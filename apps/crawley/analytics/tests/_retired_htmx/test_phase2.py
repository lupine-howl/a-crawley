"""Tests for module registry and LLM provider wiring."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from crawley.app import create_app
from crawley.llm.base import LLMError
from crawley.llm.factory import get_llm_provider, llm_status
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.openai_provider import (
    OpenAIProvider,
    completion_token_kwargs,
    uses_max_completion_tokens,
)
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
    assert registry["calendar"].panel_context()["coming_soon"] is False
    assert registry["fitness"].panel_context()["coming_soon"] is False
    assert registry["investment"].panel_context()["coming_soon"] is False
    assert registry["work"].panel_context()["coming_soon"] is False
    assert registry["diy"].panel_context()["coming_soon"] is False
    assert registry["co-parenting"].panel_context()["coming_soon"] is False
    assert registry["finance-taxes"].panel_context()["coming_soon"] is False
    assert registry["coding-creative"].panel_context()["coming_soon"] is False


def test_completion_token_param_by_model() -> None:
    assert uses_max_completion_tokens("gpt-5.4-mini")
    assert uses_max_completion_tokens("o3-mini")
    assert not uses_max_completion_tokens("gpt-4o-mini")
    assert completion_token_kwargs("gpt-5.4-mini", 256) == {
        "max_completion_tokens": 256
    }
    assert completion_token_kwargs("gpt-4o-mini", 256) == {"max_tokens": 256}


def test_openai_missing_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("CRAWLEY_LLM_PROVIDER", "openai")
    with pytest.raises(LLMError, match="missing"):
        OpenAIProvider(api_key="")
    status = llm_status()
    assert status["ok"] is False
    assert "api key" in str(status["message"]).lower() or "missing" in str(status["message"]).lower()


def test_local_llama_unreachable() -> None:
    provider = LocalLlamaProvider(base_url="http://127.0.0.1:9", timeout_s=1)
    with pytest.raises(LLMError, match="unreachable|timed out|Local LLM"):
        provider.complete([])


def test_dashboard_and_stub_panel(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    client = TestClient(create_app())
    home = client.get("/")
    assert home.status_code == 200
    assert "Crawley" in home.text
    assert "Investment" in home.text
    assert "Calendar" in home.text
    assert "Last Fitness" in home.text

    cal = client.get("/modules/calendar")
    assert cal.status_code == 200
    assert "Coming soon" not in cal.text
    assert "Skim next" in cal.text or "Connect Google" in cal.text

    fit = client.get("/modules/fitness")
    assert fit.status_code == 200
    assert "Coming soon" not in fit.text
    assert "not medical" in fit.text.lower() or "Not medical" in fit.text

    inv = client.get("/modules/investment")
    assert inv.status_code == 200
    assert "Coming soon" not in inv.text

    work = client.get("/modules/work")
    assert work.status_code == 200
    assert "Coming soon" not in work.text
    assert "Prioritize" in work.text

    diy = client.get("/modules/diy")
    assert diy.status_code == 200
    assert "Coming soon" not in diy.text
    assert "Save" in diy.text


def test_get_llm_openai_requires_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("CRAWLEY_LLM_PROVIDER", "openai")
    with pytest.raises(LLMError, match="missing"):
        get_llm_provider()
