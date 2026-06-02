# Ticket 021 — Add Benchmark Case Taxonomy Fields

## Goal

Prepare eval cases to behave like a real benchmark suite by adding lightweight taxonomy metadata to existing eval cases.

This supports the new Agent Reliability Workbench direction:

> A benchmarking, observability, and governance platform for tool-using AI agents.

The incident-investigation workflow remains the first benchmark environment. The existing Kafka duplicate-key incident remains the golden-path demo scenario.

## Why this matters

Eval cases should not be anonymous test rows. They should describe what benchmark capability they are testing.

After this ticket, eval cases should be easier to group, inspect, and later compare by:

- category
- difficulty
- risk level
- expected capability
- workflow tags

This is a foundation for future benchmark reporting and run comparison.

## Required behavior

Add the following taxonomy fields to eval cases:

txt category difficulty risk_level expected_capability workflow_tags

Use simple string/list fields unless the existing codebase already has a strong enum pattern.

Suggested values for the existing golden-path Kafka incident eval case:

txt category: incident_investigation difficulty: medium risk_level: medium expected_capability: evidence_based_root_cause_analysis workflow_tags: - kafka - spring-batch - duplicate-key - retry-exhaustion - backend-data-pipeline

Use actual existing eval case names/IDs from the repo. Do not invent a new eval system.

## Scope

This ticket should update the existing eval case structure only.

Acceptable changes:

1. Update eval case schema/type definitions.
2. Update existing eval seed data with taxonomy fields.
3. Update eval runner types only if needed so existing eval execution still works.
4. Update API response schemas only if eval cases or eval results are already exposed through the API.
5. Update frontend TypeScript types only if the API type currently breaks because of the new fields.
6. Add or update focused tests verifying taxonomy fields exist and existing eval execution still works.

## Files likely to change

Codex should inspect the repo first and choose the smallest natural set of files.

Likely backend files/directories:

txt apps/api/app/schemas/ apps/api/app/models/ apps/api/app/services/ apps/api/tests/

Likely eval-related files/directories to inspect:

txt apps/api/app/services/_eval_ apps/api/app/schemas/_eval_ apps/api/app/models/_eval_ apps/api/tests/_eval_

Likely frontend files only if needed:

txt apps/web/src/lib/api.ts apps/web/src/components/

## Files not to change

Do not change:

txt AGENTS.md README.md docs/\*\*

Do not update project docs in this ticket.

Do not redesign the frontend.

Do not change the current Kafka golden-path demo behavior.

Do not add new incident scenarios in this ticket.

## Docs to read first

Before implementing, read:

txt AGENTS.md docs/PROJECT_VISION.md docs/BENCHMARK_SPEC.md docs/EVAL_METHODOLOGY.md docs/ROADMAP.md docs/ARCHITECTURE_RECONCILIATION_CHECKLIST.md

Use these docs for direction only. Keep implementation narrow.

## Persistence decision

Prefer the smallest change that fits the current repo.

If eval cases are currently static seed/config data, add taxonomy fields there.

If eval cases are already persisted in the database, add the fields to the DB model and include an Alembic migration.

Do not introduce a database migration unless the current eval case structure already requires persistence.

## Expected behavior

After implementation:

1. Existing eval cases still run.
2. Existing eval runner does not break.
3. Existing API responses still work.
4. Existing frontend typecheck passes.
5. Eval case metadata includes:
   - category
   - difficulty
   - risk_level
   - expected_capability
   - workflow_tags
6. The existing golden-path Kafka eval case has meaningful taxonomy values.
7. Any missing optional taxonomy fields are handled safely if older data exists.

## Tests

Add or update focused tests to verify:

1. Existing eval cases include taxonomy metadata.
2. Eval runner can still execute existing eval cases.
3. API serialization still works if eval cases/results are exposed.
4. Frontend typecheck passes if frontend types are updated.

Prefer small tests around the existing eval test files. Do not create broad new test infrastructure.

## Validation commands

Run:

bash cd apps/api python -m pytest

If frontend files are changed, also run:

bash cd apps/web npm run typecheck

If a DB migration is added, run the project’s existing migration verification command if one exists.

## Non-goals

This ticket must not:

- Add 12 eval cases.
- Add scenario metadata.
- Add a comparison dashboard.
- Add run comparison APIs.
- Add prompt versioning.
- Add LangGraph.
- Rewrite the eval engine.
- Rewrite docs.
- Perform unrelated UI polish.
- Change the current MVP golden-path behavior.

## Completion criteria

This ticket is complete when:

- Eval cases support benchmark taxonomy fields.
- Existing eval seed data is updated with meaningful taxonomy values.
- Existing eval execution still works.
- API/frontend types are updated only if needed.
- Backend tests pass.
- Frontend typecheck passes if frontend files changed.
