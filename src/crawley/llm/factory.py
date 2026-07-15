"""Resolve the configured LLM provider."""

from __future__ import annotations

from crawley.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.openai_provider import OpenAIProvider
from crawley.settings import (
    resolved_llm_provider_name,
    resolved_openai_key,
    resolved_openai_model,
)


def get_llm_provider() -> LLMProvider:
    """
    Return the active provider from Settings (hot-reload on each call).

    Precedence: saved Settings API key/model/provider override `.env` when set.
    Blank Settings key keeps using OPENAI_API_KEY from the environment.
    """
    name = resolved_llm_provider_name()
    if name in {"local_llama", "local", "llama"}:
        return LocalLlamaProvider()
    if name in {"openai", ""}:
        return OpenAIProvider(
            api_key=resolved_openai_key() or None,
            model=resolved_openai_model(),
        )
    raise LLMError(
        f"Unknown LLM provider {name!r}. Use 'openai' or 'local_llama'."
    )


def llm_status() -> dict[str, str | bool]:
    """Shell-friendly status without always calling the network."""
    name = resolved_llm_provider_name()
    if name in {"local_llama", "local", "llama"}:
        return {
            "provider": "local_llama",
            "ok": False,
            "message": "LocalLlama is a placeholder — not runnable yet. Switch provider in Settings.",
        }
    key = resolved_openai_key()
    model = resolved_openai_model()
    if not key:
        return {
            "provider": "openai",
            "ok": False,
            "message": "No API key configured. Add one in Settings or .env.",
        }
    return {
        "provider": "openai",
        "ok": True,
        "message": f"ready · model {model}",
    }


def test_llm_connection() -> dict[str, str | bool]:
    """Ping the configured provider with a tiny completion."""
    name = resolved_llm_provider_name()
    if name in {"local_llama", "local", "llama"}:
        return {
            "ok": False,
            "state": "unavailable",
            "message": "LocalLlama is not available yet.",
        }
    if not resolved_openai_key():
        return {
            "ok": False,
            "state": "missing_key",
            "message": "No API key configured. Add one here or in .env.",
        }
    try:
        provider = get_llm_provider()
        result = provider.complete(
            [
                ChatMessage(role="user", content="Reply with the single word: pong"),
            ],
            max_tokens=8,
        )
        return {
            "ok": True,
            "state": "success",
            "message": f"Connected — model responded ({result.model}).",
            "provider": provider.name,
            "model": result.model,
        }
    except LLMError as exc:
        return {
            "ok": False,
            "state": "failure",
            "message": str(exc),
        }
