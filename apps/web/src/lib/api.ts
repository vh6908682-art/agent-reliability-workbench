export const DEFAULT_INCIDENT_PROMPT =
  "A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.";

export const PROMPT_VERSION_OPTIONS = [
  { value: "v1", label: "Prompt v1" },
  { value: "v2", label: "Prompt v2" }
] as const;

export type PromptVersion = (typeof PROMPT_VERSION_OPTIONS)[number]["value"];

export type ContextSource = {
  source_path?: string;
  title?: string;
  document_type?: string;
  relevance_score?: number;
};

export type TraceStep = {
  id: number;
  step_index: number;
  step_type: string;
  name: string;
  input: Record<string, unknown> | null;
  output: Record<string, unknown> | null;
  latency_ms: number | null;
  created_at: string;
};

export type IncidentDiagnosis = {
  likely_cause?: string;
  evidence?: string[];
  recommended_next_steps?: string[];
  prevention?: string[];
  confidence?: string;
};

export type AgentUnderTest = {
  name: string;
  version: string | null;
  type: "reference" | "http_json" | "mock";
};

export type AgentRunDetailResponse = {
  run_id: number;
  task: string;
  status: string;
  final_answer: string | null;
  structured_output: Record<string, unknown> | null;
  validation_status: string | null;
  guardrail_result?: {
    passed?: boolean;
    checks?: unknown[];
  } | null;
  approval?: {
    run_id: number;
    status: string;
    reviewer_note: string | null;
    requires_approval: boolean;
    updated_at: string | null;
  };
  started_at: string | null;
  completed_at: string | null;
  latency_ms: number | null;
  cost_usd: string | number | null;
  estimated_cost_usd: string | number | null;
  model_name: string | null;
  prompt_version: string | null;
  workflow_type: string | null;
  toolset_name: string | null;
  guardrail_mode: string | null;
  agent_under_test?: AgentUnderTest | null;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  created_at: string;
  updated_at: string;
  trace_steps: TraceStep[];
};

export type AgentRunSummaryResponse = {
  run_id: number;
  task: string;
  status: string;
  created_at: string;
  started_at: string | null;
  completed_at: string | null;
  latency_ms: number | null;
  model_name: string | null;
  input_tokens: number;
  output_tokens: number;
  total_tokens: number;
  estimated_cost_usd: string | number | null;
  guardrail_status: string | null;
  approval_status: string | null;
  requires_approval: boolean;
  agent_under_test?: AgentUnderTest | null;
};

export type AgentRunResponse = {
  run_id?: number | null;
  task?: string;
  answer?: string;
  structured_output?: IncidentDiagnosis | Record<string, unknown> | null;
  validation_status?: string | null;
  guardrail_result?: AgentRunDetailResponse["guardrail_result"];
  approval_status?: string | null;
  requires_approval?: boolean;
  latency_ms?: number | null;
  model_name?: string | null;
  prompt_version?: string | null;
  workflow_type?: string | null;
  toolset_name?: string | null;
  guardrail_mode?: string | null;
  agent_under_test?: AgentUnderTest | null;
  input_tokens?: number;
  output_tokens?: number;
  total_tokens?: number;
  estimated_cost_usd?: string | number | null;
  context_sources?: ContextSource[];
  trace_detail?: AgentRunDetailResponse | null;
  trace_error?: string;
};

export type EvalCheckResult = {
  name?: string;
  passed?: boolean;
  details?: Record<string, unknown>;
};

export type EvalCaseResult = {
  case_id?: string;
  name?: string;
  passed?: boolean;
  score?: number;
  checks?: EvalCheckResult[];
};

export type EvalRunSummary = {
  total?: number;
  passed?: number;
  failed?: number;
  agent_under_test?: AgentUnderTest | null;
  results?: EvalCaseResult[];
};

export type EvalRunRequest = {
  prompt_version?: PromptVersion;
  agent_target_id?: number;
};

export type EvalComparisonItem = {
  eval_run_id: number;
  created_at: string;
  total_cases: number;
  passed: number;
  failed: number;
  pass_rate: number;
  avg_score: number | null;
  avg_latency: number | null;
  avg_cost: number | null;
  guardrail_failure_count: number;
  model_name: string | null;
  prompt_version: string | null;
  workflow_type: string | null;
  toolset_name: string | null;
  guardrail_mode: string | null;
  agent_under_test?: AgentUnderTest | null;
};

export type EvalComparisonResponse = {
  items: EvalComparisonItem[];
};

export type AgentTarget = {
  id: number;
  name: string;
  agent_type: "reference" | "http_json";
  endpoint_url?: string | null;
  auth_type: "none" | "bearer";
  has_auth_token?: boolean;
  version?: string | null;
  description?: string | null;
  is_default: boolean;
  created_at?: string;
  updated_at?: string;
};

