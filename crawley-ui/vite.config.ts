import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

export default defineConfig({
  plugins: [react()],
  optimizeDeps: {
    include: ["sql.js/dist/sql-wasm-browser.js"],
    needsInterop: ["sql.js/dist/sql-wasm-browser.js"],
  },
  server: {
    port: 5173,
    proxy: {
      // Crawley analytics (Python) — UI never holds secrets.
      "/api/analytics": {
        target: "http://127.0.0.1:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api\/analytics/, ""),
      },
      // Optional Phone Preview local API (Connections). Not the analytics brain.
      "/api": {
        target: "http://127.0.0.1:3001",
        changeOrigin: true,
      },
    },
  },
});
