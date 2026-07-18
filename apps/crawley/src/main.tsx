/**
 * Crawley product host (apps/crawley).
 *
 * Merge into phone-preview monorepo: copy this folder → apps/crawley,
 * copy packages/crawley-* → packages/, add packs to the array below.
 *
 * Platform imports today use `@phone-preview/core` (published). When the
 * upstream monorepo lands `@phone-preview/shell`, swap the import path only.
 */
import "@phone-preview/core/styles.css";
import { Shell, starterPacks } from "@phone-preview/core";
import {
  asxDeskPack,
  asxPortfolioPack,
  asxRecommendationsPack,
  asxThemesPack,
} from "@crawley/asx";
import { senderInboxPack } from "@crawley/inbox";
import { analyticsSettingsPack } from "@crawley/settings";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import brand from "./brand/brand.json";

/** Product packs — portable `@crawley/*` packages only (no app-local pack sources). */
export const crawleyPacks = [
  asxDeskPack,
  senderInboxPack,
  asxRecommendationsPack,
  asxPortfolioPack,
  asxThemesPack,
  analyticsSettingsPack,
];

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Shell
      brand={{ name: brand.name, id: "crawley" }}
      packs={[...starterPacks(), ...crawleyPacks]}
    />
  </StrictMode>,
);
