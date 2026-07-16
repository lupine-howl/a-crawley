import "@phone-preview/core/styles.css";
import { Shell, starterPacks } from "@phone-preview/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import brand from "./brand/brand.json";
import { analyticsSettingsPack } from "./packs/analyticsSettingsPack";
import { asxDeskPack } from "./packs/asxDeskPack";
import { asxPortfolioPack } from "./packs/asxPortfolioPack";
import { asxRecommendationsPack } from "./packs/asxRecommendationsPack";
import { asxThemesPack } from "./packs/asxThemesPack";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Shell
      brand={{ name: brand.name, id: "crawley-ui" }}
      packs={[
        ...starterPacks(),
        asxDeskPack,
        asxRecommendationsPack,
        asxPortfolioPack,
        asxThemesPack,
        analyticsSettingsPack,
      ]}
    />
  </StrictMode>,
);
