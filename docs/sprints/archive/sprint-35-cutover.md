# Sprint 35 — Cutover: delete HTMX, quarantine modules

**Status:** closed (archived)  
**Archived:** 2026-07-16  
**Promoted next:** none — migration band complete ([`../current.md`](../current.md))  
**Duration:** one symbolic week  
**Backlog refs:** B99, B100  
**Depends on:** Sprint 34 Gmail pack  
**Architecture:** [ADR-001](../../adr/001-fastapi-htmx.md) superseded · [ADR-009](../../adr/009-phone-preview-analytics.md)  
**Quarantine:** [`../../../src/crawley/_quarantine/`](../../../src/crawley/_quarantine/)  
**Previous:** Migration Sprint 34 closed  

## Goal

**Delete** the Jinja/HTMX product UI. Quarantine Calendar + lite modules. Supported path = analytics JSON + `crawley-ui`.

## Demo

1. `uv run python -m crawley` — `/` is 404; `/health` and `/v1/…` work  
2. Connect Google via `/modules/gmail/oauth/start` → connected page → crawley-ui  
3. Calendar / Fitness / etc. not in registry  

## Committed

### S35.1 — Remove Jinja product UI (B99)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B99 |

- [x] `shell/` deleted; `jinja2` dependency removed  
- [x] Thin `api/oauth_routes.py` keeps stable OAuth paths  
- [x] README = analytics + crawley-ui only  
- [x] HTMX panel tests retired under `tests/_retired_htmx/`; CI green on `/v1` + cutover tests  
- [x] ADR-001 superseded  

### S35.2 — Quarantine Calendar + lite modules (B100)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B100 |

- [x] Empty `build_registry()`; modules under `_quarantine/`  
- [x] PRODUCT Later notes Calendar return  
- [x] Day brief unwired with shell  

## Explicitly out of sprint

- Calendar pack implementation  
- Labels/send/VIP packs  
- Rewriting every historical HTMX assertion (retired instead)  
