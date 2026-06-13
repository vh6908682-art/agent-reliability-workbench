"use client";

import { useState } from "react";

import { AgentRunForm } from "../components/AgentRunForm";
import { AgentRunResult } from "../components/AgentRunResult";
import { AgentTargetsPanel } from "../components/AgentTargetsPanel";
import { EvalComparisonPanel } from "../components/EvalComparisonPanel";
import { EvalRunnerPanel } from "../components/EvalRunnerPanel";
import { RecentRunsPanel } from "../components/RecentRunsPanel";
import { TraceViewer } from "../components/TraceViewer";
import type { AgentRunResponse } from "../lib/api";

const navItems = [
  "Run Agent",
  "Runs",
  "Traces",
  "Validation",
  "Agent Targets",
  "Evals",
  "Guardrails",
  "Approvals"
];

export default function Home() {
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [runsRefreshKey, setRunsRefreshKey] = useState(0);
  const [comparisonRefreshKey, setComparisonRefreshKey] = useState(0);

  function handleResult(nextResult: AgentRunResponse) {
    setResult(nextResult);
    setRunsRefreshKey((current) => current + 1);
  }

  return (
    <main className="min-h-screen bg-panel text-ink">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-7xl flex-col gap-5 px-6 py-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Developer Support / Incident Triage Agent
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-slate-950">
              AgentOps Workbench
            </h1>
            <p className="mt-2 max-w-2xl text-base leading-7 text-slate-600">
              Production layer for tool-using LLM agents: traces, validation, evals, cost,
              guardrails, and approvals around every answer.
            </p>
          </div>
          <nav aria-label="Primary navigation" className="flex flex-wrap gap-2">
            {navItems.map((item) => (
              <a
                className="rounded-md border border-slate-200 px-3 py-2 text-sm font-medium text-slate-700 transition hover:border-slate-300 hover:bg-slate-50"
                href={`#${item.toLowerCase().replaceAll(" ", "-")}`}
                key={item}
              >
                {item}
              </a>
            ))}
          </nav>
        </div>
      </div>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[320px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            MVP Demo Guide
          </h2>
          <ul className="mt-4 space-y-3 text-sm leading-6 text-slate-700">
            <li>Run an incident or debugging prompt.</li>
            <li>Inspect the persisted trace and retrieved context.</li>
            <li>Review validation, guardrail, and approval status.</li>
            <li>Check latency, token usage, and estimated cost.</li>
            <li>Reopen previous runs from Recent Runs.</li>
            <li>Run evals to verify answer quality.</li>
          </ul>
        </aside>

        <div className="space-y-5">
          <AgentRunForm onResult={handleResult} />
          <RecentRunsPanel
            onSelectRun={setResult}
            refreshKey={runsRefreshKey}
            selectedRunId={result?.run_id ?? null}
          />
          <AgentRunResult result={result} />
          <TraceViewer result={result} />
          <AgentTargetsPanel />
          <EvalRunnerPanel
            onRunComplete={() => setComparisonRefreshKey((current) => current + 1)}
          />
          <EvalComparisonPanel refreshKey={comparisonRefreshKey} />
        </div>
      </section>
    </main>
  );
}
