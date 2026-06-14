# System Overview

Agent Reliability Workbench is a monorepo developer platform for running, tracing, evaluating, debugging, and governing tool-using AI agents.

The MVP focuses on one golden path: benchmarking an incident-investigation Agent Under Test.
The bundled `ReferenceIncidentAgent` is the default reference target for local demos. Registered HTTP JSON Agent Targets can also be benchmarked through the same harness. The workbench owns the benchmark cases, trace capture, validation, guardrails, scoring, and comparison around whichever target is selected.

Example user task:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

## Core user flow

1. User opens the web app.
2. User selects or enters an incident-style task.
3. Backend starts an agent run against the selected Agent Under Test.
4. The default `ReferenceIncidentAgent` reads seeded logs and documents.
5. Agent produces:
   - diagnosis
   - likely root cause
   - recommended next steps
   - confidence level
   - structured JSON output
6. Platform stores the run, trace events, tool calls, validation result, latency, and estimated cost.
7. User views the trace timeline in the UI.
8. User can inspect reasoning artifacts, tool calls, errors, and final structured output.
9. User can run deterministic evals against the selected Agent Target.
10. User can compare eval runs by agent target, prompt/config metadata, quality, latency, cost, and guardrail outcomes.

## MVP components

### Web app

Location: `apps/web`

Responsibilities:

- Provide the main developer UI.
- Start new agent runs.
- Show run history.
- Show trace timeline.
- Show tool calls.
- Show structured final output.
- Show validation and eval results.
- Register and test HTTP JSON Agent Targets.

### API service

Location: `apps/api`

Responsibilities:

- Expose HTTP endpoints for the frontend.
- Run the selected Agent Under Test through the backend adapter.
- Validate final outputs with Pydantic.
- Persist runs, trace events, tool calls, eval cases, and eval results.
- Manage Agent Targets, including the default reference target and external HTTP JSON targets.
- Estimate latency and cost metadata.
- Read seed logs and seed documents for the bundled reference agent.

### Database

PostgreSQL stores durable platform data:

- agent runs
- trace events
- tool calls
- documents
- eval cases
- eval results
- agent targets
- approval records

### Seed data

Location: `seed/`

Seed data exists so the project has a reliable demo without needing external company data.

Planned seed folders:

- `seed/documents/`
- `seed/mock_logs/`
- `seed/eval_cases/`

## Initial backend architecture

The MVP uses a simple Agent Under Test adapter before adding heavier orchestration.
The default adapter wraps the existing incident triage loop as `ReferenceIncidentAgent`; it is the reference benchmark subject, not the benchmark harness itself. The HTTP JSON adapter lets external agents receive the same eval tasks through a stable JSON contract.

The loop should roughly be:

1. Receive task.
2. Create run record.
3. Add trace event: run started.
4. Load relevant seed logs/documents.
5. Call LLM.
6. Validate structured output.
7. Store final answer.
8. Store trace events and metadata.
9. Return run response.

LangGraph may be introduced later if the workflow becomes graph-shaped enough to justify it.

## Non-goals for MVP

The MVP should not try to build:

- multi-tenant auth
- complex RBAC
- enterprise deployment controls
- real production log ingestion
- real Kafka integration
- real ticketing integration
- advanced agent orchestration
- large-scale eval infrastructure
- billing
- cloud deployment automation

## Engineering principle

Codex should be used as the implementation engineer.

This means:

- keep tickets small
- keep files focused
- avoid giant rewrites
- ask Codex to implement one slice at a time
- test each slice before moving forward
- prefer boring, understandable code
