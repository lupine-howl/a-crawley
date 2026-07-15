# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and two Cursor agent roles.

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Brief, roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Implements `docs/sprints/current.md` |

Shared contract: [`AGENTS.md`](./AGENTS.md)

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

Enable the **Product owner** rule, then:

> You are the product owner. Run Interview 1 only. Read PRODUCT.md and ROADMAP.md, interview me about the project, then write PRODUCT.md (project brief) and ROADMAP.md. Do not write the backlog or Sprint 1 yet. Do not write application code.

### 2. Product owner — Interview 2 (backlog & sprint)

Same rule, preferably a **new** PO chat (or continue after Interview 1 is confirmed):

> You are the product owner. Run Interview 2 only. Read PRODUCT.md and ROADMAP.md (already filled). Interview me about near-term priorities, then write BACKLOG.md and replace docs/sprints/current.md with Sprint 1. Do not write application code.

### 3. Architect — implement sprint

Enable the **Architect / developer** rule, then:

> You are the senior architect/developer. Read AGENTS.md, docs/architecture.md, and docs/sprints/current.md. Implement the sprint in order. If AC is unclear, mark the story blocked and stop.

### 4. Review

PO (or you) checks the diff against sprint acceptance criteria, then archives/starts the next sprint.
