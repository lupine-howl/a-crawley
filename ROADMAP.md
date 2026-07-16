# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley  
**Code check (2026-07-16):** Sprints **6–16 are implemented** (ASX paper desk, history/pins, fitness import in 14–16).  
**Retro:** [Sprints 1–5](docs/sprints/archive/sprints-1-5-retrospective.md)  
**Pivot:** **11** Settings Update → **12** Sender Inbox → **13** ASX desk → **14–16** paper + history + fitness import. Remaining former *planned* 11–40 queue is [shelved](docs/sprints/shelved/README.md).

## Now

**Shipped through Sprint 16** (code + automated tests):

- [x] Shared Python core + stable module contract (confirm-first write-back live for Calendar)
- [x] Local browser dashboard: themes, Settings, Markdown, home At a glance, Day brief
- [x] Investment + Gmail + Calendar (read); Calendar **confirm-first insert**
- [x] Fitness, Work, Co-parenting, DIY, Finance/Taxes, Coding/Creative lite modules
- [x] Opt-in phone-on-LAN; ADR-006 write-back model
- [x] LocalLlama (Ollama HTTP) operable; ADR-007
- [x] Shared context seed (standing notes + capped snapshots + history pins); ADR-008
- [x] Settings → **Update** (git pull + hot reload) — Sprint 11
- [x] Sender Inbox PoC — Sprint 12
- [x] ASX desk scanner + profiles — Sprint 13
- [x] ASX recommendations + paper portfolio + simulation settings — Sprint 14
- [x] Snapshot history browser + shared-context pins — Sprint 15
- [x] Fitness activity import lite — Sprint 16

*Still out of Now:* native desktop wrapper, Gmail send, public hosting, multi-user, **live brokerage order placement**

## Next

- Scale beyond 20-email / 20-company PoC caps
- Un-shelve selected former 11–40 items where useful ([shelved](docs/sprints/shelved/README.md))

Latest delivery: [`docs/sprints/current.md`](docs/sprints/current.md) (Sprints 14–16)

## Closed

| Sprints | Theme | Evidence |
|---------|-------|----------|
| 1 | Shell + Investment/Gmail lite | [archive](docs/sprints/archive/sprint-1-local-shell.md) |
| 2 | Themes, settings, Markdown, glance | [archive](docs/sprints/archive/sprint-2-themes-settings-glance.md) |
| 3–4 | Google + Investment/Fitness | [archive](docs/sprints/archive/sprint-3-4-google-investment-fitness.md) |
| 5 | LAN + Work + write-back design | [archive](docs/sprints/archive/sprint-5-lan-work-writeback.md) |
| 6–10 | Life modules, Day brief, Calendar write-back, LocalLlama, shared context | [archive](docs/sprints/archive/sprint-6-10-life-modules-llm-context.md) · [code verification](docs/sprints/archive/sprint-6-10-code-verification.md) |
| 11 | Settings Update (git pull + hot reload) | [archive](docs/sprints/archive/sprint-11-settings-update.md) · `tests/test_sprint11_update.py` |
| 12 | Sender Inbox PoC | [archive](docs/sprints/archive/sprint-12-sender-inbox.md) |
| 13 | ASX desk scanner + profiles | [archive](docs/sprints/archive/sprint-13-asx-profiles.md) |
| 14–16 | Paper portfolio + history/pins + fitness import | [current](docs/sprints/current.md) · `tests/test_sprints_14_16.py` |

## Later (shelved — do not start)

Former **planned** Sprints 11–40 (platform Later + Email/Investment depth arc) — filenames `planned/sprint-11.md`…`sprint-40.md` collide with pivot; use pivot-named files. B35–B37 were un-shelved into Sprints 15–16.

## Icebox

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Live automated trading / order placement** (paper portfolio ≠ this)
- Professional medical/financial advice liability framing
- Tax e-file / bank aggregation SaaS
