"use client";

import { useEffect, useState } from "react";

import {
  DEFAULT_REFERENCE_AGENT_TARGET,
  DEFAULT_REFERENCE_AGENT_TARGET_ID,
  PROMPT_VERSION_OPTIONS,
  isApiUnavailableError,
  listAgentTargets,
  runEvals,
  type AgentTarget,
  type AgentUnderTest,
  type EvalRunSummary,
  type PromptVersion
} from "../lib/api";
import { EvalResultCard } from "./EvalResultCard";

type EvalRunnerPanelProps = {
  onRunComplete?: () => void;
  onSelectedAgentTargetChange?: (targetId: number | null) => void;
  selectedAgentTargetId?: number | null;
};

function targetOptionLabel(target: AgentTarget): string {
  const version = target.version || "n/a";
  if (target.agent_type === "reference") {
    return `${target.name} ${version} - built-in reference`;
  }

  return `${target.name} ${version} - HTTP JSON endpoint`;
}

function defaultTargetId(targets: AgentTarget[]): number | null {
  return (
    targets.find((target) => target.is_default)?.id ??
    targets.find((target) => target.agent_type === "reference")?.id ??
    null
  );
}

function formatAgentType(type: AgentUnderTest["type"]): string {
  if (type === "reference") {
    return "Built-in reference";
  }
  if (type === "http_json") {
    return "HTTP JSON";
  }
  if (type === "mock") {
    return "Benchmark target";
  }
  return "Benchmark target";
}

function AgentIdentitySummary({ agent }: { agent?: AgentUnderTest | null }) {
  if (!agent) {
    return null;
  }

  return (
    <div className="rounded-md border border-slate-200 bg-slate-50 p-3 text-sm">
      <p className="font-semibold text-slate-950">Agent Under Test: {agent.name}</p>
      <dl className="mt-2 grid gap-2 text-slate-600 sm:grid-cols-2">
        <div>
          <dt className="font-semibold text-slate-500">Type</dt>
          <dd>{formatAgentType(agent.type)}</dd>
        </div>
        <div>
          <dt className="font-semibold text-slate-500">Version</dt>
          <dd>{agent.version || "n/a"}</dd>
        </div>
      </dl>
    </div>
  );
}

export function EvalRunnerPanel({
  onRunComplete,
  onSelectedAgentTargetChange,
  selectedAgentTargetId
}: EvalRunnerPanelProps) {
  const [result, setResult] = useState<EvalRunSummary | null>(null);
  const [promptVersion, setPromptVersion] = useState<PromptVersion>("v1");
  const [agentTargets, setAgentTargets] = useState<AgentTarget[]>([]);
  const [localSelectedAgentTargetId, setLocalSelectedAgentTargetId] = useState<number | null>(
    selectedAgentTargetId ?? null
  );
  const [targetsError, setTargetsError] = useState<string | null>(null);
  const [isLoadingTargets, setIsLoadingTargets] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    let isCurrent = true;

    async function loadTargets() {
      setTargetsError(null);
      setIsLoadingTargets(true);

      try {
        const targets = await listAgentTargets();
        if (!isCurrent) {
          return;
        }

        setAgentTargets(targets);
        setLocalSelectedAgentTargetId((current) => {
          if (current != null && targets.some((target) => target.id === current)) {
            return current;
          }
          const nextTargetId = defaultTargetId(targets);
          onSelectedAgentTargetChange?.(nextTargetId);
          return nextTargetId;
        });
      } catch (caught) {
        if (isCurrent) {
          if (isApiUnavailableError(caught)) {
            setAgentTargets([DEFAULT_REFERENCE_AGENT_TARGET]);
            setLocalSelectedAgentTargetId(DEFAULT_REFERENCE_AGENT_TARGET_ID);
            onSelectedAgentTargetChange?.(DEFAULT_REFERENCE_AGENT_TARGET_ID);
          } else {
            setTargetsError(
              caught instanceof Error ? caught.message : "Agent targets could not be loaded."
            );
          }
        }
      } finally {
        if (isCurrent) {
          setIsLoadingTargets(false);
        }
      }
    }

    void loadTargets();

    return () => {
      isCurrent = false;
    };
  }, [onSelectedAgentTargetChange]);

  useEffect(() => {
    if (selectedAgentTargetId !== undefined) {
      setLocalSelectedAgentTargetId(selectedAgentTargetId);
    }
  }, [selectedAgentTargetId]);

  function handleSelectAgentTarget(targetId: number | null) {
    setLocalSelectedAgentTargetId(targetId);
    onSelectedAgentTargetChange?.(targetId);
  }

  async function handleRunEvals() {
    setError(null);
    setIsLoading(true);

    try {
      const nextResult = await runEvals({
        prompt_version: promptVersion,
        agent_target_id:
          localSelectedAgentTargetId === DEFAULT_REFERENCE_AGENT_TARGET_ID
            ? undefined
            : localSelectedAgentTargetId ?? undefined
      });
      setResult(nextResult);
      onRunComplete?.();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Eval run failed.");
    } finally {
      setIsLoading(false);
    }
  }

  const results = result?.results ?? [];
  const selectedTarget = agentTargets.find((target) => target.id === localSelectedAgentTargetId);

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Deterministic evals
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Eval Results</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Benchmark the selected Agent Target against deterministic incident cases and review
            case-level failures.
          </p>
          <p className="mt-2 text-sm font-medium text-slate-800">
            Current target: {selectedTarget?.name ?? "ReferenceIncidentAgent"} / Prompt{" "}
            {promptVersion}
          </p>
        </div>
        <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-end">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Agent Under Test</span>
            <select
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200 sm:w-72"
              disabled={isLoading || isLoadingTargets}
              onChange={(event) => handleSelectAgentTarget(Number(event.target.value))}
              value={localSelectedAgentTargetId ?? ""}
            >
              {agentTargets.length ? (
                agentTargets.map((target) => (
                  <option key={target.id} value={target.id}>
                    {targetOptionLabel(target)}
                  </option>
                ))
              ) : (
                <option value={DEFAULT_REFERENCE_AGENT_TARGET_ID}>
                  ReferenceIncidentAgent v1 - built-in reference
                </option>
              )}
            </select>
          </label>
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Prompt version</span>
            <select
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200 sm:w-36"
              disabled={isLoading}
              onChange={(event) => setPromptVersion(event.target.value as PromptVersion)}
              value={promptVersion}
            >
              {PROMPT_VERSION_OPTIONS.map((option) => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </label>
          <button
            className="inline-flex w-full items-center justify-center rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 sm:w-auto"
            disabled={isLoading}
            onClick={handleRunEvals}
            type="button"
          >
            {isLoading ? "Running..." : "Run Evals"}
          </button>
        </div>
      </div>

      {targetsError ? (
        <div className="mt-4 rounded-md border border-amber-200 bg-amber-50 px-3 py-2 text-sm text-amber-800">
          Agent targets could not be loaded. Evals can still run against the backend default agent.
          <span className="mt-1 block">{targetsError}</span>
        </div>
      ) : null}

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
          <AgentIdentitySummary agent={result.agent_under_test} />

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
