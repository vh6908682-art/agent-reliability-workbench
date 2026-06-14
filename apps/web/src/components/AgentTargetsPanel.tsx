"use client";

import { FormEvent, useEffect, useState } from "react";

import {
  DEFAULT_REFERENCE_AGENT_TARGET,
  DEFAULT_REFERENCE_AGENT_TARGET_ID,
  createAgentTarget,
  isApiUnavailableError,
  listAgentTargets,
  testAgentTarget,
  type AgentTarget,
  type AgentTargetTestResult
} from "../lib/api";

type FormState = {
  name: string;
  endpointUrl: string;
  version: string;
  description: string;
  authType: "none" | "bearer";
  authToken: string;
};

const DEFAULT_FORM: FormState = {
  name: "",
  endpointUrl: "",
  version: "v1",
  description: "",
  authType: "none",
  authToken: ""
};

function targetKindLabel(target: AgentTarget): string {
  if (target.agent_type === "reference") {
    return "Built-in reference agent";
  }

  return "External HTTP JSON agent";
}

function formatType(value: AgentTarget["agent_type"]): string {
  return value.replaceAll("_", " ");
}

function targetTestMessage(result: AgentTargetTestResult): string {
  return `Connection test ${result.ok ? "passed" : "failed"}: ${result.message}`;
}

