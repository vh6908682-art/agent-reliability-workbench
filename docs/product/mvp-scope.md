# MVP Scope

Agent Reliability Workbench is a developer platform for running, tracing, evaluating, debugging, and governing tool-using AI agents.

The MVP focuses on one golden path:

Developer Support / Incident Triage Agent.

A user submits an incident-like task:

> A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

## MVP User Journey

1. User starts a new incident triage run.
2. Backend creates a run record.
3. Agent calls mock tools.
4. System records trace events.
5. Agent produces structured diagnosis JSON.
6. Output validator checks the schema.
7. Eval engine scores the run.
8. UI shows final output, trace timeline, tool calls, validation result, and eval result.

## Must-Have MVP Features

- Agent run creation
- Trace event storage
- Structured output validation
- Typed tool registry
- Mock incident triage tools
- Guardrail and approval model
- Deterministic eval engine
- Demo-friendly dashboard

## MVP Tools

- search_logs
- validate_payload
- lookup_service_config
- create_ticket_mock

## Out of Scope for MVP

Do not build these first:

- authentication
- billing
- multi-tenancy
- Kubernetes
- real Jira integration
- real Slack integration
- complex multi-agent orchestration
- fine-tuning
- RLHF

## Success Criteria

The MVP is successful when a local user can run the incident triage workflow and inspect:

- final structured diagnosis
- tool-call trace
- validation result
- eval result
- latency/cost placeholders
- guardrail/approval behavior
