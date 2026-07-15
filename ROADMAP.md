# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Code check (2026-07-15):** Sprints **6–10 are implemented** in `src/crawley/` (verified modules + `tests/test_sprint6_10.py` green).  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)  
**Pivot:** Sender Inbox + ASX PoCs start at **Sprint 11**. Former *planned* 11–40 depth/platform queue is [shelved](docs/sprints/shelved/README.md) — not the delivered 6–10 work.

## Now

**Shipped through Sprint 10** (code + automated tests):

- [x] Shared Python core + stable module contract (confirm-first write-back live for Calendar)
- [x] Local browser dashboard: themes, Settings, Markdown, home At a glance, Day brief
- [x] Investment + Gmail + Calendar (read); Calendar **confirm-first insert**
- [x] Fitness, Work, Co-parenting, DIY, Finance/Taxes, Coding/Creative lite modules
- [x] Opt-in phone-on-LAN; ADR-006 write-back model
- [x] LocalLlama (Ollama HTTP) operable; ADR-007
- [x] Shared context seed (standing notes + capped snapshots); ADR-008

*Still out of Now:* native desktop wrapper, Gmail send, public hosting, multi-user, **live brokerage order placement** (paper portfolio planned in Sprint 13)

## Next

**Sender Inbox + ASX depth PoCs**

### Sprint 11 (ready) — Sender Inbox PoC (+ UX contract)
Background one-at-a-time email categorize; inbox **grouped by sender**; LLM sender profiles; actionable todos; **~20 email** cap.  
[`docs/sprints/current.md`](docs/sprints/current.md) · B65–B70 · UX: [`docs/ux/sender-inbox-asx.md`](docs/ux/sender-inbox-asx.md)

### Sprint 12 (planned) — ASX company scanner + profiles PoC
Large ASX universe; background scan; per-company profiles; sources + prompts; **~20 company** slice.  
[`docs/sprints/planned/sprint-12-asx-profiles.md`](docs/sprints/planned/sprint-12-asx-profiles.md) · B71–B74

### Sprint 13 (planned) — ASX recommendations + paper portfolio
Structured recommendations; simulated portfolio page; brokerage/simulation settings (no live orders).  
[`docs/sprints/planned/sprint-13-asx-paper-portfolio.md`](docs/sprints/planned/sprint-13-asx-paper-portfolio.md) · B75–B77

### After Sprint 13

- Scale beyond 20-email / 20-company PoC caps
- Un-shelve selected former 11–40 items where useful ([shelved](docs/sprints/shelved/README.md))

## Closed

| Sprints | Theme | Evidence |
|---------|-------|----------|
| 1 | Shell + Investment/Gmail lite | [archive](docs/sprints/archive/sprint-1-local-shell.md) |
| 2 | Themes, settings, Markdown, glance | [archive](docs/sprints/archive/sprint-2-themes-settings-glance.md) |
| 3–4 | Google + Investment/Fitness | [archive](docs/sprints/archive/sprint-3-4-google-investment-fitness.md) |
| 5 | LAN + Work + write-back design | [archive](docs/sprints/archive/sprint-5-lan-work-writeback.md) |
| 6–10 | Life modules, Day brief, Calendar write-back, LocalLlama, shared context | [archive](docs/sprints/archive/sprint-6-10-life-modules-llm-context.md) · [code verification](docs/sprints/archive/sprint-6-10-code-verification.md) |

## Later (shelved — do not start)

Former **planned** Sprints 11–40 (platform Later + Email/Investment depth arc) — filenames `planned/sprint-11.md`…`sprint-40.md` collide with pivot; use `sprint-11-sender-inbox.md` etc. for active work.

## Icebox

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Live automated trading / order placement** (paper portfolio ≠ this)
- Professional medical/financial advice liability framing
- Tax e-file / bank aggregation SaaS
