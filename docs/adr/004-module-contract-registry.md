# ADR-004: Module contract with explicit in-repo registry

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Roadmap requires a stable module contract so life domains (investment, mail/calendar, fitness stub, placeholders) plug in without rewriting the core. Write-back is deferred but must be anticipatable. Plugin discovery systems are attractive but add complexity before any external packages exist.

## Decision

- Define a Python **Protocol / ABC** for modules: lifecycle, config/credential hooks, inputs/outputs, and **reserved write-back hooks** (unimplemented in PoC).
- Ship modules as **in-repo packages**.
- **Register** them explicitly in core for PoC (no setuptools entry-point discovery yet).

## Consequences

- **Positive:** Clear extension path; easy to review; write-back won’t require a contract rewrite.
- **Negative:** Adding a module means a registry edit until discovery is introduced.
- **Later:** Entry-point or filesystem plugin loading if/when external modules appear.
