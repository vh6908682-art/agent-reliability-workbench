# Demo Script

This document defines the MVP demo path for AgentOps Workbench.

The demo should show why the product exists: agent answers are not enough. Developers need to inspect the production layer behind the answer.

## Demo thesis

Most AI agent demos only show the final response.

AgentOps Workbench shows:

- what the agent looked at
- what tools it used
- what it ignored
- whether the final output matched a schema
- how long it took
- what it likely cost
- whether it passed an eval

## Golden path

The user runs a Developer Support / Incident Triage Agent.

Demo task:

A Kafka consumer failed while processing a customer update event. Logs show duplicate key violation and retry exhaustion. Diagnose likely cause and recommend next steps.

## Demo flow

## 1. Open dashboard

Show:

- recent runs
- run status
- validation status
- latency
- estimated cost

Message:

This is not just a chatbot. This is an operations workbench for tool-using agents.

## 2. Start a new run

User submits the incident triage task.

The backend creates a run and records trace events.

## 3. Show final answer

The agent returns:

- summary
- likely root cause
- recommended next steps
- confidence
- evidence

The answer should mention that duplicate key violations often point to idempotency, event replay, ordering, or stale state issues.

## 4. Show trace timeline

Show events like:

- run started
- mock logs loaded
- runbook document loaded
- LLM called
- structured output validated
- run completed

Message:

This lets developers debug the agent, not just read its answer.

## 5. Show tool calls

Show the seed log lookup and document lookup as tool-like steps.

For MVP these can be simulated tools backed by local seed files.

## 6. Show validation result

Show whether the final output passed the expected Pydantic schema.

If validation fails, show validation errors.

## 7. Run eval

Run the same task as an eval case.

Show:

- pass or fail
- score
- expected keywords found
- missing expected behavior

If the app is not running live, use the compact sample artifacts in `docs/examples/` to show the agent run, trace, eval run, and eval comparison shapes.

## 8. Closing story

AgentOps Workbench helps teams answer:

- Can we trust this agent?
- What did it use as evidence?
- Did it follow the expected output contract?
- Did quality regress?
- Is it ready for a safer release?

## MVP demo constraints

The first demo does not need:

- real Kafka
- real logs
- real ticketing integration
- real production approvals
- streaming traces
- auth

Seed files are enough for the first credible demo.
