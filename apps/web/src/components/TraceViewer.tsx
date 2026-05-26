import type { AgentRunResponse, ContextSource, TraceStep } from "../lib/api";
import { ToolCallCard } from "./ToolCallCard";
import { TraceStepCard } from "./TraceStepCard";

type TraceViewerProps = {
  result: AgentRunResponse | null;
};

function formatDate(value?: string | null): string {
  if (!value) {
    return "not returned";
  }

  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

function formatCost(value?: string | number | null): string {
  if (value == null) {
    return "not returned";
  }

  const amount = Number(value);
  if (Number.isNaN(amount)) {
    return String(value);
  }

  return `$${amount.toFixed(6)}`;
}

function formatNumber(value?: number | null): string {
  if (value == null) {
    return "not returned";
  }

  return new Intl.NumberFormat().format(value);
}

function JsonBlock({ value, emptyText }: { value: unknown; emptyText: string }) {
  if (value == null) {
    return <p className="text-sm text-slate-500">{emptyText}</p>;
  }

  return (
    <pre className="max-h-80 overflow-auto rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

function EvidenceList({ sources }: { sources?: ContextSource[] }) {
  if (!sources?.length) {
    return <p className="text-sm text-slate-500">No retrieved documents returned.</p>;
  }

  return (
    <ul className="space-y-2 text-sm text-slate-700">
      {sources.map((source) => (
        <li
          className="rounded-md border border-slate-200 bg-white px-3 py-2"
          key={`${source.source_path ?? "source"}-${source.title ?? "untitled"}`}
        >
          <div className="font-medium text-slate-950">{source.title ?? "Untitled source"}</div>
          <div className="mt-1 text-xs text-slate-500">
            {source.document_type ?? "unknown"} / relevance {source.relevance_score ?? "n/a"}
          </div>
          {source.source_path ? (
            <div className="mt-1 break-words text-xs text-slate-500">{source.source_path}</div>
          ) : null}
        </li>
      ))}
    </ul>
  );
}

function isToolStep(step: TraceStep): boolean {
  const type = step.step_type.toLowerCase();
  const name = step.name.toLowerCase();
  return type.includes("tool") || name.includes("tool");
}

export function TraceViewer({ result }: TraceViewerProps) {
  const detail = result?.trace_detail;
  const traceSteps = detail?.trace_steps ?? [];
  const toolSteps = traceSteps.filter(isToolStep);
  const structuredOutput = detail?.structured_output ?? result?.structured_output ?? null;
  const validationStatus = detail?.validation_status ?? result?.validation_status ?? null;
  const prompt = detail?.task ?? result?.task ?? null;

  if (!result) {
    return (
      <section
        className="rounded-lg border border-dashed border-slate-300 bg-white p-5"
        id="traces"
      >
        <h2 className="text-lg font-semibold text-slate-950">Trace Viewer</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Run the incident triage agent to inspect trace steps, tool calls, validation, and timing.
        </p>
      </section>
    );
  }

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm" id="traces">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Trace Viewer
          </p>
          <h2 className="mt-2 text-lg font-semibold text-slate-950">Run Trace</h2>
          {result.trace_error ? (
            <p className="mt-2 text-sm text-amber-700">{result.trace_error}</p>
          ) : null}
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-wide">
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Run ID: {result.run_id ?? "not returned"}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Status: {detail?.status ?? "not returned"}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Validation: {validationStatus ?? "not returned"}
          </span>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Run Summary
          </h3>
          <dl className="mt-3 grid gap-2 text-sm text-slate-700">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Started</dt>
              <dd className="text-right text-slate-900">
                {formatDate(detail?.started_at ?? detail?.created_at)}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Completed</dt>
              <dd className="text-right text-slate-900">
                {formatDate(detail?.completed_at ?? detail?.updated_at)}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Latency</dt>
              <dd className="text-right text-slate-900">
                {detail?.latency_ms == null ? "not returned" : `${detail.latency_ms} ms`}
              </dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Model</dt>
              <dd className="text-right text-slate-900">{detail?.model_name ?? "not returned"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Input tokens</dt>
              <dd className="text-right text-slate-900">{formatNumber(detail?.input_tokens)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Output tokens</dt>
              <dd className="text-right text-slate-900">{formatNumber(detail?.output_tokens)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Total tokens</dt>
              <dd className="text-right text-slate-900">{formatNumber(detail?.total_tokens)}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Estimated cost</dt>
              <dd className="text-right text-slate-900">
                {formatCost(detail?.estimated_cost_usd ?? detail?.cost_usd)}
              </dd>
            </div>
          </dl>
        </div>

        <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Validation Result
          </h3>
          <dl className="mt-3 grid gap-2 text-sm text-slate-700">
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Status</dt>
              <dd className="text-right text-slate-900">{validationStatus ?? "not returned"}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Trace steps</dt>
              <dd className="text-right text-slate-900">{traceSteps.length}</dd>
            </div>
            <div className="flex justify-between gap-4">
              <dt className="text-slate-500">Tool calls</dt>
              <dd className="text-right text-slate-900">{toolSteps.length}</dd>
            </div>
          </dl>
        </div>

        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Input</h3>
          <p className="mt-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-800">
            {prompt ?? "No input prompt returned."}
          </p>
        </div>

        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Agent Steps
          </h3>
          <div className="mt-2 space-y-3">
            {traceSteps.length ? (
              traceSteps.map((step) => <TraceStepCard key={step.id} step={step} />)
            ) : (
              <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
                No trace steps returned for this run.
              </p>
            )}
          </div>
        </div>

        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Tool Calls
          </h3>
          <div className="mt-2 space-y-3">
            {toolSteps.length ? (
              toolSteps.map((step) => <ToolCallCard key={step.id} step={step} />)
            ) : (
              <p className="rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
                No tool call steps returned for this run.
              </p>
            )}
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Retrieved Documents
          </h3>
          <div className="mt-2">
            <EvidenceList sources={result.context_sources} />
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Structured Output
          </h3>
          <div className="mt-2">
            <JsonBlock value={structuredOutput} emptyText="No structured output returned." />
          </div>
        </div>
      </div>
    </section>
  );
}