export function AgentTargetsPanel() {
  const [targets, setTargets] = useState<AgentTarget[]>([]);
  const [form, setForm] = useState<FormState>(DEFAULT_FORM);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [isUsingDefaultFallback, setIsUsingDefaultFallback] = useState(false);
  const [formError, setFormError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [testResults, setTestResults] = useState<Record<number, AgentTargetTestResult>>({});
  const [testErrors, setTestErrors] = useState<Record<number, string>>({});
  const [testingTargetId, setTestingTargetId] = useState<number | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function loadTargets() {
    setLoadError(null);
    setIsUsingDefaultFallback(false);
    setIsLoading(true);

    try {
      setTargets(await listAgentTargets());
    } catch (caught) {
      if (isApiUnavailableError(caught)) {
        setTargets([DEFAULT_REFERENCE_AGENT_TARGET]);
        setIsUsingDefaultFallback(true);
      } else {
        setLoadError(
          caught instanceof Error ? caught.message : "Agent targets could not be loaded."
        );
      }
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    let isCurrent = true;

    async function loadCurrentTargets() {
      setLoadError(null);
      setIsUsingDefaultFallback(false);
      setIsLoading(true);

      try {
        const nextTargets = await listAgentTargets();
        if (isCurrent) {
          setTargets(nextTargets);
        }
      } catch (caught) {
        if (isCurrent) {
          if (isApiUnavailableError(caught)) {
            setTargets([DEFAULT_REFERENCE_AGENT_TARGET]);
            setIsUsingDefaultFallback(true);
          } else {
            setLoadError(
              caught instanceof Error ? caught.message : "Agent targets could not be loaded."
            );
          }
        }
      } finally {
        if (isCurrent) {
          setIsLoading(false);
        }
      }
    }

    void loadCurrentTargets();

    return () => {
      isCurrent = false;
    };
  }, []);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();

    const name = form.name.trim();
    const endpointUrl = form.endpointUrl.trim();
    if (!name) {
      setFormError("Enter a name for the HTTP JSON agent target.");
      return;
    }
    if (!endpointUrl) {
      setFormError("Enter an endpoint URL for the HTTP JSON agent target.");
      return;
    }

    setFormError(null);
    setSuccessMessage(null);
    setIsSubmitting(true);

    try {
      const created = await createAgentTarget({
        name,
        agent_type: "http_json",
        endpoint_url: endpointUrl,
        auth_type: form.authType,
        auth_token:
          form.authType === "bearer" && form.authToken.trim() ? form.authToken.trim() : null,
        version: form.version.trim() || "v1",
        description: form.description.trim() || null
      });
      setSuccessMessage(`Created agent target "${created.name}".`);
      setForm(DEFAULT_FORM);
      await loadTargets();
    } catch (caught) {
      setFormError(caught instanceof Error ? caught.message : "Agent target could not be created.");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleTestTarget(targetId: number) {
    setTestingTargetId(targetId);
    setTestErrors((current) => {
      const next = { ...current };
      delete next[targetId];
      return next;
    });

    try {
      const result = await testAgentTarget(targetId);
      setTestResults((current) => ({ ...current, [targetId]: result }));
    } catch (caught) {
      setTestResults((current) => {
        const next = { ...current };
        delete next[targetId];
        return next;
      });
      setTestErrors((current) => ({
        ...current,
        [targetId]: caught instanceof Error ? caught.message : "Agent target test failed."
      }));
    } finally {
      setTestingTargetId(null);
    }
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm" id="agent-targets">
      <div className="flex flex-col gap-2 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Agent under test
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Agent Targets</h2>
          <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">
            ARW benchmarks explicit Agent Targets. The ReferenceIncidentAgent is the default
            built-in reference target. Add an HTTP JSON endpoint to benchmark your own agent.
          </p>
        </div>
        {isLoading ? <p className="text-sm text-slate-500">Loading agent targets...</p> : null}
      </div>

      {loadError ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {loadError}
        </div>
      ) : null}

      {isUsingDefaultFallback ? (
        <div className="mt-4 rounded-md border border-slate-200 bg-slate-50 px-3 py-2 text-sm text-slate-600">
          Showing the built-in ReferenceIncidentAgent default. Start the API service to load or add
          external HTTP JSON targets.
        </div>
      ) : null}

      {!isLoading && !loadError && targets.length === 0 ? (
        <p className="mt-4 rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
          No agent targets registered yet.
        </p>
      ) : null}

      {targets.length ? (
        <div className="mt-4 grid gap-3">
          {targets.map((target) => {
            const result = testResults[target.id];
            const testError = testErrors[target.id];
            const isTesting = testingTargetId === target.id;
            const isFallbackTarget =
              isUsingDefaultFallback && target.id === DEFAULT_REFERENCE_AGENT_TARGET_ID;

            return (
              <article
                className="rounded-md border border-slate-200 bg-slate-50 p-4"
                key={target.id}
              >
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="flex flex-wrap items-center gap-2">
                      <h3 className="text-base font-semibold text-slate-950">{target.name}</h3>
                      {target.is_default ? (
                        <span className="rounded-md border border-emerald-200 bg-emerald-50 px-2 py-1 text-xs font-semibold text-emerald-700">
                          Default
                        </span>
                      ) : null}
                      <span className="rounded-md border border-slate-200 bg-white px-2 py-1 text-xs font-semibold text-slate-600">
                        {targetKindLabel(target)}
                      </span>
                    </div>
                    {target.description ? (
                      <p className="mt-2 text-sm leading-6 text-slate-600">
                        {target.description}
                      </p>
                    ) : null}
                  </div>
                  {!isFallbackTarget ? (
                    <button
                      className="inline-flex w-full items-center justify-center rounded-md border border-slate-300 bg-white px-3 py-2 text-sm font-semibold text-slate-700 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:text-slate-400 sm:w-auto"
                      disabled={isTesting}
                      onClick={() => void handleTestTarget(target.id)}
                      type="button"
                    >
                      {isTesting ? "Testing..." : "Test Connection"}
                    </button>
                  ) : null}
                </div>

                <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2 lg:grid-cols-3">
                  <div>
                    <dt className="font-semibold text-slate-500">Type</dt>
                    <dd className="mt-1 capitalize text-slate-800">{formatType(target.agent_type)}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-500">Version</dt>
                    <dd className="mt-1 text-slate-800">{target.version || "n/a"}</dd>
                  </div>
                  <div>
                    <dt className="font-semibold text-slate-500">Auth</dt>
                    <dd className="mt-1 text-slate-800">
                      {target.auth_type}
                      {target.has_auth_token != null
                        ? ` / Token configured: ${target.has_auth_token ? "yes" : "no"}`
                        : ""}
                    </dd>
                  </div>
                  {target.agent_type === "http_json" ? (
                    <div className="sm:col-span-2 lg:col-span-3">
                      <dt className="font-semibold text-slate-500">Endpoint URL</dt>
                      <dd className="mt-1 break-all font-mono text-xs text-slate-800">
                        {target.endpoint_url || "n/a"}
                      </dd>
                    </div>
                  ) : null}
                </dl>

                {result ? (
                  <div
                    className={`mt-4 rounded-md border px-3 py-2 text-sm ${
                      result.ok
                        ? "border-emerald-200 bg-emerald-50 text-emerald-800"
                        : "border-red-200 bg-red-50 text-red-700"
                    }`}
                  >
                    <div>{targetTestMessage(result)}</div>
                    {result.error ? <div className="mt-1 font-mono text-xs">{result.error}</div> : null}
                  </div>
                ) : null}

                {testError ? (
                  <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
                    {testError}
                  </div>
                ) : null}
              </article>
            );
          })}
        </div>
      ) : null}

      <form className="mt-5 space-y-4 border-t border-slate-200 pt-5" onSubmit={handleSubmit}>
        <div>
          <p className="text-sm font-semibold text-slate-950">Add HTTP JSON agent</p>
          <p className="mt-1 text-sm leading-6 text-slate-600">
            Register an external endpoint that implements the HTTP JSON agent contract.
          </p>
        </div>

        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block">
            <span className="text-sm font-medium text-slate-700">Name</span>
            <input
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              disabled={isSubmitting}
              onChange={(event) => setForm((current) => ({ ...current, name: event.target.value }))}
              value={form.name}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Endpoint URL</span>
            <input
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              disabled={isSubmitting}
              onChange={(event) =>
                setForm((current) => ({ ...current, endpointUrl: event.target.value }))
              }
              placeholder="http://host.docker.internal:9000/run"
              value={form.endpointUrl}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Version</span>
            <input
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              disabled={isSubmitting}
              onChange={(event) =>
                setForm((current) => ({ ...current, version: event.target.value }))
              }
              value={form.version}
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium text-slate-700">Auth Type</span>
            <select
              className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              disabled={isSubmitting}
              onChange={(event) =>
                setForm((current) => ({
                  ...current,
                  authType: event.target.value as FormState["authType"]
                }))
              }
              value={form.authType}
            >
              <option value="none">none</option>
              <option value="bearer">bearer</option>
            </select>
          </label>

          {form.authType === "bearer" ? (
            <label className="block sm:col-span-2">
              <span className="text-sm font-medium text-slate-700">Auth Token</span>
              <input
                className="mt-2 w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
                disabled={isSubmitting}
                onChange={(event) =>
                  setForm((current) => ({ ...current, authToken: event.target.value }))
                }
                type="password"
                value={form.authToken}
              />
            </label>
          ) : null}

          <label className="block sm:col-span-2">
            <span className="text-sm font-medium text-slate-700">Description</span>
            <textarea
              className="mt-2 min-h-24 w-full resize-y rounded-md border border-slate-300 bg-white px-3 py-2 text-sm leading-6 text-slate-900 outline-none transition focus:border-slate-500 focus:ring-2 focus:ring-slate-200"
              disabled={isSubmitting}
              onChange={(event) =>
                setForm((current) => ({ ...current, description: event.target.value }))
              }
              value={form.description}
            />
          </label>
        </div>

        {formError ? (
          <div className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
            {formError}
          </div>
        ) : null}

        {successMessage ? (
          <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-800">
            {successMessage}
          </div>
        ) : null}

        <button
          className="inline-flex w-full items-center justify-center rounded-md bg-slate-950 px-4 py-2.5 text-sm font-semibold text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:bg-slate-400 sm:w-auto"
          disabled={isSubmitting}
          type="submit"
        >
          {isSubmitting ? "Creating..." : "Create Target"}
        </button>
      </form>
    </section>
  );
}
