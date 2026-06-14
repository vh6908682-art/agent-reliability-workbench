# API Contract

This document defines the current local HTTP API for Agent Reliability Workbench.

The API stays small for the MVP and supports the reliability loop: run, trace, validate, govern, evaluate, and compare.

## Base URL

Local development uses:

- http://localhost:8000

Routes are mounted at the service root, not under an `/api` prefix.

## Health

GET /health

Purpose:

Check that the API service is running.

Response:

- status
- service: agent-reliability-workbench-api

## List Agent Targets

GET /agent-targets

Purpose:

List the registered agents that can be benchmarked. The default system-managed `ReferenceIncidentAgent` is always ensured.

Response:

- id
- name
- agent_type
- endpoint_url
- auth_type
- has_auth_token
- version
- description
- is_default
- created_at
- updated_at

The response does not include raw `auth_token` values.

## Create Agent Target

POST /agent-targets

Purpose:

Register an HTTP JSON agent target for benchmark execution.

Request body:

- name
- agent_type: http_json
- endpoint_url
- auth_type: none or bearer
- auth_token
- version
- description

Public creation of `reference` targets is not supported.

## Get Agent Target

GET /agent-targets/{target_id}

Purpose:

Read one registered agent target without exposing raw auth tokens.

## Test Agent Target

POST /agent-targets/{target_id}/test

Purpose:

Verify that a reference target is available or that an HTTP JSON target returns a valid structured result.

Response:

- ok
- agent_target_id
- agent_name
- agent_type
- message
- error

## Create Agent Run

POST /agent-runs

Purpose:

Start a new incident investigation run against the default reference Agent Target.

Request body:

- task
- prompt_version

Example task:

A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

Response:

- run_id
- task
- answer
- structured_output
- validation_status
- guardrail_result
- approval_status
- requires_approval
- latency_ms
- model_name
- prompt_version
- workflow_type
- toolset_name
- guardrail_mode
- agent_under_test
- input_tokens
- output_tokens
- total_tokens
- estimated_cost_usd
- context_sources

## List Runs

GET /agent-runs

Purpose:

Show recent agent runs in the UI.

Response:

- list of run summaries

Each summary:

- run_id
- task
- status
- created_at
- started_at
- completed_at
- latency_ms
- model_name
- input_tokens
- output_tokens
- total_tokens
- estimated_cost_usd
- guardrail_status
- approval_status
- requires_approval
- agent_under_test

## Get Run

GET /agent-runs/{run_id}

Purpose:

Show one run with its final output, metadata, approval state, and trace steps.

Response:

- run_id
- task
- status
- final_answer
- structured_output
- validation_status
- guardrail_result
- approval
- started_at
- completed_at
- latency_ms
- cost_usd
- estimated_cost_usd
- model_name
- prompt_version
- workflow_type
- toolset_name
- guardrail_mode
- agent_under_test
- input_tokens
- output_tokens
- total_tokens
- created_at
- updated_at
- trace_steps

Each trace step:

- id
- step_index
- step_type
- name
- input
- output
- latency_ms
- created_at

## Get Run Approval

GET /agent-runs/{run_id}/approval

Response:

- run_id
- status
- reviewer_note
- requires_approval
- updated_at

## Update Run Approval

POST /agent-runs/{run_id}/approval

Request body:

- status: pending_review, approved, or blocked
- reviewer_note

Response is the same approval shape returned by `GET /agent-runs/{run_id}/approval`.

## Run Eval Suite

POST /evals/run

Purpose:

Run all deterministic benchmark eval cases through the selected Agent Under Test.

Request body:

- prompt_version
- agent_target_id

If `agent_target_id` is omitted, the backend uses the default `ReferenceIncidentAgent` target.

Response:

- total
- passed
- failed
- agent_under_test
- results

Each result:

- case_id
- name
- category
- difficulty
- risk_level
- expected_capability
- workflow_tags
- passed
- score
- checks

## Compare Eval Runs

GET /evals/comparison

Response:

- items

Each item:

- eval_run_id
- created_at
- total_cases
- passed
- failed
- pass_rate
- avg_score
- avg_latency
- avg_cost
- guardrail_failure_count
- model_name
- prompt_version
- workflow_type
- toolset_name
- guardrail_mode
- agent_under_test

## External HTTP JSON Agent Contract

HTTP JSON Agent Targets receive an `AgentTask` JSON object and must return:

- diagnosis: string
- evidence: list of strings
- next_steps: list of strings
- confidence: optional string

The adapter maps those fields into ARW's structured incident diagnosis shape and then runs the same validation, guardrail, scoring, and comparison flow.

See `examples/http-json-agent/` for a runnable local target.

## Error Shape

Errors use FastAPI's `detail` field with a predictable object where practical:

- error
- message
- details

## Notes

For MVP, the API runs synchronously.

Later, long-running agent executions can move to a background worker and expose polling or streaming.