export const DEFAULT_REFERENCE_AGENT_TARGET_ID = 0;

export const DEFAULT_REFERENCE_AGENT_TARGET: AgentTarget = {
  id: DEFAULT_REFERENCE_AGENT_TARGET_ID,
  name: "ReferenceIncidentAgent",
  agent_type: "reference",
  endpoint_url: null,
  auth_type: "none",
  has_auth_token: false,
  version: "v1",
  description: "Built-in sample incident-response agent used for local demos.",
  is_default: true
};

export type AgentTargetCreate = {
  name: string;
  agent_type: "http_json";
  endpoint_url: string;
  auth_type: "none" | "bearer";
  auth_token?: string | null;
  version?: string | null;
  description?: string | null;
};

export type AgentTargetTestResult = {
  ok: boolean;
  agent_target_id: number;
  agent_name: string;
  agent_type: "reference" | "http_json";
  message: string;
  error?: string | null;
};

type ApiErrorDetail = {
  detail?:
    | {
        error?: string;
        message?: string;
        details?: unknown;
      }
    | Array<{
        loc?: Array<string | number>;
        msg?: string;
      }>
    | string;
};

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

function getErrorMessage(body: unknown, status: number, fallback: string): string {
  const detail = (body as ApiErrorDetail | null)?.detail;
  if (typeof detail === "string") {
    return detail;
  }
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        const path = item.loc?.filter((part) => part !== "body").join(".");
        return path && item.msg ? `${path}: ${item.msg}` : item.msg;
      })
      .filter(Boolean);
    if (messages.length) {
      return messages.join(" ");
    }
  }
  if (detail && typeof detail === "object" && !Array.isArray(detail) && detail.message) {
    return detail.message;
  }
  return `${fallback} with status ${status}.`;
}

export function isApiUnavailableError(caught: unknown): boolean {
  if (!(caught instanceof Error)) {
    return false;
  }

  return (
    caught instanceof TypeError ||
    caught.message === "Failed to fetch" ||
    caught.message === "fetch failed" ||
    caught.message === "Load failed" ||
    caught.message.includes("NetworkError")
  );
}

export async function listAgentTargets(): Promise<AgentTarget[]> {
  const response = await fetch(`${API_BASE_URL}/agent-targets`);
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Agent targets request failed"));
  }

  return body as AgentTarget[];
}

export async function createAgentTarget(payload: AgentTargetCreate): Promise<AgentTarget> {
  const response = await fetch(`${API_BASE_URL}/agent-targets`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Agent target creation failed"));
  }

  return body as AgentTarget;
}

export async function testAgentTarget(targetId: number): Promise<AgentTargetTestResult> {
  const response = await fetch(`${API_BASE_URL}/agent-targets/${targetId}/test`, {
    method: "POST"
  });
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Agent target test failed"));
  }

  return body as AgentTargetTestResult;
}

export async function createAgentRun(
  task: string,
  promptVersion: PromptVersion = "v1"
): Promise<AgentRunResponse> {
  const response = await fetch(`${API_BASE_URL}/agent-runs`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ task, prompt_version: promptVersion })
  });

  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Agent run failed"));
  }

  const agentRun = body as AgentRunResponse;
  if (!agentRun.run_id) {
    return agentRun;
  }

  try {
    return {
      ...agentRun,
      trace_detail: await getAgentRun(agentRun.run_id)
    };
  } catch (caught) {
    return {
      ...agentRun,
      trace_detail: null,
      trace_error: caught instanceof Error ? caught.message : "Trace details could not be loaded."
    };
  }
}

export async function getAgentRun(runId: number): Promise<AgentRunDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/agent-runs/${runId}`);
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Trace details request failed"));
  }

  return body as AgentRunDetailResponse;
}

export async function listAgentRuns(): Promise<AgentRunSummaryResponse[]> {
  const response = await fetch(`${API_BASE_URL}/agent-runs`);
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Recent runs request failed"));
  }

  return body as AgentRunSummaryResponse[];
}

export async function runEvals(payload: EvalRunRequest = { prompt_version: "v1" }): Promise<EvalRunSummary> {
  const response = await fetch(`${API_BASE_URL}/evals/run`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
  });
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Eval run failed"));
  }

  return body as EvalRunSummary;
}

export async function getEvalComparison(): Promise<EvalComparisonResponse> {
  const response = await fetch(`${API_BASE_URL}/evals/comparison`);
  const body = (await response.json().catch(() => null)) as unknown;

  if (!response.ok) {
    throw new Error(getErrorMessage(body, response.status, "Eval comparison request failed"));
  }

  return body as EvalComparisonResponse;
}
