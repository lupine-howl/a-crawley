# a-crawley

Greenfield project. Product direction and delivery are driven by markdown artifacts and two Cursor agent roles.

## Agent roles

| Role | Cursor rule | Does |
|------|-------------|------|
| Product owner | `.cursor/rules/product-owner.mdc` | Roadmap, backlog, sprints |
| Architect / developer | `.cursor/rules/architect-developer.mdc` | Implements `docs/sprints/current.md` |

Shared contract: [`AGENTS.md`](./AGENTS.md)

## Product docs

- [`PRODUCT.md`](./PRODUCT.md) — vision and constraints
- [`ROADMAP.md`](./ROADMAP.md) — Now / Next / Later
- [`BACKLOG.md`](./BACKLOG.md) — prioritized work
- [`docs/sprints/current.md`](./docs/sprints/current.md) — active sprint
- [`docs/architecture.md`](./docs/architecture.md) — technical decisions

## How to run agents

1. **Product owner session** — enable the Product owner rule, then:

   > You are the product owner. Read PRODUCT.md, ROADMAP.md, and BACKLOG.md. Interview me about goals, then update those docs and docs/sprints/current.md. Do not write application code.

2. **Architect session** — enable the Architect / developer rule, then:

   > You are the senior architect/developer. Read AGENTS.md, docs/architecture.md, and docs/sprints/current.md. Implement the sprint in order. If AC is unclear, mark the story blocked and stop.

3. **Review** — PO (or you) checks the diff against the sprint acceptance criteria, then archives/starts the next sprint.
