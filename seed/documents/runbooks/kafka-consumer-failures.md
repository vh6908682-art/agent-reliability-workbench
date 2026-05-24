# Runbook: Kafka Consumer Failures

Kafka consumer failures should be investigated by separating transient infrastructure issues from deterministic message-processing issues.

## Key fields to capture

- topic
- consumer group
- partition
- offset
- event id
- customer id or business key
- retry count
- exception type
- database constraint name, if present

## Common failure categories

### Transient

- downstream timeout
- temporary database connection issue
- rebalance interruption
- lock timeout

### Non-transient

- duplicate key violation
- invalid event payload
- missing required identifier
- schema mismatch
- business rule conflict

## Investigation steps

1. Find the failed event id, partition, and offset.
2. Check whether the message was acknowledged.
3. Check whether retries were exhausted.
4. Inspect the exception type and root cause.
5. Compare incoming event data with existing database state.
6. Check whether the consumer write path is idempotent.
7. Decide whether to fix code, repair data, or replay safely.

## Safe handling

- Do not blindly skip failed messages.
- Do not delete existing data without confirming ownership and business rules.
- Preserve failed messages for replay.
- Add targeted logging before replay if evidence is insufficient.
- Prefer deterministic fixes over increasing retry count.
