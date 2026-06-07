"use client";

import { FormEvent, useState } from "react";

import {
  createAgentRun,
  DEFAULT_INCIDENT_PROMPT,
  PROMPT_VERSION_OPTIONS,
  type AgentRunResponse,
  type PromptVersion
} from "../lib/api";

type AgentRunFormProps = {
  onResult: (result: AgentRunResponse) => void;
};

export function AgentRunForm({ onResult }: AgentRunFormProps) {
  const [task, setTask] = useState(DEFAULT_INCIDENT_PROMPT);
  const [promptVersion, setPromptVersion] = useState<PromptVersion>("v1");
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const trimmedTask = task.trim();
    if (!trimmedTask) {
      setError("Enter an incident prompt before running the agent.");
      return;
    }

    setError(null);
    setIsLoading(true);
    try {
      const result = await createAgentRun(trimmedTask, promptVersion);
      onResult(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Agent run failed.");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div>
        <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Incident triage
        </p>
        <h2 className="mt-2 text-lg font-semibold text-slate-950">Run Agent</h2>
      </div>

      <form className="mt-4 space-y-4" onSubmit={handleSubmit}>
        <label className="block">
          <span className="text-sm font-medium text-slate-700">Incident prompt</span>
          <textarea
            className="mt-2 min-h-36 w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
            disabled={isLoading}
            onChange={(event) => setTask(event.target.value)}
            value={task}
          />
        </label>

        <label className="block">
          <span className="text-sm font-medium text-slate-700">Prompt version</span>
          <select
            className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
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

        {error ? (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {error}
          </div>
        ) : null}

        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <button
            className="inline-flex w-full items-center justify-center rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 sm:w-auto"
            disabled={isLoading}
            type="submit"
          >
            {isLoading ? "Running..." : "Run Agent"}
          </button>
          {isLoading ? (
            <p className="text-sm text-slate-500">Calling backend agent run endpoint.</p>
          ) : null}
        </div>
      </form>
    </section>
  );
}
