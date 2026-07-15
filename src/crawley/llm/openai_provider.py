"""OpenAI chat provider (PoC)."""

from __future__ import annotations

import os

from openai import APIError, AuthenticationError, OpenAI

from crawley.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider

# Bound prompt/output size for PoC — callers should stay under this too.
DEFAULT_MAX_TOKENS = 512
MAX_ALLOWED_TOKENS = 1024


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str | None = None, model: str | None = None) -> None:
        key = (api_key if api_key is not None else os.environ.get("OPENAI_API_KEY", "")).strip()
        if not key:
            raise LLMError(
                "OpenAI API key is missing. Set OPENAI_API_KEY in your .env file "
                "(see .env.example)."
            )
        self._client = OpenAI(api_key=key)
        self._model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ChatResult:
        tokens = min(max(1, max_tokens), MAX_ALLOWED_TOKENS)
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": m.role, "content": m.content} for m in messages],
                max_tokens=tokens,
            )
        except AuthenticationError as exc:
            raise LLMError(
                "OpenAI API key is invalid or revoked. Check OPENAI_API_KEY in .env."
            ) from exc
        except APIError as exc:
            raise LLMError(f"OpenAI API error: {exc.message or exc}") from exc

        choice = response.choices[0].message.content if response.choices else None
        if not choice:
            raise LLMError("OpenAI returned an empty response.")
        return ChatResult(content=choice, model=response.model or self._model)
