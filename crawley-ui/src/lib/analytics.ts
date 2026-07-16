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

export async function startAsxScan(): Promise<ScanActionResponse> {
  const res = await fetch(`${BASE}/v1/asx/scan/start`, { method: "POST" });
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
