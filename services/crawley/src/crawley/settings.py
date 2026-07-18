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
class SimulationSettings:
    """Paper portfolio assumptions — never enables live trading."""

    starting_cash: float = 100_000.0
    fee_flat: float = 10.0
    fee_pct: float = 0.1
    currency: str = "AUD"
    broker_label: str = "Paper (simulation)"


HARD_SCALE_CEILING = 200


def clamp_scale_cap(value: int | float | str | None, *, default: int) -> int:
    try:
        n = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        n = default
    return max(1, min(n, HARD_SCALE_CEILING))


def _default_inbox_cap() -> int:
    return clamp_scale_cap(os.environ.get("CRAWLEY_SENDER_INBOX_CAP", "20"), default=20)


def _default_asx_cap() -> int:
    return clamp_scale_cap(os.environ.get("CRAWLEY_ASX_POC_CAP", "20"), default=20)


@dataclass
class ScaleSettings:
    """Desk scale bounds — hard ceiling 200; not a full mailbox / market product."""

    inbox_cap: int = field(default_factory=_default_inbox_cap)
    inbox_keep_max: int = 100
    asx_cap: int = field(default_factory=_default_asx_cap)


@dataclass
class AppSettings:
    theme: str = DEFAULT_THEME
    llm: LLMSettings = field(default_factory=LLMSettings)
    prompts: PromptSettings = field(default_factory=PromptSettings)
    network: NetworkSettings = field(default_factory=NetworkSettings)
    simulation: SimulationSettings = field(default_factory=SimulationSettings)
    scale: ScaleSettings = field(default_factory=ScaleSettings)

    def to_dict(self) -> dict[str, Any]:
        return {
            "theme": self.theme,
            "llm": asdict(self.llm),
            "prompts": self.prompts.to_dict(),
            "network": asdict(self.network),
            "simulation": asdict(self.simulation),
            "scale": asdict(self.scale),
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
    sim_raw = raw.get("simulation") or {}
    scale_raw = raw.get("scale") or {}
    timeout_raw = llm_raw.get("timeout_s", 60.0)
    try:
        timeout_s = float(timeout_raw)
    except (TypeError, ValueError):
        timeout_s = 60.0
    timeout_s = max(5.0, min(timeout_s, 600.0))

    def _f(key: str, default: float) -> float:
        try:
            return float(sim_raw.get(key, default))
        except (TypeError, ValueError):
            return default

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
        simulation=SimulationSettings(
            starting_cash=max(0.0, _f("starting_cash", 100_000.0)),
            fee_flat=max(0.0, _f("fee_flat", 10.0)),
            fee_pct=max(0.0, min(_f("fee_pct", 0.1), 5.0)),
            currency=(sim_raw.get("currency") or "AUD").strip().upper() or "AUD",
            broker_label=(sim_raw.get("broker_label") or "Paper (simulation)").strip()
            or "Paper (simulation)",
        ),
        scale=ScaleSettings(
            inbox_cap=clamp_scale_cap(
                scale_raw.get("inbox_cap"), default=_default_inbox_cap()
            ),
            inbox_keep_max=clamp_scale_cap(scale_raw.get("inbox_keep_max"), default=100),
            asx_cap=clamp_scale_cap(scale_raw.get("asx_cap"), default=_default_asx_cap()),
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
    # Local models have no per-token bill — raise ASX + inbox caps to the hard max.
    if current.llm.provider in {"local_llama", "local", "llama"}:
        current.scale.asx_cap = HARD_SCALE_CEILING
        current.scale.inbox_cap = HARD_SCALE_CEILING
        # Keep-max must not sit below inbox_cap or prune will discard mid-ingest.
        current.scale.inbox_keep_max = max(
            int(current.scale.inbox_keep_max), HARD_SCALE_CEILING
        )
    save_settings(current)
    if current.llm.provider in {"local_llama", "local", "llama"}:
        from crawley.asx_desk.store import sync_active_cap
        from crawley.sender_inbox.store import sync_ingest_cap

        sync_active_cap(HARD_SCALE_CEILING, expand_from_universe=True)
        sync_ingest_cap(HARD_SCALE_CEILING)
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


def update_simulation_settings(
    *,
    starting_cash: float,
    fee_flat: float,
    fee_pct: float,
    currency: str = "AUD",
    broker_label: str = "Paper (simulation)",
    reset_portfolio_cash: bool = False,
) -> AppSettings:
    current = load_settings()
    current.simulation.starting_cash = max(0.0, float(starting_cash))
    current.simulation.fee_flat = max(0.0, float(fee_flat))
    current.simulation.fee_pct = max(0.0, min(float(fee_pct), 5.0))
    current.simulation.currency = (currency or "AUD").strip().upper() or "AUD"
    current.simulation.broker_label = (
        (broker_label or "Paper (simulation)").strip() or "Paper (simulation)"
    )
    save_settings(current)
    if reset_portfolio_cash:
        from crawley.asx_desk.portfolio import reset_portfolio

        reset_portfolio()
    return current


def update_scale_settings(
    *,
    inbox_cap: int,
    inbox_keep_max: int,
    asx_cap: int,
) -> AppSettings:
    current = load_settings()
    current.scale.inbox_cap = clamp_scale_cap(inbox_cap, default=100)
    current.scale.inbox_keep_max = clamp_scale_cap(inbox_keep_max, default=100)
    current.scale.asx_cap = clamp_scale_cap(asx_cap, default=50)
    save_settings(current)
    # Sync live desk caps / prune immediately.
    from crawley.asx_desk.store import sync_active_cap
    from crawley.sender_inbox.store import prune_messages, sync_ingest_cap

    sync_ingest_cap(current.scale.inbox_cap)
    prune_messages(keep_max=current.scale.inbox_keep_max)
    sync_active_cap(current.scale.asx_cap)
    return current


def effective_inbox_cap() -> int:
    """Settings win; Local Llama always uses the hard ceiling (no per-call cost)."""
    env_default = clamp_scale_cap(os.environ.get("CRAWLEY_SENDER_INBOX_CAP", "20"), default=20)
    try:
        if resolved_llm_provider_name() in {"local_llama", "local", "llama"}:
            return HARD_SCALE_CEILING
        return clamp_scale_cap(load_settings().scale.inbox_cap, default=env_default)
    except Exception:  # noqa: BLE001
        return env_default


def effective_asx_cap() -> int:
    env_default = clamp_scale_cap(os.environ.get("CRAWLEY_ASX_POC_CAP", "20"), default=20)
    try:
        return clamp_scale_cap(load_settings().scale.asx_cap, default=env_default)
    except Exception:  # noqa: BLE001
        return env_default


def effective_inbox_keep_max() -> int:
    try:
        if resolved_llm_provider_name() in {"local_llama", "local", "llama"}:
            return max(HARD_SCALE_CEILING, clamp_scale_cap(load_settings().scale.inbox_keep_max, default=100))
        return clamp_scale_cap(load_settings().scale.inbox_keep_max, default=100)
    except Exception:  # noqa: BLE001
        return 100
