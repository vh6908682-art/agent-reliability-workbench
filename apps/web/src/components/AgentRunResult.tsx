import type { AgentRunResponse, ContextSource, IncidentDiagnosis } from "../lib/api";

type AgentRunResultProps = {
  result: AgentRunResponse | null;
};

function isDiagnosis(value: AgentRunResponse["structured_output"]): value is IncidentDiagnosis {
  return Boolean(value && typeof value === "object" && !Array.isArray(value));
}

function FieldList({ items }: { items?: string[] }) {
  if (!items?.length) {
    return <p className="text-sm text-slate-500">Not returned.</p>;
  }

  return (
    <ul className="space-y-2 text-sm leading-6 text-slate-700">
      {items.map((item) => (
        <li className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2" key={item}>
          {item}
        </li>
      ))}
    </ul>
  );
}

function ContextSources({ sources }: { sources?: ContextSource[] }) {
  if (!sources?.length) {
    return <p className="text-sm text-slate-500">No context sources returned.</p>;
  }

  return (
    <ul className="space-y-2 text-sm text-slate-700">
      {sources.map((source) => (
        <li
          className="rounded-md border border-slate-200 bg-white px-3 py-2"
          key={`${source.source_path ?? "source"}-${source.title ?? "untitled"}`}
        >
          <div className="font-medium text-slate-900">{source.title ?? "Untitled source"}</div>
          <div className="mt-1 text-xs text-slate-500">
            {source.document_type ?? "unknown"} / relevance {source.relevance_score ?? "n/a"}
          </div>
        </li>
      ))}
    </ul>
  );
}

function formatStatus(value?: string | null): string {
  return value?.replaceAll("_", " ") ?? "not returned";
}

export function AgentRunResult({ result }: AgentRunResultProps) {
  if (!result) {
    return (
      <section className="rounded-lg border border-dashed border-slate-300 bg-white p-5">
        <h2 className="text-lg font-semibold text-slate-950">Current Triage Result</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">
          Run the incident triage agent to make a result active here. Older runs stay in Recent
          History below.
        </p>
      </section>
    );
  }

  const diagnosis = isDiagnosis(result.structured_output) ? result.structured_output : null;

  return (
    <section className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <div className="flex flex-col gap-3 border-b border-slate-200 pb-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h2 className="text-lg font-semibold text-slate-950">Current Triage Result</h2>
          <p className="mt-1 text-sm text-slate-500">Run ID: {result.run_id ?? "not returned"}</p>
        </div>
        <div className="flex flex-wrap gap-2 text-xs font-semibold uppercase tracking-wide">
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Validation: {formatStatus(result.validation_status)}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Guardrail:{" "}
            {result.guardrail_result?.passed == null
              ? "not returned"
              : result.guardrail_result.passed
                ? "passed"
                : "failed"}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Approval: {formatStatus(result.approval_status)}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-slate-700">
            Confidence: {diagnosis?.confidence ?? "not returned"}
          </span>
        </div>
      </div>

      <div className="mt-5 grid gap-5 lg:grid-cols-2">
        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Diagnosis
          </h3>
          <p className="mt-2 rounded-md border border-slate-200 bg-slate-50 p-3 text-sm leading-6 text-slate-800">
            {diagnosis?.likely_cause ?? result.answer ?? "No diagnosis returned."}
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Recommended Next Steps
          </h3>
          <div className="mt-2">
            <FieldList items={diagnosis?.recommended_next_steps} />
          </div>
        </div>

        <div>
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Evidence
          </h3>
          <div className="mt-2">
            <FieldList items={diagnosis?.evidence} />
          </div>
        </div>

        <div className="lg:col-span-2">
          <h3 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            Context Sources
          </h3>
          <div className="mt-2">
            <ContextSources sources={result.context_sources} />
          </div>
        </div>
      </div>
    </section>
  );
}
