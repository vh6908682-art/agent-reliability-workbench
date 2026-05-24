# Ticket 007 — Structured Output Validation

## Goal

Add structured output validation for incident-triage agent responses.

The agent should return a predictable diagnosis object that can be validated with Pydantic before being stored or shown.

## Why this matters

AgentOps Workbench is not just a chat UI.

It should show whether an agent response followed the expected contract.

This ticket adds the first validation layer for safe, inspectable agent output.

## Scope

Work inside:

    apps/api/

Expected additions:

    apps/api/app/schemas/
      __init__.py
      incident_diagnosis.py

    apps/api/app/services/
      output_validator.py

Expected updates:

    apps/api/app/services/agent_loop.py
    apps/api/app/models/agent_run.py
    apps/api/app/api/routes/agent_runs.py

## Requirements

### 1. Incident diagnosis schema

Create a Pydantic schema for structured incident diagnosis.

Suggested fields:

- likely_cause
- evidence
- recommended_next_steps
- prevention
- confidence

Field notes:

- `likely_cause` should be a string.
- `evidence` should be a list of strings.
- `recommended_next_steps` should be a list of strings.
- `prevention` should be a list of strings.
- `confidence` should be one of `low`, `medium`, or `high`.

### 2. Prompt update

Update the agent prompt so the LLM is asked to return valid JSON matching the schema.

The prompt should still focus on:

- likely cause
- evidence from logs/context
- recommended next steps
- prevention or guardrail suggestion

### 3. Validation service

Create:

    app/services/output_validator.py

It should:

- accept raw LLM output
- parse JSON
- validate against the Pydantic schema
- return validation status and parsed output
- fail cleanly if JSON is invalid or schema validation fails

### 4. Persist validation result

Update agent run persistence to store:

- `structured_output`
- `validation_status`

Suggested statuses:

- `valid`
- `invalid_json`
- `schema_error`

If validation fails, still store the raw final answer.

### 5. API response update

Update `POST /agent-runs` response to include:

- run_id
- task
- answer
- structured_output
- validation_status
- context_sources

Update `GET /agent-runs/{run_id}` to include the same validation fields.

### 6. Tests

Add tests for:

- valid structured output
- invalid JSON
- schema validation error
- agent loop with mocked valid LLM output
- API response includes validation fields

Tests should not call OpenAI.

## Out of scope

Do not add:

- eval runner
- frontend
- approval workflows
- streaming
- embeddings
- LangGraph

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass.

With DB, seed data, and OpenAI key available:

    POST /agent-runs

should return:

- answer
- structured_output
- validation_status

The stored `agent_runs` row should include the validation result.

## Codex instructions

Implement only this ticket.

Keep validation simple and explicit.

Do not add eval runner, frontend, approvals, or LangGraph.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
