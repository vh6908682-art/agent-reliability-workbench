# Project Vision

## Project Name

Agent Reliability Workbench

## Purpose

Agent Reliability Workbench is a platform for benchmarking, observing, and governing tool-using AI agents in production-like workflows.

The current benchmark environment is incident investigation. The goal is not only to demonstrate that an agent can debug one issue. The goal is to create repeatable scenarios where different agent configurations can be evaluated on how reliably they investigate, reason, use tools, cite evidence, and recommend safe next steps.

## Product Category

Agent Reliability Workbench fits into three related categories:

- AI agent benchmarking
- AI agent observability
- AI agent guardrails and governance

## Core Question

The platform should help answer:

> When an AI agent is given a realistic operational problem, did it behave reliably?

More specifically:

- Did the agent choose the right tools?
- Did it inspect logs, configs, payloads, and runbooks before answering?
- Did it identify the likely cause correctly?
- Did it cite evidence instead of guessing?
- Did it recommend safe next steps?
- Did it avoid destructive or unsupported recommendations?
- How much did the run cost?
- How long did it take?
- Which model, prompt, or workflow performed best across the benchmark set?

## Current MVP Foundation

The current MVP provides the foundation for this direction.

At a high level, it includes:

- Backend API
- Frontend dashboard
- Agent run lifecycle
- Persisted agent runs
- Trace and step visibility
- Tool call visibility
- Retrieved evidence visibility
- Structured incident diagnosis output
- Output validation
- Guardrail checks
- Approval/review status
- Eval runner
- Eval result display
- Recent runs
- Latency, token, and estimated cost metadata where implemented
- Incident triage demo flow

This MVP should be treated as the first working slice of the broader reliability workbench.

## Benchmark Framing

Incident investigation is the first benchmark domain.

Each benchmark case should represent a realistic operational scenario, such as:

- Kafka consumer retry exhaustion
- Duplicate key errors
- Payload/schema mismatch
- Missing configuration
- Downstream service failure
- Unsafe remediation recommendation
- Insufficient evidence before conclusion

Each case should include enough data for an agent to investigate using tools rather than guessing.

A good benchmark case should test whether the agent can:

- Gather relevant evidence
- Ignore irrelevant noise
- Follow a safe investigation path
- Produce a structured diagnosis
- Explain its reasoning with cited evidence
- Avoid unsupported certainty
- Avoid unsafe actions unless approval is required

## What the Project Is Not

This project is not just:

- A chatbot for debugging incidents
- A single Kafka duplicate-key demo
- A generic RAG demo
- A prompt-only evaluation script
- A dashboard with logs but no evaluation logic

The long-term value comes from combining:

- Agent execution traces
- Tool usage visibility
- Evidence inspection
- Structured outputs
- Guardrails
- Eval results
- Cost and latency metadata
- Benchmark comparisons across agent configurations

## Intended Users

The intended users are developers, AI engineers, and platform teams who want to understand how tool-using agents behave in realistic operational workflows.

Possible users include:

- Engineers testing agent workflows before production use
- AI engineers comparing prompts, models, or orchestration strategies
- Platform teams evaluating agent safety and reliability
- Open-source users exploring agent observability and eval patterns

## Near-Term Product Direction

The near-term direction is to strengthen the project into a clear open-source portfolio system.

Priorities:

- Create focused system-of-record docs under docs/
- Keep implementation tickets small and grounded
- Expand benchmark cases carefully
- Improve eval methodology
- Make the demo story easy to understand
- Avoid bloating AGENTS.md
- Use docs as the source of truth for future Codex work

## Future Roadmap

The current MVP already includes focused docs, multiple deterministic incident eval cases, prompt/config metadata, eval comparison, and demo polish. Future work should build on that baseline rather than re-claiming it as planned.

The following are planned future improvements, not current MVP claims:

- First-class benchmark scenario metadata and taxonomy
- Richer eval scoring rubrics and failure categories
- Better trace comparison across runs
- Additional benchmark domains after incident investigation is stronger
- Optional LangGraph workflow mode if it improves traceability or repeatability
- Hosted demo mode
- Exportable benchmark reports
- Scenario authoring and contributor guides

## Success Criteria

The project is successful if a user can run benchmark incidents and clearly see:

- What the agent did
- Which tools it used
- What evidence it inspected
- What diagnosis it produced
- Whether the output passed validation
- Whether guardrails flagged risk
- Whether review/approval was needed
- How much the run cost
- How long the run took
- How different agent configurations compare over time

## Guiding Principle

Every feature should support one of these goals:

1. Make agent behavior visible.
2. Make agent quality measurable.
3. Make agent risk governable.
4. Make benchmark results repeatable.
