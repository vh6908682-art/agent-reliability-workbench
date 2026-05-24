# Ticket 013 — Guardrail Policy Checks

## Goal

Add a simple backend guardrail layer for incident triage agent outputs.

The guardrail layer should check whether an agent result is safe, complete, and reviewable before it is treated as ready for action.

## Why this matters

Production agent systems should not blindly trust generated recommendations.

AgentOps Workbench should show that agent outputs can be checked against policy before release or approval.

## Scope

Implement a lightweight guardrail checker for the golden-path incident triage output.

The checker should inspect the structured output and return policy check results.

Initial checks should include:

- Diagnosis is present
- Recommended next steps are present
- Evidence is present
- Confidence is present if required by the schema
- No destructive action is recommended without human approval
- No unsupported certainty language is used
- Output passed structured validation before guardrail approval

## Non-goals

Do not build a full policy engine.

Do not add external moderation services.

Do not add complex DSL rules.

Do not block every possible risky recommendation.

Do not build the frontend approval UI in this ticket.

## Expected implementation shape

Add a backend module similar to:

    backend/app/guardrails/checker.py

Possible functions:

    run_guardrail_checks(agent_output)
    check_required_fields(agent_output)
    check_destructive_actions(agent_output)
    check_unsupported_certainty(agent_output)

Each check should return a simple result object like:

    {
      "name": "required_fields_present",
      "passed": true,
      "severity": "error",
      "message": "Diagnosis and next steps are present."
    }

The full guardrail result can look like:

    {
      "passed": true,
      "checks": [
        {
          "name": "required_fields_present",
          "passed": true,
          "severity": "error",
          "message": "Required fields are present."
        }
      ]
    }

## Policy examples

Destructive or risky next steps should require approval.

Examples of risky recommendations:

    Delete the customer record.
    Drop the database constraint.
    Disable retries permanently.
    Purge the Kafka topic.
    Ignore duplicate key errors.

Safer recommendations should pass.

Examples of safer recommendations:

    Check idempotency key generation.
    Inspect existing customer record before retrying.
    Verify whether the event was already processed.
    Review unique constraint and upsert behavior.
    Add an idempotent write path.

## Acceptance criteria

- Backend has a guardrail checker module
- Guardrail checker returns pass/fail result
- Check-level details include name, passed, severity, and message
- Missing diagnosis fails guardrails
- Missing recommended next steps fails guardrails
- Missing evidence fails guardrails
- Risky destructive actions fail or require approval
- Safe incident triage recommendations pass
- Guardrail result can be attached to an agent run result
- Existing tests pass

## Suggested tests

Add tests for:

- Safe output passes guardrails
- Missing diagnosis fails
- Missing recommended next steps fails
- Missing evidence fails
- Destructive recommendation fails
- Unsupported certainty language fails or warns
- Multiple checks are returned together

## Codex guidance

Keep this deterministic and simple.

Use keyword-based checks for the first version.

Do not introduce a policy engine.

Do not call another LLM for guardrail checks.

Reuse existing structured output models where possible.

