# crawley-ui

Phone Preview host for **Crawley** — product UI on published `@phone-preview/core`.  
Analytics brain stays in the parent repo (`uv run python -m crawley`).

## Setup recipe (Phone Preview)

```bash
npm create phone-preview@latest crawley-ui -- --name "Crawley"
# Do NOT use --with-api as the analytics brain (sidecar is for tiny app routes only).
cd crawley-ui
npm install
```

Pin `@phone-preview/core` ≥ **0.6.1** (real `dist/` publish — not the 0.6.0 monorepo stub).

| Import | Use |
|--------|-----|
| `@phone-preview/core` | `Shell`, `starterPacks`, `FeaturePack` |
| `@phone-preview/core/platform` | `withoutEducationFeatures` if you need to strip curriculum from a larger set |
| `@phone-preview/core/education` | Curriculum packs — **not** used by Crawley |
| `@phone-preview/core/styles.css` | Required |

Pack model: `starterPacks()` (shell chrome: themes, todos, system tabs) + **app-private** packs under `src/packs/`.  
See Phone Preview `docs/build/consuming-published-core.md` in the phone-preview repo for the full consume guide.

## Run (two processes)

```bash
# Terminal A — analytics (repo root)
uv run python -m crawley

# Terminal B — UI
cd crawley-ui
npm run dev
```

Open the Vite URL (default http://127.0.0.1:5173).  
Phone Preview demo login (if prompted): `admin@demo.local` / `demo123`.

### Vite proxy

| Browser path | Target |
|--------------|--------|
| `/api/analytics/*` | `http://127.0.0.1:8000/*` (rewrite strips prefix) |
| `/api/*` | `http://127.0.0.1:3001` (optional PP local API — not ASX/Gmail workers) |

Example: UI `fetch("/api/analytics/v1/asx/companies")` → analytics `GET /v1/asx/companies`.

Contract: [`../docs/api/presentation-v1.md`](../docs/api/presentation-v1.md).

## Packs

| Pack | Path | Role |
|------|------|------|
| `asxDeskPack` | `src/packs/asxDeskPack.tsx` | Companies, **Start/Stop** scan daemon + spinner, detail + notebook |
| `asxRecommendationsPack` | `src/packs/asxRecommendationsPack.tsx` | Recommendations + paper buy |
| `asxPortfolioPack` | `src/packs/asxPortfolioPack.tsx` | Paper portfolio + ledger |
| `asxThemesPack` | `src/packs/asxThemesPack.tsx` | News themes, alerts, holdings journal |
| `analyticsSettingsPack` | `src/packs/analyticsSettingsPack.tsx` | Settings toolbar **LLM** tab (`systemTab`) |

Open **Settings → LLM** (system tab) to pick OpenAI vs Local Llama. Local Llama raises the ASX active-set ceiling (no 20-call gate).

No OpenAI/Google secrets in Vite env. Keys stay on the analytics host.

## Persistence

Phone Preview defaults (IndexedDB). Turso/Duck sync is optional via Settings → Connections — for UI workspace data only, not a replacement for analytics workers.

## Scripts

| Command | Purpose |
|---------|---------|
| `npm run dev` | Vite + proxies |
| `npm run build` | Production build |
| `npm run preview` | Preview build |
