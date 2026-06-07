"use client";

import { useState } from "react";

import { runEvals, type EvalRunSummary } from "../lib/api";
import { EvalResultCard } from "./EvalResultCard";

type EvalRunnerPanelProps = {
  onRunComplete?: () => void;
};

export function EvalRunnerPanel({ onRunComplete }: EvalRunnerPanelProps) {
  const [result, setResult] = useState<EvalRunSummary | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleRunEvals() {
    setError(null);
    setIsLoading(true);

    try {
      const nextResult = await runEvals();
      setResult(nextResult);
      onRunComplete?.();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Eval run failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const results = result?.results ?? [];

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm" id="evals">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Deterministic evals
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Eval Results</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Run the golden-path incident triage checks and review case-level failures.
          </p>
        </div>
        <button
          className="inline-flex w-full items-center justify-center rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 sm:w-auto"
          disabled={isLoading}
          onClick={handleRunEvals}
          type="button"
        >
          {isLoading ? "Running..." : "Run Evals"}
        </button>
      </div>

      {isLoading ? (
        <p className="mt-4 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm text-slate-600">
          Calling backend eval runner endpoint.
        </p>
      ) : null}

      {error ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}

      {result ? (
        <div className="mt-5 space-y-5">
          <dl className="grid gap-3 text-sm sm:grid-cols-3">
            <div className="rounded-md border border-slate-200 bg-slate-50 p-3">
              <dt className="text-slate-500">Total</dt>
              <dd className="mt-1 text-2xl font-semibold text-slate-950">{result.total ?? 0}</dd>
            </div>
            <div className="rounded-md border border-emerald-200 bg-emerald-50 p-3">
              <dt className="text-emerald-700">Passed</dt>
              <dd className="mt-1 text-2xl font-semibold text-emerald-800">
                {result.passed ?? 0}
              </dd>
            </div>
            <div className="rounded-md border border-red-200 bg-red-50 p-3">
              <dt className="text-red-700">Failed</dt>
              <dd className="mt-1 text-2xl font-semibold text-red-800">{result.failed ?? 0}</dd>
            </div>
          </dl>

          {results.length ? (
            <div className="space-y-3">
              {results.map((evalResult, index) => (
                <EvalResultCard
                  key={`${evalResult.case_id ?? "eval-case"}-${index}`}
                  result={evalResult}
                />
              ))}
            </div>
          ) : (
            <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
              No eval case results returned.
            </p>
          )}
        </div>
      ) : null}
    </section>
  );
}
