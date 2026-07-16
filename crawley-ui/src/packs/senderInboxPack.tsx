import type { FeaturePack } from "@phone-preview/core";
import { useCallback, useEffect, useState } from "react";
import {
  type GmailConnection,
  type JobStatus,
  type SenderDetail,
  type SenderListItem,
  fetchGmailConnection,
  fetchGmailIngestJob,
  fetchHealth,
  fetchSender,
  fetchSenders,
  gmailOAuthStartUrl,
  resetGmailIngest,
  startGmailIngest,
  stopGmailIngest,
} from "../lib/analytics";

function InboxIcon({ className }: { className?: string }) {
  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path
        d="M4 6h16v12H4V6zm0 4l8 5 8-5"
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

function SenderInboxPage() {
  const [senders, setSenders] = useState<SenderListItem[]>([]);
  const [job, setJob] = useState<JobStatus | null>(null);
  const [connection, setConnection] = useState<GmailConnection | null>(null);
  const [selected, setSelected] = useState<string | null>(null);
  const [detail, setDetail] = useState<SenderDetail | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyticsOk, setAnalyticsOk] = useState<boolean | null>(null);
  const [acting, setActing] = useState(false);

  const refreshList = useCallback(async () => {
    const [list, jobStatus, conn] = await Promise.all([
      fetchSenders(),
      fetchGmailIngestJob(),
      fetchGmailConnection(),
    ]);
    setSenders(list.senders);
    setJob(jobStatus);
    setConnection(conn);
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

  const busy = job?.status === "busy" || job?.status === "queued";

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
      return;
    }
    let cancelled = false;
    void fetchSender(selected)
      .then((d) => {
        if (!cancelled) setDetail(d);
      })
      .catch((err: unknown) => {
        if (!cancelled) {
          setDetail(null);
          setError(err instanceof Error ? err.message : "Failed to load sender");
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
      const res = await startGmailIngest(true);
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
      const res = await stopGmailIngest();
      setJob(res.job);
      setActionMessage(res.message);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Stop failed");
    } finally {
      setActing(false);
    }
  }

  async function onReset() {
    setActing(true);
    setActionMessage(null);
    setError(null);
    try {
      const res = await resetGmailIngest();
      setJob(res.job);
      setActionMessage(res.message);
      setSelected(null);
      await refreshList();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Reset failed");
    } finally {
      setActing(false);
    }
  }

  const progressLabel = job
    ? `${job.progress.processed} / ${job.progress.total}`
    : "—";
  const connected = connection?.connected ?? false;
  const oauthHref = connection
    ? gmailOAuthStartUrl(connection.oauth_start_path)
    : gmailOAuthStartUrl("/modules/gmail/oauth/start");

  return (
    <div className="mx-auto max-w-4xl px-4 py-8">
      <header className="border-b border-app-border pb-6">
        <h1 className="text-2xl font-semibold text-app-text">Sender Inbox</h1>
        <p className="mt-2 max-w-2xl text-app-muted">
          Start or stop the Gmail ingest daemon. Analytics scans INBOX, groups by sender, and
          builds per-sender reports. With Local Llama the ingest cap rises to the hard ceiling
          (no 20-message gate). This UI never talks to Gmail or the LLM directly.
        </p>
      </header>

      <section className="mt-6 space-y-3" aria-label="Gmail connection">
        {connected ? (
          <p className="text-sm text-app-muted">Google connected</p>
        ) : (
          <p className="text-sm text-app-muted">
            Google not connected.{" "}
            <a
              href={oauthHref}
              className="underline decoration-app-border underline-offset-2 text-app-text"
              target="_blank"
              rel="noreferrer"
            >
              Connect Google
            </a>{" "}
            on the analytics host, then return here.
          </p>
        )}
        {connection?.error ? (
          <p className="text-sm text-red-600 dark:text-red-400">{connection.error}</p>
        ) : null}
      </section>

      <section className="mt-6 space-y-3" aria-label="Ingest daemon">
        <div className="flex flex-wrap items-center gap-3">
          {!busy ? (
            <button
              type="button"
              className="inline-flex items-center gap-2 rounded-md bg-app-accent px-3 py-1.5 text-sm font-medium text-app-accent-fg disabled:opacity-50"
              disabled={acting || analyticsOk === false}
              onClick={() => void onStart()}
            >
              Start ingest
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
          <button
            type="button"
            className="rounded-md border border-app-border px-3 py-1.5 text-sm text-app-text disabled:opacity-50"
            disabled={acting || busy}
            onClick={() => void onReset()}
          >
            Reset
          </button>
          {busy ? (
            <span className="inline-flex items-center gap-2 text-sm text-app-text">
              <Spinner />
              {job?.status === "queued" ? "Queued" : "Running"} · {progressLabel}
              {job?.progress.current_item ? ` · ${job.progress.current_item}` : ""}
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

      <section className="mt-8" aria-label="Senders">
        <h2 className="text-lg font-medium text-app-text">
          Senders
          {!loading ? (
            <span className="ml-2 text-sm font-normal text-app-muted">
              ({senders.length})
            </span>
          ) : null}
        </h2>
        {loading ? (
          <p className="mt-3 text-sm text-app-muted">Loading…</p>
        ) : senders.length === 0 ? (
          <p className="mt-3 text-sm text-app-muted">
            No senders yet. Connect Google and start ingest to scan INBOX into sender reports.
          </p>
        ) : (
          <ul className="mt-3 divide-y divide-app-border border-y border-app-border">
            {senders.map((s) => {
              const active = selected === s.sender_id;
              return (
                <li key={s.sender_id}>
                  <button
                    type="button"
                    className={`flex w-full items-baseline justify-between gap-4 px-1 py-3 text-left ${
                      active ? "bg-app-surface" : ""
                    }`}
                    onClick={() => setSelected(s.sender_id)}
                  >
                    <span>
                      <span className="font-medium text-app-text">{s.display_name}</span>
                      <span className="ml-2 text-app-muted">{s.from_addr}</span>
                      {s.signals.length > 0 ? (
                        <span className="ml-2 text-xs text-app-muted">
                          {s.signals.join(" · ")}
                        </span>
                      ) : null}
                    </span>
                    <span className="shrink-0 text-sm text-app-muted">
                      {s.message_count} msg
                      {s.open_todos ? ` · ${s.open_todos} todo` : ""}
                      {s.has_profile ? " · report" : ""}
                    </span>
                  </button>
                </li>
              );
            })}
          </ul>
        )}
      </section>

      {detail ? (
        <section className="mt-10 border-t border-app-border pt-8" aria-label="Sender detail">
          <h2 className="text-lg font-medium text-app-text">{detail.display_name}</h2>
          <p className="mt-1 text-sm text-app-muted">
            {detail.from_addr} · {detail.message_count} messages
            {detail.open_todo_count ? ` · ${detail.open_todo_count} open todos` : ""}
          </p>
          {detail.profile.markdown ? (
            <pre className="mt-6 whitespace-pre-wrap font-sans text-sm text-app-text">
              {detail.profile.markdown}
            </pre>
          ) : (
            <p className="mt-6 text-sm text-app-muted">
              Report {detail.profile.status || "empty"}
              {detail.profile.error ? ` — ${detail.profile.error}` : ""}
            </p>
          )}
          {detail.todos.length > 0 ? (
            <ul className="mt-6 space-y-1 text-sm text-app-text">
              {detail.todos.map((t) => (
                <li key={t.id} className={t.done ? "text-app-muted line-through" : ""}>
                  {t.text || "(todo)"}
                </li>
              ))}
            </ul>
          ) : null}
          {detail.messages.length > 0 ? (
            <ul className="mt-8 divide-y divide-app-border border-y border-app-border">
              {detail.messages.slice(0, 20).map((m) => (
                <li key={m.id} className="py-3">
                  <p className="font-medium text-app-text">{m.subject || "(no subject)"}</p>
                  <p className="mt-1 text-sm text-app-muted">{m.snippet}</p>
                  <p className="mt-1 text-xs text-app-muted">
                    {m.internal_date}
                    {m.category ? ` · ${m.category}` : ""}
                    {m.signals.length ? ` · ${m.signals.join(", ")}` : ""}
                  </p>
                </li>
              ))}
            </ul>
          ) : null}
        </section>
      ) : null}
    </div>
  );
}

/** App-private Sender Inbox pack — reads Crawley analytics `/v1/gmail` only. */
export const senderInboxPack: FeaturePack = {
  id: "sender-inbox",
  name: "Sender Inbox",
  description: "Gmail ingest daemon start/stop, senders list, per-sender reports",
  scope: "client",
  defaultEnabled: true,
  requiredPermissions: [],
  page: {
    id: "sender-inbox",
    label: "Sender Inbox",
    title: "Sender Inbox",
    icon: InboxIcon,
    navSection: "content",
    Component: SenderInboxPage,
  },
};
