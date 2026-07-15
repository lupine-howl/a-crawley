# ADR-007: Local LLM via Ollama-compatible HTTP

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

Crawley’s LLM provider interface already listed `LocalLlama` as a placeholder. The Later theme asks for a path off cloud APIs without embedding model runtimes inside the Crawley process (ADR-003 single-process shape).

## Decision

1. Implement `LocalLlamaProvider` against an **Ollama-compatible HTTP** daemon (`/api/tags`, `/api/chat`).
2. Settings persist `provider`, `model`, `base_url`, and `timeout_s` under `data/secrets/settings.json`.
3. OpenAI remains a first-class selectable provider; no auto-switch mid-job.
4. Bound local output (`num_predict`) and timeouts; fail loudly (unreachable / timeout / missing model).

## Consequences

- **Positive:** Stakeholder installs/runs the model daemon separately; Crawley stays thin; Test connection works.
- **Negative:** Requires an external process; cold starts can feel slow vs OpenAI.
- **Follow-up:** Optional default-to-local when daemon healthy; per-module provider override (Parking lot).
