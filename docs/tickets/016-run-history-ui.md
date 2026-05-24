# Ticket 016 — Run History UI

## Goal

Create a simple run history page so users can browse previous agent runs and open a run detail view.

This gives the demo a production-platform feel: users can see past runs, compare outcomes, and inspect traces after the fact.

## Why this matters

AgentOps Workbench should not feel like a one-shot chatbot.

A real agent platform needs a history of runs showing:

- What task was run
- When it ran
- Whether it succeeded
- How long it took
- How much it cost
- Whether guardrails or approvals were involved

## Scope

Add a frontend page that lists recent agent runs.

The page should pull from the backend API and show enough metadata to understand each run at a glance.

## Backend requirements

If not already available, add or confirm an endpoint like:

    GET /api/runs

It should return a list of recent runs.

Each run item should include:

    id
    task
    status
    created_at
    completed_at
    latency_ms
    model_name
    estimated_cost_usd
    guardrail_status
    approval_status

If guardrail or approval fields do not exist yet, return null or omit them cleanly.

## Frontend requirements

Create a run history page.

Suggested route:

    /runs

Show a table or card list with:

    Run ID
    Task summary
    Status
    Created time
    Latency
    Estimated cost
    Guardrail status
    Approval status

Each row/card should link to the run detail page.

Suggested detail route:

    /runs/[id]

If the detail page already exists from earlier tickets, link to it.

If not, create a minimal placeholder that fetches the run detail and displays raw structured data.

## UI behavior

Keep it simple and demo-friendly.

Use clear status labels:

    succeeded
    failed
    pending_approval
    blocked_by_guardrail

Format latency nicely:

    1420 ms -> 1.42s

Format cost nicely:

    0.0021 -> $0.0021

If data is missing, show:

    —

Do not overbuild filtering, sorting, or charts yet.

## Acceptance criteria

- A user can open the run history page.
- Recent runs are fetched from the backend.
- Each run shows task, status, time, latency, and estimated cost.
- Guardrail and approval status display if available.
- Each run links to a detail page.
- Missing values are handled gracefully.
- UI is clean enough for the demo.
- Existing frontend and backend tests still pass.

## Out of scope

- Pagination.
- Search.
- Filtering.
- Sorting.
- Charts.
- Aggregate analytics.
- User authentication.
- Multi-project workspaces.

## Suggested Codex prompt

Implement Ticket 016 using the existing frontend and backend structure.

Add a simple run history UI at /runs that fetches recent agent runs from the backend and displays task, status, created time, latency, estimated cost, guardrail status, and approval status.

Each row should link to a run detail page. If a run detail page already exists, reuse it. If not, create a minimal placeholder detail page.

Keep the UI simple and demo-friendly. Do not add pagination, charts, auth, or workspace features.
