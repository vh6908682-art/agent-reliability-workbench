# Architecture Reconciliation Checklist

## Purpose

This checklist is used to align the existing architecture documentation with the expanded direction of Agent Reliability Workbench.

The goal is not to rewrite every architecture doc.

The goal is to make sure the existing docs no longer frame the project as only an incident triage demo, while still preserving the current MVP architecture and implementation reality.

Agent Reliability Workbench should now be framed as a benchmark, observability, and governance platform for tool-using AI agents.

The incident-investigation flow is the first benchmark environment.

## Reconciliation Strategy

Use a light-touch update strategy.

Do not delete existing architecture content unless it is clearly wrong.

Do not over-expand docs with speculative future features.

Prefer small edits that clarify:

- the current MVP behavior
- the benchmark direction
- how incident investigation fits into the larger platform
- which parts are implemented now
- which parts are future roadmap

## Docs To Review

Review these files if they exist:

```text
docs/architecture/system-overview.md
docs/architecture/data-model.md
docs/architecture/api-contract.md
docs/architecture/codex-workflow.md
docs/architecture/demo-script.md
```

Also review:

```text
README.md
AGENTS.md
docs/PROJECT_VISION.md
docs/BENCHMARK_SPEC.md
docs/EVAL_METHODOLOGY.md
docs/ROADMAP.md
```

## Global Language Updates

Search existing docs for language that makes the project sound too narrow.

Replace narrow framing such as:

```text
AI incident triage demo
incident debugging app
Kafka error demo
production incident chatbot
debugging assistant demo
```

With broader framing such as:

```text
agent reliability workbench
benchmark environment for tool-using agents
agent observability and governance platform
incident investigation benchmark
repeatable agent evaluation workflow
```

Do not remove the incident-investigation language entirely.

Instead, clarify that incident investigation is the first benchmark environment.

## System Overview Checklist

File:

```text
docs/architecture/system-overview.md
```

Check that this doc explains:

- the platform runs tool-using AI agents against benchmark scenarios
- the first benchmark environment is incident investigation
- a run captures the agent’s process, not only the final answer
- traces, tool calls, validation, guardrails, approvals, evals, latency, token usage, and cost are part of the system
- the frontend helps inspect agent behavior
- the backend manages runs, tools, validation, evals, and persistence

Avoid:

- describing the system as only a chatbot
- describing the Kafka incident as the whole product
- introducing future architecture that does not exist yet

Suggested sentence to include:

> The current incident-investigation workflow is the first benchmark environment used to prove the platform's core reliability loop: run, trace, validate, govern, evaluate, and compare.

## Data Model Checklist

File:

```text
docs/architecture/data-model.md
```

Check that this doc accurately describes current entities such as:

- Agent
- PromptVersion
- AgentRun
- RunStep
- TraceEvent
- ToolDefinition
- Approval
- EvalCase
- EvalRun
- EvalResult

If scenario metadata does not exist yet in the database, do not pretend it does.

Instead, mention it as planned or fixture-level if appropriate.

Useful clarification:

> Benchmark scenarios may initially be represented through seed data, eval cases, mock tool responses, and documentation. A first-class scenario entity may be added later if needed.

Check whether eval entities are clearly connected to benchmark behavior.

The data model should make it clear that evals are not generic tests only. They are the mechanism for measuring agent reliability across benchmark scenarios.

## API Contract Checklist

File:

```text
docs/architecture/api-contract.md
```

Check that this doc describes the APIs in terms of the current reliability loop:

- create/run an agent
- inspect run detail
- inspect trace
- list recent runs
- update approval status
- run evals
- retrieve eval results

Make sure API descriptions align with actual implemented routes.

Do not add API endpoints that do not exist yet unless clearly marked as future.

Useful clarification:

> The API surface supports the MVP reliability loop: create a run, inspect the trace, validate structured output, review guardrails and approval status, and execute deterministic evals.

## Codex Workflow Checklist

File:

```text
docs/architecture/codex-workflow.md
```

Check that this doc aligns with the current implementation workflow:

- one ticket at a time
- small focused changes
- no broad refactors
- do not bloat AGENTS.md
- read relevant docs before coding
- use current code as source of truth
- run relevant checks
- report exact files changed and commands run

Add or confirm this rule:

> If durable project context is needed, update the appropriate doc instead of adding long explanations to AGENTS.md.

Add or confirm this rule:

> When a ticket touches benchmark, eval, trace, validation, or guardrail behavior, check the corresponding system-of-record docs before implementing.

## Demo Script Checklist

File:

