import type { FeaturePack } from "@phone-preview/core";
import { useCallback, useEffect, useState } from "react";
import { fetchRecommendations, paperTrade, refreshRecommendations } from "@crawley/analytics-client";

function RecIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M12 3v18M5 10l7-7 7 7"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function RecommendationsPage() {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [status, setStatus] = useState("idle");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    const data = await fetchRecommendations();
    setRows(data.rows || []);
    setStatus(data.status || "idle");
    if (data.error) setError(data.error);
  }, []);

  useEffect(() => {
    void refresh()
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load recommendations"),
      )
      .finally(() => setLoading(false));
  }, [refresh]);

  useEffect(() => {
    if (status !== "busy") return;
    const id = window.setInterval(() => {
      void refresh().catch(() => undefined);
    }, 2000);
    return () => window.clearInterval(id);
  }, [status, refresh]);

  async function onRefresh() {
    setError(null);
    setMessage(null);
    try {
      const res = await refreshRecommendations();
      setRows(res.rows || []);
      setStatus(res.status || "idle");
      setMessage(res.message);
      if (!res.ok) setError(res.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Refresh failed");
    }
  }

  async function onPaperBuy(ticker: string) {
    setError(null);
    try {
      const res = await paperTrade({ ticker, side: "buy", qty: 10 });
      setMessage(res.message);
      if (!res.ok) setError(res.message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Trade failed");
    }
  }

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">Recommendations</h1>
        <p className="mt-2 text-app-muted">
          Desk suggestions from analytics — paper only, not licensed advice or live orders.
        </p>
      </header>
      <div className="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          className="rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg disabled:opacity-50"
          disabled={status === "busy"}
          onClick={() => void onRefresh()}
        >
          {status === "busy" ? "Refreshing…" : "Refresh recommendations"}
        </button>
        <span className="text-sm text-app-muted">Status: {status}</span>
      </div>
      {message ? <p className="mt-3 text-sm text-app-text">{message}</p> : null}
      {error ? (
        <p className="mt-3 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}
      {loading ? (
        <p className="mt-6 text-sm text-app-muted">Loading…</p>
      ) : rows.length === 0 ? (
        <p className="mt-6 text-sm text-app-muted">
          No recommendations yet — scan companies and refresh.
        </p>
      ) : (
        <ul className="mt-6 divide-y divide-app-border border-y border-app-border">
          {rows.map((row, i) => {
            const ticker = String(row.ticker || row.symbol || `row-${i}`);
            const title = String(row.title || row.action || row.summary || "");
            const rationale = String(row.rationale || row.reason || row.brief || "");
            return (
              <li key={`${ticker}-${i}`} className="flex flex-wrap items-start justify-between gap-3 py-3">
                <div>
                  <p className="font-medium text-app-text">
                    {ticker}
                    {title ? <span className="ml-2 font-normal text-app-muted">{title}</span> : null}
                  </p>
                  {rationale ? (
                    <p className="mt-1 max-w-2xl text-sm text-app-muted">{rationale}</p>
                  ) : null}
                </div>
                <button
                  type="button"
                  className="rounded-md border border-app-border px-2 py-1 text-sm text-app-text"
                  onClick={() => void onPaperBuy(ticker)}
                >
                  Paper buy 10
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

export const asxRecommendationsPack: FeaturePack = {
  id: "asx-recommendations",
  name: "Recommendations",
  description: "ASX desk recommendations + paper buy shortcut",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  page: {
    id: "asx-recommendations",
    label: "Recommendations",
    title: "Recommendations",
    icon: RecIcon,
    navSection: "content",
    Component: RecommendationsPage,
  },
};
