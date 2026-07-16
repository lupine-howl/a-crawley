import type { FeaturePack } from "@phone-preview/core";
import { useCallback, useEffect, useState } from "react";
import { fetchAlerts, fetchClusters, fetchHoldings, refreshClusters } from "../lib/analytics";

function ThemesIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="2" />
      <path d="M8 12h8M12 8v8" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
    </svg>
  );
}

function ThemesPage() {
  const [clusters, setClusters] = useState<Record<string, unknown> | null>(null);
  const [alerts, setAlerts] = useState<{ open: Record<string, unknown>[]; open_count: number }>({
    open: [],
    open_count: 0,
  });
  const [holdings, setHoldings] = useState<Record<string, unknown>[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const [c, a, h] = await Promise.all([fetchClusters(), fetchAlerts(), fetchHoldings()]);
    setClusters(c);
    setAlerts({ open: a.open || [], open_count: a.open_count || 0 });
    setHoldings(h.holdings || []);
  }, []);

  useEffect(() => {
    void refresh().catch((err: unknown) =>
      setError(err instanceof Error ? err.message : "Failed to load themes desk"),
    );
  }, [refresh]);

  useEffect(() => {
    if (clusters?.status !== "busy") return;
    const id = window.setInterval(() => {
      void fetchClusters()
        .then(setClusters)
        .catch(() => undefined);
    }, 2000);
    return () => window.clearInterval(id);
  }, [clusters?.status]);

  async function onRefreshClusters() {
    setError(null);
    setMessage(null);
    try {
      const res = await refreshClusters();
      setClusters(res);
      setMessage(String(res.message || "Clustering started"));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Cluster refresh failed");
    }
  }

  const themes = (clusters?.themes as Record<string, unknown>[]) || [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">Themes & alerts</h1>
        <p className="mt-2 text-app-muted">
          News theme clusters, open alerts, and holdings journal — not trade signals.
        </p>
      </header>

      <section className="mt-6">
        <div className="flex flex-wrap items-center gap-3">
          <h2 className="text-lg font-medium text-app-text">News themes</h2>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
            disabled={clusters?.status === "busy"}
            onClick={() => void onRefreshClusters()}
          >
            {clusters?.status === "busy" ? "Clustering…" : "Refresh themes"}
          </button>
          <span className="text-sm text-app-muted">
            {String(clusters?.method || "")} · {String(clusters?.status || "idle")}
          </span>
        </div>
        {message ? <p className="mt-2 text-sm text-app-text">{message}</p> : null}
        {themes.length === 0 ? (
          <p className="mt-3 text-sm text-app-muted">No themes yet — scan headlines, then refresh.</p>
        ) : (
          <ul className="mt-4 space-y-4">
            {themes.map((t, i) => (
              <li key={String(t.id || t.title || i)} className="border-b border-app-border pb-3">
                <p className="font-medium text-app-text">{String(t.title || t.name || "Theme")}</p>
                <p className="mt-1 text-sm text-app-muted">
                  {String(t.summary || t.description || "")}
                </p>
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium text-app-text">
          Open alerts{" "}
          <span className="text-sm font-normal text-app-muted">({alerts.open_count})</span>
        </h2>
        {alerts.open.length === 0 ? (
          <p className="mt-2 text-sm text-app-muted">No open alerts.</p>
        ) : (
          <ul className="mt-3 divide-y divide-app-border border-y border-app-border text-sm">
            {alerts.open.map((a, i) => (
              <li key={String(a.id || i)} className="py-2 text-app-text">
                {String(a.message || a.title || JSON.stringify(a))}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="mt-10">
        <h2 className="text-lg font-medium text-app-text">Holdings journal</h2>
        {holdings.length === 0 ? (
          <p className="mt-2 text-sm text-app-muted">
            No journal rows yet (edit via analytics HTMX or a later pack write UI).
          </p>
        ) : (
          <ul className="mt-3 divide-y divide-app-border border-y border-app-border text-sm">
            {holdings.map((h, i) => (
              <li key={String(h.id || i)} className="flex justify-between py-2">
                <span className="text-app-text">{String(h.ticker)}</span>
                <span className="text-app-muted">{String(h.note || h.label || "")}</span>
              </li>
            ))}
          </ul>
        )}
      </section>

      {error ? (
        <p className="mt-6 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export const asxThemesPack: FeaturePack = {
  id: "asx-themes",
  name: "Themes & alerts",
  description: "News themes, alerts, holdings journal",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  page: {
    id: "asx-themes",
    label: "Themes",
    title: "Themes & alerts",
    icon: ThemesIcon,
    navSection: "content",
    Component: ThemesPage,
  },
};
