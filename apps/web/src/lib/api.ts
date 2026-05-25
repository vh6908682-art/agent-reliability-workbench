export const DEFAULT_INCIDENT_PROMPT =
  "A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.";

export type ContextSource = {
  source_path?: string;
  title?: string;
  document_type?: string;
  relevance_score?: number;
};

export type IncidentDiagnosis = {
  likely_cause?: string;
  evidence?: string[];
  recommended_next_steps?: string[];
  prevention?: string[];
  confidence?: string;
};

export type AgentRunResponse = {
  run_id?: number | null;
  task?: string;
  answer?: string;
  structured_output?: IncidentDiagnosis | Record<string, unknown> | null;
  validation_status?: string | null;
  context_sources?: ContextSource[];
};

type ApiErrorDetail = {
  detail?: {
    error?: string;
    message?: string;
    details?: unknown;
  };
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function getErrorMessage(body: unknown, status: number): string {
  const detail = (body as ApiErrorDetail | null)?.detail;
  if (detail?.message) {
    return detail.message;
  }
  return `Agent run failed with status ${status}.`;
}

export async function createAgentRun(task: string): Promise<AgentRunResponse> {
  const response = await fetch(`${API_BASE_URL}/agent-runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ task })
  });

  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status));
  }

  return body as AgentRunResponse;
}
