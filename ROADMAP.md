# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Code check (2026-07-15):** Sprints **6–10 are implemented** in `src/crawley/` (verified modules + `tests/test_sprint6_10.py` green).  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)  
**Pivot:** **11** Settings Update → **12** Sender Inbox → **13** ASX profiles → **14–20** dual-desk depth (paper portfolio through playbooks). Former *planned* 11–40 platform/depth queue is [shelved](docs/sprints/shelved/README.md) — not the delivered 6–10 work.

## Now

**Shipped through Sprint 13** (code + automated tests where applicable):

- [x] Shared Python core + stable module contract (confirm-first write-back live for Calendar)
- [x] Local browser dashboard: themes, Settings, Markdown, home At a glance, Day brief
- [x] Investment + Gmail + Calendar (read); Calendar **confirm-first insert**
- [x] Fitness, Work, Co-parenting, DIY, Finance/Taxes, Coding/Creative lite modules
- [x] Opt-in phone-on-LAN; ADR-006 write-back model
- [x] LocalLlama (Ollama HTTP) operable; ADR-007
- [x] Shared context seed (standing notes + capped snapshots); ADR-008
- [x] Settings → **Update** (git pull + hot reload) — Sprint 11
- [x] **Sender Inbox** PoC (~20 emails) — Sprint 12
- [x] **ASX desk** scanner + company profiles (~20 slice) — Sprint 13

*Still out of Now:* native desktop wrapper, Gmail send, public hosting, multi-user, **live brokerage order placement** (paper portfolio is Sprint 14 — not Icebox)

## Next

**Dual-desk depth — Sprints 14–20** (active: Sprint 14)

### Sprint 14 (current) — ASX recommendations + paper portfolio
Structured recommendations; simulated portfolio page; brokerage/simulation settings (**no live orders**).  
[`docs/sprints/current.md`](docs/sprints/current.md) · B75–B77 · UX: [`docs/ux/sender-inbox-asx.md`](docs/ux/sender-inbox-asx.md)

### Sprint 15 (planned) — Sender Inbox scale
Raise ingest cap + retention/prune; search/filter across senders/categories/todos.  
[`docs/sprints/planned/sprint-15-sender-inbox-scale.md`](docs/sprints/planned/sprint-15-sender-inbox-scale.md) · B79–B80

### Sprint 16 (planned) — ASX scale + earnings/events
Expand active set beyond 20; bounded earnings/events skim.  
[`docs/sprints/planned/sprint-16-asx-scale-events.md`](docs/sprints/planned/sprint-16-asx-scale-events.md) · B81–B82

### Sprint 17 (planned) — Email × ASX bridge
Mail mentions of ASX tickers / paper holdings → bridge digest + deep links.  
[`docs/sprints/planned/sprint-17-email-asx-bridge.md`](docs/sprints/planned/sprint-17-email-asx-bridge.md) · B83

### Sprint 18 (planned) — Gmail confirm-first send
Draft → confirm → send → audit (ADR-006); complements Sender Inbox todos.  
[`docs/sprints/planned/sprint-18-gmail-send.md`](docs/sprints/planned/sprint-18-gmail-send.md) · B84

### Sprint 19 (planned) — ASX alerts + recommendation feedback
Local in-panel alerts; disposition loop on recommendations (no live orders).  
[`docs/sprints/planned/sprint-19-asx-alerts.md`](docs/sprints/planned/sprint-19-asx-alerts.md) · B85–B86

### Sprint 20 (planned) — Dual-desk playbooks + polish
Named playbooks for Sender Inbox / ASX runs; focused polish pass.  
[`docs/sprints/planned/sprint-20-playbooks-polish.md`](docs/sprints/planned/sprint-20-playbooks-polish.md) · B87–B88

### Sprint 21 (planned) — Google OAuth ops
Tailscale/LAN first-Connect ergonomics + softer consent prompts (fewer unnecessary re-auth screens).  
[`docs/sprints/planned/sprint-21-google-oauth-ops.md`](docs/sprints/planned/sprint-21-google-oauth-ops.md) · B89–B90  
*May pull forward if OAuth friction blocks desk use before Sprint 20 finishes.*

### After Sprint 21

- Un-shelve selected former platform/depth items where useful ([shelved](docs/sprints/shelved/README.md))
- Icebox stays closed without PRODUCT revision

## Closed

| Sprints | Theme | Evidence |
|---------|-------|----------|
| 1 | Shell + Investment/Gmail lite | [archive](docs/sprints/archive/sprint-1-local-shell.md) |
| 2 | Themes, settings, Markdown, glance | [archive](docs/sprints/archive/sprint-2-themes-settings-glance.md) |
| 3–4 | Google + Investment/Fitness | [archive](docs/sprints/archive/sprint-3-4-google-investment-fitness.md) |
| 5 | LAN + Work + write-back design | [archive](docs/sprints/archive/sprint-5-lan-work-writeback.md) |
| 6–10 | Life modules, Day brief, Calendar write-back, LocalLlama, shared context | [archive](docs/sprints/archive/sprint-6-10-life-modules-llm-context.md) · [code verification](docs/sprints/archive/sprint-6-10-code-verification.md) |
| 11 | Settings Update (git pull + hot reload) | [archive](docs/sprints/archive/sprint-11-settings-update.md) · `tests/test_sprint11_update.py` |
| 12 | Sender Inbox PoC | [archive](docs/sprints/archive/sprint-12-sender-inbox.md) · `tests/test_sprint12_sender_inbox.py` |
| 13 | ASX desk scanner + company profiles | [archive](docs/sprints/archive/sprint-13-asx-profiles.md) · `tests/test_sprint13_asx.py` |

## Later (shelved — do not start)

Former **planned** Sprints 11–40 (platform Later + Email/Investment depth arc) — filenames `planned/sprint-11.md`…`sprint-40.md` collide with pivot; use the pivot-named files (`sprint-11-update.md` … `sprint-20-playbooks-polish.md`, `sprint-21-google-oauth-ops.md`). Bare `sprint-21.md` remains shelved (B44 thread digests).

## Icebox

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Live automated trading / order placement** (paper portfolio ≠ this)
- Professional medical/financial advice liability framing
- Tax e-file / bank aggregation SaaS
