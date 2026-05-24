# Ticket 006 — Run Trace Capture

## Goal

Persist agent runs and trace steps when the incident-triage agent executes.

This ticket should connect the golden path agent loop to the core data model from Ticket 003.

## Why this matters

The main thesis of AgentOps Workbench is showing the production layer behind an agent answer.

This ticket makes the backend store:

- the submitted task
- final answer
- retrieved context steps
- LLM call step
- latency
- status
- basic run metadata

## Scope

Work inside:

    apps/api/

Expected updates:

    apps/api/app/services/
      agent_loop.py
      context_retriever.py
      llm_client.py

    apps/api/app/api/routes/
      agent_runs.py

    apps/api/app/models/
      agent_run.py
      trace_step.py

Expected additions if useful:

    apps/api/app/services/
      trace_recorder.py

## Requirements

### 1. Persist AgentRun

When `POST /agent-runs` is called, create an `agent_runs` row.

Store:

- task
- status
- final_answer
- latency_ms
- structured_output if available
- validation_status if available

For now:

- status can be `completed` or `failed`
- structured_output can be null
- validation_status can be null

### 2. Persist TraceStep records

Create trace steps for major agent operations.

Minimum steps:

- context retrieval
- LLM prompt/call
- final response

Each trace step should include:

- agent_run_id
- step_index
- step_type
- name
- input
- output
- latency_ms

Suggested step types:

- `retrieval`
- `llm`
- `response`

### 3. API response includes run id

Update `POST /agent-runs` response to include:

    {
      "run_id": "...",
      "task": "...",
      "answer": "...",
      "context_sources": [...]
    }

### 4. Add run detail endpoint

Add:

    GET /agent-runs/{run_id}

Response should include:

- run metadata
- final answer
- trace steps ordered by step_index

This endpoint will support the frontend run viewer later.

### 5. Error handling

If the agent fails:

- store an `agent_runs` row with status `failed`
- include a clean error response
- do not expose secrets
- record useful failure info in trace output if safe

### 6. Tests

Add tests for:

- successful run persistence with mocked LLM
- trace step ordering
- run detail endpoint
- failed run persistence with mocked failure

Tests should not call OpenAI.

Tests should use isolated DB behavior, mocks, or test fixtures.

## Out of scope

Do not add:

- structured output validation
- eval runner
- frontend
- guardrail approvals
- streaming
- embeddings

## Acceptance criteria

From `apps/api`:

    python -m pytest

should pass without calling OpenAI.

With DB, migrations, seed data, and OpenAI key available:

    curl -X POST http://localhost:8000/agent-runs \
      -H "Content-Type: application/json" \
      -d '{"task":"A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps."}'

should return a `run_id`.

Then:

    curl http://localhost:8000/agent-runs/<run_id>

should return the run and ordered trace steps.

## Codex instructions

Implement only this ticket.

Keep the diff focused on persistence and trace capture.

Do not add validation, eval execution, frontend, or approvals yet.

After implementation, show:

1. files changed
2. commands run
3. test result
4. any assumptions made
