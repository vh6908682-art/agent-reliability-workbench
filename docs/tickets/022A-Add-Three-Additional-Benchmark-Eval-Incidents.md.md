# Ticket 022A — Add Three Additional Benchmark Eval Incidents

## Goal

Expand the eval seed data from the MVP golden-path case into a small benchmark set by adding three additional deterministic incident-investigation eval cases.

This ticket should build on Ticket 021’s benchmark taxonomy fields.

The goal is not to reach the full 12-case benchmark yet. The goal is to prove that the eval suite can support multiple realistic incident cases without redesigning the eval runner.

## Why this matters

Agent Reliability Workbench is being reframed as a benchmarking, observability, and governance platform for tool-using AI agents.

A single Kafka duplicate-key case is useful for the demo, but a benchmark platform needs multiple repeatable cases that test different capabilities.

This ticket adds a small, controlled expansion so future tickets can safely scale the benchmark suite.

## Required benchmark cases

Keep the existing golden-path case:

1. Kafka duplicate key retry exhaustion

Add these three new cases:

2. Missing required payload field  
3. Schema version mismatch  
4. Downstream timeout

Do not add the remaining 8 cases in this ticket.

## Required behavior

Each new eval case should include:

- stable eval case ID
- title/name
- short description
- taxonomy fields from Ticket 021:
  - category
  - difficulty
  - risk_level
  - expected_capability
  - workflow_tags
- realistic but compact mock evidence
- expected diagnosis
- expected evidence
- safe next steps
- scoring checks compatible with the existing eval runner

The eval runner should be able to run all existing and newly added cases.

## Suggested taxonomy values

Use the existing project style where possible.

### Case 2 — Missing required payload field

Suggested values:

txt category: incident_investigation difficulty: easy risk_level: low expected_capability: payload_validation_failure_detection workflow_tags:   - payload-validation   - missing-field   - backend-data-pipeline 

Expected diagnosis theme:

txt The incident is caused by an incoming payload missing a required field, causing validation or parsing failure before normal processing can complete. 

Expected evidence examples:

txt - log line showing missing required field - payload sample missing the field - runbook or schema evidence showing the field is required 

Safe next steps examples:

txt - quarantine or reject malformed messages - notify upstream producer team - add validation/error reporting if missing - do not mutate production data without approval 

### Case 3 — Schema version mismatch

Suggested values:

txt category: incident_investigation difficulty: medium risk_level: medium expected_capability: schema_contract_mismatch_detection workflow_tags:   - schema-version   - contract-mismatch   - payload-validation   - backend-data-pipeline 

Expected diagnosis theme:

txt The incident is caused by a producer/consumer schema version mismatch where the service receives a payload version it does not support or parse correctly. 

Expected evidence examples:

txt - log line showing unsupported schema version - payload containing unexpected schemaVersion - service config or runbook showing supported versions 

Safe next steps examples:

txt - confirm expected schema versions - coordinate producer/consumer rollout - route incompatible messages to DLQ/quarantine - avoid risky production changes without approval 

### Case 4 — Downstream timeout

Suggested values:

txt category: incident_investigation difficulty: medium risk_level: medium expected_capability: downstream_dependency_failure_analysis workflow_tags:   - downstream-timeout   - dependency-failure   - retry   - backend-service 

Expected diagnosis theme:

txt The incident is caused by repeated timeout failures when calling a downstream dependency, leading to retries and delayed or failed processing. 

Expected evidence examples:

txt - log line showing downstream timeout - retry exhaustion or repeated failed calls - service config showing timeout/retry settings - runbook guidance for downstream dependency degradation 

Safe next steps examples:

txt - verify downstream service health - check timeout and retry configuration - escalate to dependency owner if needed - avoid high-risk remediation without approval 

## Scope

This ticket should only add or update eval seed/mock data and focused tests.

Acceptable changes:

1. Add new eval case definitions.
2. Add compact mock logs/payloads/configs/runbook snippets only where needed.
3. Add scoring checks using the existing eval check style.
4. Update tests to verify all eval cases load and run.
5. Update expected counts in tests if current tests assume only one eval case.

## Files likely to change

Codex should inspect the repo first and choose the smallest natural set of files.

Likely areas:

txt apps/api/app/services/*eval* apps/api/app/schemas/*eval* apps/api/tests/*eval* 

Possible mock/fixture areas:

txt apps/api/app/mock* apps/api/app/seed* apps/api/app/fixtures* apps/api/tests/fixtures* 

Use the actual repo structure. Do not create a new parallel fixture system if one already exists.

## Files not to change

Do not change:

txt AGENTS.md README.md docs/** apps/web/** 

Do not update frontend UI in this ticket.

Do not change the core agent loop unless the eval runner cannot load the new cases without a small compatibility fix.

Do not change database models unless eval cases are already persisted and the existing pattern requires it.

## Docs to read first

Before implementing, read:

txt AGENTS.md docs/PROJECT_VISION.md docs/BENCHMARK_SPEC.md docs/EVAL_METHODOLOGY.md docs/ROADMAP.md docs/ARCHITECTURE_RECONCILIATION_CHECKLIST.md 

Use these docs for direction only. Keep the implementation narrow.

## Mock evidence guidelines

Keep mock evidence realistic but compact.

Avoid giant mock files.

Each new case should have enough evidence for the agent/eval runner to distinguish the intended root cause.

Do not make cases ambiguous unless the case explicitly tests ambiguity. These three cases should be deterministic.

## Existing golden-path case

Do not remove or rewrite the existing Kafka duplicate-key retry exhaustion case.

Only update it if needed to keep the eval seed structure consistent with Ticket 021 taxonomy fields.

The current golden-path demo behavior must remain intact.

## Tests

Add or update focused tests to verify:

1. Eval seed loading includes the existing Kafka case plus the three new cases.
2. Each new case has required taxonomy fields.
3. Each new case has expected diagnosis/evidence/safe next steps.
4. Eval runner can run all cases without breaking.
5. Existing eval tests still pass.

Prefer extending existing eval tests instead of creating broad new test infrastructure.

## Validation commands

Run:

bash cd apps/api python -m pytest 

Also run:

bash git status 

Do not run frontend commands unless frontend files are changed, which should not happen in this ticket.

## Non-goals

This ticket must not:

- Add all 12 benchmark incidents.
- Add comparison APIs.
- Add comparison dashboard UI.
- Add prompt versioning.
- Add LangGraph.
- Redesign eval scoring.
- Redesign the eval runner.
- Rewrite docs.
- Perform unrelated frontend polish.
- Change the current MVP golden-path behavior.

## Completion criteria

This ticket is complete when:

- The eval suite includes the existing Kafka golden-path case plus three new deterministic incident cases.
- The three new cases include taxonomy metadata from Ticket 021.
- Each new case includes compact mock evidence, expected diagnosis, expected evidence, safe next steps, and scoring checks.
- The eval runner can run all included cases.
- Backend tests pass.
- No unrelated files were changed.