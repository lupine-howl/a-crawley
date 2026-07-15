"""Local Llama-class provider — placeholder until post-PoC."""

from __future__ import annotations

from crawley.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider


class LocalLlamaProvider(LLMProvider):
    """Placeholder. Local model hosting is out of Sprint 1."""

    name = "local_llama"

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
    ) -> ChatResult:
        raise LLMError(
            "LocalLlama is a placeholder only. Use the OpenAI provider for Sprint 1 "
            "(set OPENAI_API_KEY). Local model hosting comes after the PoC."
        )
