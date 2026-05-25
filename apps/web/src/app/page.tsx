const navItems = ["Runs", "Traces", "Validation", "Evals", "Guardrails", "Approvals"];

const workbenchCards = [
  {
    title: "Run Agent",
    eyebrow: "Incident triage",
    description: "Start the developer support workflow for backend failures and inspect each step."
  },
  {
    title: "Trace Viewer",
    eyebrow: "Tool calls",
    description: "Review retrieved context, tool inputs, outputs, timing, and execution order."
  },
  {
    title: "Eval Results",
    eyebrow: "Deterministic checks",
    description: "See pass/fail outcomes that verify the diagnosis and recommended actions."
  },
  {
    title: "Structured Output",
    eyebrow: "Schema validation",
    description: "Confirm the final response matches the contract expected by downstream systems."
  },
  {
    title: "Guardrails",
    eyebrow: "Policy decisions",
    description: "Surface blocked actions, risk labels, and safety checks before release."
  },
  {
    title: "Approvals",
    eyebrow: "Human review",
    description: "Queue risky mock actions for explicit approval before they can proceed."
  }
];

export default function Home() {
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
                href={`#${item.toLowerCase()}`}
                key={item}
              >
                {item}
              </a>
            ))}
          </nav>
        </div>
      </div>

      <section className="mx-auto grid max-w-7xl gap-6 px-6 py-8 lg:grid-cols-[280px_1fr]">
        <aside className="rounded-lg border border-slate-200 bg-white p-5">
          <h2 className="text-sm font-semibold uppercase tracking-wide text-slate-500">
            MVP Surface
          </h2>
          <ul className="mt-4 space-y-3 text-sm text-slate-700">
            <li>Submit an incident-like backend failure.</li>
            <li>Inspect the reliability layer behind the answer.</li>
            <li>Approve or block risky mock actions.</li>
          </ul>
        </aside>

        <div>
          <div className="mb-5">
            <h2 className="text-xl font-semibold text-slate-950">Workbench Areas</h2>
            <p className="mt-1 text-sm leading-6 text-slate-600">
              These placeholders define the first product shell. Backend integration comes later.
            </p>
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {workbenchCards.map((card) => (
              <article
                className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm"
                id={card.title.split(" ")[0].toLowerCase()}
                key={card.title}
              >
                <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
                  {card.eyebrow}
                </p>
                <h3 className="mt-3 text-lg font-semibold text-slate-950">{card.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-600">{card.description}</p>
              </article>
            ))}
          </div>
        </div>
      </section>
    </main>
  );
}
