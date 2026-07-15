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
    base_url: str = "http://127.0.0.1:11434"
    timeout_s: float = 60.0


@dataclass
class NetworkSettings:
    """LAN reach preferences. Bind change requires process restart."""

    lan_enabled: bool = False


@dataclass
class AppSettings:
    theme: str = DEFAULT_THEME
    llm: LLMSettings = field(default_factory=LLMSettings)
    prompts: PromptSettings = field(default_factory=PromptSettings)
    network: NetworkSettings = field(default_factory=NetworkSettings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "llm": asdict(self.llm),
            "prompts": self.prompts.to_dict(),
            "network": asdict(self.network),
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
    net_raw = raw.get("network") or {}
    timeout_raw = llm_raw.get("timeout_s", 60.0)
    try:
        timeout_s = float(timeout_raw)
    except (TypeError, ValueError):
        timeout_s = 60.0
    timeout_s = max(5.0, min(timeout_s, 600.0))
    return AppSettings(
        theme=_normalize_theme(raw.get("theme")),
        llm=LLMSettings(
            provider=(llm_raw.get("provider") or "openai").strip().lower() or "openai",
            model=(llm_raw.get("model") or "gpt-4o-mini").strip() or "gpt-4o-mini",
            api_key=(llm_raw.get("api_key") or "").strip(),
            base_url=(
                (llm_raw.get("base_url") or "http://127.0.0.1:11434").strip()
                or "http://127.0.0.1:11434"
            ),
            timeout_s=timeout_s,
        ),
        prompts=prompts_from_dict(raw.get("prompts")),
        network=NetworkSettings(
            lan_enabled=bool(net_raw.get("lan_enabled", False)),
        ),
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


def resolved_local_base_url() -> str:
    settings = load_settings()
    return (
        settings.llm.base_url.strip()
        or os.environ.get("CRAWLEY_LOCAL_LLM_URL", "http://127.0.0.1:11434").strip()
        or "http://127.0.0.1:11434"
    )


def resolved_local_model() -> str:
    settings = load_settings()
    if settings.llm.provider in {"local_llama", "local", "llama"} and settings.llm.model:
        return settings.llm.model.strip()
    return os.environ.get("CRAWLEY_LOCAL_LLM_MODEL", "llama3.2").strip() or "llama3.2"


def resolved_local_timeout_s() -> float:
    return float(load_settings().llm.timeout_s)


def update_llm_settings(
    *,
    provider: str,
    model: str,
    api_key: str | None,
    base_url: str | None = None,
    timeout_s: float | None = None,
) -> AppSettings:
    """
    Persist LLM settings. Blank api_key means keep the previously stored key.
    """
    current = load_settings()
    current.llm.provider = (provider or "openai").strip().lower() or "openai"
    current.llm.model = (model or "gpt-4o-mini").strip() or "gpt-4o-mini"
    if api_key is not None and api_key.strip():
        current.llm.api_key = api_key.strip()
    if base_url is not None and base_url.strip():
        current.llm.base_url = base_url.strip().rstrip("/")
    if timeout_s is not None:
        current.llm.timeout_s = max(5.0, min(float(timeout_s), 600.0))
    save_settings(current)
    return current


def update_prompt_settings(**fields: str) -> AppSettings:
    current = load_settings()
    merged = current.prompts.to_dict()
    for key, value in fields.items():
        if key in merged and value is not None:
            merged[key] = value
    current.prompts = prompts_from_dict(merged)
    save_settings(current)
    return current


def update_theme_setting(theme: str) -> AppSettings:
    current = load_settings()
    current.theme = _normalize_theme(theme)
    save_settings(current)
    return current


def update_network_settings(*, lan_enabled: bool) -> AppSettings:
    current = load_settings()
    current.network.lan_enabled = bool(lan_enabled)
    save_settings(current)
    return current
