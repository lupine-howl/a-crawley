# ADR-001: FastAPI + Jinja2/HTMX for local UI

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Crawley needs a local browser UI on the stakeholder’s machine. Product constraints: Python brain, single PoC UI stack, optional native desktop wrapper only Later (wrapping the same UI). Choices considered: server-rendered FastAPI + HTMX vs FastAPI API + React/Vite SPA.

## Decision

Use **FastAPI** with **Jinja2** templates and **HTMX** for progressive enhancement. The shell serves HTML panels; modules contribute partials/fragments rather than a separate SPA.

## Consequences

- **Positive:** One language for PoC delivery paths; less frontend toolchain; fits personal localhost use.
- **Negative:** Highly interactive client UIs are harder than with a SPA; if that becomes a bottleneck, migrate UI later without splitting into two competing product UIs for the same PoC.
- **Neutral:** Static assets and HTMX stay co-located with the Python app.
