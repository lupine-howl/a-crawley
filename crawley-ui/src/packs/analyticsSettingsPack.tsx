import type { FeaturePack } from "@phone-preview/core";

function LlmIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3a4 4 0 014 4v1h1a3 3 0 010 6h-1v1a4 4 0 11-8 0v-1H7a3 3 0 010-6h1V7a4 4 0 014-4z"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinejoin="round"
      />
    </svg>
  );
}

/**
 * Registers a Phone Preview Settings toolbar tab (systemTab) for Crawley LLM.
 * Open via the Settings / system chrome — not a nav content page.
 */
export const analyticsSettingsPack: FeaturePack = {
  id: "crawley-analytics-settings",
  name: "Crawley LLM",
  description: "LLM provider and model for Crawley analytics",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  systemTab: {
    id: "crawley-llm",
    label: "LLM",
    icon: LlmIcon,
    loadTab: () => import("./LlmSettingsTab").then((m) => ({ default: m.LlmSettingsTab })),
  },
};
