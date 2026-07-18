import { useEffect, useState, type FormEvent } from "react";
import {
  type LlmSettings,
  fetchLlmModels,
  fetchLlmSettings,
  saveLlmSettings,
  testLlm,
} from "@crawley/analytics-client";

/** Settings toolbar tab — LLM provider / model (Phone Preview systemTab). */
export function LlmSettingsTab() {
  const [settings, setSettings] = useState<LlmSettings | null>(null);
  const [models, setModels] = useState<string[]>([]);
  const [provider, setProvider] = useState<"openai" | "local_llama">("openai");
  const [model, setModel] = useState("");
  const [apiKey, setApiKey] = useState("");
  const [baseUrl, setBaseUrl] = useState("http://127.0.0.1:11434");
  const [timeoutS, setTimeoutS] = useState("60");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [modelsError, setModelsError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function load(refreshModels = false) {
    const [llm, catalog] = await Promise.all([
      fetchLlmSettings(),
      fetchLlmModels(refreshModels),
    ]);
    setSettings(llm);
    setProvider(llm.provider === "local_llama" ? "local_llama" : "openai");
    setModel(llm.model);
    setBaseUrl(llm.base_url || "http://127.0.0.1:11434");
    setTimeoutS(String(llm.timeout_s ?? 60));
    setModels(catalog.models || []);
    setModelsError(catalog.error ? String(catalog.error) : null);
  }

  useEffect(() => {
    void load()
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load LLM settings"),
      )
      .finally(() => setLoading(false));
  }, []);

  async function onSave(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setNotice(null);
    try {
      const saved = await saveLlmSettings({
        provider,
        model,
        api_key: apiKey.trim() || undefined,
        base_url: baseUrl,
        timeout_s: Number(timeoutS) || 60,
      });
      setSettings(saved);
      setApiKey("");
      setNotice(
        saved.provider === "local_llama"
          ? "Saved. Local Llama selected — ASX active set expands to the hard ceiling (no 20-call gate)."
          : "Saved. New requests use this LLM configuration.",
      );
      await load(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    }
  }

  async function onTest() {
    setError(null);
    setNotice(null);
    try {
      const res = await testLlm();
      if (res.ok) setNotice(res.message || "Connection OK");
      else setError(res.message || "Test failed");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Test failed");
    }
  }

  if (loading) {
    return <p className="p-4 text-sm text-app-muted">Loading LLM settings…</p>;
  }

  return (
    <div className="space-y-4 p-4">
      <div>
        <h2 className="text-lg font-semibold text-app-text">Crawley LLM</h2>
        <p className="mt-1 text-sm text-app-muted">
          Analytics host only — keys stay on Python. Status:{" "}
          <span className="text-app-text">{settings?.status_message || "—"}</span>
        </p>
      </div>

      <form className="space-y-3" onSubmit={(e) => void onSave(e)}>
        <label className="block text-sm text-app-muted">
          Provider
          <select
            className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
            value={provider}
            onChange={(e) => setProvider(e.target.value as "openai" | "local_llama")}
          >
            <option value="openai">OpenAI</option>
            <option value="local_llama">Local Llama (Ollama)</option>
          </select>
        </label>

        <label className="block text-sm text-app-muted">
          Model
          {models.length > 0 ? (
            <select
              className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            >
              {models.map((m) => (
                <option key={m} value={m}>
                  {m}
                </option>
              ))}
            </select>
          ) : (
            <input
              className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
              value={model}
              onChange={(e) => setModel(e.target.value)}
            />
          )}
        </label>

        {provider === "openai" ? (
          <label className="block text-sm text-app-muted">
            API key {settings?.has_api_key ? "(stored — leave blank to keep)" : ""}
            <input
              type="password"
              autoComplete="off"
              className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
              value={apiKey}
              onChange={(e) => setApiKey(e.target.value)}
              placeholder={settings?.has_api_key ? "••••••••" : "sk-…"}
            />
          </label>
        ) : (
          <label className="block text-sm text-app-muted">
            Base URL
            <input
              className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
              value={baseUrl}
              onChange={(e) => setBaseUrl(e.target.value)}
            />
          </label>
        )}

        <label className="block text-sm text-app-muted">
          Timeout (seconds)
          <input
            className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
            value={timeoutS}
            onChange={(e) => setTimeoutS(e.target.value)}
          />
        </label>

        <div className="flex flex-wrap gap-2 pt-1">
          <button
            type="submit"
            className="rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg"
          >
            Save
          </button>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text"
            onClick={() => void onTest()}
          >
            Test connection
          </button>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text"
            onClick={() => void load(true).catch((err: unknown) => setError(String(err)))}
          >
            Refresh models
          </button>
        </div>
      </form>

      {modelsError ? <p className="text-sm text-app-muted">{modelsError}</p> : null}
      {notice ? <p className="text-sm text-app-text">{notice}</p> : null}
      {error ? (
        <p className="text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}
