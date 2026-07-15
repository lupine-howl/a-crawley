# Sprint 5 — LAN reach, Work lite, write-back design (planned)

**Status:** planned (activates after Sprint 4 closes)  
**Duration:** one symbolic week  
**Backlog refs:** B12, B17, B18  
**Depends on:** Stable shell from Sprint 2; modules from 3–4 preferred  
**Architecture:** [`docs/architecture.md`](../architecture.md) + new ADR for write-back  
**UX:** LAN caution copy + Work panel; optional UX pass for bind/auth warnings

## Goal

Make Crawley reachable on the **local network only when consciously enabled** (phone-on-LAN testing), land one more day-to-day domain (**Work** lite), and **design** (not ship) write-back so later sprints can add explicit-confirm mutations safely.

## Demo

Operator can:

1. Enable LAN bind from Settings (default remains localhost-only); see clear warning about exposure
2. Open the dashboard from a phone on the same LAN (or documented equivalent test)
3. Use **Work** module: capture tasks/notes and get an LLM prioritization/summary (local data; Markdown)
4. Read an accepted ADR + architecture section describing write-back stages (draft → confirm → mutate) for Gmail/Calendar — **no live write APIs yet**

## Committed

### S5.1 — Phone-on-LAN access pattern (B12)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B12 |

**Acceptance criteria:**

- [ ] Default bind remains `127.0.0.1` (intrusion-minded)
- [ ] Conscious enable: Settings toggle and/or env (`CRAWLEY_HOST=0.0.0.0`) with **restart or documented hot-bind policy**
- [ ] UI warning when LAN enabled; README: firewall/WSL port notes, “trusted LAN only”
- [ ] Optional simple shared secret / basic gate **or** explicit “no auth; trusted LAN only” decision documented (pick one; prefer minimal gate if phone test needs it)
- [ ] Disable path returns to localhost-only

---

### S5.2 — Work module lite (B17)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B17 |

**Acceptance criteria:**

- [ ] Work leaves Coming soon
- [ ] Operator can save a small local task list or paste a “this week” note (filesystem/DuckDB — architect chooses)
- [ ] Run → LLM Markdown prioritization / next-actions summary
- [ ] Job status + snapshot on home glance
- [ ] No third-party work suite OAuth required this sprint

---

### S5.3 — Write-back design (docs + contract hooks only) (B18)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B18 |

**Acceptance criteria:**

- [ ] ADR accepted: write-back requires explicit user confirm; draft-first; per-module capability flags
- [ ] Module contract write-back hooks documented/exercised with **no-op or dry-run** stub (no Gmail send / Calendar insert in production paths)
- [ ] Architecture outlines stages: propose → show diff/draft → confirm → execute → audit log local
- [ ] Out of scope callout: no silent automation, no multi-user ACLs

**Out of scope (sprint):**

- Actual Gmail send / Calendar insert
- LocalLlama production hosting
- Native desktop wrapper
- Co-parenting / DIY / Finance live modules → Sprints 6–7

## Parking lot

- Co-parenting schedule module → **[Sprint 6](sprint-6.md)**
- Real write-back implementation after ADR soak → **[Sprint 8](sprint-8.md)**
- LocalLlama install path → **[Sprint 9](sprint-9.md)**
- DIY / Finance / Day brief / Coding+context → [Sprint 7](sprint-7.md), [Sprint 10](sprint-10.md); [index](README.md)
