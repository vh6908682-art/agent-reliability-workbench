# Ticket 014 — Human Approval Workflow

## Goal

Add a basic human approval workflow for incident triage agent recommendations.

The system should allow an agent run to be marked as pending approval, approved, or blocked based on human review.

## Why this matters

Production agent systems often need human-in-the-loop review before recommendations become actions.

AgentOps Workbench should demonstrate that risky or important outputs can be reviewed before release.

## Scope

Implement backend support for approval status on agent runs or recommendations.

Approval states should include:

- pending_review
- approved
- blocked

The workflow should support:

- Reading current approval status
- Approving an agent run
- Blocking an agent run
- Saving an optional reviewer note
- Showing whether guardrails required approval

## Non-goals

Do not build authentication.

Do not build user roles.

Do not build email notifications.

Do not build complex approval chains.

Do not build the full frontend approval UI unless it is very small and directly useful.

## Expected implementation shape

Add or update backend pieces similar to:

    backend/app/approvals/models.py
    backend/app/approvals/service.py
    backend/app/api/approvals.py

Possible endpoints:

    GET /api/runs/{run_id}/approval
    POST /api/runs/{run_id}/approval

Example request:

    {
      "status": "approved",
      "reviewer_note": "Recommendation looks safe. Proceed with investigation steps."
    }

Example response:

    {
      "run_id": "run_123",
      "status": "approved",
      "reviewer_note": "Recommendation looks safe. Proceed with investigation steps.",
      "requires_approval": true,
      "updated_at": "2026-01-01T00:00:00Z"
    }

## Approval behavior

If guardrails pass cleanly:

    status can default to approved or pending_review depending on current data model

If guardrails warn or fail because of risky actions:

    status should be pending_review or blocked

For the MVP, prefer simple behavior:

    New run starts as pending_review
    User can approve it
    User can block it
    Reviewer note is optional

## Acceptance criteria

- Agent run or recommendation can store approval status
- Approval status supports pending_review, approved, and blocked
- Backend exposes a way to read approval status
- Backend exposes a way to update approval status
- Optional reviewer note can be saved
- Invalid approval status is rejected
- Approval result includes run ID and updated status
- Existing tests pass

## Suggested tests

Add tests for:

- New approval starts as pending_review
- Approving a run updates status to approved
- Blocking a run updates status to blocked
- Invalid status is rejected
- Reviewer note is saved
- Reading approval status returns expected data

## Codex guidance

Keep this small.

Reuse existing run data model if possible.

Do not add auth.

Do not add roles.

Do not create a separate complex workflow engine.

