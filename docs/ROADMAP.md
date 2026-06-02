# Roadmap

## Purpose

This roadmap describes how Agent Reliability Workbench should evolve after the MVP.

The project has already proven the basic golden path: a user can run an agent against a production-like incident, inspect the trace, view validation and guardrail results, see cost and latency metadata, and run deterministic evals.

The next goal is to turn the MVP into a stronger benchmark, observability, and governance platform for tool-using AI agents.

## Product Direction

Agent Reliability Workbench is not only an incident triage demo.

It is a platform for evaluating and observing agent behavior in repeatable benchmark environments.

The current incident-investigation domain is the first benchmark environment. It should be strengthened before adding unrelated domains.

The project should evolve through focused stages:

1. clarify the benchmark system
2. improve eval quality
3. improve trace and run comparison
4. add more scenarios
5. improve governance workflows
6. prepare the project for open-source use

## Guiding Principles

### Keep the Core Simple

Avoid adding large frameworks or abstractions before the product behavior is clear.

The strongest version of this project is not the one with the most tools. It is the one where the reliability story is obvious.

### Build Around Repeatability

Every scenario, eval case, tool response, and seed fixture should support repeatable runs.

A user should be able to run the same benchmark multiple times and compare behavior.

### Make Agent Behavior Inspectable

The project should make it easy to answer:

- what did the agent do?
- what tools did it call?
- what evidence did it use?
- where did it fail?
- did it follow guardrails?
- how much did it cost?
- how long did it take?

### Prefer Focused Tickets

Each implementation step should be small.

Avoid tickets that change backend, frontend, docs, schema, and seed data all at once unless absolutely necessary.

### Do Not Bloat AGENTS.md

Durable project knowledge belongs in docs.

AGENTS.md should remain a short routing file for implementation agents.

## Stage 0: MVP Baseline

Status: mostly complete.

The MVP includes:

- local monorepo setup
- FastAPI backend
- Next.js frontend
- PostgreSQL persistence
- agent run creation
- run detail retrieval
- trace viewer
- mock tools
- structured output validation
- guardrail checks
- approval status
- latency, token, and cost metadata
- recent runs panel
- deterministic eval runner
- demo guide in the UI

The MVP should be treated as the stable baseline.

Future work should preserve this golden path unless a ticket explicitly changes it.

## Stage 1: Documentation and Product Alignment

Goal: make the expanded project direction clear.

Key docs:

