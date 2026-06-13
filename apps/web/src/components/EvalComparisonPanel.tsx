"use client";

import { useEffect, useState } from "react";

import { getEvalComparison, type AgentUnderTest, type EvalComparisonItem } from "../lib/api";

const EMPTY = "n/a";

type EvalComparisonPanelProps = {
  refreshKey?: number;
};

function formatText(value?: string | null): string {
  return value || EMPTY;
}

function formatAgentType(value?: AgentUnderTest["type"] | null): string {
  if (!value) {
    return EMPTY;
  }
  if (value === "reference") {
    return "Built-in sample";
  }
  if (value === "http_json") {
    return "HTTP JSON";
  }
  return value.replaceAll("_", " ");
}

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

function formatPercent(value?: number | null): string {
  if (value == null) {
    return EMPTY;
  }

  return `${(value * 100).toFixed(0)}%`;
}

function formatScore(value?: number | null): string {
  if (value == null) {
    return EMPTY;
  }

  return value.toFixed(2);
}

function formatLatency(value?: number | null): string {
  if (value == null) {
    return EMPTY;
  }

  if (value >= 1000) {
    return `${(value / 1000).toFixed(2)}s`;
  }

  return `${value.toFixed(0)} ms`;
}

function formatCost(value?: number | null): string {
  if (value == null) {
    return EMPTY;
  }

  return `$${value.toFixed(6)}`;
}

function ConfigSummary({ item }: { item: EvalComparisonItem }) {
  return (
    <div>
      <div className="font-mono text-xs font-semibold text-slate-800">
        Eval #{item.eval_run_id}
      </div>
      <div className="mt-1 text-xs text-slate-500">{formatDate(item.created_at)}</div>
      <dl className="mt-2 grid gap-x-3 gap-y-1 text-xs text-slate-600 sm:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2">
        <div>
          <dt className="font-semibold text-slate-500">Agent</dt>
          <dd>{formatText(item.agent_under_test?.name)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Agent type</dt>
          <dd>{formatAgentType(item.agent_under_test?.type)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Agent version</dt>
          <dd>{formatText(item.agent_under_test?.version)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Model</dt>
          <dd>{formatText(item.model_name)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Prompt</dt>
          <dd>{formatText(item.prompt_version)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Workflow</dt>
          <dd>{formatText(item.workflow_type)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Toolset</dt>
          <dd>{formatText(item.toolset_name)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Guardrails</dt>
          <dd>{formatText(item.guardrail_mode)}</dd>
        </div>
      </dl>
    </div>
  );
}

export function EvalComparisonPanel({ refreshKey = 0 }: EvalComparisonPanelProps) {
  const [items, setItems] = useState<EvalComparisonItem[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let isCurrent = true;

    async function loadComparison() {
      setError(null);
      setIsLoading(true);

      try {
        const comparison = await getEvalComparison();
        if (isCurrent) {
          setItems(comparison.items ?? []);
        }
      } catch (caught) {
        if (isCurrent) {
          setError(
            caught instanceof Error ? caught.message : "Eval comparison could not be loaded."
          );
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    void loadComparison();

    return () => {
      isCurrent = false;
    };
  }, [refreshKey]);

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-2 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Benchmark comparison
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Eval Comparison</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Compare recent eval run quality, latency, cost, and guardrail outcomes.
          </p>
        </div>
        {isLoading ? <p className="text-sm text-slate-500">Loading comparison...</p> : null}
      </div>

      {error ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {!isLoading && !error && items.length === 0 ? (
        <p className="mt-4 rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
          No eval runs available yet. Run an eval to compare benchmark results.
        </p>
      ) : null}

      {items.length ? (
        <div className="mt-4 overflow-x-auto rounded-md border border-slate-200">
          <table className="min-w-[980px] divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-xs font-semibold uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-3 py-2">Eval run / config</th>
                <th className="px-3 py-2">Pass rate</th>
                <th className="px-3 py-2">Avg score</th>
                <th className="px-3 py-2">Avg latency</th>
                <th className="px-3 py-2">Avg cost</th>
                <th className="px-3 py-2">Guardrail failures</th>
                <th className="px-3 py-2">Total / passed / failed</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200 bg-white">
              {items.map((item) => (
                <tr key={item.eval_run_id} className="align-top">
                  <td className="max-w-[300px] px-3 py-3">
                    <ConfigSummary item={item} />
                  </td>
                  <td className="px-3 py-3 font-semibold text-slate-950">
                    {formatPercent(item.pass_rate)}
                  </td>
                  <td className="px-3 py-3 text-slate-700">{formatScore(item.avg_score)}</td>
                  <td className="px-3 py-3 text-slate-700">{formatLatency(item.avg_latency)}</td>
                  <td className="px-3 py-3 text-slate-700">{formatCost(item.avg_cost)}</td>
                  <td className="px-3 py-3 text-slate-700">
                    {item.guardrail_failure_count}
                  </td>
                  <td className="px-3 py-3 text-slate-700">
                    {item.total_cases} / {item.passed} / {item.failed}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
