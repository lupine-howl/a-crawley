# Roadmap

Ordered outcomes (not tasks). Product owner owns this file.  
**Working title:** Crawley

## Now

**Local shell + proof that modules and real sources work** — *Sprint 1 closed 2026-07-15*

- [x] Shared Python core with a **stable module contract** (lifecycle, config/credentials hooks, inputs/outputs; read paths first; **write-back reserved** for later).
- [x] Local **browser** dashboard: navigate modules; click into panels.
- [x] **Investment module PoC:** quick web search/crawl → LLM synthesis of findings into short advice/summary (OpenAI for prototyping).
- [x] **Gmail PoC:** read-only connection → inbox summary the user can skim. *(Calendar remains stub until Sprint 3.)*
- [x] **Fitness module:** visible stub (panel + contract compliance).
- [x] Placeholders / registration for a sensible base set of other life modules (Coming soon panels).

*Still out of Now:* local LLM hosting, write-back, desktop wrapper, automated trading, multi-user, public hosting.

## Next

**Harden the personal OS and deepen the highest-value modules**

### Sprint 2 (active) — Operable shell
Themes, LLM settings/test, Markdown summaries, home At a glance — [`docs/sprints/current.md`](docs/sprints/current.md)

### Sprint 3 (planned) — Google life reads
Shared Google OAuth; **Calendar** live; harden Gmail — [`docs/sprints/planned/sprint-3.md`](docs/sprints/planned/sprint-3.md)

### Sprint 4 (planned) — Signal depth
Harden **Investment**; **Fitness** lite (non-clinical) — [`docs/sprints/planned/sprint-4.md`](docs/sprints/planned/sprint-4.md)

### Sprint 5 (planned) — Reach + Work + write-back design
**Phone-on-LAN** (opt-in); **Work** lite; write-back **ADR/dry-run only** — [`docs/sprints/planned/sprint-5.md`](docs/sprints/planned/sprint-5.md)

### Sprint 6 (planned) — Co-parenting + DIY lite
Local schedule + project notes → LLM Markdown; home glance slots — [`docs/sprints/planned/sprint-6.md`](docs/sprints/planned/sprint-6.md)

### Sprint 7 (planned) — Finance lite + Day brief
Finance/Taxes planning path (non-advice); Calendar+Gmail **Day brief** on home — [`docs/sprints/planned/sprint-7.md`](docs/sprints/planned/sprint-7.md)

### Sprint 8 (planned) — Confirm-first Calendar write-back
First real mutation after Sprint 5 ADR soak; audit log viewer — [`docs/sprints/planned/sprint-8.md`](docs/sprints/planned/sprint-8.md)

### Sprint 9 (planned) — Local LLM operable
LocalLlama (or equivalent) behind existing provider interface; OpenAI remains selectable — [`docs/sprints/planned/sprint-9.md`](docs/sprints/planned/sprint-9.md)

### Sprint 10 (planned) — Coding/Creative + shared context seed
Last top-tier lite module; thin cross-module context for prompts — [`docs/sprints/planned/sprint-10.md`](docs/sprints/planned/sprint-10.md)

### After Sprint 10 (unscheduled)
- Optional **native desktop shell** (wrap existing UI)
- Gmail draft-then-send write-back; further selective mutations
- Scheduled overnight Day brief; deeper shared memory / search if seed proves useful
- Wearables, brokerage, tax e-file — only if explicitly pulled from Icebox/Later bets

## Later

**Thicker local intelligence and optional desktop chrome**

- Optional **native desktop shell** wrapping the existing web UI (dock icon / window)—not a second UI stack.
- Deeper shared memory (searchable history, optional embeddings) after Sprint 10 seed.
- Broader integrations as needed: workout wearables, tax/finance depth, co-parenting ↔ Calendar sync.
- Additional selective write-back (e.g. Gmail) with the same confirm-first discipline.
- *(Local LLM path and top-tier lite modules are scheduled in Sprints 9–10 above.)*

## Icebox

Valuable or tempting, explicitly not sequenced:

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Automated trading / order placement**
- Anything framed as professional medical or financial advice liability product
