# Ticket 008 — Eval Runner

## Goal

Create a simple backend eval runner for the golden-path incident triage agent.

The eval runner should execute predefined incident triage cases from:

    seed/eval_cases/incident-triage-evals.json

It should run the agent against each case, capture the result, validate the structured output, and produce a clear pass/fail summary.

## Why this matters

AgentOps Workbench should not only run agents manually. It should show how teams evaluate whether an agent is reliable before shipping changes.

This ticket introduces the first version of the evaluation workflow.

## Scope

Implement a backend eval runner that can:

- Load eval cases from the seed JSON file
- Run each eval case through the golden-path agent loop
- Validate that each result matches the expected structured output shape
- Compare key expectations from the eval case
- Print or return a summary of pass/fail results
- Store eval run results only if the existing data model already supports it

## Non-goals

Do not build a full eval dashboard yet.

Do not introduce LangGraph.

Do not add complex scoring frameworks.

Do not call external evaluation services.

Do not over-engineer semantic grading.

## Expected implementation shape

Add a backend module similar to:

    backend/app/evals/runner.py

Possible responsibilities:

    load_eval_cases()
    run_eval_case(case)
    run_all_evals()
    summarize_eval_results(results)

Add an API endpoint only if it fits the current backend structure, for example:

    POST /api/evals/run

The endpoint may run all evals and return a JSON summary.

## Eval case behavior

Each eval case should include enough input to call the existing incident triage agent.

For each case, the runner should check:

- The agent returns valid structured output
- The diagnosis is present
- Recommended next steps are present
- At least one relevant evidence item is present
- The output does not fail schema validation
- Expected keywords or expectations from the eval case are satisfied, if available

Use simple deterministic checks first.

Example check style:

    expected keyword: duplicate key
    expected keyword: retry exhaustion
    expected category: idempotency

## Output shape

The eval runner should return a summary like:

    {
      "total": 3,
      "passed": 2,
      "failed": 1,
      "results": [
        {
          "case_id": "incident_duplicate_key_retry_exhaustion",
          "passed": true,
          "checks": [
            {
              "name": "structured_output_valid",
              "passed": true
            }
          ]
        }
      ]
    }

## Acceptance criteria

- Eval cases can be loaded from the seed eval JSON file
- All eval cases can be run with one backend function
- Each eval result includes case ID, pass/fail status, and check-level details
- Invalid structured output fails the eval
- Missing diagnosis fails the eval
- Missing recommended next steps fails the eval
- The runner produces a useful total passed/failed summary
- The implementation is simple enough to extend later
- Existing tests pass

## Suggested tests

Add tests for:

- Loading eval cases from JSON
- Running a mocked successful eval case
- Failing when structured output is invalid
- Failing when diagnosis is missing
- Failing when recommended next steps are missing
- Summary counts total, passed, and failed correctly

## Codex guidance

Keep this small.

Reuse the existing agent loop and structured output validation code from previous tickets.

Prefer deterministic checks over LLM-as-judge.

Do not introduce a new framework.

