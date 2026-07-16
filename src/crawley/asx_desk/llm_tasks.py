"""LLM helpers for ASX scan sentiment + company profiles."""

from __future__ import annotations

import json
import re
from typing import Any

from crawley.asx_desk.schema import SENTIMENTS, normalize_snapshot
from crawley.asx_desk.sources import load_config
from crawley.llm.base import ChatMessage
from crawley.llm.factory import get_llm_provider

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\{.*?\})\s*```", re.DOTALL | re.IGNORECASE)


def extract_json_obj(text: str) -> dict[str, Any]:
    text = (text or "").strip()
    if not text:
        raise ValueError("Empty LLM response")
    fence = _JSON_FENCE.search(text)
    if fence:
        raw = json.loads(fence.group(1))
    else:
        try:
            raw = json.loads(text)
        except json.JSONDecodeError:
            start = text.find("{")
            end = text.rfind("}")
            if start < 0 or end <= start:
                raise ValueError("No JSON object found") from None
            raw = json.loads(text[start : end + 1])
    if not isinstance(raw, dict):
        raise ValueError("Expected JSON object")
    return raw


def enrich_sentiment(scan: dict[str, Any], company: dict[str, Any]) -> dict[str, Any]:
    prompts = load_config()["prompts"]
    snap = normalize_snapshot(scan.get("snapshot"))
    headlines = scan.get("headlines") or []
    lines = [h.get("title") or "" for h in headlines[:5]]
    user = (
        f"Ticker: {company.get('ticker')} · {company.get('name')}\n"
        f"Price: {snap.get('price')} · move: {snap.get('change_pct')}%\n"
        f"Headlines:\n- " + "\n- ".join(lines or ["(none)"])
    )
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=prompts.get("sentiment_system") or ""),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=180,
    )
    raw = extract_json_obj(result.content)
    sentiment = str(raw.get("sentiment") or "unknown").lower()
    if sentiment not in SENTIMENTS:
        sentiment = "unknown"
    snap["sentiment"] = sentiment
    if raw.get("rationale"):
        snap["headline"] = str(raw.get("rationale"))[:240]
    elif snap.get("headline") == "" and lines:
        snap["headline"] = lines[0][:240]
    scan = {**scan, "snapshot": snap}
    return scan


def generate_profile(company: dict[str, Any], scan: dict[str, Any]) -> str:
    prompts = load_config()["prompts"]
    snap = normalize_snapshot(scan.get("snapshot"))
    headlines = scan.get("headlines") or []
    hl = "\n".join(f"- {h.get('title')}" for h in headlines[:6]) or "- (none)"
    gaps = ", ".join(snap.get("gaps") or []) or "none noted"
    user = (
        f"Company: {company.get('ticker')} · {company.get('name')} · {company.get('sector')}\n"
        f"Price: {snap.get('price')} {snap.get('currency')} · "
        f"% move: {snap.get('change_pct')} · volume: {snap.get('volume')}\n"
        f"Sentiment: {snap.get('sentiment')}\n"
        f"Data gaps: {gaps}\n"
        f"Headlines:\n{hl}\n"
    )
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=prompts.get("profile_system") or ""),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=550,
    )
    return (result.content or "").strip()


def generate_recommendations(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """rows: {ticker, name, sector, move, sentiment, profile_excerpt}"""
    from datetime import UTC, datetime

    from crawley.asx_desk.recommendations import normalize_recommendation

    prompts = load_config()["prompts"]
    lines = []
    for r in rows[:20]:
        lines.append(
            f"- {r.get('ticker')} {r.get('name')} | move={r.get('move')} | "
            f"sentiment={r.get('sentiment')} | profile={r.get('profile_excerpt', '')[:180]}"
        )
    from crawley.asx_desk.feedback import feedback_prompt_slice

    feedback = feedback_prompt_slice()
    user = "PoC company set:\n" + "\n".join(lines or ["(none)"])
    if feedback:
        user = user + "\n\n" + feedback
    provider = get_llm_provider()
    result = provider.complete(
        [
            ChatMessage(role="system", content=prompts.get("recommendations_system") or ""),
            ChatMessage(role="user", content=user),
        ],
        max_tokens=900,
    )
    text = (result.content or "").strip()
    # Prefer array extract
    try:
        raw = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start < 0 or end <= start:
            raise ValueError("No JSON array in recommendations response") from None
        raw = json.loads(text[start : end + 1])
    if not isinstance(raw, list):
        raise ValueError("Recommendations must be a JSON array")
    now = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    out: list[dict[str, Any]] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, dict):
            continue
        rec = normalize_recommendation(item)
        if not rec["ticker"] or rec["ticker"] in seen:
            continue
        seen.add(rec["ticker"])
        rec["generated_at"] = now
        out.append(rec)
    return out
