"""Operator settings persisted under data/secrets (gitignored)."""

from __future__ import annotations

import json
import os
import threading
from dataclasses import asdict, dataclass, field
from typing import Any

from crawley.data.paths import SECRETS_DIR, ensure_data_dirs
from crawley.prompts import PromptSettings, prompts_from_dict

SETTINGS_PATH = SECRETS_DIR / "settings.json"
THEME_IDS = ("paper", "slate", "ink", "moss")
DEFAULT_THEME = "paper"
THEME_COOKIE = "crawley_theme"

_lock = threading.Lock()


@dataclass
class LLMSettings:
    provider: str = "openai"
    model: str = "gpt-4o-mini"
    api_key: str = ""


@dataclass
class AppSettings:
    theme: str = DEFAULT_THEME
    llm: LLMSettings = field(default_factory=LLMSettings)
    prompts: PromptSettings = field(default_factory=PromptSettings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "llm": asdict(self.llm),
            "prompts": self.prompts.to_dict(),
        }


def _normalize_theme(theme: str | None) -> str:
    value = (theme or DEFAULT_THEME).strip().lower()
    return value if value in THEME_IDS else DEFAULT_THEME


def load_settings() -> AppSettings:
    ensure_data_dirs()
    if not SETTINGS_PATH.exists():
        return AppSettings()
    try:
        raw = json.loads(SETTINGS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return AppSettings()
    llm_raw = raw.get("llm") or {}
    return AppSettings(
        theme=_normalize_theme(raw.get("theme")),
        llm=LLMSettings(
            provider=(llm_raw.get("provider") or "openai").strip().lower() or "openai",
            model=(llm_raw.get("model") or "gpt-4o-mini").strip() or "gpt-4o-mini",
            api_key=(llm_raw.get("api_key") or "").strip(),
        ),
        prompts=prompts_from_dict(raw.get("prompts")),
    )


def save_settings(settings: AppSettings) -> None:
    ensure_data_dirs()
    settings.theme = _normalize_theme(settings.theme)
    with _lock:
        SETTINGS_PATH.write_text(
            json.dumps(settings.to_dict(), indent=2) + "\n",
            encoding="utf-8",
        )


def resolve_theme(*, cookie_value: str | None = None) -> str:
    """Cookie wins for immediate apply; else settings file; else default."""
    if cookie_value:
        return _normalize_theme(cookie_value)
    return _normalize_theme(load_settings().theme)


def resolved_openai_key() -> str:
    """UI/settings key overrides env when non-empty; else OPENAI_API_KEY."""
    settings = load_settings()
    if settings.llm.api_key:
        return settings.llm.api_key
    return os.environ.get("OPENAI_API_KEY", "").strip()


def resolved_llm_provider_name() -> str:
    settings = load_settings()
    name = settings.llm.provider.strip().lower()
    if name:
        return name
    return os.environ.get("CRAWLEY_LLM_PROVIDER", "openai").strip().lower() or "openai"


def resolved_openai_model() -> str:
    settings = load_settings()
    if settings.llm.model:
        return settings.llm.model
    return os.environ.get("OPENAI_MODEL", "gpt-4o-mini").strip() or "gpt-4o-mini"


def update_llm_settings(
    *,
    provider: str,
    model: str,
    api_key: str | None,
) -> AppSettings:
    """
    Persist LLM settings. Blank api_key means keep the previously stored key.
    """
    current = load_settings()
    current.llm.provider = (provider or "openai").strip().lower() or "openai"
    current.llm.model = (model or "gpt-4o-mini").strip() or "gpt-4o-mini"
    if api_key is not None and api_key.strip():
        current.llm.api_key = api_key.strip()
    save_settings(current)
    return current


def update_prompt_settings(
    *,
    investment_system: str,
    investment_user_footer: str,
    gmail_system: str,
    gmail_user_header: str,
) -> AppSettings:
    current = load_settings()
    current.prompts = prompts_from_dict(
        {
            "investment_system": investment_system,
            "investment_user_footer": investment_user_footer,
            "gmail_system": gmail_system,
            "gmail_user_header": gmail_user_header,
        }
    )
    save_settings(current)
    return current


def update_theme_setting(theme: str) -> AppSettings:
    current = load_settings()
    current.theme = _normalize_theme(theme)
    save_settings(current)
    return current
