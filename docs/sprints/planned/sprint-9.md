# Sprint 9 — Local LLM operable (planned)

**Status:** closed (delivered in Sprint 6–10 bundle)  
**Duration:** one symbolic week  
**Backlog refs:** B27, B31  
**Depends on:** Sprint 2 LLM settings + Test connection (B8); provider interface (B3)  
**Architecture:** [`docs/architecture.md`](../architecture.md) + new ADR for local runtime choice  
**UX:** Light Settings copy pass for local provider URL/model/test states (follow Sprint 2 Settings patterns)

## Goal

Prove the roadmap **path to a locally hosted LLM**: make the LocalLlama (or equivalent) provider **operable** against a documented local runtime so core advice can run without OpenAI when the stakeholder’s machine is set up — without deleting the cloud path.

## Demo

Operator can:

1. Run a local LLM runtime (documented, e.g. Ollama) with a chosen model
2. In Settings, select the local provider, set base URL / model, Save
3. **Test connection** succeeds when the daemon is up; fails clearly when unreachable or model missing
4. Run at least one existing module summary via the local provider, with clear busy/timeout behavior
5. Switch back to OpenAI if desired; both remain first-class choices

## Committed

### S9.1 — LocalLlama provider operable (B27)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B27 |

**Acceptance criteria:**

- [ ] Local provider implements the existing LLM interface (prefer HTTP-local like Ollama; record in ADR)
- [ ] Settings: provider select, base URL, model id; secrets/local URL stay gitignored as appropriate
- [ ] **Test connection** success / failure / unreachable / missing-model states
- [ ] Modules honor active provider after save (hot-reload vs restart documented)
- [ ] README: stakeholder install/run assumptions; OpenAI remains selectable
- [ ] Architecture updated: LocalLlama no longer “placeholder only”

---

### S9.2 — Local provider bounds & module-run errors (B31)

| Field | Value |
|-------|-------|
| Status | todo |
| Backlog ref | B31 |
| Depends on | S9.1 |

**Acceptance criteria:**

- [ ] Documented timeouts / max output bounds suitable for local hardware (not unbounded waits)
- [ ] Module run surfaces distinct errors when local daemon dies mid-job vs model timeout vs OpenAI path errors
- [ ] No silent hang in busy state; cancel-or-fail path documented
- [ ] Architecture notes local-vs-cloud latency expectations for the operator

**Out of scope (sprint):**

- Shipping model weights in-repo
- Auto GPU installer / hardware advisor product
- Multi-provider ensemble routing
- New life-domain modules (Sprint 6–8 / 10 tracks)

## Architect notes

- Prefer **Ollama HTTP** (or compatible) over embedding a model runtime in-process — keeps Crawley’s single-process shape and matches ADR-003.
- Do not auto-switch providers mid-job; active provider is sticky per Settings save.
- Leave Coding/Creative for Sprint 10 so this sprint stays a focused Later-theme spike.

## Parking lot

- Default-to-local when daemon healthy
- Per-module provider override
- Quantization / hardware profile presets
