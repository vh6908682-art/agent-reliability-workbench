# Schema: Customer Update Event

This document describes the mock customer update event used in the MVP demo.

## Event name

CustomerUpdated

## Purpose

Represents an upstream customer profile change that should update customer contact records in the modern customer domain database.

## Important fields

- event_id
- event_type
- occurred_at
- customer_id
- legacy_involvement_id
- changed_fields
- email
- phone
- address

## Example payload shape

- event_id: cust-upd-88312
- event_type: CustomerUpdated
- customer_id: C-104882
- legacy_involvement_id: null
- changed_fields: email, phone, address
- phone.type: PRIMARY_PHONE

## Processing expectations

The consumer should:

- validate required identifiers
- check existing customer state
- avoid duplicate contact rows
- update existing contact records when appropriate
- preserve failed messages for replay
- log enough evidence for debugging

## Known risk

If a customer contact row already exists but the consumer attempts a fresh insert, the database may raise a duplicate key violation.

This is especially likely when:

- an event is replayed
- retry logic repeats a non-idempotent insert
- linkage data is incomplete
- the consumer misses an existing record during lookup
