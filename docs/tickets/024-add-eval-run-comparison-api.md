# Ticket 024 — Add Eval Run Comparison API

## Goal

Add backend support for comparing eval runs so the platform can report how different agent configurations perform across benchmark incidents.

This ticket should expose comparison-ready backend data only. Do not build the frontend dashboard in this ticket.

## Context

Agent Reliability Workbench is moving toward a benchmarking, observability, and governance platform for tool-using AI agents.

The eval system already runs benchmark incidents and records eval results. Now we need an API that can compare eval runs across key metrics such as pass/fail count, score, latency, cost, guardrail failures, and configuration metadata.

This will later support the “compare models/prompts/workflows/toolsets” view.

## Scope

Backend only.

Add an API endpoint that returns comparison summaries across eval runs using existing eval result data where possible.

Possible endpoint shape:

http GET /api/evals/compare 

or, if the existing routing style prefers it:

http GET /api/eval-runs/compare 

Use the existing API naming conventions in the project.

## Files likely involved

- Existing eval result models
- Existing eval run models
- Eval runner/eval service layer
- API route/controller for eval comparison
- Response schemas
- Backend tests

Only touch frontend files if a tiny generated/shared API type update is unavoidable. Do not build UI.

## Required behavior

The backend should expose comparison data across eval runs.

For each eval run, return:

- eval_run_id
- created_at / run timestamp if available
- total_cases
- passed
- failed
- average_score
- average_latency
- average_cost
- guardrail_failures

Also include agent configuration metadata if available from Ticket 023 / existing run metadata:

- model_name
- prompt_version
- workflow_type
- toolset_version
- guardrail_mode

If some metadata does not exist yet in the database or is nullable, return null rather than inventing values.

## Aggregation rules

Use existing eval result data.

Suggested calculations:

- total_cases: count of eval results for the eval run
- passed: count where the result passed according to the existing pass/fail field or status
- failed: total cases minus passed, or count of explicit failed results if that is how the existing model works
- average_score: average of existing score field
- average_latency: average of existing latency field, if available
- average_cost: average of existing cost field, if available
- guardrail_failures: count of results where the existing result/status/failure reason indicates guardrail failure

Do not change the scoring methodology.

Do not add a new scoring system.

Do not rewrite the eval runner unless a very small change is needed to expose already-recorded fields.

## Empty-state behavior

The API must handle empty/no eval runs gracefully.

If there are no eval runs, return a valid empty response, for example:

json {   "items": [] } 

Do not return a 500.

## Response schema

Add typed response schemas.

Example shape:

json {   "items": [     {       "eval_run_id": "uuid-or-id",       "created_at": "2026-06-01T00:00:00Z",       "total_cases": 12,       "passed": 9,       "failed": 3,       "average_score": 0.82,       "average_latency": 1234.5,       "average_cost": 0.04,       "guardrail_failures": 1,       "model_name": "gpt-4.1",       "prompt_version": "v1",       "workflow_type": "single_agent",       "toolset_version": "incident_tools_v1",       "guardrail_mode": "strict"     }   ] } 

Adapt field types to match the project’s existing conventions.

## Tests

Add backend tests covering:

1. Empty eval runs return an empty comparison list.
2. A single eval run aggregates correctly:
   - total cases
   - passed
   - failed
   - average score
3. Multiple eval runs aggregate independently.
4. Average latency and cost are included if the fields exist.
5. Guardrail failures are counted correctly if the existing data supports this.
6. Metadata fields are returned when available and null when unavailable.

Use existing test patterns and fixtures.

## Acceptance criteria

- Backend exposes an eval comparison API.
- API returns one summary item per eval run.
- Comparison includes:
  - total cases
  - passed
  - failed
  - average score
  - average latency
  - average cost
  - guardrail failures
  - model/prompt/workflow/toolset/guardrail metadata if available
- API handles empty/no eval runs gracefully.
- Tests cover comparison aggregation.
- Existing eval scoring behavior is not changed.
- No dashboard UI is added.

## Validation commands

Run:

bash cd apps/api && python -m pytest git status 

## Guardrails

- Backend only unless tiny frontend type additions are unavoidable.
- Do not build dashboard UI.
- Do not alter scoring methodology unnecessarily.
- Prefer service-layer aggregation over putting complex logic directly in the route.
- Use existing eval result data where possible.
- Do not invent metadata values.
- Keep the implementation small and reviewable.