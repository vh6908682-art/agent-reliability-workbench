# Benchmark Specification

## Purpose

Agent Reliability Workbench uses domain-specific benchmark suites for evaluating tool-using AI agents.
Each benchmark case is executed against an Agent Under Test. The default target is the built-in `ReferenceIncidentAgent`, and the same cases can run against registered external HTTP JSON agents.
The backend represents the selected agent as an Agent Target. The default system-managed target is `ReferenceIncidentAgent`, and HTTP JSON targets allow external agents to be registered without changing the benchmark harness.

The current built-in suite is `incident_triage_v1`, which uses production-like incident scenarios as the first benchmark environment. The goal is not only to solve one incident. The goal is to measure whether an agent can perform a realistic domain task in a repeatable, observable, and governable way.

Each benchmark scenario should test the agent's ability to:

- understand an incident prompt
- choose appropriate tools
- retrieve relevant evidence
- avoid unsupported conclusions
- produce structured output
- pass deterministic validation checks
- respect guardrails
- expose reasoning through traces
- support repeatable evaluation across Agent Targets, prompts, models, and configs

## Benchmark Philosophy

A useful agent benchmark should not only ask whether the final answer looks correct.

It should also evaluate the path the agent took.

Agent Reliability Workbench treats the investigation process itself as part of the benchmark. Tool calls, retrieved evidence, intermediate trace steps, validation status, guardrail results, latency, token usage, and cost all matter.

This makes the benchmark closer to a production reliability review than a simple Q&A test.

## Current Benchmark Environment

The current benchmark environment is incident investigation. The 12 seeded eval cases are the default `incident_triage_v1` suite.

The agent receives a production-like incident and must investigate it using available tools and internal evidence.

The initial scenario focuses on a Kafka consumer failure involving duplicate-key behavior, retry exhaustion, and customer data synchronization issues.

This scenario is intentionally specific enough to be realistic, but general enough to demonstrate the core platform capabilities:

- traceable tool use
- evidence-backed diagnosis
- structured output validation
- deterministic eval cases
- governance around risky recommendations

These incident-triage cases are not universal tests for every kind of agent. Other agent categories should use their own benchmark suites with domain-specific tasks, evidence, expected outcomes, and risk checks.

## Current Scenario: Kafka Duplicate Key Incident

### Scenario Summary

A backend service is consuming Kafka events related to customer account data synchronization.

A production incident occurs where event processing fails because of duplicate-key behavior. The agent must investigate logs, payloads, configuration, and service behavior to identify the likely cause and recommend next steps.

### Expected Agent Behavior

The agent should:

- inspect relevant logs
- identify the duplicate-key failure pattern
- connect the failure to retry exhaustion or event processing behavior
- validate the event payload where appropriate
- check service configuration where appropriate
- produce an evidence-backed diagnosis
- avoid claiming certainty without evidence
- recommend safe next steps
- flag risky or destructive recommendations for approval when needed

### Expected Output Shape

The agent should produce structured output with fields such as:

- likely_cause
- recommended_next_steps
- evidence
- confidence

The exact schema is defined in the backend validation layer and should remain consistent with the current API contract.

## Benchmark Components

Each benchmark scenario should define the following components.

### 1. Scenario ID

A stable identifier for the scenario.

Example:

```text
kafka_duplicate_key_retry_exhaustion
```

### 2. Incident Prompt

The user-facing incident description given to the agent.

The prompt should be realistic, specific, and operationally meaningful.

It should not directly reveal the answer.

### 3. Available Evidence

Evidence may include:

- mock logs
- payload samples
- service configuration
- runbooks
- internal documentation
- previous incident notes
- tool responses
- database-like records
- validation results

Evidence should be deterministic so eval results can be repeated.

### 4. Available Tools

Each scenario should define which tools the agent may use.

Current tool examples include:

- search_logs
- validate_payload
- lookup_service_config
- create_ticket_mock

Tools should have clear risk levels:

- read-only
- low-risk
- high-risk

High-risk tools or recommendations should connect to guardrails and approval workflows.

### 5. Expected Findings

Each scenario should define the important findings the agent should discover.

Expected findings should be specific enough for deterministic evaluation, but not so brittle that only one exact phrasing passes.

Example findings:

- duplicate-key exception appears in the consumer logs
- retries are exhausted after repeated processing failures
- payload or service behavior suggests an idempotency or record identity issue
- recommended next steps should include investigation or remediation without unsafe production changes

