import type { TraceStep } from "../lib/api";

type ToolCallCardProps = {
  step: TraceStep;
};

function getStatus(step: TraceStep): string {
  const output = step.output;
  if (output && typeof output.error_type === "string") {
    return "error";
  }
  if (output && typeof output.status === "string") {
    return output.status;
  }
  return "recorded";
}

function getSummary(output: TraceStep["output"]): string {
  if (!output) {
    return "No output recorded.";
  }
  if (typeof output.summary === "string") {
    return output.summary;
  }
  if (typeof output.message === "string") {
    return output.message;
  }
  if (Array.isArray(output.context_sources)) {
    return `${output.context_sources.length} context source(s) returned.`;
  }
  return JSON.stringify(output, null, 2);
}

export function ToolCallCard({ step }: ToolCallCardProps) {
  const status = getStatus(step);
  const error =
    step.output && typeof step.output.message === "string" && status === "error"
      ? step.output.message
      : null;

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-950">{step.name}</div>
          <div className="mt-1 text-xs font-medium uppercase tracking-wide text-slate-500">
            Tool / {status}
          </div>
        </div>
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {step.latency_ms ?? "n/a"} ms
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Input</h4>
          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-slate-50 p-3 text-xs leading-5 text-slate-700">
            {JSON.stringify(step.input ?? {}, null, 2)}
          </pre>
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">
            Output Summary
          </h4>
          <pre className="mt-2 max-h-48 overflow-auto rounded-md bg-slate-50 p-3 text-xs leading-5 text-slate-700">
            {getSummary(step.output)}
          </pre>
        </div>
      </div>

      {error ? (
        <div className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">
          {error}
        </div>
      ) : null}
    </article>
  );
}
