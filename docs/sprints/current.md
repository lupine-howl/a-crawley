# Sprints 6–10 — Life modules, Day brief, write-back, local LLM, shared context (bundled)

**Status:** done (delivered as one implementation bundle)  
**Duration:** one symbolic compound sprint  
**Backlog refs:** B19–B31  
**Depends on:** Sprint 5 (LAN, Work, ADR-006)  
**Architecture:** [`docs/architecture.md`](../architecture.md) + ADR-007 / ADR-008  
**Previous:** [`archive/sprint-5-lan-work-writeback.md`](archive/sprint-5-lan-work-writeback.md)  
**Planned sources:** [`planned/sprint-6.md`](planned/sprint-6.md) … [`planned/sprint-10.md`](planned/sprint-10.md)

## Goal

Finish the original top-tier module set, ship a morning **Day brief**, land the first **confirm-first Calendar insert**, make **LocalLlama (Ollama HTTP)** operable, and seed **shared context** across modules.

## Demo

1. Use Co-parenting / DIY / Finance / Coding-Creative lite panels (Save + Run → Markdown + home glance)
2. Refresh Day brief on home from Calendar + Gmail snapshots (optional LLM + shared context)
3. Propose → Confirm/Cancel a Calendar event; skim write-back audit in Settings
4. Settings → LocalLlama base URL/model → Test connection; module runs honor timeouts
5. Edit standing notes; optionally include shared context on Coding/Creative or Day brief

## Committed

### S6 — Co-parenting + DIY (B19–B21)

| Field | Value |
|-------|-------|
| Status | done |

- [x] Co-parenting leaves Coming soon; local schedule JSON; bounded window Markdown; snapshot
- [x] DIY leaves Coming soon; notes → next-steps Markdown; snapshot
- [x] Home glance slots for both

### S7 — Finance + Day brief (B22–B24)

| Field | Value |
|-------|-------|
| Status | done |

- [x] Finance/Taxes lite with non-advice disclaimer; snapshot
- [x] Day brief from Calendar + Gmail snapshots; partial/empty honest; optional LLM refresh
- [x] Finance glance slot

### S8 — Calendar write-back (B25–B26)

| Field | Value |
|-------|-------|
| Status | done |

- [x] Propose → confirm → execute → audit for Calendar insert; cancel performs no remote write
- [x] Calendar events write scope only (reconnect path); no Gmail send
- [x] Audit viewer in Settings + Calendar panel

### S9 — Local LLM (B27, B31)

| Field | Value |
|-------|-------|
| Status | done |

- [x] LocalLlama via Ollama HTTP; Settings base URL / model / timeout; Test connection
- [x] Distinct unreachable / timeout / missing-model errors; OpenAI remains selectable
- [x] ADR-007

### S10 — Coding/Creative + shared context (B28–B30)

| Field | Value |
|-------|-------|
| Status | done |

- [x] Coding/Creative lite; snapshot on home
- [x] Standing notes + capped snapshot shared-context seed; opt-in injection
- [x] ADR-008

## Out of scope (bundle)

- Gmail send / label mutation
- Native desktop wrapper
- Vector DB / embeddings RAG
- Automated trading / bank OAuth

## Parking lot

- Gmail draft-then-send after Calendar soak
- Scheduled overnight Day brief
- Optional native desktop shell
