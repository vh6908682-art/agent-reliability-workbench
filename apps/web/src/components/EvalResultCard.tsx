import type { EvalCaseResult, EvalCheckResult } from "../lib/api";

type EvalResultCardProps = {
  result: EvalCaseResult;
};

function statusLabel(passed?: boolean): string {
  if (passed === true) {
    return "passed";
  }
  if (passed === false) {
    return "failed";
  }
  return "not returned";
}

function statusClassName(passed?: boolean): string {
  if (passed === true) {
    return "bg-emerald-50 text-emerald-700 ring-1 ring-emerald-200";
  }
  if (passed === false) {
    return "bg-red-50 text-red-700 ring-1 ring-red-200";
  }
  return "bg-slate-100 text-slate-700 ring-1 ring-slate-200";
}

function formatDetails(details?: Record<string, unknown>): string | null {
  if (!details || !Object.keys(details).length) {
    return null;
  }

  const missingKeywords = details.missing_keywords;
  if (Array.isArray(missingKeywords) && missingKeywords.length > 0) {
    return `Missing: ${missingKeywords.map(String).join(", ")}`;
  }

  return JSON.stringify(details);
}

function CheckRow({ check }: { check: EvalCheckResult }) {
  const details = formatDetails(check.details);

  return (
    <li className="rounded-md border border-slate-200 bg-slate-50 px-3 py-2">
      <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
        <span className="break-words text-sm font-medium text-slate-900">
          {check.name ?? "unnamed_check"}
        </span>
        <span
          className={`w-fit rounded-md px-2 py-1 text-xs font-semibold uppercase tracking-wide ${statusClassName(
            check.passed
          )}`}
        >
          {statusLabel(check.passed)}
        </span>
      </div>
      {details ? <p className="mt-2 break-words text-xs leading-5 text-slate-600">{details}</p> : null}
    </li>
  );
}

export function EvalResultCard({ result }: EvalResultCardProps) {
  const checks = result.checks ?? [];

  return (
    <article className="rounded-md border border-slate-200 bg-white p-4">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h3 className="text-base font-semibold text-slate-950">
            {result.name ?? "Untitled eval case"}
          </h3>
          <p className="mt-1 text-sm text-slate-500">Case ID: {result.case_id ?? "not returned"}</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <span
            className={`rounded-md px-2.5 py-1 text-xs font-semibold uppercase tracking-wide ${statusClassName(
              result.passed
            )}`}
          >
            {statusLabel(result.passed)}
          </span>
          <span className="rounded-md bg-slate-100 px-2.5 py-1 text-xs font-semibold uppercase tracking-wide text-slate-700">
            Score: {result.score ?? "n/a"}
          </span>
        </div>
      </div>

      <div className="mt-4">
        <h4 className="text-sm font-semibold uppercase tracking-wide text-slate-500">Checks</h4>
        {checks.length ? (
          <ul className="mt-2 space-y-2">
            {checks.map((check, index) => (
              <CheckRow check={check} key={`${check.name ?? "check"}-${index}`} />
            ))}
          </ul>
        ) : (
          <p className="mt-2 rounded-md border border-dashed border-slate-300 bg-slate-50 p-3 text-sm text-slate-500">
            No check-level results returned.
          </p>
        )}
      </div>
    </article>
  );
}
