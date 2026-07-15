"""LLM provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


class LLMError(Exception):
    """User-visible LLM configuration or call failure."""


@dataclass(frozen=True)
class ChatMessage:
    role: str
    content: str


@dataclass(frozen=True)
class ChatResult:
    content: str
    model: str


class LLMProvider(ABC):
    name: str

    @abstractmethod
    def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = 512,
    ) -> ChatResult:
        """Run a bounded chat completion."""
