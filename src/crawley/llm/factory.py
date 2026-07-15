"""Resolve the configured LLM provider."""

from __future__ import annotations

from crawley.llm.base import ChatMessage, LLMError, LLMProvider
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.openai_provider import OpenAIProvider
from crawley.settings import (
    resolved_llm_provider_name,
    resolved_local_base_url,
    resolved_local_model,
    resolved_local_timeout_s,
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
        return LocalLlamaProvider(
            base_url=resolved_local_base_url(),
            model=resolved_local_model(),
            timeout_s=resolved_local_timeout_s(),
        )
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
        model = resolved_local_model()
        return {
            "provider": "local_llama",
            "ok": True,
            "message": f"local · model {model} @ {resolved_local_base_url()}",
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
    """Ping the configured provider with a tiny completion / health check."""
    name = resolved_llm_provider_name()
    if name in {"local_llama", "local", "llama"}:
        provider = LocalLlamaProvider(
            base_url=resolved_local_base_url(),
            model=resolved_local_model(),
            timeout_s=resolved_local_timeout_s(),
        )
        ping = provider.ping()
        if not ping.get("ok"):
            return ping
        try:
            result = provider.complete(
                [ChatMessage(role="user", content="Reply with the single word: pong")],
                max_tokens=8,
            )
            return {
                "ok": True,
                "state": "success",
                "message": f"Connected — local model responded ({result.model}).",
                "provider": provider.name,
                "model": result.model,
            }
        except LLMError as exc:
            msg = str(exc)
            state = "failure"
            if "unreachable" in msg.lower():
                state = "unreachable"
            elif "timed out" in msg.lower():
                state = "timeout"
            elif "not found" in msg.lower() or "missing" in msg.lower():
                state = "missing_model"
            return {"ok": False, "state": state, "message": msg}

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
