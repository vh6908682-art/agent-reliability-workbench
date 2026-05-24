# Ticket 017 — Polish Demo Flow

## Goal

Polish the golden-path demo so AgentOps Workbench feels cohesive, understandable, and impressive in a short walkthrough.

This ticket does not add major new architecture. It makes the existing MVP easier to demo.

## Why this matters

The project should clearly communicate its thesis:

Most AI agent demos show only the final answer. AgentOps Workbench shows the production layer behind the answer.

A viewer should quickly understand:

- What task the agent ran
- What tools or context it used
- What output it produced
- Whether the output passed validation
- What the trace looked like
- Whether guardrails or approvals were triggered
- How latency and cost looked
- Whether evals passed

## Scope

Improve the end-to-end demo experience around the Developer Support / Incident Triage Agent.

Focus on clarity, labels, default data, and simple UX polish.

## Backend requirements

Ensure the demo seed data supports one strong golden-path run.

The seeded example should involve:

    Kafka consumer failure
    customer update event
    duplicate key violation
    retry exhaustion
    likely idempotency or persistence issue
    recommended next steps

Confirm that the agent can use the existing mock logs, runbooks, schemas, and eval cases.

If needed, add one helper endpoint or script to reset demo data.

Suggested command:

    make seed

or:

    make demo-reset

Only add this if it fits the existing Makefile cleanly.

## Frontend requirements

Polish the main demo path.

The UI should make it easy to:

    start a demo run
    view the final diagnosis
    inspect trace steps
    see structured output validation
    see latency and cost
    see guardrail or approval status
    open eval results

Add clear copy and labels so the demo is understandable without extra explanation.

Example UI labels:

    Run Incident Triage Demo
    Final Diagnosis
    Evidence Used
    Tool Calls
    Structured Output
    Validation Result
    Guardrail Status
    Human Approval
    Latency and Cost
    Eval Result

## Demo defaults

Add a default task prompt in the UI:

    A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

The user should be able to run the demo without typing anything.

## Empty and loading states

Improve basic states:

    loading run
    running agent
    no trace steps yet
    no eval results yet
    failed to load run
    failed to start run

Keep these states simple and readable.

## Visual polish

Use consistent spacing, headings, and status badges.

Make the demo look intentional but not overdesigned.

Prioritize:

    clarity
    readable trace timeline
    obvious final answer area
    easy navigation between run, trace, evals, and approval

## Acceptance criteria

- The main demo can be run with one click.
- The default incident triage task is prefilled or easily available.
- The final diagnosis is easy to find.
- Trace steps are easy to inspect.
- Structured output validation result is visible.
- Latency and cost metrics are visible if Ticket 015 is complete.
- Guardrail and approval status are visible if Tickets 013 and 014 are complete.
- Eval results are reachable from the demo flow.
- Loading and empty states are handled gracefully.
- The UI feels cohesive enough for a portfolio demo.

## Out of scope

- New agent capabilities.
- New eval methodology.
- Auth.
- Workspaces.
- Advanced dashboards.
- Streaming UI.
- Dark mode perfection.
- Full design system.

## Suggested Codex prompt

Implement Ticket 017 using the existing project structure.

Polish the golden-path demo flow for the Developer Support / Incident Triage Agent.

Make the demo runnable with one obvious default incident prompt, improve labels and empty/loading states, and make final diagnosis, trace steps, structured output validation, guardrail status, approval status, latency/cost, and eval results easy to find.

Do not introduce major new architecture or advanced dashboard features.
