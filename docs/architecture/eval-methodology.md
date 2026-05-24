# Eval Methodology

This document defines the MVP evaluation approach for AgentOps Workbench.

The goal is not to build a perfect eval platform immediately. The goal is to show that agent quality can be tested, tracked, and debugged.

## MVP eval goal

For the incident triage agent, evals should check whether the answer:

- identifies a plausible root cause
- cites useful evidence
- recommends safe next steps
- avoids unsupported certainty
- follows the structured output schema

## Eval case format

Each eval case should include:

- name
- task
- expected_keywords
- expected_failure_modes
- minimum_score

## Example expected keywords

For the Kafka duplicate key incident, useful keywords may include:

- duplicate key
- retry exhaustion
- idempotency
- replay
- ordering
- stale state
- existing record
- database constraint
- next steps

## Example failure modes

Bad answers may:

- claim certainty without enough evidence
- ignore duplicate key violation
- ignore retries
- recommend deleting production data without investigation
- fail to mention idempotency or replay
- return unstructured output
- omit next steps

## Scoring

Start with a simple deterministic score.

Suggested scoring:

- schema valid: 30 points
- contains important root cause keywords: 30 points
- includes useful next steps: 25 points
- includes evidence: 15 points

Total: 100 points.

Passing threshold:

- 70 or higher

## Why deterministic first

LLM-as-judge can be added later, but deterministic evals are better for the MVP because they are:

- easier to understand
- easier to debug
- cheaper
- repeatable
- good enough for demo quality checks

## Eval result output

Each eval result should show:

- passed
- score
- found keywords
- missing keywords
- notes
- linked run id

## Future eval improvements

Later versions may add:

- LLM-as-judge
- regression tracking over time
- comparison across models
- cost and latency thresholds
- golden dataset management
- human review workflow
- CI-based eval runs