```text
docs/architecture/demo-script.md
```

Check that the demo narrative is no longer:

> Here is an AI that debugs a Kafka incident.

It should become:

> Here is a reliability workbench that benchmarks and observes a tool-using AI agent while it investigates a production-like incident.

The demo should show:

- start an agent run
- watch or inspect trace steps
- inspect tool calls and evidence
- view structured output
- view validation result
- view guardrail and approval status
- view cost and latency metadata
- inspect recent runs
- run evals
- explain how this supports repeatable benchmarking

Useful demo framing:

> The point of the demo is not that the agent solved one Kafka issue. The point is that the platform makes the agent's investigation observable, validated, governed, and repeatably evaluated.

## README Checklist

File:

```text
README.md
```

The README should be public-facing and clear.

It should explain:

- what the project is
- why it exists
- what problem it solves
- how to run it locally
- what the demo shows
- what is implemented now
- what is planned later

Keep it concise.

Avoid making claims that sound like a finished SaaS product if the project is still local MVP.

Possible positioning:

> Agent Reliability Workbench is a local-first platform for benchmarking and observing tool-using AI agents in production-like scenarios.

Possible MVP description:

> The current MVP uses an incident-investigation benchmark to demonstrate trace capture, structured validation, guardrails, approvals, evals, and run-level cost/latency visibility.

## PROJECT_VISION.md Checklist

File:

```text
docs/PROJECT_VISION.md
```

Check that this doc clearly answers:

- what the project is becoming
- why benchmarking tool-using agents matters
- why incident investigation is a good first environment
- how this differs from a simple incident triage chatbot
- what the MVP proves
- what future versions may add

It should be inspiring but not bloated.

## BENCHMARK_SPEC.md Checklist

File:

```text
docs/BENCHMARK_SPEC.md
```

Check that this doc clearly defines:

- benchmark scenarios
- incident-investigation environment
- expected findings
- available evidence
- available tools
- success criteria
- scenario design rules
- future scenario expansion

Make sure it does not promise unimplemented product features as already done.

## EVAL_METHODOLOGY.md Checklist

File:

```text
docs/EVAL_METHODOLOGY.md
```

Check that this doc clearly defines:

- what gets evaluated
- structured output validity
- diagnosis correctness
- evidence grounding
- tool use quality
- recommendation quality
- safety and guardrails
- trace inspectability
- scoring
- failure categories
- run comparison goals

Make sure the methodology aligns with current and near-future implementation.

## ROADMAP.md Checklist

File:

```text
docs/ROADMAP.md
```

Check that roadmap stages are realistic.

The next few stages should prioritize:

- docs alignment
- scenario metadata
- eval quality
- trace readability
- run comparison
- governance improvements
- additional benchmark scenarios
- open-source readiness

Avoid prioritizing:

- full LangGraph rewrite
- multi-agent orchestration
- cloud deployment
- public leaderboard
- authentication
- large UI redesign

## Consistency Rules

Across all docs, use these terms consistently:

```text
Agent Reliability Workbench
benchmark scenario
benchmark environment
tool-using AI agent
agent run
trace
tool call
structured output
validation
guardrail
approval
eval case
eval run
eval result
scenario evidence
expected findings
```

Avoid switching between many names for the same thing.

## Current Implementation Reality

The docs should reflect that the current MVP includes:

- FastAPI backend
- Next.js frontend
- PostgreSQL persistence
- local-first development
- mock tools
- incident-investigation benchmark
- agent run lifecycle
- trace capture
- structured output validation
- guardrail checks
- approval status
- eval runner
- recent run inspection
- run-level latency, token, and estimated cost metadata

Do not document unimplemented capabilities as already complete.

Future capabilities should be labeled as planned, future, or roadmap.

## Red Flags To Fix

Fix docs that imply:

- the project is only a Kafka incident debugger
- the final answer matters more than trace and process
- evals are only backend tests
- guardrails are optional UI decoration
- traces are just logs rather than core observability artifacts
- scenarios are random demos rather than benchmark environments
- LangGraph or multi-agent workflow is required immediately
- the project is already a production SaaS platform

## Done Criteria

Architecture reconciliation is done when:

- AGENTS.md is lean and points to system-of-record docs
- PROJECT_VISION.md, BENCHMARK_SPEC.md, EVAL_METHODOLOGY.md, and ROADMAP.md exist
- existing architecture docs do not contradict the benchmark direction
- README positioning is aligned with the new direction
- current MVP behavior is accurately described
- future work is clearly separated from implemented behavior
- a new implementation agent can understand the project without reading a bloated prompt
