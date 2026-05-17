import type { TrackType } from "@/lib/schemas/agents";
import { dataStatusSchema, type DataStatus } from "@/lib/schemas/data";
import {
  intakeFormSchema,
  type IntakeForm,
} from "@/lib/schemas/intake";
import {
  planResponseSchema,
  type PlanResponse,
} from "@/lib/schemas/plan";

const API_BASE =
  process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") ?? "http://localhost:8000";

export type HealthResponse = {
  status: string;
  app: string;
  supabase_configured: boolean;
};

async function apiGet<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, { next: { revalidate: 0 } });
  if (!res.ok) {
    throw new Error(`API request failed: ${path} (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export async function fetchHealth(): Promise<HealthResponse> {
  return apiGet<HealthResponse>("/api/health");
}

export async function fetchDataStatus(): Promise<DataStatus> {
  const data = await apiGet<DataStatus>("/api/data/status");
  return dataStatusSchema.parse(data);
}

export type IntakeCreateResponse = {
  submission_id: string;
  status: string;
  created_at: string;
};

export type IntakeGetResponse = {
  submission_id: string;
  status: string;
  created_at: string;
  form_data: IntakeForm;
};

async function parseApiError(res: Response): Promise<string> {
  try {
    const body = (await res.json()) as { detail?: string | { msg: string }[] };
    if (typeof body.detail === "string") return body.detail;
    if (Array.isArray(body.detail)) {
      return body.detail.map((d) => d.msg).join("; ");
    }
  } catch {
    /* fall through */
  }
  return `Request failed (${res.status})`;
}

async function apiPost<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }
  return res.json() as Promise<T>;
}

export async function submitIntake(
  form: IntakeForm,
): Promise<IntakeCreateResponse> {
  intakeFormSchema.parse(form);
  return apiPost<IntakeCreateResponse>("/api/intake", form);
}

export async function fetchIntake(
  submissionId: string,
): Promise<IntakeGetResponse> {
  const data = await apiGet<IntakeGetResponse>(`/api/intake/${submissionId}`);
  return { ...data, form_data: intakeFormSchema.parse(data.form_data) };
}

async function apiClient<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    cache: "no-store",
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });
  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }
  return res.json() as Promise<T>;
}

export async function fetchPlan(planId: string): Promise<PlanResponse> {
  const data = await apiClient<PlanResponse>(`/api/plans/${planId}`);
  return planResponseSchema.parse(data);
}

export async function fetchPlanByIntake(
  intakeId: string,
): Promise<PlanResponse> {
  const data = await apiClient<PlanResponse>(
    `/api/plans/by-intake/${intakeId}`,
  );
  return planResponseSchema.parse(data);
}

export async function startPlan(intakeId: string): Promise<PlanResponse> {
  const data = await apiClient<PlanResponse>(
    `/api/plans/start/${intakeId}`,
    { method: "POST" },
  );
  return planResponseSchema.parse(data);
}

export async function selectPlanTrack(
  planId: string,
  trackType: TrackType,
): Promise<PlanResponse> {
  const data = await apiClient<PlanResponse>(`/api/plans/${planId}/track`, {
    method: "PATCH",
    body: JSON.stringify({ track_type: trackType }),
  });
  return planResponseSchema.parse(data);
}

export async function downloadPlanPdf(plan: PlanResponse): Promise<void> {
  const isDemo = plan.plan_id === "demo";
  const url = isDemo
    ? `${API_BASE}/api/plans/export-pdf`
    : `${API_BASE}/api/plans/${encodeURIComponent(plan.plan_id)}/export.pdf`;

  const res = await fetch(url, {
    method: isDemo ? "POST" : "GET",
    cache: "no-store",
    headers: isDemo ? { "Content-Type": "application/json" } : undefined,
    body: isDemo ? JSON.stringify(plan) : undefined,
  });

  if (!res.ok) {
    throw new Error(await parseApiError(res));
  }

  const blob = await res.blob();
  const disposition = res.headers.get("Content-Disposition");
  let filename = "mission-plan.pdf";
  const match = disposition?.match(/filename="([^"]+)"/);
  if (match?.[1]) filename = match[1];

  const objectUrl = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = objectUrl;
  anchor.download = filename;
  anchor.click();
  URL.revokeObjectURL(objectUrl);
}

export { API_BASE };
export type { PlanResponse };
