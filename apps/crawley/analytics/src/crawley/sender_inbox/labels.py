"""Confirm-first Gmail label apply/remove (Sprint 26 / B48)."""

from __future__ import annotations

import json
import logging
import uuid
from typing import Any

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from crawley.data.paths import GMAIL_DIR, ensure_data_dirs
from crawley.google_oauth import load_credentials
from crawley.writeback import record_audit

logger = logging.getLogger(__name__)

LABEL_DRAFTS_PATH = GMAIL_DIR / "pending_label_drafts.json"

# User-facing label ops exclude system-only mutations for PoC.
SYSTEM_LABELS = frozenset(
    {
        "INBOX",
        "SENT",
        "DRAFT",
        "TRASH",
        "SPAM",
        "UNREAD",
        "STARRED",
        "IMPORTANT",
        "CATEGORY_PERSONAL",
        "CATEGORY_SOCIAL",
        "CATEGORY_PROMOTIONS",
        "CATEGORY_UPDATES",
        "CATEGORY_FORUMS",
    }
)


def _load_drafts() -> dict[str, Any]:
    ensure_data_dirs()
    if not LABEL_DRAFTS_PATH.exists():
        return {}
    try:
        raw = json.loads(LABEL_DRAFTS_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return dict(raw) if isinstance(raw, dict) else {}


def _save_drafts(drafts: dict[str, Any]) -> None:
    ensure_data_dirs()
    LABEL_DRAFTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = LABEL_DRAFTS_PATH.with_suffix(".tmp")
    tmp.write_text(json.dumps(drafts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(LABEL_DRAFTS_PATH)


def list_user_labels(creds) -> list[dict[str, str]]:
    """Return user-visible labels [{id, name}]."""
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    listed = service.users().labels().list(userId="me").execute()
    out: list[dict[str, str]] = []
    for row in listed.get("labels") or []:
        lid = str(row.get("id") or "")
        name = str(row.get("name") or lid)
        if not lid:
            continue
        out.append({"id": lid, "name": name})
    out.sort(key=lambda r: r["name"].lower())
    return out


def message_label_ids(creds, message_id: str) -> list[str]:
    service = build("gmail", "v1", credentials=creds, cache_discovery=False)
    full = (
        service.users()
        .messages()
        .get(userId="me", id=message_id, format="metadata", metadataHeaders=[])
        .execute()
    )
    return [str(x) for x in (full.get("labelIds") or [])]


def propose_label_change(
    *,
    message_id: str,
    label_id: str,
    op: str,
    sender_id: str = "",
    label_name: str = "",
) -> dict[str, Any]:
    message_id = (message_id or "").strip()
    label_id = (label_id or "").strip()
    op = (op or "").strip().lower()
    if not message_id:
        raise ValueError("message_id required")
    if not label_id:
        raise ValueError("label_id required")
    if op not in {"add", "remove"}:
        raise ValueError("op must be add or remove")
    draft_id = str(uuid.uuid4())
    draft = {
        "draft_id": draft_id,
        "module_id": "gmail",
        "action": "modify_labels",
        "payload": {
            "message_id": message_id,
            "label_id": label_id,
            "label_name": (label_name or label_id)[:120],
            "op": op,
            "sender_id": (sender_id or "").strip(),
        },
        "would_mutate": True,
        "api": "gmail.users.messages.modify",
    }
    drafts = _load_drafts()
    drafts[draft_id] = draft
    _save_drafts(drafts)
    record_audit(
        module_id="gmail",
        stage="propose",
        draft=draft,
        note=f"Label {op} draft stored pending confirm",
        dry_run=False,
        success=None,
    )
    return draft


def cancel_label_change(draft_id: str) -> dict[str, Any] | None:
    drafts = _load_drafts()
    draft = drafts.pop((draft_id or "").strip(), None)
    _save_drafts(drafts)
    if draft is None:
        return None
    record_audit(
        module_id="gmail",
        stage="cancel",
        draft=draft,
        note="Cancelled — no remote label change",
        dry_run=False,
        success=True,
    )
    return draft


def confirm_label_change(draft_id: str, *, modify_ok: bool) -> tuple[bool, str, dict[str, Any] | None]:
    drafts = _load_drafts()
    draft = drafts.get((draft_id or "").strip())
    if not draft:
        return False, "Draft missing or expired. Propose again.", None
    if not modify_ok:
        msg = "Gmail modify scope missing. Reconnect with label permission."
        record_audit(
            module_id="gmail",
            stage="execute",
            draft=draft,
            note=msg,
            dry_run=False,
            success=False,
        )
        return False, msg, draft
    try:
        creds = load_credentials()
        if not creds:
            return False, "Google token missing. Reconnect Google.", draft
        p = draft["payload"]
        body: dict[str, Any] = {}
        if p.get("op") == "add":
            body["addLabelIds"] = [p["label_id"]]
        else:
            body["removeLabelIds"] = [p["label_id"]]
        service = build("gmail", "v1", credentials=creds, cache_discovery=False)
        service.users().messages().modify(
            userId="me", id=p["message_id"], body=body
        ).execute()
        drafts.pop(draft_id, None)
        _save_drafts(drafts)
        record_audit(
            module_id="gmail",
            stage="execute",
            draft=draft,
            note=f"Label {p.get('op')} applied",
            dry_run=False,
            success=True,
        )
        return True, f"Label {p.get('op')} applied.", draft
    except HttpError as exc:
        status = getattr(exc.resp, "status", None)
        msg = f"Gmail label API error ({status or '?'}): {exc.reason or exc}"
        record_audit(
            module_id="gmail",
            stage="execute",
            draft=draft,
            note=msg,
            dry_run=False,
            success=False,
        )
        return False, msg, draft
    except Exception as exc:  # noqa: BLE001
        logger.exception("Label modify failed")
        msg = f"Label change failed: {exc}"
        record_audit(
            module_id="gmail",
            stage="execute",
            draft=draft,
            note=msg,
            dry_run=False,
            success=False,
        )
        return False, msg, draft


def get_pending_draft(draft_id: str = "") -> dict[str, Any] | None:
    drafts = _load_drafts()
    if draft_id:
        return drafts.get(draft_id)
    # newest-ish: arbitrary first
    return next(iter(drafts.values()), None)
