import type { FeaturePack } from "@phone-preview/core";
import { useCallback, useEffect, useState, type FormEvent } from "react";
import { fetchPortfolio, paperTrade } from "../lib/analytics";

function PortIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <rect x="3" y="6" width="18" height="14" rx="2" stroke="currentColor" strokeWidth="2" />
      <path d="M3 10h18" stroke="currentColor" strokeWidth="2" />
    </svg>
  );
}

function PortfolioPage() {
  const [data, setData] = useState<Record<string, unknown> | null>(null);
  const [ticker, setTicker] = useState("CBA");
  const [qty, setQty] = useState("10");
  const [side, setSide] = useState<"buy" | "sell">("buy");
  const [error, setError] = useState<string | null>(null);
  const [message, setMessage] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setData(await fetchPortfolio());
  }, []);

  useEffect(() => {
    void refresh().catch((err: unknown) =>
      setError(err instanceof Error ? err.message : "Failed to load portfolio"),
    );
  }, [refresh]);

  async function onTrade(event: FormEvent) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    try {
      const res = await paperTrade({
        ticker,
        side,
        qty: Number(qty) || 0,
      });
      setMessage(res.message);
      if (!res.ok) setError(res.message);
      setData(res.portfolio);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Trade failed");
    }
  }

  const positions = (data?.positions as Record<string, unknown>[]) || [];
  const ledger = (data?.ledger as Record<string, unknown>[]) || [];

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">Paper portfolio</h1>
        <p className="mt-2 text-app-muted">
          Simulation ledger only — {String(data?.broker_label || "Paper")}. No brokerage orders.
        </p>
      </header>

      <section className="mt-6 grid gap-4 sm:grid-cols-3">
        <div>
          <p className="text-sm text-app-muted">Cash</p>
          <p className="text-lg text-app-text">
            {String(data?.currency || "AUD")} {Number(data?.cash ?? 0).toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-sm text-app-muted">Equity MTM</p>
          <p className="text-lg text-app-text">{Number(data?.equity_mtm ?? 0).toFixed(2)}</p>
        </div>
        <div>
          <p className="text-sm text-app-muted">Unrealized PnL</p>
          <p className="text-lg text-app-text">{Number(data?.total_pnl ?? 0).toFixed(2)}</p>
        </div>
      </section>

      <form className="mt-8 flex flex-wrap items-end gap-3" onSubmit={(e) => void onTrade(e)}>
        <label className="text-sm text-app-muted">
          Ticker
          <input
            className="mt-1 block w-28 rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
            value={ticker}
            onChange={(e) => setTicker(e.target.value.toUpperCase())}
          />
        </label>
        <label className="text-sm text-app-muted">
          Side
          <select
            className="mt-1 block rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
            value={side}
            onChange={(e) => setSide(e.target.value as "buy" | "sell")}
          >
            <option value="buy">Buy</option>
            <option value="sell">Sell</option>
          </select>
        </label>
        <label className="text-sm text-app-muted">
          Qty
          <input
            className="mt-1 block w-24 rounded-md border border-app-border bg-app-surface px-2 py-1.5 text-app-text"
            value={qty}
            onChange={(e) => setQty(e.target.value)}
          />
        </label>
        <button
          type="submit"
          className="rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg"
        >
          Record paper trade
        </button>
      </form>
      {message ? <p className="mt-3 text-sm text-app-text">{message}</p> : null}
      {error ? (
        <p className="mt-3 text-sm text-red-600 dark:text-red-400" role="alert">
          {error}
        </p>
      ) : null}

      <h2 className="mt-10 text-lg font-medium text-app-text">Positions</h2>
      {positions.length === 0 ? (
        <p className="mt-2 text-sm text-app-muted">No positions yet.</p>
      ) : (
        <ul className="mt-3 divide-y divide-app-border border-y border-app-border">
          {positions.map((p) => (
            <li key={String(p.ticker)} className="flex justify-between py-2 text-sm">
              <span className="text-app-text">{String(p.ticker)}</span>
              <span className="text-app-muted">
                qty {Number(p.qty)} · avg {Number(p.avg).toFixed(2)} · last{" "}
                {p.last == null ? "—" : Number(p.last).toFixed(2)} · pnl{" "}
                {p.pnl == null ? "—" : Number(p.pnl).toFixed(2)}
              </span>
            </li>
          ))}
        </ul>
      )}

      <h2 className="mt-10 text-lg font-medium text-app-text">Ledger</h2>
      {ledger.length === 0 ? (
        <p className="mt-2 text-sm text-app-muted">No trades yet.</p>
      ) : (
        <ul className="mt-3 divide-y divide-app-border border-y border-app-border text-sm">
          {ledger.slice(0, 20).map((e, i) => (
            <li key={String(e.id || i)} className="flex justify-between py-2 text-app-muted">
              <span>
                {String(e.at)} · {String(e.side)} {String(e.ticker)} × {Number(e.qty)}
              </span>
              <span>@{Number(e.price).toFixed(2)}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export const asxPortfolioPack: FeaturePack = {
  id: "asx-portfolio",
  name: "Paper portfolio",
  description: "Paper portfolio simulation",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  page: {
    id: "asx-portfolio",
    label: "Paper portfolio",
    title: "Paper portfolio",
    icon: PortIcon,
    navSection: "content",
    Component: PortfolioPage,
  },
};
