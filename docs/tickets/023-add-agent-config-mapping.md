# Ticket 023 — Persist Agent Configuration Metadata on Runs

## Goal

Add configuration metadata to each agent run so future benchmark, evaluation, and comparison features can group and compare runs by model, prompt, workflow, toolset, and guardrail mode.

This ticket does not build comparison logic yet. It only stores and returns the run-level configuration snapshot.

## Why this matters

The project is moving from a single MVP incident demo toward an agent reliability workbench where runs can be compared across different agent setups.

To support that, every run needs to record the configuration under which it was executed, such as:

- which model was used
- which prompt version was used
- which workflow style was used
- which toolset was available
- which guardrail mode was active

This gives us the foundation for later tickets like benchmark comparison, model-vs-model evals, workflow-vs-workflow evals, and governance experiments.

## Files likely involved

Backend:

- apps/api/app/models/...
  - Agent run database model
- apps/api/alembic/versions/...
  - New migration
- apps/api/app/schemas/...
  - Agent run create/detail/summary schemas if needed
- apps/api/app/services/...
  - Agent run creation and retrieval logic
- apps/api/app/agent/...
  - Agent loop / run creation path if metadata is created there
- apps/api/app/api/routes/...
  - Agent run API route responses
- apps/api/tests/...
  - Backend tests for default metadata and API response fields

Frontend:

- apps/web/src/lib/api.ts
  - Run response types
- apps/web/src/components/...
  - Trace viewer or run detail metadata display
- Any frontend tests/typecheck-related files if applicable

## Metadata fields to persist

Add the following nullable-or-defaulted fields to the agent run record:

- model_name
- prompt_version
- workflow_type
- toolset_name
- guardrail_mode

Suggested default values:

- model_name: "gpt-4o-mini" or the current default model used by the app
- prompt_version: "incident_triage_v1"
- workflow_type: "single_agent_loop"
- toolset_name: "incident_triage_tools_v1"
- guardrail_mode: "standard"

Use the current project conventions if similar values already exist elsewhere.

## Required behavior

### Backend

- Existing run creation must continue working without requiring the client to pass these fields.
- When a run is created, these metadata fields should be saved with defaults.
- If the existing create-run schema already accepts config-like values, use them carefully.
- Run detail API should return these metadata fields.
- Recent run/list API may return these fields only if that fits the existing response shape. Do not force large frontend changes unless simple.
- Keep this as a run-level snapshot, not a live reference to mutable config.

### Frontend

- Update frontend API types to include the new metadata fields.
- Display the metadata somewhere lightweight in the run detail / trace viewer area.
- The display should be compact and not dominate the demo UI.
- If a field is missing or null, avoid ugly rendering. Use simple fallback behavior.

Possible display format:

text Config Model: gpt-4o-mini Prompt: incident_triage_v1 Workflow: single_agent_loop Toolset: incident_triage_tools_v1 Guardrails: standard 

## Acceptance criteria

- Agent runs persist:
  - model_name
  - prompt_version
  - workflow_type
  - toolset_name
  - guardrail_mode
- Existing run creation still works without passing these fields manually.
- Run detail API returns the metadata.
- Frontend types are updated.
- Frontend displays the metadata in the run detail / trace view if available.
- Backend tests cover default values being applied.
- Backend tests cover API response fields.
- Frontend typecheck passes.

## Validation commands

Run backend tests:

bash cd apps/api && python -m pytest 

Run frontend typecheck:

bash cd apps/web && npm run typecheck 

Run Alembic migration check if practical:

bash cd apps/api && alembic upgrade head cd apps/api && alembic downgrade -1 cd apps/api && alembic upgrade head 

## Guardrails for Codex

- Do not add prompt version switching yet.
- Do not build comparison APIs yet.
- Do not introduce LangGraph.
- Do not create a full agent configuration management system.
- Do not create separate model/prompt/toolset tables.
- Do not add benchmark grouping UI yet.
- Do not change the golden-path incident behavior.
- Keep defaults simple and hardcoded for now if no config source exists.
- Keep the frontend display lightweight.
- Keep this ticket focused on persistence, API response, and basic visibility.

## Implementation notes

This ticket should be treated as a small foundation ticket.

The important design principle is that each run captures the configuration used at the time of execution. Later changes to defaults should not rewrite old runs.

This allows future tickets to ask questions like:

- Did the same incident perform better under another model?
- Did stricter guardrails reduce unsafe actions?
- Did a different workflow type improve investigation quality?
- Did a richer toolset improve diagnosis accuracy?
- Which prompt version produced the best benchmark score?

Do not implement those questions yet. Just store the metadata needed to answer them later.