"""Paper portfolio simulation (Sprint 14) — local only, no broker APIs."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from crawley.asx_desk.schema import normalize_snapshot
from crawley.asx_desk.store import (
    _path,
    _read_json,
    _write_json,
    _lock,
    load_scans,
)
from crawley.settings import load_settings


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def default_portfolio() -> dict[str, Any]:
    sim = load_settings().simulation
    return {
        "cash": float(sim.starting_cash),
        "currency": sim.currency or "AUD",
        "positions": {},  # ticker -> {qty, avg_price}
        "ledger": [],
        "updated_at": "",
    }


def load_portfolio() -> dict[str, Any]:
    with _lock:
        raw = _read_json(_path("portfolio.json"), None)
        if not isinstance(raw, dict):
            return default_portfolio()
        base = default_portfolio()
        base.update(raw)
        if not isinstance(base.get("positions"), dict):
            base["positions"] = {}
        if not isinstance(base.get("ledger"), list):
            base["ledger"] = []
        return base


def save_portfolio(portfolio: dict[str, Any]) -> None:
    with _lock:
        portfolio = {**portfolio, "updated_at": _now_iso()}
        _write_json(_path("portfolio.json"), portfolio)


def reset_portfolio() -> dict[str, Any]:
    port = default_portfolio()
    save_portfolio(port)
    return port


def _fee(notional: float) -> float:
    sim = load_settings().simulation
    return max(0.0, float(sim.fee_flat) + abs(notional) * float(sim.fee_pct) / 100.0)


def last_price(ticker: str) -> float | None:
    scan = load_scans().get(ticker.upper()) or {}
    snap = normalize_snapshot(scan.get("snapshot"))
    price = snap.get("price")
    return float(price) if price is not None else None


def add_paper_trade(
    *,
    ticker: str,
    side: str,
    qty: float,
    price: float | None = None,
    note: str = "",
) -> tuple[bool, str, dict[str, Any] | None]:
    """Buy or sell paper shares. side in {buy, sell}."""
    ticker = ticker.strip().upper()
    side = side.strip().lower()
    if side not in {"buy", "sell"}:
        return False, "Side must be buy or sell.", None
    try:
        qty = float(qty)
    except (TypeError, ValueError):
        return False, "Quantity must be a number.", None
    if qty <= 0:
        return False, "Quantity must be positive.", None

    px = price if price is not None else last_price(ticker)
    if px is None or px <= 0:
        return False, "Need a positive price (scan the ticker or enter price).", None
    px = float(px)

    port = load_portfolio()
    notional = qty * px
    fee = _fee(notional)
    positions = dict(port.get("positions") or {})
    pos = dict(positions.get(ticker) or {"qty": 0.0, "avg_price": 0.0})
    cash = float(port.get("cash") or 0.0)

    if side == "buy":
        cost = notional + fee
        if cost > cash + 1e-9:
            return False, f"Insufficient cash (need {cost:.2f}, have {cash:.2f}).", None
        new_qty = float(pos["qty"]) + qty
        avg = (
            (float(pos["qty"]) * float(pos["avg_price"]) + notional) / new_qty
            if new_qty
            else px
        )
        pos = {"qty": new_qty, "avg_price": avg}
        cash -= cost
    else:
        have = float(pos.get("qty") or 0.0)
        if qty > have + 1e-9:
            return False, f"Insufficient shares (have {have}).", None
        proceeds = notional - fee
        cash += proceeds
        new_qty = have - qty
        if new_qty <= 1e-9:
            positions.pop(ticker, None)
            pos = None
        else:
            pos = {"qty": new_qty, "avg_price": float(pos["avg_price"])}

    if pos is not None:
        positions[ticker] = pos
    port["positions"] = positions
    port["cash"] = cash
    entry = {
        "id": str(uuid.uuid4()),
        "at": _now_iso(),
        "ticker": ticker,
        "side": side,
        "qty": qty,
        "price": px,
        "fee": fee,
        "note": (note or "")[:200],
    }
    ledger = list(port.get("ledger") or [])
    ledger.insert(0, entry)
    port["ledger"] = ledger[:200]
    save_portfolio(port)
    return True, "Paper trade recorded.", port


def portfolio_view() -> dict[str, Any]:
    port = load_portfolio()
    sim = load_settings().simulation
    cash = float(port.get("cash") or 0.0)
    rows = []
    equity = 0.0
    unrealized = 0.0
    for ticker, pos in sorted((port.get("positions") or {}).items()):
        qty = float(pos.get("qty") or 0.0)
        avg = float(pos.get("avg_price") or 0.0)
        last = last_price(ticker)
        mtm = (last * qty) if last is not None else None
        pnl = (mtm - avg * qty) if mtm is not None else None
        if mtm is not None:
            equity += mtm
        if pnl is not None:
            unrealized += pnl
        rows.append(
            {
                "ticker": ticker,
                "qty": qty,
                "avg": avg,
                "last": last,
                "mtm": mtm,
                "pnl": pnl,
            }
        )
    total_pnl = unrealized  # PoC: mark-to-market vs cost; realized embedded in cash
    return {
        "cash": cash,
        "equity_mtm": equity,
        "total_pnl": total_pnl,
        "currency": port.get("currency") or sim.currency or "AUD",
        "fee_flat": sim.fee_flat,
        "fee_pct": sim.fee_pct,
        "broker_label": sim.broker_label,
        "positions": rows,
        "ledger": list(port.get("ledger") or [])[:40],
        "updated_at": port.get("updated_at") or "",
    }
