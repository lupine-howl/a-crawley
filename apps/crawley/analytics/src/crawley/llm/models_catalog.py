"""Fetch OpenAI model ids for the Settings dropdown."""

from __future__ import annotations

import logging
import time

from openai import APIError, AuthenticationError, OpenAI

from crawley.llm.base import LLMError
from crawley.settings import resolved_openai_key

logger = logging.getLogger(__name__)

# Prefer chat-capable families; keep list usable.
_PREFIXES = ("gpt-", "o1", "o3", "o4", "chatgpt-")
_FALLBACK_MODELS = (
    "gpt-4o-mini",
    "gpt-4o",
    "gpt-4.1-mini",
    "gpt-4.1",
    "gpt-4-turbo",
)

_cache: dict[str, object] = {"at": 0.0, "models": list(_FALLBACK_MODELS), "error": None}
_CACHE_TTL_SEC = 300.0


def _looks_chat_model(model_id: str) -> bool:
    mid = model_id.lower()
    if any(x in mid for x in ("instruct", "audio", "realtime", "tts", "whisper", "embedding", "moderation", "image", "dall-e", "davinci", "babbage", "curie", "ada")):
        return False
    return mid.startswith(_PREFIXES)


def list_openai_models(*, force_refresh: bool = False) -> dict[str, object]:
    """
    Return {"models": [...], "error": str|None, "source": "api"|"fallback"|"cache"}.
    """
    now = time.monotonic()
    if (
        not force_refresh
        and _cache["models"]
        and (now - float(_cache["at"])) < _CACHE_TTL_SEC
        and _cache.get("error") is None
    ):
        return {
            "models": list(_cache["models"]),  # type: ignore[arg-type]
            "error": None,
            "source": "cache",
        }

    key = resolved_openai_key()
    if not key:
        models = list(_FALLBACK_MODELS)
        _cache.update({"at": now, "models": models, "error": "missing_key"})
        return {
            "models": models,
            "error": "No API key configured — showing common defaults until a key is saved.",
            "source": "fallback",
        }

    try:
        client = OpenAI(api_key=key)
        page = client.models.list()
        ids = sorted({m.id for m in page.data if _looks_chat_model(m.id)})
        if not ids:
            ids = list(_FALLBACK_MODELS)
        _cache.update({"at": now, "models": ids, "error": None})
        return {"models": ids, "error": None, "source": "api"}
    except AuthenticationError as exc:
        msg = "OpenAI API key is invalid — showing defaults."
        logger.warning("models.list auth failed: %s", exc)
        models = list(_FALLBACK_MODELS)
        _cache.update({"at": now, "models": models, "error": "auth"})
        return {"models": models, "error": msg, "source": "fallback"}
    except (APIError, OSError, LLMError) as exc:
        msg = f"Could not list models ({exc}); showing defaults."
        logger.warning("models.list failed: %s", exc)
        models = list(_FALLBACK_MODELS)
        _cache.update({"at": now, "models": models, "error": "api"})
        return {"models": models, "error": msg, "source": "fallback"}


def ensure_model_in_options(model: str, models: list[str]) -> list[str]:
    """Keep the currently selected model visible even if not in the API list."""
    options = list(models)
    if model and model not in options:
        options = [model, *options]
    return options
