# ADR-005: LLM provider interface (OpenAI first)

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

PoC uses the OpenAI API. Product goal after PoC is a locally hosted Llama-class model. Modules must not hard-code a vendor SDK.

## Decision

Introduce a thin **LLM provider interface** (chat/completions-oriented). Implement **OpenAI** for PoC. Keep a **LocalLlama** (or equivalent) slot for Later. Modules and shell depend only on the interface.

## Consequences

- **Positive:** Swap path to local LLM without module rewrites; easier to mock in tests.
- **Negative:** Lowest-common-denominator API; vendor-specific features stay behind provider-specific options or later extensions.
- **Constraint:** Local model hosting/ops remain out of Now / Sprint 1 unless the sprint explicitly changes that.
