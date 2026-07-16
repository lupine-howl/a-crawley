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
  pauseAsxScan,
  resetAsxScan,
  resumeAsxScan,
  startAsxScan,
} from "../lib/analytics";

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

function AsxDeskPage() {
  const [companies, setCompanies] = useState<CompanyListItem[]>([]);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<CompanyDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsOk, setAnalyticsOk] = useState<boolean | null>(null);

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

  useEffect(() => {
    if (job?.status !== "busy") return;
    const id = window.setInterval(() => {
      void refreshList().catch((err: unknown) => {
        setError(err instanceof Error ? err.message : "Job poll failed");
      });
    }, 2000);
    return () => window.clearInterval(id);
  }, [job?.status, refreshList]);

  useEffect(() => {
    if (!selected) {
      setDetail(null);
      return;
    }
    let cancelled = false;
    void fetchCompany(selected)
      .then((d) => {
        if (!cancelled) setDetail(d);
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

  async function runAction(action: "start" | "pause" | "resume" | "reset") {
    setActionMessage(null);
    setError(null);
    try {
      const fn =
        action === "start"
          ? startAsxScan
          : action === "pause"
            ? pauseAsxScan
            : action === "resume"
              ? resumeAsxScan
              : resetAsxScan;
      const res = await fn();
      setJob(res.job);
      setActionMessage(res.message);
      // Failed start (e.g. already scanned) — show once as guidance, not as a hard error.
      if (!res.ok && action === "start") {
        setActionMessage(res.message);
      } else if (!res.ok) {
        setError(res.message);
      }
      if (action === "reset") {
        setSelected(null);
        setDetail(null);
      }
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Scan action failed");
    }
  }

  const busy = job?.status === "busy";
  const scanComplete =
    job?.status === "done" ||
    (job != null &&
      job.progress.total > 0 &&
      job.progress.processed >= job.progress.total &&
      job.status !== "busy");
  const progressLabel = job
    ? `${job.progress.processed} / ${job.progress.total}`
    : "—";

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">ASX desk</h1>
        <p className="mt-2 max-w-2xl text-app-muted">
          Active-set companies from Crawley analytics. Start a scan; this UI never talks to Yahoo
          or the LLM directly.
        </p>
      </header>

      <section className="mt-6 space-y-3" aria-label="Scan controls">
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            className="rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg disabled:opacity-50"
            disabled={busy || analyticsOk === false || scanComplete}
            onClick={() => void runAction("start")}
          >
            Start scan
          </button>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
            disabled={!busy}
            onClick={() => void runAction("pause")}
          >
            Pause
          </button>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
            disabled={busy || job?.status !== "paused"}
            onClick={() => void runAction("resume")}
          >
            Resume
          </button>
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
            disabled={busy || analyticsOk === false}
            onClick={() => void runAction("reset")}
            title="Clear PoC scan and profile data so you can scan again"
          >
            Reset
          </button>
          <p className="text-sm text-app-muted">
            Job <span className="text-app-text">{job?.status ?? "…"}</span>
            {" · "}
            {progressLabel}
            {job?.progress.current_ticker
              ? ` · ${job.progress.current_ticker}`
              : ""}
          </p>
        </div>
        {job?.message ? <p className="text-sm text-app-muted">{job.message}</p> : null}
        {actionMessage && actionMessage !== job?.message ? (
          <p className="text-sm text-app-text">{actionMessage}</p>
        ) : null}
        {scanComplete && !busy ? (
          <p className="text-sm text-app-muted">
            Active set already scanned. Use <span className="text-app-text">Reset</span> to clear
            PoC data, then Start scan again.
          </p>
        ) : null}
        {analyticsOk === false ? (
          <p className="text-sm text-red-600 dark:text-red-400">
            Analytics offline — run <code className="text-app-text">uv run python -m crawley</code>{" "}
            (proxy <code className="text-app-text">/api/analytics</code> → :8000).
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
            Active set is empty. Configure tickers on the analytics host, then refresh.
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
                      {c.error ? " · error" : ""}
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
              {detail.snapshot.as_of ? (
                <span className="ml-2 text-sm text-app-muted">as of {detail.snapshot.as_of}</span>
              ) : null}
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
              {detail.profile.error ? ` — ${detail.profile.error}` : ""}
            </p>
          )}
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
  description: "Active-set companies, scan control, and company detail via analytics API",
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
