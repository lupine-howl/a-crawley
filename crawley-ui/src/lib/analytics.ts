/**
 * Crawley analytics client — browser calls go through the Vite proxy
 * `/api/analytics` → analytics host (no secrets in this app).
 */

const BASE = "/api/analytics";

export type CompanyListItem = {
  ticker: string;
  name: string;
  sector: string;
  scan_status: string;
  change_pct: number | null;
  move: string;
  sentiment: string;
  scanned_at: string;
  error: string;
};

export type CompanyListResponse = {
  companies: CompanyListItem[];
  count: number;
  active_set_size: number;
};

export type CompanyDetail = {
  ticker: string;
  name: string;
  sector: string;
  scan_status: string;
  snapshot: {
    price: number | null;
    change_pct: number | null;
    volume: number | null;
    currency: string;
    sentiment: string;
    headline: string;
    as_of: string;
    gaps: string[];
  };
  move: string;
  headlines: { title: string; url: string; source: string }[];
  sources_used: string[];
  profile: {
    status: string;
    markdown: string;
    error: string;
    updated_at: string;
  };
  disclaimer: string;
};

export type JobStatus = {
  id: string;
  kind: string;
  status: "idle" | "busy" | "paused" | "done" | "error";
  message: string;
  error: string;
  progress: {
    processed: number;
    total: number;
    remaining: number;
    current_ticker: string;
  };
  updated_at: string;
  pause_requested: boolean;
};

export type ScanActionResponse = {
  ok: boolean;
  message: string;
  job: JobStatus;
};

export type LlmSettings = {
  provider: string;
  model: string;
  base_url: string;
  timeout_s: number;
  has_api_key: boolean;
  status_ok: boolean;
  status_message: string;
};

async function readJson<T>(res: Response): Promise<T> {
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`;
    try {
      const body = (await res.json()) as { detail?: string };
      if (body?.detail) detail = String(body.detail);
    } catch {
      /* ignore */
    }
    throw new Error(detail);
  }
  return (await res.json()) as T;
}

export async function fetchHealth(): Promise<{ ok: boolean; service?: string }> {
  const res = await fetch(`${BASE}/health`);
  return readJson(res);
}

export async function fetchCompanies(): Promise<CompanyListResponse> {
  const res = await fetch(`${BASE}/v1/asx/companies`);
  return readJson(res);
}

export async function fetchCompany(ticker: string): Promise<CompanyDetail> {
  const res = await fetch(`${BASE}/v1/asx/companies/${encodeURIComponent(ticker)}`);
  return readJson(res);
}

export async function fetchAsxScanJob(): Promise<JobStatus> {
  const res = await fetch(`${BASE}/v1/jobs/asx-scan`);
  return readJson(res);
}

export async function startAsxScan(force = true): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ force }),
  });
  return readJson(res);
}

export async function stopAsxScan(): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/stop`, { method: "POST" });
  return readJson(res);
}

export async function pauseAsxScan(): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/pause`, { method: "POST" });
  return readJson(res);
}

export async function resumeAsxScan(): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/resume`, { method: "POST" });
  return readJson(res);
}

export async function resetAsxScan(): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/reset`, { method: "POST" });
  return readJson(res);
}

export async function fetchRecommendations(): Promise<{
  rows: Record<string, unknown>[];
  status: string;
  error: string;
  updated_at: string;
}> {
  const res = await fetch(`${BASE}/v1/asx/recommendations`);
  return readJson(res);
}

export async function refreshRecommendations(): Promise<{
  ok: boolean;
  message: string;
  rows: Record<string, unknown>[];
  status: string;
}> {
  const res = await fetch(`${BASE}/v1/asx/recommendations/refresh`, { method: "POST" });
  return readJson(res);
}

export async function fetchPortfolio(): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/v1/asx/portfolio`);
  return readJson(res);
}

export async function paperTrade(body: {
  ticker: string;
  side: "buy" | "sell";
  qty: number;
  price?: number | null;
  note?: string;
}): Promise<{ ok: boolean; message: string; portfolio: Record<string, unknown> }> {
  const res = await fetch(`${BASE}/v1/asx/portfolio/trade`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJson(res);
}

export async function fetchClusters(): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/v1/asx/clusters`);
  return readJson(res);
}

export async function refreshClusters(): Promise<Record<string, unknown>> {
  const res = await fetch(`${BASE}/v1/asx/clusters/refresh`, { method: "POST" });
  return readJson(res);
}

export async function fetchAlerts(): Promise<{
  rules: Record<string, unknown>[];
  open: Record<string, unknown>[];
  open_count: number;
}> {
  const res = await fetch(`${BASE}/v1/asx/alerts`);
  return readJson(res);
}

export async function fetchHoldings(): Promise<{
  holdings: Record<string, unknown>[];
  count: number;
}> {
  const res = await fetch(`${BASE}/v1/asx/holdings`);
  return readJson(res);
}

export async function fetchNotebook(ticker: string): Promise<{
  ticker: string;
  thesis: string;
  notes: string;
  updated_at: string;
}> {
  const res = await fetch(
    `${BASE}/v1/asx/companies/${encodeURIComponent(ticker)}/notebook`,
  );
  return readJson(res);
}

export async function saveNotebook(
  ticker: string,
  body: { thesis: string; notes: string },
): Promise<{ ticker: string; thesis: string; notes: string; updated_at: string }> {
  const res = await fetch(
    `${BASE}/v1/asx/companies/${encodeURIComponent(ticker)}/notebook`,
    {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    },
  );
  return readJson(res);
}

export async function fetchLlmSettings(): Promise<LlmSettings> {
  const res = await fetch(`${BASE}/v1/settings/llm`);
  return readJson(res);
}

export async function saveLlmSettings(body: {
  provider: "openai" | "local_llama";
  model: string;
  api_key?: string;
  base_url?: string;
  timeout_s?: number;
}): Promise<LlmSettings> {
  const res = await fetch(`${BASE}/v1/settings/llm`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  return readJson(res);
}

export async function testLlm(): Promise<{ ok: boolean; message?: string; state?: string }> {
  const res = await fetch(`${BASE}/v1/settings/llm/test`, { method: "POST" });
  return readJson(res);
}

export async function fetchLlmModels(refresh = false): Promise<{
  models: string[];
  error?: string | null;
  provider: string;
}> {
  const res = await fetch(
    `${BASE}/v1/settings/llm/models${refresh ? "?refresh=true" : ""}`,
  );
  return readJson(res);
}
