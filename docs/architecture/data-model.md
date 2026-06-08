# Data Model

This document defines the initial PostgreSQL data model for Agent Reliability Workbench.

The MVP schema should stay small and support the golden path first: running, tracing, validating, and evaluating an incident triage agent.

## Tables

## agent_runs

Represents one user-triggered agent execution.

Columns:

- id
- task
- status
- final_answer
- structured_output
- validation_status
- validation_errors
- model
- started_at
- completed_at
- latency_ms
- estimated_cost_usd
- created_at

Statuses:

- queued
- running
- succeeded
- failed

## trace_events

Represents the timeline of what happened during a run.

Columns:

- id
- run_id
- event_type
- title
- message
- metadata
- created_at

Event types:

- run_started
- document_loaded
- tool_called
- llm_called
- validation_passed
- validation_failed
- run_completed
- run_failed

## tool_calls

Represents tool usage during an agent run.

Columns:

- id
- run_id
- tool_name
- input
- output
- status
- latency_ms
- created_at

Statuses:

- succeeded
- failed

## documents

Represents seed knowledge available to the demo agent.

Columns:

- id
- title
- source
- content
- metadata
- created_at

For MVP, documents can be loaded from seed files first. Database persistence can come later.

## eval_cases

Represents predefined test cases for agent quality.

Columns:

- id
- name
- task
- expected_keywords
- expected_failure_modes
- metadata
- created_at

## eval_results

Represents one evaluation run against one eval case.

Columns:

- id
- eval_case_id
- run_id
- passed
- score
- notes
- created_at

## Relationships

- One agent_run has many trace_events.
- One agent_run has many tool_calls.
- One eval_case has many eval_results.
- One eval_result may reference one agent_run.

## JSON fields

Use JSONB for flexible metadata:

- agent_runs.structured_output
- agent_runs.validation_errors
- trace_events.metadata
- tool_calls.input
- tool_calls.output
- documents.metadata
- eval_cases.expected_keywords
- eval_cases.expected_failure_modes
- eval_cases.metadata

## MVP structured output shape

The incident triage agent should return:

- summary
- likely_root_cause
- recommended_next_steps
- confidence
- evidence

Confidence should be one of:

- low
- medium
- high

## First useful database slice

The first migration should support:

- creating an agent run
- appending trace events
- storing final structured output
- reading a run by ID
