# Consuming published `@phone-preview/core` (Crawley pin)

**Status:** Pinned for `crawley-ui` (Sprint 32)  
**Upstream:** Prefer the phone-preview repo `docs/build/consuming-published-core.md` when available; this file records what Crawley uses.  
**Packages:** `@phone-preview/core` ≥ **0.6.1**, `create-phone-preview` ≥ **0.4.1**

## Do not use

- `@phone-preview/core@0.6.0` — monorepo re-export stub (no `dist/` Shell).
- `create-phone-preview --with-api` as the **analytics brain** (Hono sidecar is for tiny app routes only).
- Education / curriculum packs (`@phone-preview/core/education`).
- Putting OpenAI / Google secrets in the Vite app.
- Iframe-wrapping legacy HTMX.

## Scaffold

```bash
npm create phone-preview@latest crawley-ui -- --name "Crawley"
cd crawley-ui
npm install
# ensure package.json has "@phone-preview/core": "^0.6.1"
npm run dev
```

Login (Phone Preview shell demo): `admin@demo.local` / `demo123`

## Host pattern

```tsx
import "@phone-preview/core/styles.css";
import { Shell, starterPacks } from "@phone-preview/core";
import { asxDeskPack } from "./packs/asxDeskPack";

<Shell
  brand={{ name: "Crawley", id: "crawley-ui" }}
  packs={[...starterPacks(), asxDeskPack]}
/>
```

| Import | Purpose |
|--------|---------|
| `@phone-preview/core` | `Shell`, `starterPacks`, `FeaturePack` types |
| `@phone-preview/core/platform` | `withoutEducationFeatures` (strip curriculum from a larger set) |
| `@phone-preview/core/education` | Curriculum — **not** for Crawley |
| `@phone-preview/core/styles.css` | Required |

### Pluggable packs

- **`starterPacks()`** — lean host chrome (themes, todos, system tabs). Use this as the base.
- **App-private packs** — `src/packs/*.tsx` exporting a `FeaturePack` (`id`, `page.Component`, optional `attachServices`, `systemTab`, …).
- Core merges `packServices` from `attachServices` into app services; packs may `fetch` relative URLs.

Crawley Sprint 32 pack: `asxDeskPack` (client scope) — list/detail/scan via analytics JSON only.

## Dev proxy (external analytics)

Vite (`crawley-ui/vite.config.ts`):

```ts
server: {
  proxy: {
    "/api/analytics": {
      target: "http://127.0.0.1:8000",
      changeOrigin: true,
      rewrite: (p) => p.replace(/^\/api\/analytics/, ""),
    },
    // Optional PP local API — not ASX/Gmail workers
    "/api": { target: "http://127.0.0.1:3001", changeOrigin: true },
  },
}
```

UI calls e.g. `fetch("/api/analytics/v1/asx/companies")` → Python `GET /v1/asx/companies`.  
Contract: [`../api/presentation-v1.md`](../api/presentation-v1.md).

## Persistence / Connections

- Default: Phone Preview **IndexedDB** (local-first).
- Turso / Duck via Settings → Connections are for **UI workspace** sync — not a replacement for analytics worker stores.
- Prefer **Local only** until a PP API is intentionally running.

## Auth split

| Concern | Host |
|---------|------|
| Shell login / workspaces | Phone Preview |
| Google OAuth (Gmail) | Crawley analytics (redirect URIs on Python) |
| LLM keys | Analytics `.env` only |

“Connect Google” later: Settings deep-link / open analytics OAuth URL — not Vite env secrets.

## Two-process demo

```bash
# A — repo root
uv run python -m crawley

# B
cd crawley-ui && npm run dev
```

Open Vite → **ASX desk** pack → company list + Start scan → job progress from `/v1/jobs/asx-scan`.

## Ownership

| Repo | Owns |
|------|------|
| `a-crawley` | `/v1` JSON, OpenAPI, workers, OAuth, LLM |
| `crawley-ui` | Shell, packs, Connections UX, job controls |
| Shared | OpenAPI + presentation field docs in `a-crawley` |
