# Agent contract

Shared rules for every agent working in this repo. Role-specific behavior lives in `.cursor/rules/`.

## Source of truth

| Concern | File |
|---------|------|
| Product vision & constraints | `PRODUCT.md` |
| Themes / outcomes | `ROADMAP.md` |
| Prioritized work | `BACKLOG.md` |
| Active sprint | `docs/sprints/current.md` |
| Technical decisions | `docs/architecture.md` |

Do not invent lasting product decisions only in chat. Write them into the files above.

## Roles

- **Product owner** — owns brief, roadmap, backlog, and sprints. Does not implement application code. Bootstrap uses two interviews: (1) `PRODUCT.md` + `ROADMAP.md`, (2) `BACKLOG.md` + Planned Sprint 1.
- **Architect / developer** — bootstrap uses two interviews: (1) author `docs/architecture.md`, (2) implement Sprint 1 in `docs/sprints/current.md`. Later sprints: implement only what’s in the current sprint file; keep architecture docs current.

## Definition of done (per story)

- Acceptance criteria in the sprint file are met
- Behavior is covered by automated tests when the story implies logic worth protecting
- Relevant docs updated (`docs/architecture.md` for material design changes)
- No silent scope expansion; new ideas go to Parking lot or `BACKLOG.md`

## Working agreements

1. Prefer small, reviewable changes aligned to one sprint story at a time.
2. If requirements are ambiguous or blocked, stop, record the blocker on the story, and ask the human stakeholder.
3. Keep `AGENTS.md` behavioral and short — product state belongs in the product docs.
4. Never commit secrets, credentials, or `.env` files.
