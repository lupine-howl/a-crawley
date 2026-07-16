import "@phone-preview/core/styles.css";
import { Shell, starterPacks } from "@phone-preview/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import brand from "./brand/brand.json";
import { asxDeskPack } from "./packs/asxDeskPack";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <Shell
      brand={{ name: brand.name, id: "crawley-ui" }}
      packs={[...starterPacks(), asxDeskPack]}
    />
  </StrictMode>,
);
