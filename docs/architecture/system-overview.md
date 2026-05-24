# System Overview

AgentOps Workbench is a monorepo developer platform for running, tracing, evaluating, debugging, and safely releasing tool-using LLM agents.

The MVP focuses on one golden path: a Developer Support / Incident Triage Agent.

Example user task:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

## Core user flow

1. User opens the web app.
2. User selects or enters an incident-style task.
3. Backend starts an agent run.
4. Agent reads seeded logs and documents.
5. Agent produces:
   - diagnosis
   - likely root cause
   - recommended next steps
   - confidence level
   - structured JSON output
6. Platform stores the run, trace events, tool calls, validation result, latency, and estimated cost.
7. User views the trace timeline in the UI.
8. User can inspect reasoning artifacts, tool calls, errors, and final structured output.
9. User can run an eval case against expected behavior.
10. Later releases can add approvals, guardrails, and deployment promotion.

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

### API service

Location: `apps/api`

Responsibilities:

- Expose HTTP endpoints for the frontend.
- Run the custom agent loop.
- Validate final outputs with Pydantic.
- Persist runs, trace events, tool calls, eval cases, and eval results.
- Estimate latency and cost metadata.
- Read seed logs and seed documents for the demo agent.

### Database

PostgreSQL stores durable platform data:

- agent runs
- trace events
- tool calls
- documents
- eval cases
- eval results
- approval records, later

### Seed data

Location: `seed/`

Seed data exists so the project has a reliable demo without needing external company data.

Planned seed folders:

- `seed/documents/`
- `seed/mock_logs/`
- `seed/eval_cases/`

## Initial backend architecture

The MVP should use a simple custom agent loop before adding heavier orchestration.

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
