# Ticket 025 — Build Eval Comparison Dashboard UI

## Goal

Add a simple frontend benchmark comparison view that displays eval run comparison data from the backend API added in Ticket 024.

This ticket should make the comparison capability visible in the UI without redesigning the dashboard or adding heavy polish.

## Context

Agent Reliability Workbench is moving toward a benchmarking, observability, and governance platform for tool-using AI agents.

Ticket 024 added backend support for comparing eval runs/configurations. Ticket 025 should consume that API and display the comparison data in a simple readable table.

The purpose is to let a user quickly compare how different agent runs/configurations performed across benchmark incidents.

## Scope

Frontend-focused.

Build a simple benchmark comparison section/table in the existing dashboard or eval area.

Do not redesign the entire app.

Do not add charts unless there is already an extremely simple existing pattern and it requires almost no extra work.

Do not add new UI dependencies.

## Files likely involved

- Frontend API client
- Frontend type definitions
- Eval comparison component
- Main page/dashboard layout
- Existing eval UI components if available

Possible files may include:

- apps/web/src/lib/api.ts
- apps/web/src/app/page.tsx
- apps/web/src/components/...
- Existing eval-related frontend files

Use the project’s current frontend structure and naming conventions.

## Required behavior

The frontend should fetch eval comparison data from the backend comparison API.

Expected API source from Ticket 024:

http GET /api/evals/compare 

or whatever endpoint was actually implemented in Ticket 024.

The UI should display a simple benchmark comparison table.

Each row should represent one eval run/configuration.

The table should display:

- Eval run/config identifier
- Model name, if available
- Prompt version, if available
- Workflow type, if available
- Toolset version, if available
- Guardrail mode, if available
- Total cases
- Passed
- Failed
- Pass rate
- Average score
- Average latency
- Average cost
- Guardrail failures

If metadata fields are missing/null, show a readable fallback such as —.

## Pass rate calculation

If the API does not already return pass rate, calculate it in the frontend:

ts passRate = total_cases > 0 ? passed / total_cases : 0 

Display it as a percentage, for example:

text 75% 

Do not change backend scoring behavior.

Do not invent new metrics.

## UI states

The component must handle:

1. Loading state  
   Show a small loading message or placeholder.

2. Error state  
   Show a readable error message if the API request fails.

3. Empty state  
   If the API returns no comparison items, show a friendly empty state such as:

text No eval runs available yet. Run an eval to compare benchmark results. 

4. Success state  
   Show the comparison table.

## UI placement

Add the comparison view in a practical location in the existing dashboard.

Preferred approach:

- Add a compact “Eval Comparison” or “Benchmark Comparison” section near the existing eval/demo area.
- Keep the existing run/trace/validation UI intact.
- Avoid layout churn.

This should feel like an MVP comparison panel, not a full analytics dashboard.

## Formatting expectations

Keep formatting simple and readable.

Suggested formatting:

- Average score: 2 decimal places
- Pass rate: whole percentage or 1 decimal place
- Average latency: milliseconds if that is how the API returns it
- Average cost: dollar-style if cost is numeric, for example $0.04

Be defensive with missing/null values.

Do not let null/undefined values break the UI.

## Type definitions

Add or update frontend TypeScript types for the eval comparison response.

Example shape:

ts export type EvalComparisonItem = {   eval_run_id: string;   created_at?: string | null;   total_cases: number;   passed: number;   failed: number;   average_score?: number | null;   average_latency?: number | null;   average_cost?: number | null;   guardrail_failures: number;   model_name?: string | null;   prompt_version?: string | null;   workflow_type?: string | null;   toolset_version?: string | null;   guardrail_mode?: string | null; };  export type EvalComparisonResponse = {   items: EvalComparisonItem[]; }; 

Adapt names to match the actual backend contract from Ticket 024.

## API client

Add a small API client function for fetching comparison data.

Example:

ts export async function getEvalComparison(): Promise<EvalComparisonResponse> {   // use existing fetch/client pattern } 

Use the project’s existing API client conventions.

## Tests / validation

Run:

bash cd apps/web && npm run typecheck 

If the API contract or backend schemas are touched, also run:

bash cd apps/api && python -m pytest 

## Acceptance criteria

- Frontend fetches eval comparison API.
- UI displays a simple benchmark comparison table.
- Table includes:
  - eval run/config identifier
  - pass rate
  - average score
  - average latency
  - average cost
  - guardrail failures
  - available config metadata
- UI handles loading, error, and empty states.
- No new UI dependencies are added.
- Existing dashboard is not redesigned.
- Existing eval/run/trace functionality remains intact.
- TypeScript typecheck passes.

## Guardrails

- Do not redesign the entire dashboard.
- Do not build a complex analytics page.
- Do not add charts unless extremely small and already supported by existing code.
- Do not add new UI libraries.
- Do not alter eval scoring logic.
- Do not alter backend behavior unless a tiny contract adjustment is required.
- Keep the UI readable and MVP-level.
- Prefer small, localized component changes.