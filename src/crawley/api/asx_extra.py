"""Additional ASX presentation endpoints (recs, paper, clusters, alerts, notebook)."""

from __future__ import annotations

from typing import Any, Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter(tags=["asx-extra-api"])


class PaperTradeBody(BaseModel):
    ticker: str
    side: Literal["buy", "sell"] = "buy"
    qty: float = 1.0
    price: float | None = None
    note: str = ""


class NotebookBody(BaseModel):
    thesis: str = ""
    notes: str = ""


@router.get("/v1/asx/recommendations")
def asx_recommendations() -> dict[str, Any]:
    from crawley.asx_desk.feedback import apply_feedback_to_rows
    from crawley.asx_desk.store import load_recommendations

    recs = load_recommendations()
    rows = apply_feedback_to_rows(list(recs.get("rows") or []))
    return {**recs, "rows": rows}


@router.post("/v1/asx/recommendations/refresh")
def asx_recommendations_refresh(request: Request) -> dict[str, Any]:
    from crawley.asx_desk.worker import refresh_recommendations

    ok, msg = refresh_recommendations(request.app.state.executor)
    return {"ok": ok, "message": msg, **asx_recommendations()}


@router.get("/v1/asx/portfolio")
def asx_portfolio() -> dict[str, Any]:
    from crawley.asx_desk.portfolio import portfolio_view

    return portfolio_view()


@router.post("/v1/asx/portfolio/trade")
def asx_portfolio_trade(body: PaperTradeBody) -> dict[str, Any]:
    from crawley.asx_desk.portfolio import add_paper_trade, portfolio_view

    ok, msg, _port = add_paper_trade(
        ticker=body.ticker,
        side=body.side,
        qty=body.qty,
        price=body.price,
        note=body.note,
    )
    return {"ok": ok, "message": msg, "portfolio": portfolio_view()}


@router.get("/v1/asx/clusters")
def asx_clusters() -> dict[str, Any]:
    from crawley.asx_desk.clusters import load_clusters

    return load_clusters()


@router.post("/v1/asx/clusters/refresh")
def asx_clusters_refresh(request: Request) -> dict[str, Any]:
    from crawley.asx_desk.clusters import load_clusters, start_cluster_refresh

    ok, msg = start_cluster_refresh(request.app.state.executor)
    return {"ok": ok, "message": msg, **load_clusters()}


@router.get("/v1/asx/alerts")
def asx_alerts() -> dict[str, Any]:
    from crawley.asx_desk.alerts import load_rules, load_triggered, open_alert_count

    return {
        "rules": load_rules(),
        "open": load_triggered(),
        "open_count": open_alert_count(),
    }


@router.get("/v1/asx/holdings")
def asx_holdings() -> dict[str, Any]:
    from crawley.asx_desk.holdings import load_holdings

    rows = load_holdings()
    return {"holdings": rows, "count": len(rows)}


@router.get("/v1/asx/companies/{ticker}/notebook")
def asx_notebook_get(ticker: str) -> dict[str, Any]:
    from crawley.asx_desk.notebook import load_notebook
    from crawley.asx_desk.store import company_detail

    if company_detail(ticker) is None:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker.upper()}")
    return load_notebook(ticker)


@router.put("/v1/asx/companies/{ticker}/notebook")
def asx_notebook_put(ticker: str, body: NotebookBody) -> dict[str, Any]:
    from crawley.asx_desk.notebook import save_notebook
    from crawley.asx_desk.store import company_detail

    if company_detail(ticker) is None:
        raise HTTPException(status_code=404, detail=f"Unknown ticker: {ticker.upper()}")
    return save_notebook(ticker, thesis=body.thesis, notes=body.notes)
