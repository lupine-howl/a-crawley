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

### Sprint 2 (closed) — Operable shell
Themes, LLM settings/test, Markdown summaries, home At a glance — archived

### Sprint 3–4 (closed, bundled) — Google life reads + signal depth
Shared Google OAuth; **Calendar** live; harden Gmail; deepen **Investment**; **Fitness** lite — archived

### Sprint 5 (closed) — Reach + Work + write-back design
**Phone-on-LAN** (opt-in); **Work** lite; write-back **ADR/dry-run only** — [`docs/sprints/current.md`](docs/sprints/current.md)

### After Sprint 5 (unscheduled Next)
- Co-parenting / DIY / Finance modules as needed
- Real write-back implementation (after ADR soak)
- Further UX polish passes

## Later

**Local intelligence and thicker life coverage**

- Run on a **locally hosted LLM** (Llama-class or similar); reduce reliance on cloud APIs for core advice.
- Optional **native desktop shell** wrapping the existing web UI (dock icon / window)—not a second UI stack.
- Broader module set: DIY, coding/creative projects, taxes/finance depth, co-parenting workflows as needed.
- Selective write-back and automation with strong user confirmation.
- Stronger local data organisation across modules (shared memory/context across domains).

## Icebox

Valuable or tempting, explicitly not sequenced:

- Commercial productization or public hosting
- Multi-user / family accounts
- Dedicated mobile app store binary
- **Automated trading / order placement**
- Anything framed as professional medical or financial advice liability product
