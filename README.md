# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and two Cursor agent roles.

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Architecture doc, then implements sprint |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Bootstrap sequence

1. **PO Interview 1** — `PRODUCT.md` + `ROADMAP.md`
2. **PO Interview 2** — `BACKLOG.md` + Planned Sprint 1 (still in Sprint 0)
3. **Architect Interview 1** — `docs/architecture.md` (no app code)
4. **Architect Interview 2** — implement Sprint 1

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) — project brief
- [`ROADMAP.md`](./ROADMAP.md) — Now / Next / Later
- [`BACKLOG.md`](./BACKLOG.md) — prioritized work
- [`docs/sprints/current.md`](./docs/sprints/current.md) — active sprint
- [`docs/architecture.md`](./docs/architecture.md) — technical decisions

## Enabling a rule on an Agent chat

These rules use `alwaysApply: false` (manual / intelligent — not always on). For each PO or Architect session:

1. Open a **new Agent** chat (separate chats for PO vs Architect).
2. In the chat input, type `@` and select the rule — e.g. `@product-owner` or `@architect-developer`.
3. Check the **context ring** next to the input → **Rules** to confirm it’s attached.
4. Send your prompt.

To change how a rule attaches later: **Customize → Rules** (or open the `.mdc` file) and use the type dropdown — Always Apply / Apply Intelligently / Apply to Specific Files / Apply Manually.

## How to run agents

### 1. Product owner — Interview 1 (brief & roadmap)

`@product-owner`, then:

> You are the product owner. Run Interview 1 only. Read PRODUCT.md and ROADMAP.md, interview me about the project, then write PRODUCT.md (project brief) and ROADMAP.md. Do not write the backlog or Sprint 1 yet. Do not write application code.

### 2. Product owner — Interview 2 (backlog & Planned Sprint 1)

`@product-owner`, then:

> You are the product owner. Run Interview 2 only. Read PRODUCT.md and ROADMAP.md. Interview me about near-term priorities, then write BACKLOG.md and fill the Planned Sprint 1 section in docs/sprints/current.md. Do not replace Sprint 0 yet. Do not write architecture or application code.

### 3. Architect — Interview 1 (architecture)

`@architect-developer`, then:

> You are the senior architect/developer. Run Interview 1 only. Read PRODUCT.md, ROADMAP.md, BACKLOG.md, and the Planned Sprint 1 section in docs/sprints/current.md. Interview me about technical constraints and stack, then write docs/architecture.md. When confirmed, archive Sprint 0 and promote Planned Sprint 1 to docs/sprints/current.md. Do not implement Sprint 1 yet.

### 4. Architect — Interview 2 (implement Sprint 1)

`@architect-developer`, then:

> You are the senior architect/developer. Run Interview 2. Read AGENTS.md, docs/architecture.md, and docs/sprints/current.md. Implement Sprint 1 in order. If AC is unclear, mark the story blocked and stop.

### 5. Review

PO (or you) checks the diff against sprint acceptance criteria, then plans the next sprint.
