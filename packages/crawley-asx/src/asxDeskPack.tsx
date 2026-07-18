import type { FeaturePack } from "@phone-preview/core";
import { useCallback, useEffect, useState } from "react";
import {
  type CompanyDetail,
  type CompanyListItem,
  type JobStatus,
  fetchAsxScanJob,
  fetchCompanies,
  fetchCompany,
  fetchHealth,
  fetchNotebook,
  saveNotebook,
  startAsxScan,
  stopAsxScan,
} from "@crawley/analytics-client";

function AsxIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 18V6M4 18h16M8 14l3-4 3 2 4-6"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

function Spinner({ className }: { className?: string }) {
  return (
    <svg
      className={`animate-spin ${className ?? "h-4 w-4"}`}
      viewBox="0 0 24 24"
      fill="none"
      aria-hidden
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"
      />
    </svg>
  );
}

function AsxDeskPage() {
  const [companies, setCompanies] = useState<CompanyListItem[]>([]);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<CompanyDetail | null>(null);
  const [thesis, setThesis] = useState("");
  const [notes, setNotes] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsOk, setAnalyticsOk] = useState<boolean | null>(null);
  const [acting, setActing] = useState(false);

  const refreshList = useCallback(async () => {
    const [list, jobStatus] = await Promise.all([fetchCompanies(), fetchAsxScanJob()]);
    setCompanies(list.companies);
    setJob(jobStatus);
  }, []);

  useEffect(() => {
    let cancelled = false;
    void (async () => {
      setLoading(true);
      setError(null);
      try {
        const health = await fetchHealth();
        if (cancelled) return;
        setAnalyticsOk(Boolean(health.ok));
        await refreshList();
      } catch (err) {
        if (!cancelled) {
          setAnalyticsOk(false);
          setError(
            err instanceof Error
              ? err.message
              : "Cannot reach Crawley analytics. Start the Python process and check the Vite proxy.",
          );
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [refreshList]);

  const busy = job?.status === "busy";

  useEffect(() => {
    if (!busy) return;
    const id = window.setInterval(() => {
      void refreshList().catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Job poll failed");
      });
    }, 1500);
    return () => window.clearInterval(id);
  }, [busy, refreshList]);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      setThesis("");
      setNotes("");
      return;
    }
    let cancelled = false;
    void Promise.all([fetchCompany(selected), fetchNotebook(selected)])
      .then(([d, nb]) => {
        if (cancelled) return;
        setDetail(d);
        setThesis(nb.thesis);
        setNotes(nb.notes);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setDetail(null);
          setError(err instanceof Error ? err.message : "Failed to load company");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [selected, job?.progress.processed]);

  async function onStart() {
    setActing(true);
    setActionMessage(null);
    setError(null);
    try {
      const res = await startAsxScan(true);
      setJob(res.job);
      setActionMessage(res.message);
      if (!res.ok) setError(res.message);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Start failed");
    } finally {
      setActing(false);
    }
  }

  async function onStop() {
    setActing(true);
    setActionMessage(null);
    setError(null);
    try {
      const res = await stopAsxScan();
      setJob(res.job);
      setActionMessage(res.message);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Stop failed");
    } finally {
      setActing(false);
    }
  }

  async function onSaveNotebook() {
    if (!selected) return;
    setError(null);
    try {
      const nb = await saveNotebook(selected, { thesis, notes });
      setActionMessage(`Notebook saved ${nb.updated_at || ""}`.trim());
    } catch (err) {
      setError(err instanceof Error ? err.message : "Notebook save failed");
    }
  }

  const progressLabel = job
    ? `${job.progress.processed} / ${job.progress.total}`
    : "—";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">ASX desk</h1>
        <p className="mt-2 max-w-2xl text-app-muted">
          Start or stop the analytics scan daemon. With Local Llama the active set expands toward
          the universe ceiling (no 20-call gate). This UI never talks to Yahoo or the LLM
          directly.
        </p>
      </header>

      <section className="mt-6 space-y-3" aria-label="Scan daemon">
        <div className="flex flex-wrap items-center gap-3">
          {!busy ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg disabled:opacity-50"
              disabled={acting || analyticsOk === false}
              onClick={() => void onStart()}
            >
              Start scan
            </button>
          ) : (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
              disabled={acting}
              onClick={() => void onStop()}
            >
              <Spinner />
              Stop
            </button>
          )}
          {busy ? (
            <span className="inline-flex items-center gap-2 text-sm text-app-text">
              <Spinner />
              Running · {progressLabel}
              {job?.progress.current_ticker ? ` · ${job.progress.current_ticker}` : ""}
            </span>
          ) : (
            <p className="text-sm text-app-muted">
              Job <span className="text-app-text">{job?.status ?? "…"}</span>
              {" · "}
              {progressLabel}
            </p>
          )}
        </div>
        {job?.message ? <p className="text-sm text-app-muted">{job.message}</p> : null}
        {actionMessage && actionMessage !== job?.message ? (
          <p className="text-sm text-app-text">{actionMessage}</p>
        ) : null}
        {analyticsOk === false ? (
          <p className="text-sm text-red-600 dark:text-red-400">
            Analytics offline — run <code className="text-app-text">uv run python -m crawley</code>.
          </p>
        ) : null}
        {error ? (
          <p className="text-sm text-red-600 dark:text-red-400" role="alert">
            {error}
          </p>
        ) : null}
      </section>

      <section className="mt-8" aria-label="Companies">
        <h2 className="text-lg font-medium text-app-text">
          Companies
          {!loading ? (
            <span className="ml-2 text-sm font-normal text-app-muted">
              ({companies.length} in active set)
            </span>
          ) : null}
        </h2>
        {loading ? (
          <p className="mt-3 text-sm text-app-muted">Loading…</p>
        ) : companies.length === 0 ? (
          <p className="mt-3 text-sm text-app-muted">
            Active set is empty. Switch to Local Llama in Settings → LLM (or start a scan) to pad
            from the universe.
          </p>
        ) : (
          <ul className="mt-3 divide-y divide-app-border border-y border-app-border">
            {companies.map((c) => {
              const active = selected === c.ticker;
              return (
                <li key={c.ticker}>
                  <button
                    type="button"
                    className={`flex w-full items-baseline justify-between gap-4 px-1 py-3 text-left ${
                      active ? "bg-app-surface" : ""
                    }`}
                    onClick={() => setSelected(c.ticker)}
                  >
                    <span>
                      <span className="font-medium text-app-text">{c.ticker}</span>
                      <span className="ml-2 text-app-muted">{c.name}</span>
                    </span>
                    <span className="shrink-0 text-sm text-app-muted">
                      {c.move} · {c.scan_status}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      {detail ? (
        <section className="mt-10 border-t border-app-border pt-8" aria-label="Company detail">
          <h2 className="text-lg font-medium text-app-text">
            {detail.ticker}{" "}
            <span className="font-normal text-app-muted">{detail.name}</span>
          </h2>
          <p className="mt-1 text-sm text-app-muted">
            {detail.sector} · {detail.move} · {detail.snapshot.sentiment} · scan{" "}
            {detail.scan_status}
          </p>
          {detail.snapshot.price != null ? (
            <p className="mt-3 text-app-text">
              {detail.snapshot.currency} {detail.snapshot.price}
            </p>
          ) : (
            <p className="mt-3 text-sm text-app-muted">No price yet — run a scan.</p>
          )}
          {detail.headlines.length > 0 ? (
            <ul className="mt-4 list-disc space-y-1 pl-5 text-sm text-app-text">
              {detail.headlines.slice(0, 8).map((h, i) => (
                <li key={`${h.title}-${i}`}>
                  {h.url ? (
                    <a
                      href={h.url}
                      target="_blank"
                      rel="noreferrer"
                      className="underline decoration-app-border underline-offset-2"
                    >
                      {h.title}
                    </a>
                  ) : (
                    h.title
                  )}
                </li>
              ))}
            </ul>
          ) : null}
          {detail.profile.markdown ? (
            <pre className="mt-6 whitespace-pre-wrap font-sans text-sm text-app-text">
              {detail.profile.markdown}
            </pre>
          ) : (
            <p className="mt-6 text-sm text-app-muted">
              Profile {detail.profile.status || "empty"}
            </p>
          )}

          <div className="mt-8 space-y-3 border-t border-app-border pt-6">
            <h3 className="text-base font-medium text-app-text">Research notebook</h3>
            <label className="block text-sm text-app-muted">
              Thesis
              <textarea
                className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-3 py-2 text-app-text"
                rows={3}
                value={thesis}
                onChange={(e) => setThesis(e.target.value)}
              />
            </label>
            <label className="block text-sm text-app-muted">
              Notes
              <textarea
                className="mt-1 w-full rounded-md border border-app-border bg-app-surface px-3 py-2 text-app-text"
                rows={4}
                value={notes}
                onChange={(e) => setNotes(e.target.value)}
              />
            </label>
            <button
              type="button"
              className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text"
              onClick={() => void onSaveNotebook()}
            >
              Save notebook
            </button>
          </div>
          <p className="mt-8 text-xs text-app-muted">{detail.disclaimer}</p>
        </section>
      ) : null}
    </div>
  );
}

/** App-private ASX desk pack — reads Crawley analytics `/v1` only. */
export const asxDeskPack: FeaturePack = {
  id: "asx-desk",
  name: "ASX desk",
  description: "Active-set companies, scan daemon start/stop, company detail + notebook",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  page: {
    id: "asx-desk",
    label: "ASX desk",
    title: "ASX desk",
    icon: AsxIcon,
    navSection: "content",
    Component: AsxDeskPage,
  },
};
