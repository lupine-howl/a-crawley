# ADR-008: Cross-module shared context seed

- **Status:** Accepted (amended Sprints 15)
- **Date:** 2026-07-15
- **Amended:** 2026-07-16

## Context

The Later theme asks for stronger local data organisation across modules. A full vector/RAG product is out of scope. Day brief and Coding/Creative need a thin way to optionally cite recent module signal plus operator standing notes. Sprint 15 adds browsable history and opt-in pins without becoming a second brain.

## Decision

1. Shared context is a **read model** built from:
   - optional standing notes (`data/standing_notes.txt`) — operator-authored seed;
   - recent successful snapshots (`data/snapshots.json`) — last success per module;
   - optional **pins** from bounded history (`data/snapshot_history.json` via `shared_context_meta.json`) — operator-selected excerpts.
2. Hard character caps apply (standing notes, each snapshot/pin slice, pin count, total bundle).
3. Injection is **opt-in** (checkbox on Day brief refresh / Coding-Creative run).
4. Never load API keys, OAuth tokens, or other secrets into the context bundle.
5. History retention is a ring buffer (≤20 entries per module); pruning is automatic on append. Standing notes are not auto-pruned.

## Consequences

- **Positive:** Cross-domain prompts without a second brain service; safe defaults when unchecked; history pins deepen context without RAG.
- **Negative:** Truncation can drop detail; no semantic search yet; pin UI lives in Settings.
- **Follow-up:** Embeddings / vector search only if this seed proves useful.
