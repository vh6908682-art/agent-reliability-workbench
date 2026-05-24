# Ticket 011 — Trace Viewer UI

## Goal

Create the first frontend trace viewer for agent runs.

The UI should let a user inspect what happened during an incident triage run: the prompt, tool calls, intermediate steps, final structured output, validation status, and basic timing/cost fields if available.

## Why this matters

The core thesis of AgentOps Workbench is that production agent systems need visibility into what happened behind the final answer.

This ticket makes that thesis visible in the product.

## Scope

Add a trace viewer section to the frontend.

The trace viewer should display data from an existing run/trace response if the backend already exposes it.

Display the trace in a clean, readable layout with sections such as:

- Run summary
- Input prompt
- Agent steps
- Tool calls
- Retrieved documents or evidence
- Structured output
- Validation result
- Errors, if any
- Latency and cost placeholders, if available

## Non-goals

Do not build advanced graph visualization.

Do not add replay functionality.

Do not add filtering/search yet.

Do not add eval results UI yet.

Do not redesign the whole frontend.

Do not create fake backend trace logic if trace capture already exists.

## Expected implementation shape

Add or update frontend files similar to:

    frontend/components/TraceViewer.tsx
    frontend/components/TraceStepCard.tsx
    frontend/components/ToolCallCard.tsx
    frontend/lib/api.ts
    frontend/app/page.tsx

The trace viewer can initially render the latest run result from the agent run flow.

If the backend exposes a route such as:

    GET /api/runs/{run_id}
    GET /api/traces/{run_id}

use the existing route.

If no separate trace fetch endpoint exists yet, display trace fields already returned by the agent run response.

## Display expectations

Each trace step should be easy to scan.

Example layout:

    Run ID
    Status
    Started at
    Completed at
    Latency

    Input

    Steps
      Step 1: model_call
      Step 2: tool_call
      Step 3: validation

    Final Output

    Validation
      passed: true

Tool calls should show:

- Tool name
- Input
- Output summary
- Status
- Error, if any

## Acceptance criteria

- Frontend shows a trace viewer after a successful agent run
- Run ID is displayed if available
- Agent steps are displayed if available
- Tool calls are displayed if available
- Structured output is displayed
- Validation status is displayed if available
- Missing optional fields do not crash the UI
- Empty trace data shows a useful placeholder
- Existing frontend checks still pass
- Existing backend tests still pass

## Suggested tests/checks

Manual checks are enough if no frontend test setup exists yet:

    cd frontend
    npm run dev

Then verify:

- Run the default incident triage prompt
- Trace viewer appears after success
- Tool calls or trace steps render clearly
- Missing trace fields do not break the page
- Backend error state still displays cleanly

## Codex guidance

Keep this focused on UI display.

Do not introduce a graph library.

Do not add complex state management.

Prefer simple cards and readable JSON sections where needed.

Reuse existing API helpers and response types where possible.

