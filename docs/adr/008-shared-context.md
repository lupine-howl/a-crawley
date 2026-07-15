# ADR-008: Cross-module shared context seed

- **Status:** Accepted
- **Date:** 2026-07-15

## Context

The Later theme asks for stronger local data organisation across modules. A full vector/RAG product is out of scope. Day brief and Coding/Creative need a thin way to optionally cite recent module signal plus operator standing notes.

## Decision

1. Shared context is a **read model**: recent successful snapshots (`data/snapshots.json`) + optional standing notes (`data/standing_notes.txt`).
2. Hard character caps apply (standing notes, each snapshot slice, total bundle).
3. Injection is **opt-in** (checkbox on Day brief refresh / Coding-Creative run).
4. Never load API keys, OAuth tokens, or other secrets into the context bundle.

## Consequences

- **Positive:** Cross-domain prompts without a second brain service; safe defaults when unchecked.
- **Negative:** Truncation can drop detail; no semantic search yet.
- **Follow-up:** Searchable history / embeddings only if this seed proves useful.
