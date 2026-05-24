# Runbook: Duplicate Key Violations

Duplicate key violations usually mean the application attempted to insert a row that already exists under a unique constraint.

## Common causes

- Event replay created the same record twice.
- Consumer retry logic is not idempotent.
- Application used insert when it should have used upsert.
- The lookup path missed an existing record because of stale or incomplete state.
- Event ordering caused an update to arrive before linkage data was available.
- Two workers processed logically overlapping records.

## Investigation steps

1. Identify the unique constraint that failed.
2. Extract the key values from the error detail.
3. Check whether the record already exists in the database.
4. Check whether the message was replayed or retried.
5. Check whether the write path is idempotent.
6. Check whether the consumer should update an existing row instead of inserting.
7. Check recent deployments or schema changes.
8. Review related trace events and upstream event history.

## Safe next steps

- Do not delete production data as a first action.
- Preserve the failed message for replay after the fix.
- Add idempotency around the write path.
- Consider upsert behavior if business rules allow it.
- Add logging for lookup result, constraint name, and key fields.
