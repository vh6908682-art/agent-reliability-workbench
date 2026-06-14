"use client";

import { useState } from "react";
import type { ReactNode } from "react";

import { AgentRunForm } from "../components/AgentRunForm";
import { AgentRunResult } from "../components/AgentRunResult";
import { AgentTargetsPanel } from "../components/AgentTargetsPanel";
import { EvalComparisonPanel } from "../components/EvalComparisonPanel";
import { EvalRunnerPanel } from "../components/EvalRunnerPanel";
import { RecentRunsPanel } from "../components/RecentRunsPanel";
import { TraceViewer } from "../components/TraceViewer";
import { DEFAULT_REFERENCE_AGENT_TARGET_ID, type AgentRunResponse } from "../lib/api";

const navItems = [
  "Agent Targets",
  "Run Agent",
  "Review",
  "Evals",
  "Compare",
  "Recent History"
];

type WorkflowStepProps = {
  eyebrow: string;
  id: string;
  step: string;
  title: string;
  description: string;
  children: ReactNode;
};

function WorkflowStep({ eyebrow, id, step, title, description, children }: WorkflowStepProps) {
  return (
    <section className="scroll-mt-6" id={id}>
      <div className="mb-3 flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">{eyebrow}</p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">
            <span className="mr-2 inline-flex h-7 w-7 items-center justify-center rounded-full bg-slate-950 text-sm font-semibold text-white">
              {step}
            </span>
            {title}
          </h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{description}</p>
        </div>
      </div>
      {children}
    </section>
  );
}

export default function Home() {
  const [result, setResult] = useState<AgentRunResponse | null>(null);
  const [runsRefreshKey, setRunsRefreshKey] = useState(0);
  const [comparisonRefreshKey, setComparisonRefreshKey] = useState(0);
  const [selectedAgentTargetId, setSelectedAgentTargetId] = useState<number | null>(
    DEFAULT_REFERENCE_AGENT_TARGET_ID
  );

  function handleResult(nextResult: AgentRunResponse) {
    setResult(nextResult);
    setRunsRefreshKey((current) => current + 1);
  }

  return (
    <main className="min-h-screen bg-panel text-ink">
      <div className="border-b border-slate-200 bg-white">
        <div className="mx-auto flex max-w-6xl flex-col gap-5 px-6 py-6 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <p className="text-sm font-medium uppercase tracking-wide text-slate-500">
              Agent benchmarking / incident investigation
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-slate-950">
              Agent Reliability Workbench
            </h1>
            <p className="mt-2 max-w-2xl text-base leading-7 text-slate-600">
              Guided demo for benchmarking a built-in ReferenceIncidentAgent or an external HTTP
              JSON Agent Target, then reviewing trace, validation, guardrail, approval, eval, and
              comparison behavior.
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

      <section className="mx-auto max-w-6xl px-6 py-8">
        <div className="mb-8 rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Demo workflow
          </h2>
          <div className="mt-4 grid gap-3 text-sm leading-6 text-slate-700 md:grid-cols-5">
            {["Agent Target", "Run Agent", "Review", "Run Eval", "Compare"].map((item, index) => (
              <div className="border-l-2 border-slate-300 pl-3" key={item}>
                <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Step {index + 1}
                </div>
                <div className="mt-1 font-semibold text-slate-950">{item}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="space-y-6">
          <WorkflowStep
            description="Select the built-in reference agent or register an HTTP JSON endpoint as the benchmark subject."
            eyebrow="Benchmark target"
            id="agent-targets"
            step="1"
            title="Agent Target"
          >
            <AgentTargetsPanel
              onSelectedTargetChange={setSelectedAgentTargetId}
              selectedTargetId={selectedAgentTargetId}
            />
          </WorkflowStep>

          <WorkflowStep
            description="Run the incident investigation prompt and make the newly created run the active demo result."
            eyebrow="Incident case"
            id="run-agent"
            step="2"
            title="Run Agent"
          >
            <AgentRunForm onResult={handleResult} />
          </WorkflowStep>

          <WorkflowStep
            description="Inspect the current run only: final diagnosis, evidence, trace steps, validation, guardrail, approval, cost, and latency."
            eyebrow="Current result"
            id="review"
            step="3"
            title="Review Trace / Validation / Guardrail / Approval"
          >
            <div className="space-y-5">
              <AgentRunResult result={result} />
              <TraceViewer result={result} />
            </div>
          </WorkflowStep>

          <WorkflowStep
            description="Run deterministic benchmark cases against the selected Agent Target and keep the latest eval result visible here."
            eyebrow="Benchmark eval"
            id="evals"
            step="4"
            title="Run Benchmark Eval"
          >
            <EvalRunnerPanel
              onRunComplete={() => setComparisonRefreshKey((current) => current + 1)}
              onSelectedAgentTargetChange={setSelectedAgentTargetId}
              selectedAgentTargetId={selectedAgentTargetId}
            />
          </WorkflowStep>

          <WorkflowStep
            description="Compare recent eval outcomes by target, prompt/config metadata, quality, latency, cost, and guardrail behavior."
            eyebrow="Eval comparison"
            id="compare"
            step="5"
            title="Compare Results"
          >
            <EvalComparisonPanel refreshKey={comparisonRefreshKey} />
          </WorkflowStep>

          <section className="scroll-mt-6" id="recent-history">
            <div className="mb-3">
              <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                Secondary records
              </p>
              <h2 className="mt-2 text-lg font-semibold text-slate-950">Recent History</h2>
              <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
                Older database records stay available for inspection, but the active run and eval
                above remain the primary demo state.
              </p>
            </div>
            <RecentRunsPanel
              limit={5}
              onSelectRun={setResult}
              refreshKey={runsRefreshKey}
              selectedRunId={result?.run_id ?? null}
            />
          </section>
        </div>
      </section>
    </main>
  );
}
