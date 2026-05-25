import type { TraceStep } from "../lib/api";

type TraceStepCardProps = {
  step: TraceStep;
};

function JsonBlock({ value }: { value: unknown }) {
  if (value == null) {
    return <p className="text-sm text-slate-500">Not recorded.</p>;
  }

  return (
    <pre className="max-h-72 overflow-auto rounded-md bg-slate-950 p-3 text-xs leading-5 text-slate-100">
      {JSON.stringify(value, null, 2)}
    </pre>
  );
}

export function TraceStepCard({ step }: TraceStepCardProps) {
  return (
    <article className="rounded-md border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-sm font-semibold text-slate-950">
            Step {step.step_index}: {step.step_type}
          </div>
          <div className="mt-1 text-sm text-slate-600">{step.name}</div>
        </div>
        <div className="text-xs font-medium uppercase tracking-wide text-slate-500">
          {step.latency_ms ?? "n/a"} ms
        </div>
      </div>

      <div className="mt-4 grid gap-4 lg:grid-cols-2">
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Input</h4>
          <div className="mt-2">
            <JsonBlock value={step.input} />
          </div>
        </div>
        <div>
          <h4 className="text-xs font-semibold uppercase tracking-wide text-slate-500">Output</h4>
          <div className="mt-2">
            <JsonBlock value={step.output} />
          </div>
        </div>
      </div>
    </article>
  );
}
