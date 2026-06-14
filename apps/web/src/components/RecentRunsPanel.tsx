"use client";

import { useEffect, useState } from "react";

import {
  getAgentRun,
  listAgentRuns,
  type AgentRunResponse,
  type AgentRunSummaryResponse
} from "../lib/api";

type RecentRunsPanelProps = {
  limit?: number;
  onSelectRun: (result: AgentRunResponse) => void;
  refreshKey: number;
  selectedRunId?: number | null;
};

const EMPTY = "\u2014";

function formatDate(value?: string | null): string {
  if (!value) {
    return EMPTY;
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatLatency(value?: number | null): string {
  if (value == null) {
    return EMPTY;
  }

  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}s`;
  }

  return `${value} ms`;
}

function formatCost(value?: string | number | null): string {
  if (value == null) {
    return EMPTY;
  }

  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return String(value);
  }

  return `$${amount.toFixed(6)}`;
}

function formatTokenSummary(run: AgentRunSummaryResponse): string {
  const total = run.total_tokens ?? 0;
  const input = run.input_tokens ?? 0;
  const output = run.output_tokens ?? 0;

  if (total === 0 && input === 0 && output === 0) {
    return EMPTY;
  }

  return `${total.toLocaleString()} total (${input.toLocaleString()} in / ${output.toLocaleString()} out)`;
}

function statusLabel(value?: string | null): string {
  return value?.replaceAll("_", " ") ?? EMPTY;
}

function taskPreview(task: string): string {
  return task.length > 120 ? `${task.slice(0, 117)}...` : task;
}

function sortNewestFirst(runs: AgentRunSummaryResponse[]): AgentRunSummaryResponse[] {
  return [...runs].sort((left, right) => {
    const leftTime = new Date(left.created_at).getTime();
    const rightTime = new Date(right.created_at).getTime();

    if (Number.isNaN(leftTime) || Number.isNaN(rightTime)) {
      return right.run_id - left.run_id;
    }

    return rightTime - leftTime;
  });
}

export function RecentRunsPanel({
  limit = 5,
  onSelectRun,
  refreshKey,
  selectedRunId
}: RecentRunsPanelProps) {
  const [runs, setRuns] = useState<AgentRunSummaryResponse[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [loadingRunId, setLoadingRunId] = useState<number | null>(null);

  useEffect(() => {
    let isCurrent = true;

    async function loadRuns() {
      setError(null);
      setIsLoading(true);
      try {
        const recentRuns = await listAgentRuns();
        if (isCurrent) {
          setRuns(sortNewestFirst(recentRuns).slice(0, limit));
        }
      } catch (caught) {
        if (isCurrent) {
          setError(caught instanceof Error ? caught.message : "Recent runs could not be loaded.");
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    void loadRuns();

    return () => {
      isCurrent = false;
    };
  }, [limit, refreshKey]);

  async function handleSelectRun(runId: number) {
    setError(null);
    setLoadingRunId(runId);
    try {
      const detail = await getAgentRun(runId);
      onSelectRun({
        run_id: detail.run_id,
        task: detail.task,
        answer: detail.final_answer ?? undefined,
        structured_output: detail.structured_output,
        validation_status: detail.validation_status,
        guardrail_result: detail.guardrail_result,
        approval_status: detail.approval?.status ?? null,
        requires_approval: detail.approval?.requires_approval ?? false,
        latency_ms: detail.latency_ms,
        model_name: detail.model_name,
        input_tokens: detail.input_tokens,
        output_tokens: detail.output_tokens,
        total_tokens: detail.total_tokens,
        estimated_cost_usd: detail.estimated_cost_usd ?? detail.cost_usd,
        context_sources: [],
        trace_detail: detail
      });
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Run details could not be loaded.");
    } finally {
      setLoadingRunId(null);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm" id="runs">
      <div className="flex flex-col gap-2 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Recent history
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Recent Runs</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Showing the {limit} newest persisted runs. Selecting one promotes it into the current
            review panels above.
          </p>
        </div>
        {isLoading ? <p className="text-sm text-slate-500">Loading recent runs...</p> : null}
      </div>

      {error ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {!isLoading && runs.length === 0 ? (
        <p className="mt-4 rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
          No recent run history yet.
        </p>
      ) : null}

      {runs.length ? (
        <div className="mt-4 overflow-hidden rounded-md border border-slate-200">
          <div className="hidden grid-cols-[90px_1.4fr_110px_150px_100px_120px_120px] gap-3 border-b border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold uppercase tracking-wide text-slate-500 lg:grid">
            <div>Run ID</div>
            <div>Task</div>
            <div>Status</div>
            <div>Timing</div>
            <div>Model</div>
            <div>Tokens / Cost</div>
            <div>Controls</div>
          </div>
          <div className="divide-y divide-slate-200">
            {runs.map((run) => {
              const isSelected = selectedRunId === run.run_id;
              const isLoadingDetail = loadingRunId === run.run_id;

              return (
                <button
                  className={`grid w-full gap-3 px-3 py-3 text-left text-sm transition hover:bg-slate-50 lg:grid-cols-[90px_1.4fr_110px_150px_100px_120px_120px] ${
                    isSelected ? "bg-slate-50 ring-1 ring-inset ring-slate-300" : "bg-white"
                  }`}
                  disabled={isLoadingDetail}
                  key={run.run_id}
                  onClick={() => void handleSelectRun(run.run_id)}
                  type="button"
                >
                  <div className="font-mono text-xs text-slate-700">#{run.run_id}</div>
                  <div>
                    <div className="font-medium text-slate-950">{taskPreview(run.task)}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      Guardrail: {statusLabel(run.guardrail_status)} / Approval:{" "}
                      {statusLabel(run.approval_status)}
                    </div>
                  </div>
                  <div className="capitalize text-slate-700">{statusLabel(run.status)}</div>
                  <div className="text-slate-700">
                    <div>{formatDate(run.created_at)}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      Latency: {formatLatency(run.latency_ms)}
                    </div>
                  </div>
                  <div className="text-slate-700">{run.model_name ?? EMPTY}</div>
                  <div className="text-slate-700">
                    <div>{formatTokenSummary(run)}</div>
                    <div className="mt-1 text-xs text-slate-500">
                      {formatCost(run.estimated_cost_usd)}
                    </div>
                  </div>
                  <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                    {isLoadingDetail ? "Opening..." : isSelected ? "Selected" : "Open trace"}
                  </div>
                </button>
              );
            })}
          </div>
        </div>
      ) : null}
    </section>
  );
}
