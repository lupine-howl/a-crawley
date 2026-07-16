"""LLM helpers for categorize / profile / todos."""

from __future__ import annotations

import json
import re
import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.llm.base import ChatMessage, LLMError
from crawley.llm.factory import get_llm_provider
from crawley.sender_inbox.schema import normalize_metrics

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", re.DOTALL | re.IGNORECASE)


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def extract_json(text: str) -> Any:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty LLM response")
    fence = _JSON_FENCE.search(text)
    if fence:
        return json.loads(fence.group(1))
    # Prefer the outermost JSON value (array vs object).
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    first_obj = text.find("{")
    first_arr = text.find("[")
    if first_arr >= 0 and (first_obj < 0 or first_arr < first_obj):
        end = text.rfind("]")
        if end > first_arr:
            return json.loads(text[first_arr : end + 1])
    if first_obj >= 0:
        end = text.rfind("}")
        if end > first_obj:
            return json.loads(text[first_obj : end + 1])
    raise ValueError("No JSON object found in LLM response")


def categorize_message(message: dict[str, Any]) -> dict[str, Any]:
    system = (
        "You categorize one email for a personal operator inbox. "
        "Reply with ONLY a JSON object (no markdown) using this schema:\n"
        "{\n"
        '  "urgency": "low|medium|high|critical",\n'
        '  "requires_reply": boolean,\n'
        '  "action_needed": boolean,\n'
        '  "vip": boolean,\n'
        '  "category": "personal|work|billing|newsletter|other",\n'
        '  "signals": ["reply","urgent","action","vip", ...],\n'
        '  "brief": "one short line"\n'
        "}\n"
        "signals: short lowercase tags (max 5). Prefer reply/urgent/action/vip when true."
    )
    user = (
        f"From: {message.get('from_name') or ''} <{message.get('from_addr') or ''}>\n"
        f"Subject: {message.get('subject') or ''}\n"
        f"Date: {message.get('internal_date') or ''}\n"
        f"Snippet: {message.get('snippet') or ''}\n\n"
        f"Body:\n{message.get('body_text') or message.get('snippet') or ''}\n"
    )
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=280,
    )
    raw = extract_json(result.content)
    if not isinstance(raw, dict):
        raise ValueError("Categorization JSON must be an object")
    metrics = normalize_metrics(raw)
    metrics["_model"] = result.model
    return metrics


def generate_sender_profile(sender: dict[str, Any], messages: list[dict[str, Any]]) -> str:
    lines = []
    for m in messages[:12]:
        metrics = m.get("metrics") or {}
        lines.append(
            f"- [{m.get('internal_date')}] {m.get('subject')} "
            f"(urgency={metrics.get('urgency')}; reply={metrics.get('requires_reply')}; "
            f"brief={metrics.get('brief') or m.get('snippet', '')[:120]})"
        )
    system = (
        "Write a concise Markdown profile of how this sender relates to the operator, "
        "based only on the ingested emails. Sections: Relationship, Topics, Open loops. "
        "Be honest when data is thin. No fabricated facts."
    )
    user = (
        f"Sender: {sender.get('from_name') or ''} <{sender.get('from_addr') or ''}>\n"
        f"Messages ({len(messages)}):\n" + "\n".join(lines)
    )
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=system),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=500,
    )
    return (result.content or "").strip()


def extract_todos(
    sender_id: str,
    messages: list[dict[str, Any]],
    existing: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Return merged todo list for sender (keeps done state for matching text)."""
    open_existing = {t.get("text", "").strip().lower(): t for t in existing}
    lines = []
    for m in messages[:12]:
        lines.append(
            f"- id={m.get('id')} subject={m.get('subject')} "
            f"brief={((m.get('metrics') or {}).get('brief') or m.get('snippet') or '')[:160]}"
        )
    system = (
        "Extract actionable todos for the operator from this sender's emails. "
        "Reply with ONLY a JSON array of objects: "
        '[{"text":"short action","from_subject":"email subject","message_id":"id or empty"}]. '
        "Max 8 items. Skip newsletters with no action. No send/calendar automation."
    )
    user = "Emails:\n" + "\n".join(lines)
    provider = get_llm_provider()
    try:
        result = provider.complete(
            [
                ChatMessage(role="system", content=system),
                ChatMessage(role="user", content=user),
            ],
            max_tokens=400,
        )
        raw = extract_json(result.content)
    except (LLMError, ValueError, json.JSONDecodeError):
        return existing

    if not isinstance(raw, list):
        return existing

    merged: list[dict[str, Any]] = []
    seen_text: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "").strip()
        if not text or text.lower() in seen_text:
            continue
        seen_text.add(text.lower())
        prev = open_existing.get(text.lower())
        merged.append(
            {
                "id": (prev or {}).get("id") or str(uuid.uuid4()),
                "sender_id": sender_id,
                "text": text[:240],
                "from_subject": str(item.get("from_subject") or "")[:200],
                "message_id": str(item.get("message_id") or ""),
                "done": bool((prev or {}).get("done")),
                "created_at": (prev or {}).get("created_at") or _now_iso(),
            }
        )

    # Keep done items not rediscovered so history isn't wiped.
    for t in existing:
        if t.get("done") and t.get("text", "").strip().lower() not in seen_text:
            merged.append(t)
    return merged
