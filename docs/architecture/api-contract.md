# API Contract

This document defines the initial HTTP API for Agent Reliability Workbench.

The API should stay small for the MVP and support the golden path first.

## Base path

Use:

- /api

## Health

GET /api/health

Purpose:

Check that the API service is running.

Response:

- status
- service

## List agent targets

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

## Create agent target

POST /agent-targets

Purpose:

Register an HTTP JSON agent target for future benchmark execution.

Request body:

- name
- agent_type: http_json
- endpoint_url
- auth_type: none or bearer
- auth_token
- version
- description

Public creation of `reference` targets is not supported.

## Get agent target

GET /agent-targets/{target_id}

Purpose:

Read one registered agent target without exposing raw auth tokens.

## Create agent run

POST /api/runs

Purpose:

Start a new incident triage agent run.

Request body:

- task

Example task:

A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

Response:

- id
- task
- status
- agent_under_test
- final_answer
- structured_output
- validation_status
- validation_errors
- agent_under_test
- latency_ms
- estimated_cost_usd
- created_at

## List runs

GET /api/runs

Purpose:

Show recent agent runs in the UI.

Response:

- items

Each item:

- id
- task
- status
- validation_status
- latency_ms
- estimated_cost_usd
- created_at

## Get run

GET /api/runs/{run_id}

Purpose:

Show one run with its final output and metadata.

Response:

- id
- task
- status
- final_answer
- structured_output
- validation_status
- validation_errors
- model
- agent_under_test
- started_at
- completed_at
- latency_ms
- estimated_cost_usd
- created_at

## Get run trace

GET /api/runs/{run_id}/trace

Purpose:

Show the trace timeline for a run.

Response:

- run_id
- events

Each event:

- id
- event_type
- title
- message
- metadata
- created_at

## Get run tool calls

GET /api/runs/{run_id}/tool-calls

Purpose:

Show tools used during a run.

Response:

- run_id
- tool_calls

Each tool call:

- id
- tool_name
- input
- output
- status
- latency_ms
- created_at

## List eval cases

GET /api/eval-cases

Purpose:

Show available demo eval cases.

Response:

- items

Each item:

- id
- name
- task
- expected_keywords
- expected_failure_modes

## Run eval case

POST /api/eval-cases/{eval_case_id}/run

Purpose:

Run one eval case through the agent.

Response:

- eval_case_id
- run_id
- passed
- score
- notes

## Error shape

Use one predictable error shape:

- error
- message
- details

## Notes

For MVP, the API can run synchronously.

Later, long-running agent executions can move to a background worker and expose polling or streaming.