### 6. Evaluation Checks

Each scenario should define checks that measure agent behavior.

Checks may include:

- required fields are present
- diagnosis mentions the correct failure mode
- evidence references relevant logs or payloads
- recommendations are actionable
- unsupported certainty language is avoided
- risky recommendations trigger approval
- output passes schema validation
- tool calls are appropriate for the scenario

### 7. Success Criteria

A scenario passes when the agent:

- produces a valid structured response
- identifies the likely cause
- supports conclusions with evidence
- recommends safe next steps
- avoids unsupported claims
- satisfies deterministic eval checks

A scenario should fail when the agent:

- invents evidence
- ignores available tools
- misses the core failure mode
- recommends destructive action without approval
- produces invalid structure
- gives vague or unsupported recommendations

## Scenario Design Rules

Good benchmark scenarios should be:

- realistic
- deterministic
- repeatable
- narrow enough to evaluate
- rich enough to require investigation
- grounded in available evidence
- connected to product behavior
- safe to run locally

Avoid scenarios that are:

- too broad
- dependent on live external systems
- impossible to score deterministically
- only testing generic chatbot reasoning
- disconnected from tool use
- based on hidden knowledge unavailable to the agent

## Eval Case Relationship

Eval cases are concrete tests derived from benchmark scenarios.

A benchmark scenario describes the environment and expected behavior.

An eval case defines a specific prompt, expected checks, scoring rules, and pass/fail result.

One benchmark scenario may have multiple eval cases.

Example:

```text
Benchmark Scenario: Kafka duplicate-key retry exhaustion
Eval Cases:
- basic diagnosis
- missing evidence handling
- risky recommendation guardrail
- payload validation required
- config lookup required
```

## Future Scenario Expansion

The incident benchmark environment should expand beyond the initial Kafka incident.

Future scenarios may include:

- missing configuration causing failed downstream calls
- malformed payload causing validation failure
- stale runbook leading to incorrect diagnosis
- ambiguous logs requiring multiple tool calls
- high-risk remediation requiring approval
- partial evidence where the agent must express uncertainty
- conflicting evidence across logs and documentation
- repeated failure across multiple services
- incident where the safest answer is to escalate

The goal is not to add random incidents.

The goal is to create a scenario suite that tests different dimensions of agent reliability.

Future benchmark suites can target other agent categories, such as customer support, refund decisioning, code review, compliance intake, or sales operations. Each suite should preserve the same reliability principles while defining domain-specific eval cases. For the current supported JSON structure and manual customization path, see [Custom Benchmark Suites](CUSTOM_BENCHMARK_SUITES.md).

## Reliability Dimensions

Agent Reliability Workbench should evaluate agents across multiple dimensions:

### Investigation Quality

Can the agent find and use the right evidence?

### Tool Use Quality

Does the agent call useful tools in a reasonable order?

### Grounding

Are conclusions supported by retrieved evidence?

### Structured Output

Does the agent produce valid, machine-readable output?

### Safety and Governance

Does the agent avoid unsafe actions and respect approval boundaries?

### Repeatability

Can the same scenario be run repeatedly and compared across prompts, models, or agent versions?

### Observability

Can a human inspect what happened during the run?

### Cost and Latency Awareness

Can runs be compared not only by correctness, but also by time, token usage, and cost?

## Product Implication

The benchmark system is the core product direction.

The incident-investigation domain is the first environment used to prove the platform.

As the project grows, new benchmark scenarios and eval cases should be added without rewriting the core platform.

The platform should make it easy to answer questions such as:

- Which agent version performs better?
- Which model produces more reliable diagnoses?
- Which prompts reduce unsupported conclusions?
- Which scenarios trigger guardrails?
- Which runs are expensive or slow?
- Which failures are due to reasoning, tool use, validation, or governance?

## Non-Goals

This benchmark spec does not require the project to immediately support:

- live production integrations
- real company incident data
- full multi-agent orchestration
- cloud deployment
- authentication
- customer-facing SaaS features
- large-scale benchmark leaderboards

Those may be future extensions, but the immediate goal is a strong local benchmark and observability platform.

## Current Priority

The current priority is to strengthen the MVP into a coherent benchmark platform by improving:

- scenario definitions
- eval methodology
- trace readability
- run comparison
- guardrail visibility
- documentation clarity
- repeatable demo flow

The project should continue evolving through small focused tickets.
