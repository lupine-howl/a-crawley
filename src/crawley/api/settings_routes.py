"""JSON settings / LLM for crawley-ui (no secrets echoed)."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter
from pydantic import BaseModel, Field

from crawley.llm.factory import llm_status, test_llm_connection
from crawley.llm.local_llama import LocalLlamaProvider
from crawley.llm.models_catalog import ensure_model_in_options, list_openai_models
from crawley.settings import (
    HARD_SCALE_CEILING,
    load_settings,
    resolved_llm_provider_name,
    resolved_local_base_url,
    resolved_local_model,
    resolved_local_timeout_s,
    update_llm_settings,
    update_scale_settings,
)

router = APIRouter(tags=["settings-api"])


class LlmSettingsView(BaseModel):
    provider: str
    model: str
    base_url: str
    timeout_s: float
    has_api_key: bool
    status_ok: bool
    status_message: str


class LlmSettingsUpdate(BaseModel):
    provider: Literal["openai", "local_llama"] = "openai"
    model: str = "gpt-4o-mini"
    api_key: str | None = Field(
        default=None,
        description="Omit or blank to keep the stored key; never returned by GET",
    )
    base_url: str | None = None
    timeout_s: float | None = None


class ScaleSettingsView(BaseModel):
    asx_cap: int
    inbox_cap: int
    inbox_keep_max: int
    hard_ceiling: int = HARD_SCALE_CEILING
    local_llama_uncapped: bool = Field(
        description="True when provider is local_llama (active set pads to hard ceiling)"
    )


class ScaleSettingsUpdate(BaseModel):
    asx_cap: int | None = None
    inbox_cap: int | None = None
    inbox_keep_max: int | None = None


def _llm_view() -> LlmSettingsView:
    settings = load_settings()
    status = llm_status()
    return LlmSettingsView(
        provider=str(status.get("provider") or settings.llm.provider),
        model=settings.llm.model,
        base_url=settings.llm.base_url,
        timeout_s=float(settings.llm.timeout_s),
        has_api_key=bool(settings.llm.api_key),
        status_ok=bool(status.get("ok")),
        status_message=str(status.get("message") or ""),
    )


@router.get("/v1/settings/llm", response_model=LlmSettingsView)
def get_llm_settings() -> LlmSettingsView:
    return _llm_view()


@router.put("/v1/settings/llm", response_model=LlmSettingsView)
def put_llm_settings(body: LlmSettingsUpdate) -> LlmSettingsView:
    update_llm_settings(
        provider=body.provider,
        model=body.model,
        api_key=body.api_key,
        base_url=body.base_url,
        timeout_s=body.timeout_s,
    )
    return _llm_view()


@router.post("/v1/settings/llm/test")
def post_llm_test() -> dict[str, Any]:
    return test_llm_connection()


@router.get("/v1/settings/llm/models")
def get_llm_models(refresh: bool = False) -> dict[str, Any]:
    name = resolved_llm_provider_name()
    if name in {"local_llama", "local", "llama"}:
        provider = LocalLlamaProvider(
            base_url=resolved_local_base_url(),
            model=resolved_local_model(),
            timeout_s=resolved_local_timeout_s(),
        )
        catalog = provider.list_models()
    else:
        catalog = list_openai_models(force_refresh=refresh)
    models = ensure_model_in_options(
        load_settings().llm.model,
        list(catalog.get("models") or []),  # type: ignore[arg-type]
    )
    return {
        "models": models,
        "error": catalog.get("error"),
        "source": catalog.get("source"),
        "provider": "local_llama" if name in {"local_llama", "local", "llama"} else "openai",
    }


@router.get("/v1/settings/scale", response_model=ScaleSettingsView)
def get_scale_settings() -> ScaleSettingsView:
    settings = load_settings()
    name = resolved_llm_provider_name()
    return ScaleSettingsView(
        asx_cap=int(settings.scale.asx_cap),
        inbox_cap=int(settings.scale.inbox_cap),
        inbox_keep_max=int(settings.scale.inbox_keep_max),
        local_llama_uncapped=name in {"local_llama", "local", "llama"},
    )


@router.patch("/v1/settings/scale", response_model=ScaleSettingsView)
def patch_scale_settings(body: ScaleSettingsUpdate) -> ScaleSettingsView:
    current = load_settings()
    update_scale_settings(
        inbox_cap=body.inbox_cap if body.inbox_cap is not None else current.scale.inbox_cap,
        inbox_keep_max=(
            body.inbox_keep_max
            if body.inbox_keep_max is not None
            else current.scale.inbox_keep_max
        ),
        asx_cap=body.asx_cap if body.asx_cap is not None else current.scale.asx_cap,
    )
    return get_scale_settings()
