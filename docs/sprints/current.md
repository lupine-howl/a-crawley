# Sprint 5 — LAN reach, Work lite, write-back design

**Status:** done  
**Duration:** one symbolic week  
**Backlog refs:** B12, B17, B18  
**Depends on:** Sprint 2–4 shell and modules  
**Architecture:** [`docs/architecture.md`](../architecture.md) + [`docs/adr/006-write-back-confirm.md`](../adr/006-write-back-confirm.md)  
**Previous:** [`archive/sprint-3-4-google-investment-fitness.md`](archive/sprint-3-4-google-investment-fitness.md)  
**Planned source:** [`planned/sprint-5.md`](planned/sprint-5.md)

## Goal

Make Crawley reachable on the **local network only when consciously enabled**, land **Work** lite, and **design** (not ship) write-back with an ADR + dry-run hooks.

## Demo

1. Enable LAN bind from Settings; see warning; restart; open from phone on trusted LAN
2. Use Work: save notes/tasks → LLM prioritization → home snapshot
3. Read ADR-006 + architecture write-back stages; dry-run hooks only (no live mutations)

## Committed

### S5.1 — Phone-on-LAN access pattern (B12)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B12 |

**Acceptance criteria:**

- [x] Default bind remains `127.0.0.1`
- [x] Settings toggle + optional `CRAWLEY_HOST` env; **restart required**
- [x] UI warning when LAN enabled; README firewall/WSL notes
- [x] Decision: **no auth; trusted LAN only** (documented)
- [x] Disable → localhost-only after restart

---

### S5.2 — Work module lite (B17)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B17 |

**Acceptance criteria:**

- [x] Work leaves Coming soon
- [x] Local notes file under `data/work/notes.txt`; Save + Prioritize
- [x] Run → LLM Markdown prioritization / next-actions summary
- [x] Job status + snapshot on home glance
- [x] No third-party work suite OAuth

---

### S5.3 — Write-back design (B18)

| Field | Value |
|-------|-------|
| Status | done |
| Backlog ref | B18 |

**Acceptance criteria:**

- [x] ADR-006 accepted: confirm; draft-first; per-module capability flags
- [x] Module contract dry-run `write_back()`; Gmail/Calendar exercise buttons; audit `data/writeback_audit.jsonl`
- [x] Architecture outlines propose → draft → confirm → execute → audit
- [x] Out of scope: silent automation, multi-user ACLs, live Gmail/Calendar mutations

## Out of scope (sprint)

- Actual Gmail send / Calendar insert → **Sprint 8** ([planned](planned/sprint-8.md)) for Calendar confirm-first; Gmail send later
- LocalLlama production hosting → **Sprint 9** ([planned](planned/sprint-9.md))
- Native desktop wrapper → After Sprint 10 / Later
- Co-parenting / DIY / Finance live modules → **Sprints 6–7** ([index](planned/README.md))

## Parking lot

- Co-parenting schedule module → **[Sprint 6](planned/sprint-6.md)**
- Real write-back implementation after ADR soak → **[Sprint 8](planned/sprint-8.md)**
- LocalLlama install path → **[Sprint 9](planned/sprint-9.md)**
- Finance + Day brief / Coding+context → [Sprint 7](planned/sprint-7.md), [Sprint 10](planned/sprint-10.md)
- Optional LAN shared-secret gate (deferred; trusted LAN policy for now)