- docs/PROJECT_VISION.md
- docs/BENCHMARK_SPEC.md
- docs/EVAL_METHODOLOGY.md
- docs/ROADMAP.md
- existing docs/architecture/*

Expected outcome:

- contributors understand that this is a benchmark and reliability platform
- the incident domain is clearly framed as the first benchmark environment
- AGENTS.md points to deeper docs instead of containing everything
- future tickets can be written against a clear system of record

Suggested tickets:

- Add benchmark and eval methodology docs
- Reconcile existing architecture docs with new product direction
- Update README to describe benchmark positioning without overhyping
- Add a clean demo narrative linked to the benchmark concept

## Stage 2: Scenario System

Goal: make benchmark scenarios explicit, inspectable, and extensible.

Current state:

- scenario behavior exists through seed data, mock tools, prompts, and eval cases
- the concept of a benchmark scenario is not yet first-class enough

Improvements:

- define scenario metadata
- connect eval cases to scenario IDs
- make scenario fixtures easier to inspect
- document expected findings for each scenario
- separate scenario evidence from generic app data where useful
- support multiple incident scenarios without confusing the demo

Possible scenario metadata:

text id="dazigf" scenario_id title description incident_prompt available_tools evidence_sources expected_findings risk_profile eval_case_ids 

Suggested tickets:

- Add scenario metadata fixture
- Link eval cases to scenario IDs
- Display scenario name in eval results
- Add scenario summary to run detail
- Add one additional incident scenario with deterministic evidence

## Stage 3: Evaluation Quality

Goal: make evals more credible, explainable, and useful.

Current state:

- deterministic eval runner exists
- eval results show pass/fail counts and check-level results
- checks are useful but should become more clearly tied to benchmark methodology

Improvements:

- classify failures by category
- expose check descriptions
- make pass/fail thresholds explicit
- improve failure messages
- add scenario-specific expected findings
- make eval results easier to compare
- distinguish validation failure, diagnosis failure, grounding failure, tool-use failure, and safety failure

Suggested tickets:

- Add failure category to eval check results
- Add human-readable check descriptions
- Show scenario ID and benchmark dimension in eval result cards
- Add more eval cases for the current Kafka scenario
- Add eval cases that intentionally test guardrail behavior
- Add eval cases for partial evidence and uncertainty handling

## Stage 4: Trace and Observability Improvements

Goal: make agent runs easier to inspect and explain.

Current state:

- trace viewer exists
- run detail shows steps, tool calls, structured output, validation, guardrails, cost, and latency

Improvements:

- improve trace step grouping
- make tool calls visually clearer
- show evidence used in final answer
- show validation and guardrail status more prominently
- display failure reasons clearly
- support trace comparison between runs later
- make run timeline easier to understand

Suggested tickets:

- Add trace timeline ordering and labels
- Improve tool call display
- Add evidence section to run detail
- Highlight validation failures
- Highlight guardrail failures or pending approval
- Add clearer empty states for missing trace data

## Stage 5: Run Comparison

Goal: support comparison across runs, prompts, models, and scenarios.

Current state:

- recent runs can be listed and selected
- individual run details can be inspected

Improvements:

- compare two runs side by side
- show differences in status, score, latency, cost, model, and guardrail result
- compare final outputs
- compare tool-call count and sequence
- compare eval results across runs
- compare prompt versions when available

Suggested tickets:

- Add run comparison data shape
- Add frontend run comparison view
- Compare run metadata and final output
- Compare validation and guardrail results
- Compare cost and latency
- Add basic prompt version display if already available in data model

## Stage 6: Governance and Approval Workflows

Goal: make safety and human oversight more meaningful.

Current state:

- guardrail checks exist
- runs can require approval
- approval status can be updated

Improvements:

- make approval reasons explicit
- add reviewer notes to UI clearly
- distinguish guardrail warning vs failure
- track approval history
- show which recommendation triggered approval
- make high-risk tool actions or destructive recommendations more visible

Suggested tickets:

- Add approval reason field
- Improve approval UI state
- Add guardrail severity
- Add guardrail result explanation
- Add approval event history
- Connect high-risk recommendations to approval requirement

## Stage 7: Additional Benchmark Scenarios

Goal: broaden the benchmark suite without losing focus.

New scenarios should test different reliability dimensions.

Possible scenarios:

- malformed payload causes validation failure
- missing service config causes downstream failure
- stale runbook conflicts with logs
- ambiguous logs require uncertainty
- high-risk remediation requires approval
- repeated failure across two services
- noisy logs require filtering
- incident where escalation is the safest recommendation

Scenario expansion should be deliberate.

Each new scenario should include:

- scenario metadata
- deterministic evidence
- expected findings
- eval cases
- guardrail expectations if relevant
- demo value

Suggested tickets:

- Add malformed payload scenario
- Add stale runbook conflict scenario
- Add high-risk remediation scenario
- Add uncertainty-handling scenario
- Add noisy logs scenario

## Stage 8: Agent Architecture Improvements

Goal: improve agent implementation only after benchmark behavior is strong.

Possible future improvements:

- clearer agent planning steps
- better tool selection logic
- prompt versioning
- model selection
- optional LangGraph orchestration
- multi-step agent workflows
- multi-agent experiments

Important constraint:

Do not add LangGraph or multi-agent orchestration just for buzzwords.

Add them only when they improve benchmark clarity, traceability, repeatability, or comparison.

Suggested tickets:

- Add prompt version metadata to runs
- Add model selector configuration
- Add clearer agent step types
- Prototype LangGraph branch behind a small isolated ticket
- Compare simple loop vs LangGraph execution on the same scenario

## Stage 9: Open-Source Readiness

Goal: make the repo understandable and usable by other developers.

Improvements:

- polish README
- add screenshots or demo GIFs
- add quickstart instructions
- add example eval output
- add architecture diagram
- add contribution guide
- add issue templates
- add scenario authoring guide
- add local troubleshooting guide
- make seed/reset flow reliable

Suggested tickets:

- Add local quickstart section
- Add demo walkthrough
- Add scenario authoring guide
- Add contribution guide
- Add architecture diagram
- Add troubleshooting doc
- Add screenshots after UI stabilizes

## Stage 10: Public Narrative and Blog

Goal: explain the project clearly to technical readers.

The strongest public narrative is:

text id="0xxvgs" I built a reliability workbench for tool-using AI agents: benchmark scenarios, trace inspection, structured validation, guardrails, approvals, evals, latency, token, and cost visibility. 

Possible blog themes:

- evaluating AI agents beyond final answers
- why agent traces matter
- building deterministic benchmark scenarios for tool-using agents
- guardrails and approvals for operational AI systems
- comparing agent runs by correctness, cost, latency, and safety
- lessons from building an agent reliability workbench

This stage should happen after the project is coherent and demo-ready.

## Near-Term Priority Order

The next work should happen in this order:

1. Finish system-of-record docs
2. Reconcile existing architecture docs with benchmark direction
3. Update README positioning
4. Add scenario metadata
5. Improve eval check descriptions and failure categories
6. Add more eval cases for current scenario
7. Improve trace readability
8. Add one new incident scenario
9. Add basic run comparison
10. Prepare open-source polish

## What Not To Do Next

Do not immediately jump into:

- full LangGraph rewrite
- multi-agent orchestration
- cloud deployment
- authentication
- public leaderboard
- large UI redesign
- unrelated incident domains
- complex ML-based grading
- huge refactors

These may become useful later, but they are not the next best step.

## Definition of a Strong Next Version

The next strong version of Agent Reliability Workbench should allow a user to say:

text id="usulqu" Here is a benchmark scenario for a tool-using incident agent. I can run the agent, inspect every step, see the evidence it used, validate the output, enforce guardrails, run evals, and compare whether changes improved or worsened behavior. 

That is the product foundation.