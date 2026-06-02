# Ticket 022B — Add second batch of deterministic benchmark eval incidents

## Goal

Expand the benchmark suite by adding the next small batch of deterministic incident-investigation eval cases.

This ticket should build on Ticket 022A and add a second batch of benchmark incidents without changing core runner behavior, UI behavior, or the existing MVP golden path.

The purpose is to make the benchmark suite broader while keeping every case deterministic, easy to inspect, and suitable for comparing tool-using agents.

## Context

The project is now Agent Reliability Workbench: a benchmarking, observability, and governance platform for tool-using AI agents.

Incident investigation is the first benchmark environment.

The core loop is:

run → trace → validate → govern → evaluate → compare

The Kafka duplicate-key retry exhaustion scenario remains the golden-path demo and must continue to work.

Ticket 021 added or tightened benchmark taxonomy fields such as:

- category
- difficulty
- risk_level
- expected_capability
- workflow_tags

Ticket 022 is split into 22A, 22B, and 22C to avoid adding all 12 benchmark incidents at once.

## Docs to read first

Read only the relevant docs before editing:

- AGENTS.md
- docs/PROJECT_VISION.md
- docs/BENCHMARK_SPEC.md
- docs/EVAL_METHODOLOGY.md
- docs/ROADMAP.md
- docs/ARCHITECTURE_RECONCILIATION_CHECKLIST.md

Also inspect the files changed by Ticket 022A before editing.

## Files likely to change

Exact file names may differ. Inspect the repo first.

Likely areas:

- eval seed data files
- mock logs
- mock payloads
- mock service configs
- mock runbooks
- eval case definitions
- tests for eval seed loading or benchmark case validity

## Files not to change

Do not change unless absolutely required:

- AGENTS.md
- README.md
- frontend UI files
- core agent loop logic
- approval/governance logic
- database models or migrations
- unrelated API routes
- unrelated eval runner behavior

## Expected behavior

Add the second batch of deterministic benchmark incidents.

Target: add 4 new eval cases, unless the current repo structure clearly suggests a smaller number is safer.

Each new eval case must include enough deterministic context for the existing agent/eval machinery to run consistently.

Each case should include:

- clear incident title
- short incident description
- mock logs or evidence
- expected diagnosis
- expected supporting evidence
- expected tool-use behavior where applicable
- benchmark taxonomy fields from Ticket 021:
  - category
  - difficulty
  - risk_level
  - expected_capability
  - workflow_tags

The new cases should diversify the benchmark beyond the existing Kafka duplicate-key golden path.

Prefer cases that test different agent capabilities, for example:

- distinguishing symptom vs root cause
- checking config before making a conclusion
- validating payload shape or schema mismatch
- identifying retry/dead-letter behavior
- recognizing missing required fields
- using runbook guidance instead of guessing

The cases should be deterministic and production-like, but not overly complex.

## Suggested incident themes

Use repo-consistent naming and formats. These are suggestions, not mandatory if the existing seed structure points to better names.

Possible cases:

1. Consumer lag caused by downstream timeout  
   - Category: incident_triage / dependency_failure  
   - Tests whether the agent connects repeated timeout logs with consumer lag and avoids blaming Kafka itself.

2. Payload validation failure due to missing required field  
   - Category: schema_validation / data_quality  
   - Tests whether the agent validates payload evidence before diagnosing.

3. Feature/config flag mismatch between environments  
   - Category: config_drift  
   - Tests whether the agent checks service config instead of relying only on logs.

4. Dead-letter queue growth caused by poison message  
   - Category: retry_exhaustion / dlq_analysis  
   - Tests whether the agent identifies repeated failure of the same payload rather than broad service outage.

Do not force these exact cases if they conflict with existing mock data patterns. Keep the implementation consistent with the repo.

## Tests

Add or update focused tests only.

Tests should verify:

- new eval cases load successfully
- required taxonomy fields are present
- expected diagnosis/evidence fields are present
- benchmark case identifiers are unique
- existing golden-path eval case still loads
- total benchmark case count increases correctly from the state after 22A

Avoid broad snapshot tests unless the repo already uses them.

## Validation commands

Run the smallest relevant checks first.

Likely commands may include:

bash cd apps/api && pytest 

If the repo has narrower eval tests, run those first, then the full backend test suite if reasonable.

Also run any existing lint/typecheck command if already standard for this repo.

Do not add new tooling.

## Non-goals

Do not:

- add frontend benchmark comparison UI
- add LangGraph orchestration
- change the core eval scoring algorithm
- rewrite eval schemas unless required by existing validation
- add database migrations
- change the golden-path Kafka demo
- introduce nondeterministic LLM-dependent expected outputs
- add more than the intended small batch

## Completion criteria

This ticket is complete when:

- the second batch of deterministic benchmark incidents is added
- all new cases have the required taxonomy fields
- all new cases have deterministic expected outputs/evidence
- tests pass
- existing MVP golden path remains unchanged
- total benchmark coverage moves closer to the planned 12-case suite without bloating the implementation