"""Local Llama-class provider via Ollama-compatible HTTP API."""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from typing import Any

from crawley.llm.base import ChatMessage, ChatResult, LLMError, LLMProvider


DEFAULT_BASE_URL = "http://127.0.0.1:11434"
DEFAULT_MODEL = "llama3.2"
DEFAULT_TIMEOUT_S = 60
DEFAULT_MAX_TOKENS = 512


class LocalLlamaProvider(LLMProvider):
    """Talk to a local Ollama (or compatible) HTTP daemon."""

    name = "local_llama"

    def __init__(
        self,
        *,
        base_url: str | None = None,
        model: str | None = None,
        timeout_s: float | None = None,
    ) -> None:
        self.base_url = (base_url or DEFAULT_BASE_URL).rstrip("/")
        self.model = (model or DEFAULT_MODEL).strip() or DEFAULT_MODEL
        self.timeout_s = float(timeout_s if timeout_s is not None else DEFAULT_TIMEOUT_S)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _post_json(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self._url(path),
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace") if exc.fp else ""
            raise LLMError(
                f"Local LLM HTTP {exc.code} at {self.base_url}: {detail or exc.reason}"
            ) from exc
        except urllib.error.URLError as exc:
            raise LLMError(
                f"Local LLM unreachable at {self.base_url}: {exc.reason}. "
                "Start Ollama (or your local daemon) and check Settings base URL."
            ) from exc
        except TimeoutError as exc:
            raise LLMError(
                f"Local LLM timed out after {self.timeout_s:.0f}s "
                f"(model {self.model!r}). Try a smaller model or raise timeout."
            ) from exc
        try:
            return json.loads(body)
        except json.JSONDecodeError as exc:
            raise LLMError(f"Local LLM returned non-JSON: {body[:200]}") from exc

    def ping(self) -> dict[str, str | bool]:
        """Health + model presence check for Settings Test connection."""
        req = urllib.request.Request(self._url("/api/tags"), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=min(10.0, self.timeout_s)) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            return {
                "ok": False,
                "state": "failure",
                "message": f"Local daemon HTTP {exc.code}: {exc.reason}",
            }
        except urllib.error.URLError as exc:
            return {
                "ok": False,
                "state": "unreachable",
                "message": (
                    f"Local LLM unreachable at {self.base_url}: {exc.reason}. "
                    "Start Ollama and retry."
                ),
            }
        except TimeoutError:
            return {
                "ok": False,
                "state": "timeout",
                "message": f"Local LLM ping timed out ({self.base_url}).",
            }
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {
                "ok": False,
                "state": "failure",
                "message": "Local daemon returned invalid JSON from /api/tags.",
            }
        names = {
            str(m.get("name") or m.get("model") or "").split(":")[0]
            for m in (payload.get("models") or [])
            if isinstance(m, dict)
        }
        model_base = self.model.split(":")[0]
        if names and model_base not in names and self.model not in {
            str(m.get("name") or "") for m in (payload.get("models") or []) if isinstance(m, dict)
        }:
            return {
                "ok": False,
                "state": "missing_model",
                "message": (
                    f"Model {self.model!r} not found on local daemon. "
                    f"Pull it (e.g. `ollama pull {self.model}`) or change Settings."
                ),
            }
        return {
            "ok": True,
            "state": "success",
            "message": f"Connected — local daemon reachable; model {self.model}.",
            "provider": self.name,
            "model": self.model,
        }

    def list_models(self) -> dict[str, Any]:
        """Return installed model names from the local daemon (`/api/tags`)."""
        req = urllib.request.Request(self._url("/api/tags"), method="GET")
        try:
            with urllib.request.urlopen(req, timeout=min(10.0, self.timeout_s)) as resp:
                body = resp.read().decode("utf-8")
        except Exception as exc:  # noqa: BLE001
            return {
                "models": [self.model],
                "error": f"Could not list local models: {exc}",
                "source": "fallback",
            }
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return {
                "models": [self.model],
                "error": "Local daemon returned invalid JSON from /api/tags.",
                "source": "fallback",
            }
        names = sorted(
            {
                str(m.get("name") or m.get("model") or "").strip()
                for m in (payload.get("models") or [])
                if isinstance(m, dict) and (m.get("name") or m.get("model"))
            }
        )
        if self.model and self.model not in names:
            names = [self.model, *names]
        return {"models": names or [self.model], "error": None, "source": "api"}

    def complete(
        self,
        messages: list[ChatMessage],
        *,
        max_tokens: int = DEFAULT_MAX_TOKENS,
    ) -> ChatResult:
        # Cap output for local hardware (S9.2).
        capped = max(1, min(int(max_tokens), DEFAULT_MAX_TOKENS))
        payload = {
            "model": self.model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "stream": False,
            "options": {"num_predict": capped},
        }
        try:
            data = self._post_json("/api/chat", payload)
        except LLMError:
            raise
        except Exception as exc:  # noqa: BLE001
            raise LLMError(f"Local LLM request failed: {exc}") from exc

        message = data.get("message") or {}
        content = (message.get("content") or "").strip()
        if not content:
            raise LLMError(
                f"Local LLM returned empty content for model {self.model!r}."
            )
        return ChatResult(content=content, model=str(data.get("model") or self.model))
