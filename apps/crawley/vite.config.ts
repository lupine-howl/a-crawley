import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import path from "node:path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    dedupe: ["react", "react-dom", "@phone-preview/core"],
    alias: {
      // Workspace source packages (TypeScript, no prebuild).
      "@crawley/analytics-client": path.resolve(
        __dirname,
        "../../packages/crawley-analytics-client/src/index.ts",
      ),
      "@crawley/asx": path.resolve(__dirname, "../../packages/crawley-asx/src/index.ts"),
      "@crawley/inbox": path.resolve(__dirname, "../../packages/crawley-inbox/src/index.ts"),
      "@crawley/settings": path.resolve(
        __dirname,
        "../../packages/crawley-settings/src/index.ts",
      ),
    },
  },
  optimizeDeps: {
    include: ["sql.js/dist/sql-wasm-browser.js"],
    needsInterop: ["sql.js/dist/sql-wasm-browser.js"],
  },
  server: {
    port: 5173,
    proxy: {
      "/api/analytics": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api\/analytics/, ""),
      },
      "/api": {
        target: "http://127.0.0.1:3001",
        changeOrigin: true,
      },
    },
  },
});
