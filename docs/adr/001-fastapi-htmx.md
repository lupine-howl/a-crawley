# ADR-001: FastAPI + Jinja2/HTMX for local UI

- **Status:** **Superseded** (product surface deleted in Sprint 35) — see [ADR-009](009-phone-preview-analytics.md)
- **Date:** 2026-07-15 (superseded 2026-07-16)

## Context

Crawley needed a local browser UI on the stakeholder’s machine. Product constraints: Python brain, single PoC UI stack. Choices considered: server-rendered FastAPI + HTMX vs FastAPI API + React/Vite SPA.

## Decision (original)

Use **FastAPI** with **Jinja2** templates and **HTMX** for progressive enhancement.

## Outcome

Sprint **35** removed the Jinja/HTMX product shell. Supported operator UI is **`crawley-ui`** (Phone Preview). This repo serves JSON `/v1` + thin OAuth HTML (`/modules/gmail/oauth/*`) only. FastAPI remains the analytics host.
