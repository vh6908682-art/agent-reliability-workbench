# Runbook: Retry and Idempotency

Retries are useful for transient failures, but they can amplify non-transient failures.

A retry is safe only when the operation is idempotent or when duplicate work is explicitly handled.

## Transient failures

Retry may help with:

- temporary network issues
- temporary database connection failures
- rate limits
- downstream service timeout
- lock timeout

## Non-transient failures

Retry usually will not help with:

- duplicate key violations
- invalid payload shape
- missing required business keys
- authorization failures
- permanent schema mismatch

## Idempotency checklist

For message consumers:

1. Use a stable event id or business key.
2. Record whether an event has already been processed.
3. Make writes update-safe when possible.
4. Prefer upsert only when business rules allow it.
5. Avoid creating duplicate child records on replay.
6. Log the event id, customer id, constraint name, and retry count.
7. Do not acknowledge messages that failed before durable processing.

## Incident guidance

When retries are exhausted after a duplicate key violation, treat the failure as likely non-transient.

Recommended next steps:

- inspect the existing row
- compare existing state with incoming event
- verify whether the event was replayed
- verify whether insert should become update or upsert
- add idempotency protection before replaying the message
