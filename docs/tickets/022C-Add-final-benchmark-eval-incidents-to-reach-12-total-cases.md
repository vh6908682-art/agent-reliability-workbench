# Ticket 022C — Add final benchmark eval incidents to reach 12 total cases

## Goal

Complete Ticket 022 by adding the final deterministic benchmark eval incidents so the suite reaches the planned 12 benchmark incidents total.

This ticket should finish the benchmark seed expansion started in 22A and 22B.

The focus is completion, consistency, and validation — not new architecture.

## Context

Agent Reliability Workbench is now positioned as a benchmarking, observability, and governance platform for tool-using AI agents.

Incident investigation is the first benchmark environment.

The benchmark suite should support the core loop:

run → trace → validate → govern → evaluate → compare

The Kafka duplicate-key retry exhaustion incident remains the golden-path demo and must continue to work.

Ticket 022 was intentionally split:

- 22A: first small batch of deterministic benchmark incidents
- 22B: second batch
- 22C: final batch to reach 12 total benchmark incidents

Ticket 021 added benchmark taxonomy fields:

- category
- difficulty
- risk_level
- expected_capability
- workflow_tags

## Docs to read first

Read only what is necessary:

- AGENTS.md
- docs/PROJECT_VISION.md
- docs/BENCHMARK_SPEC.md
- docs/EVAL_METHODOLOGY.md
- docs/ROADMAP.md
- docs/ARCHITECTURE_RECONCILIATION_CHECKLIST.md

Also inspect the eval cases added in 22A and 22B before editing.

## Files likely to change

Exact file names may differ. Inspect the repo first.

Likely areas:

- eval seed data files
- mock logs
- mock payloads
- mock service configs
- mock runbooks
- eval case definitions
- eval seed loading tests
- benchmark fixture validity tests

## Files not to change

Do not change unless absolutely necessary:

- AGENTS.md
- README.md
- frontend UI files
- core agent loop logic
- approval/governance logic
- database models or migrations
- unrelated API routes
- unrelated eval runner behavior

## Expected behavior

Add the final batch of deterministic benchmark incidents so the benchmark suite reaches 12 total cases.

Before adding new cases:

1. Count the current benchmark eval incidents after 22A and 22B.
2. Add only the number needed to reach 12 total.
3. Do not exceed 12 unless the repo already contains non-benchmark eval cases that are clearly separate from the planned benchmark set.

Each final case must include:

- clear incident title
- short incident description
- deterministic mock evidence
- expected diagnosis
- expected supporting evidence
- expected tool-use behavior where applicable
- taxonomy fields:
  - category
  - difficulty
  - risk_level
  - expected_capability
  - workflow_tags

The final set should feel like a coherent benchmark suite, not random sample data.

## Coverage goals

After this ticket, the 12-case benchmark suite should include a healthy spread across:

- log investigation
- payload validation
- config lookup
- runbook usage
- retry/dead-letter reasoning
- dependency failure reasoning
- data quality reasoning
- governance/risk awareness where applicable

Do not force every capability into every case. The suite should be balanced across cases.

## Suggested final incident themes

Use repo-consistent naming and formats. These are suggestions, not mandatory if the existing seed data structure suggests better options.

Possible final cases:

1. Idempotency key missing causes duplicate downstream writes  
   - Tests whether the agent identifies missing idempotency protection instead of blaming retries alone.

2. Stale service config causes wrong topic or endpoint usage  
   - Tests whether the agent checks config evidence and identifies config drift.

3. Runbook-required escalation for high-risk remediation  
   - Tests whether the agent recognizes a governance boundary and avoids unsafe direct remediation.

4. Partial upstream outage causes intermittent failures  
   - Tests whether the agent avoids overgeneralizing from mixed success/failure logs.

Keep the cases simple enough for deterministic evals.

## Tests

Add or update focused tests to verify:

- total planned benchmark incident count is 12
- all 12 benchmark cases load successfully
- all 12 benchmark cases have unique identifiers
- all 12 benchmark cases include required taxonomy fields
- all 12 benchmark cases include expected diagnosis/evidence fields
- the original Kafka duplicate-key golden path still exists
- no case uses vague or empty expected outputs

If the repo already has eval fixture validation tests, extend those rather than creating a parallel test framework.

## Validation commands

Run the smallest relevant checks first.

Likely commands:

bash cd apps/api && pytest 

If narrower eval tests exist, run them first.

If the frontend is untouched, do not spend time changing or debugging frontend code.

Run typecheck/lint only if already standard for touched files.

## Non-goals

Do not:

- build a benchmark comparison dashboard
- add LangGraph
- change scoring methodology
- change core agent execution
- rewrite the eval runner
- add migrations
- rewrite existing incidents unless they are malformed
- modify the MVP golden-path demo behavior
- expand beyond 12 planned benchmark incidents

## Completion criteria

This ticket is complete when:

- the benchmark suite has exactly 12 planned benchmark incidents
- all cases are deterministic
- all cases include required taxonomy metadata
- all cases include expected diagnosis/evidence
- tests validate the suite shape and pass
- the Kafka duplicate-key golden path still works
- no unrelated app behavior was changed