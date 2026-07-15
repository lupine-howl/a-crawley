"""Resolve the configured LLM provider."""

from __future__ import annotations

import os

from crawley.llm.base import LLMError, LLMProvider
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.openai_provider import OpenAIProvider


def get_llm_provider() -> LLMProvider:
    """
    Return the active provider.

    CRAWLEY_LLM_PROVIDER: openai (default) | local_llama
    """
    name = os.environ.get("CRAWLEY_LLM_PROVIDER", "openai").strip().lower()
    if name in {"local_llama", "local", "llama"}:
        return LocalLlamaProvider()
    if name in {"openai", ""}:
        return OpenAIProvider()
    raise LLMError(
        f"Unknown LLM provider {name!r}. Use 'openai' or 'local_llama'."
    )


def llm_status() -> dict[str, str | bool]:
    """Shell-friendly status without always calling the network."""
    name = os.environ.get("CRAWLEY_LLM_PROVIDER", "openai").strip().lower() or "openai"
    if name in {"local_llama", "local", "llama"}:
        return {
            "provider": "local_llama",
            "ok": False,
            "message": "LocalLlama is a placeholder — not runnable in Sprint 1.",
        }
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not key:
        return {
            "provider": "openai",
            "ok": False,
            "message": "OPENAI_API_KEY is missing. Copy .env.example to .env and set the key.",
        }
    return {
        "provider": "openai",
        "ok": True,
        "message": "OpenAI provider configured.",
    }
